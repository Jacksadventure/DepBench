#!/usr/bin/env python3
"""Estimate and pull Docker images referenced by Harbor task.toml files."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import platform as py_platform
import random
import re
import subprocess
import sys
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests
import tomllib


DEFAULT_TASKS_ROOT = Path("harbor_benchmark/tasks_v4")
MANIFEST_ACCEPT = ", ".join(
    [
        "application/vnd.oci.image.index.v1+json",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        "application/vnd.oci.image.manifest.v1+json",
        "application/vnd.docker.distribution.manifest.v2+json",
    ]
)
LIST_MEDIA_TYPES = {
    "application/vnd.oci.image.index.v1+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
}
MANIFEST_MEDIA_TYPES = {
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.docker.distribution.manifest.v2+json",
}


@dataclass(frozen=True)
class ImageRef:
    original: str
    registry: str
    repository: str
    reference: str

    @property
    def registry_url(self) -> str:
        if self.registry == "docker.io":
            return "registry-1.docker.io"
        return self.registry


@dataclass
class Estimate:
    image: str
    ok: bool
    bytes_total: int = 0
    descriptor_count: int = 0
    manifest_digest: str | None = None
    error: str | None = None
    descriptors: tuple[tuple[str, int], ...] = ()


@dataclass
class PullResult:
    image: str
    ok: bool
    attempts: int
    elapsed_sec: float
    error: str | None = None


class RegistryClient:
    def __init__(self, timeout: float, retries: int) -> None:
        self.timeout = timeout
        self.retries = retries
        self._tokens: dict[tuple[str, str], str] = {}
        self._lock = threading.Lock()
        self._local = threading.local()

    @property
    def session(self) -> requests.Session:
        if not hasattr(self._local, "session"):
            self._local.session = requests.Session()
        return self._local.session

    def get_manifest(self, ref: ImageRef, reference: str) -> tuple[dict[str, Any], str | None]:
        path = f"/v2/{ref.repository}/manifests/{reference}"
        url = f"https://{ref.registry_url}{path}"
        headers = {"Accept": MANIFEST_ACCEPT}
        for attempt in range(1, self.retries + 1):
            try:
                response = self.session.get(url, headers=headers, timeout=self.timeout)
                if response.status_code == 401:
                    token = self._get_bearer_token(ref, response.headers.get("WWW-Authenticate", ""))
                    response = self.session.get(
                        url,
                        headers={**headers, "Authorization": f"Bearer {token}"},
                        timeout=self.timeout,
                    )
                if response.status_code in {429, 500, 502, 503, 504}:
                    raise RuntimeError(f"registry returned HTTP {response.status_code}")
                response.raise_for_status()
                return response.json(), response.headers.get("Docker-Content-Digest")
            except Exception:
                if attempt == self.retries:
                    raise
                self._sleep_before_retry(attempt)
        raise AssertionError("unreachable")

    def _get_bearer_token(self, ref: ImageRef, challenge: str) -> str:
        params = self._parse_www_authenticate(challenge)
        realm = params.get("realm")
        service = params.get("service")
        scope = params.get("scope", f"repository:{ref.repository}:pull")
        if not realm:
            raise RuntimeError(f"registry {ref.registry_url} requested auth without a realm")
        cache_key = (ref.registry_url, scope)
        with self._lock:
            cached = self._tokens.get(cache_key)
        if cached:
            return cached
        query = {k: v for k, v in {"service": service, "scope": scope}.items() if v}
        token_url = f"{realm}?{urlencode(query)}"
        response = self.session.get(token_url, timeout=self.timeout)
        response.raise_for_status()
        payload = response.json()
        token = payload.get("token") or payload.get("access_token")
        if not token:
            raise RuntimeError(f"token endpoint did not return a token for {ref.repository}")
        with self._lock:
            self._tokens[cache_key] = token
        return token

    @staticmethod
    def _parse_www_authenticate(value: str) -> dict[str, str]:
        if value.lower().startswith("bearer "):
            value = value[7:]
        return {m.group(1): m.group(2) for m in re.finditer(r'(\w+)="([^"]*)"', value)}

    @staticmethod
    def _sleep_before_retry(attempt: int) -> None:
        time.sleep(min(30.0, 0.75 * (2 ** (attempt - 1))) + random.random())


def parse_image_ref(image: str) -> ImageRef:
    name = image
    reference = "latest"
    if "@" in name:
        name, reference = name.rsplit("@", 1)
    else:
        last_slash = name.rfind("/")
        last_colon = name.rfind(":")
        if last_colon > last_slash:
            name, reference = name[:last_colon], name[last_colon + 1 :]

    parts = name.split("/", 1)
    if len(parts) == 2 and (
        "." in parts[0] or ":" in parts[0] or parts[0] == "localhost"
    ):
        registry, repository = parts
    else:
        registry = "docker.io"
        repository = name
        if "/" not in repository:
            repository = f"library/{repository}"
    return ImageRef(original=image, registry=registry, repository=repository, reference=reference)


def parse_platform(value: str) -> tuple[str, str, str | None]:
    bits = value.split("/")
    if len(bits) < 2:
        raise ValueError(f"platform must look like os/arch, got {value!r}")
    variant = bits[2] if len(bits) > 2 else None
    return bits[0], bits[1], variant


def detect_docker_platform() -> str:
    arch_map = {"x86_64": "amd64", "aarch64": "arm64"}
    try:
        output = subprocess.check_output(
            ["docker", "info", "--format", "{{.OSType}}/{{.Architecture}}"],
            text=True,
            stderr=subprocess.DEVNULL,
            timeout=10,
        ).strip()
        if output and "<no value>" not in output:
            os_name, arch, *rest = output.split("/")
            variant = f"/{rest[0]}" if rest else ""
            return f"{os_name}/{arch_map.get(arch, arch)}{variant}"
    except Exception:
        pass
    machine = py_platform.machine().lower()
    return f"linux/{arch_map.get(machine, machine)}"


def collect_images(tasks_root: Path, image_file: Path | None) -> list[str]:
    images: list[str] = []
    if image_file:
        for line in image_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                images.append(line)

    for task_toml in sorted(tasks_root.glob("*/task.toml")):
        try:
            data = tomllib.loads(task_toml.read_text())
        except Exception as exc:
            raise RuntimeError(f"failed to parse {task_toml}: {exc}") from exc
        image = data.get("environment", {}).get("docker_image")
        if image:
            images.append(str(image))

    return sorted(dict.fromkeys(images))


def estimate_image(client: RegistryClient, image: str, target_platform: str) -> Estimate:
    try:
        ref = parse_image_ref(image)
        manifest, digest = client.get_manifest(ref, ref.reference)
        media_type = manifest.get("mediaType")
        if media_type in LIST_MEDIA_TYPES:
            child = select_platform_manifest(manifest, target_platform)
            manifest, digest = client.get_manifest(ref, child["digest"])
            media_type = manifest.get("mediaType")
        if media_type not in MANIFEST_MEDIA_TYPES:
            raise RuntimeError(f"unsupported manifest media type {media_type!r}")

        descriptors: list[tuple[str, int]] = []
        config = manifest.get("config") or {}
        if config.get("digest") and isinstance(config.get("size"), int):
            descriptors.append((config["digest"], int(config["size"])))
        for layer in manifest.get("layers") or []:
            digest_value = layer.get("digest")
            size = layer.get("size")
            if digest_value and isinstance(size, int):
                descriptors.append((digest_value, int(size)))
        return Estimate(
            image=image,
            ok=True,
            bytes_total=sum(size for _, size in descriptors),
            descriptor_count=len(descriptors),
            manifest_digest=digest,
            descriptors=tuple(descriptors),
        )
    except Exception as exc:
        return Estimate(image=image, ok=False, error=str(exc))


def select_platform_manifest(index: dict[str, Any], target_platform: str) -> dict[str, Any]:
    target_os, target_arch, target_variant = parse_platform(target_platform)
    candidates = index.get("manifests") or []
    fallback = None
    for child in candidates:
        child_platform = child.get("platform") or {}
        if child_platform.get("os") != target_os or child_platform.get("architecture") != target_arch:
            continue
        if target_variant is None or child_platform.get("variant") == target_variant:
            return child
        fallback = fallback or child
    if fallback:
        return fallback
    available = ", ".join(
        "/".join(
            str(part)
            for part in (
                (child.get("platform") or {}).get("os", "?"),
                (child.get("platform") or {}).get("architecture", "?"),
                (child.get("platform") or {}).get("variant"),
            )
            if part
        )
        for child in candidates
    )
    raise RuntimeError(f"no manifest for {target_platform}; available: {available or 'unknown'}")


def image_is_present(image: str) -> bool:
    return (
        subprocess.run(
            ["docker", "image", "inspect", image],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).returncode
        == 0
    )


def pull_image(image: str, platform: str | None, quiet: bool, retries: int) -> PullResult:
    started = time.monotonic()
    last_error = None
    for attempt in range(1, retries + 1):
        cmd = ["docker", "pull"]
        if platform:
            cmd.extend(["--platform", platform])
        if quiet:
            cmd.append("-q")
        cmd.append(image)
        proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if proc.returncode == 0:
            return PullResult(image=image, ok=True, attempts=attempt, elapsed_sec=time.monotonic() - started)
        last_error = (proc.stdout or "").strip() or f"docker pull exited {proc.returncode}"
        if attempt < retries:
            time.sleep(min(60.0, 2.0 * (2 ** (attempt - 1))) + random.random())
    return PullResult(
        image=image,
        ok=False,
        attempts=retries,
        elapsed_sec=time.monotonic() - started,
        error=last_error,
    )


def human_bytes(num_bytes: int) -> str:
    value = float(num_bytes)
    for unit in ["B", "KiB", "MiB", "GiB", "TiB"]:
        if value < 1024 or unit == "TiB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{value:.1f} TiB"


def print_estimate_summary(estimates: list[Estimate], present: set[str]) -> None:
    ok = [item for item in estimates if item.ok]
    failed = [item for item in estimates if not item.ok]
    all_descriptors: dict[str, int] = {}
    missing_descriptors: dict[str, int] = {}
    for item in ok:
        for digest, size in item.descriptors:
            all_descriptors.setdefault(digest, size)
            if item.image not in present:
                missing_descriptors.setdefault(digest, size)

    print("\nEstimate")
    print(f"  Images discovered:        {len(estimates)}")
    print(f"  Manifests estimated:      {len(ok)}")
    print(f"  Already present locally:  {len(present)}")
    print(f"  Failed estimates:         {len(failed)}")
    print(
        "  Unique compressed total: "
        f"{human_bytes(sum(all_descriptors.values()))} "
        f"({len(all_descriptors)} unique configs/layers)"
    )
    print(
        "  Excluding present refs:   "
        f"{human_bytes(sum(missing_descriptors.values()))} "
        f"({len(missing_descriptors)} unique configs/layers)"
    )
    print(
        "  Note: Docker may download less if it already has shared layers; "
        "registry manifests expose compressed layer sizes, not exact local-cache deltas."
    )
    if failed:
        print("\nEstimate failures")
        for item in failed[:20]:
            print(f"  - {item.image}: {item.error}")
        if len(failed) > 20:
            print(f"  ... {len(failed) - 20} more")


def write_json_report(path: Path, estimates: list[Estimate], pulls: list[PullResult]) -> None:
    payload = {
        "estimates": [
            {
                "image": item.image,
                "ok": item.ok,
                "bytes_total": item.bytes_total,
                "descriptor_count": item.descriptor_count,
                "manifest_digest": item.manifest_digest,
                "error": item.error,
            }
            for item in estimates
        ],
        "pulls": [
            {
                "image": item.image,
                "ok": item.ok,
                "attempts": item.attempts,
                "elapsed_sec": round(item.elapsed_sec, 3),
                "error": item.error,
            }
            for item in pulls
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Estimate and pull Docker images from harbor_benchmark/tasks_v4 task.toml files."
    )
    parser.add_argument("--tasks-root", type=Path, default=DEFAULT_TASKS_ROOT)
    parser.add_argument("--image-file", type=Path, help="Optional newline-delimited image list.")
    parser.add_argument("--platform", help="Target platform, e.g. linux/amd64. Defaults to Docker daemon platform.")
    parser.add_argument("--metadata-concurrency", type=int, default=32)
    parser.add_argument("--pull-concurrency", type=int, default=12)
    parser.add_argument("--retries", type=int, default=4)
    parser.add_argument("--timeout", type=float, default=30.0, help="Registry request timeout in seconds.")
    parser.add_argument("--skip-present", action="store_true", help="Do not pull refs already present locally.")
    parser.add_argument("--dry-run", action="store_true", help="Estimate only; do not pull.")
    parser.add_argument("--yes", action="store_true", help="Do not prompt after the estimate.")
    parser.add_argument("--verbose-pull", action="store_true", help="Show docker pull progress output.")
    parser.add_argument("--json-report", type=Path, help="Write estimates and pull results as JSON.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    platform = args.platform or detect_docker_platform()
    images = collect_images(args.tasks_root, args.image_file)
    if not images:
        print("No images found.", file=sys.stderr)
        return 2

    print(f"Discovered {len(images)} unique images from {args.tasks_root}")
    print(f"Estimating compressed sizes for platform {platform} ...")

    client = RegistryClient(timeout=args.timeout, retries=args.retries)
    estimates: list[Estimate] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.metadata_concurrency) as executor:
        futures = {executor.submit(estimate_image, client, image, platform): image for image in images}
        for idx, future in enumerate(concurrent.futures.as_completed(futures), 1):
            estimate = future.result()
            estimates.append(estimate)
            if idx % 25 == 0 or idx == len(futures):
                print(f"  estimated {idx}/{len(futures)}", flush=True)
    estimates.sort(key=lambda item: item.image)

    present = {image for image in images if image_is_present(image)}
    print_estimate_summary(estimates, present)

    pulls: list[PullResult] = []
    if args.dry_run:
        if args.json_report:
            write_json_report(args.json_report, estimates, pulls)
        return 0

    if not args.yes:
        answer = input("\nProceed with docker pull? [y/N] ").strip().lower()
        if answer not in {"y", "yes"}:
            print("Aborted before pulling.")
            if args.json_report:
                write_json_report(args.json_report, estimates, pulls)
            return 0

    pull_images = [image for image in images if not (args.skip_present and image in present)]
    print(f"\nPulling {len(pull_images)} images with concurrency {args.pull_concurrency} ...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.pull_concurrency) as executor:
        futures = {
            executor.submit(
                pull_image,
                image,
                args.platform,
                not args.verbose_pull,
                args.retries,
            ): image
            for image in pull_images
        }
        for idx, future in enumerate(concurrent.futures.as_completed(futures), 1):
            result = future.result()
            pulls.append(result)
            status = "ok" if result.ok else "FAIL"
            print(
                f"  [{idx}/{len(futures)}] {status} {result.image} "
                f"({result.attempts} attempt(s), {result.elapsed_sec:.1f}s)",
                flush=True,
            )
    pulls.sort(key=lambda item: item.image)

    failed_pulls = [item for item in pulls if not item.ok]
    print("\nPull summary")
    print(f"  Pulled successfully: {len(pulls) - len(failed_pulls)}")
    print(f"  Failed:              {len(failed_pulls)}")
    if failed_pulls:
        for item in failed_pulls[:20]:
            print(f"  - {item.image}: {item.error}")
        if len(failed_pulls) > 20:
            print(f"  ... {len(failed_pulls) - 20} more")

    if args.json_report:
        write_json_report(args.json_report, estimates, pulls)
        print(f"JSON report written to {args.json_report}")

    return 1 if failed_pulls else 0


if __name__ == "__main__":
    raise SystemExit(main())
