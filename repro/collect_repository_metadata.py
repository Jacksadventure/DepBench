#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Collect GitHub repository metadata for the released benchmark tasks."""

from __future__ import annotations

import argparse
import csv
import json
import os
import subprocess
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


API_ROOT = "https://api.github.com"
API_VERSION = "2022-11-28"

LICENSE_OVERRIDES = {
    "Graylog2/graylog2-server": {
        "license_spdx_id": "SSPL-1.0",
        "license_name": "Server Side Public License 1.0",
        "license_file_url": "https://github.com/Graylog2/graylog2-server/blob/master/LICENSE",
        "license_status": "verified_license_file",
        "license_category": "source_available",
        "license_source": "repository_license_file",
    },
    "INRIA/spoon": {
        "license_spdx_id": "MIT OR CECILL-C",
        "license_name": "MIT License or CeCILL-C",
        "license_file_url": "https://github.com/INRIA/spoon/blob/master/README.md#license",
        "license_status": "verified_license_file",
        "license_category": "open_source",
        "license_source": "repository_license_files_and_readme",
    },
    "apexskier/github-release-commenter": {
        "license_spdx_id": "MIT",
        "license_name": "MIT License",
        "license_file_url": "https://github.com/apexskier/github-release-commenter/blob/main/package.json",
        "license_status": "verified_package_metadata",
        "license_category": "open_source",
        "license_source": "package_json",
    },
    "bbc/simorgh": {
        "license_spdx_id": "Apache-2.0",
        "license_name": "Apache License 2.0",
        "license_file_url": "https://github.com/bbc/simorgh/blob/latest/LICENSE",
        "license_status": "verified_license_file",
        "license_category": "open_source",
        "license_source": "repository_license_file",
    },
    "chainflip-io/chainflip-sdk-monorepo": {
        "license_spdx_id": "ISC",
        "license_name": "ISC License",
        "license_file_url": "https://github.com/chainflip-io/chainflip-sdk-monorepo/blob/main/package.json",
        "license_status": "verified_package_metadata",
        "license_category": "open_source",
        "license_source": "package_json",
    },
    "cryostatio/cryostat-legacy": {
        "license_spdx_id": "Apache-2.0",
        "license_name": "Apache License 2.0",
        "license_file_url": "https://github.com/cryostatio/cryostat-legacy/blob/main/LICENSE.txt",
        "license_status": "verified_license_file",
        "license_category": "open_source",
        "license_source": "repository_license_file",
    },
    "databricks/cli": {
        "license_spdx_id": "LicenseRef-Databricks",
        "license_name": "Databricks License",
        "license_file_url": "https://github.com/databricks/cli/blob/main/LICENSE",
        "license_status": "verified_license_file",
        "license_category": "custom",
        "license_source": "repository_license_file",
    },
    "elastic/cloud-on-k8s": {
        "license_spdx_id": "Elastic-2.0",
        "license_name": "Elastic License 2.0",
        "license_file_url": "https://github.com/elastic/cloud-on-k8s/blob/main/LICENSE.txt",
        "license_status": "verified_license_file",
        "license_category": "source_available",
        "license_source": "repository_license_file",
    },
    "kanton-bern/hellodata-be": {
        "license_spdx_id": "BSD-3-Clause",
        "license_name": "BSD 3-Clause License",
        "license_file_url": "https://github.com/kanton-bern/hellodata-be/blob/develop/LICENSE",
        "license_status": "verified_license_file",
        "license_category": "open_source",
        "license_source": "repository_license_file",
    },
    "libp2p/js-libp2p-bootstrap": {
        "license_spdx_id": "MIT OR Apache-2.0",
        "license_name": "MIT License or Apache License 2.0",
        "license_file_url": "https://github.com/libp2p/js-libp2p-bootstrap/blob/master/LICENSE",
        "license_status": "verified_license_file",
        "license_category": "open_source",
        "license_source": "repository_license_file",
    },
    "liquibase/liquibase": {
        "license_spdx_id": "FSL-1.1-ALv2",
        "license_name": "Functional Source License 1.1, ALv2 Future License",
        "license_file_url": "https://github.com/liquibase/liquibase/blob/main/LICENSE.txt",
        "license_status": "verified_license_file",
        "license_category": "source_available",
        "license_source": "repository_license_file",
    },
    "matsim-org/matsim-libs": {
        "license_spdx_id": "GPL-2.0-or-later",
        "license_name": "GNU General Public License v2.0 or later",
        "license_file_url": "https://github.com/matsim-org/matsim-libs/blob/main/matsim/LICENSE",
        "license_status": "verified_license_file",
        "license_category": "open_source",
        "license_source": "repository_license_file",
    },
    "mitre/heimdall2": {
        "license_spdx_id": "LicenseRef-Apache-2.0-with-MITRE-terms",
        "license_name": "Apache License 2.0 with MITRE additional terms",
        "license_file_url": "https://github.com/mitre/heimdall2/blob/master/LICENSE.md",
        "license_status": "verified_license_file",
        "license_category": "custom",
        "license_source": "repository_license_file",
    },
    "nearform/brokeneck": {
        "license_spdx_id": "NOASSERTION",
        "license_name": "No repository-level license declared",
        "license_file_url": "",
        "license_status": "not_declared",
        "license_category": "not_declared",
        "license_source": "repository_and_package_metadata_review",
    },
    "opengovsg/askgovsg": {
        "license_spdx_id": "LicenseRef-MIT-with-GovTech-terms",
        "license_name": "MIT License with GovTech Singapore additional terms",
        "license_file_url": "https://github.com/opengovsg/askgovsg/blob/develop/LICENSE",
        "license_status": "verified_license_file",
        "license_category": "custom",
        "license_source": "repository_license_file",
    },
    "opentripplanner/OpenTripPlanner": {
        "license_spdx_id": "LGPL-3.0-or-later",
        "license_name": "GNU Lesser General Public License v3.0 or later",
        "license_file_url": "https://github.com/opentripplanner/OpenTripPlanner/blob/dev-2.x/LICENSE",
        "license_status": "verified_license_file",
        "license_category": "open_source",
        "license_source": "repository_license_file",
    },
    "sourcenetwork/defradb": {
        "license_spdx_id": "BUSL-1.1",
        "license_name": "Business Source License 1.1",
        "license_file_url": "https://github.com/sourcenetwork/defradb/blob/develop/licenses/BSL.txt",
        "license_status": "verified_license_file",
        "license_category": "source_available",
        "license_source": "repository_license_file",
    },
    "yahoo/elide": {
        "license_spdx_id": "Apache-2.0",
        "license_name": "Apache License 2.0",
        "license_file_url": "https://github.com/yahoo/elide/blob/master/LICENSE.txt",
        "license_status": "verified_license_file",
        "license_category": "open_source",
        "license_source": "repository_license_file",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tasks-dir", type=Path, default=Path("dataset/tasks"))
    parser.add_argument("--output-dir", type=Path, default=Path("analysis"))
    parser.add_argument(
        "--token-env",
        default="GH_TOKEN",
        help="environment variable containing a GitHub token",
    )
    return parser.parse_args()


def task_repository(task: str) -> str:
    repository_key, separator, pull_request = task.rpartition("__")
    if not separator or not pull_request.isdigit() or "__" not in repository_key:
        raise ValueError(f"unexpected task folder name: {task}")
    owner, repository = repository_key.split("__", 1)
    return f"{owner}/{repository}"


def github_get(path: str, token: str) -> dict:
    request = urllib.request.Request(
        f"{API_ROOT}{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "User-Agent": "depbench-repository-metadata",
            "X-GitHub-Api-Version": API_VERSION,
        },
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            if error.code != 403 or attempt == 3:
                raise
        except urllib.error.URLError:
            if attempt == 3:
                raise
        time.sleep(2**attempt)
    raise RuntimeError(f"failed to fetch {path}")


def license_metadata(repository: str, token: str, repo_data: dict) -> dict:
    canonical_repository = repo_data["full_name"]
    if canonical_repository in LICENSE_OVERRIDES:
        return LICENSE_OVERRIDES[canonical_repository]

    license_data = repo_data.get("license") or {}
    license_file_url = ""
    try:
        detected = github_get(f"/repos/{repository}/license", token)
        license_data = detected.get("license") or license_data
        license_file_url = detected.get("html_url") or ""
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise

    spdx_id = license_data.get("spdx_id") or ""
    name = license_data.get("name") or ""
    if not spdx_id and not name:
        status = "not_detected"
    elif spdx_id == "NOASSERTION":
        status = "detected_non_spdx"
    else:
        status = "detected"
    return {
        "license_spdx_id": spdx_id,
        "license_name": name,
        "license_file_url": license_file_url,
        "license_status": f"github_{status}",
        "license_category": "open_source" if status == "detected" else "unreviewed",
        "license_source": "github_license_api",
    }


def release_commit() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    token = os.environ.get(args.token_env)
    if not token:
        raise SystemExit(f"{args.token_env} is required")

    tasks = sorted(path.name for path in args.tasks_dir.iterdir() if path.is_dir())
    repository_tasks: dict[str, list[str]] = defaultdict(list)
    for task in tasks:
        repository_tasks[task_repository(task)].append(task)

    repository_rows = []
    for index, (repository, repo_tasks) in enumerate(sorted(repository_tasks.items()), 1):
        print(f"[{index}/{len(repository_tasks)}] {repository}", flush=True)
        repo_data = github_get(f"/repos/{repository}", token)
        license_data = license_metadata(repository, token, repo_data)
        repository_rows.append(
            {
                "source_repository": repository,
                "canonical_repository": repo_data["full_name"],
                "repository_url": repo_data["html_url"],
                **license_data,
                "primary_language": repo_data.get("language") or "",
                "archived": str(bool(repo_data.get("archived"))).lower(),
                "task_count": len(repo_tasks),
                "tasks": ";".join(repo_tasks),
            }
        )

    repository_by_source = {
        row["source_repository"]: row for row in repository_rows
    }
    task_rows = []
    for task in tasks:
        source_repository = task_repository(task)
        repository = repository_by_source[source_repository]
        task_rows.append(
            {
                "task": task,
                "source_repository": source_repository,
                "canonical_repository": repository["canonical_repository"],
                "repository_url": repository["repository_url"],
                "license_spdx_id": repository["license_spdx_id"],
                "license_name": repository["license_name"],
                "license_file_url": repository["license_file_url"],
                "license_status": repository["license_status"],
                "license_category": repository["license_category"],
                "license_source": repository["license_source"],
                "primary_language": repository["primary_language"],
                "archived": repository["archived"],
            }
        )

    args.output_dir.mkdir(parents=True, exist_ok=True)
    repository_fields = [
        "source_repository",
        "canonical_repository",
        "repository_url",
        "license_spdx_id",
        "license_name",
        "license_file_url",
        "license_status",
        "license_category",
        "license_source",
        "primary_language",
        "archived",
        "task_count",
        "tasks",
    ]
    task_fields = [
        "task",
        "source_repository",
        "canonical_repository",
        "repository_url",
        "license_spdx_id",
        "license_name",
        "license_file_url",
        "license_status",
        "license_category",
        "license_source",
        "primary_language",
        "archived",
    ]
    write_csv(
        args.output_dir / "repository_metadata.csv",
        repository_rows,
        repository_fields,
    )
    write_csv(
        args.output_dir / "task_repository_metadata.csv",
        task_rows,
        task_fields,
    )

    document = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_release_commit": release_commit(),
        "task_count": len(task_rows),
        "repository_count": len(repository_rows),
        "repositories": repository_rows,
    }
    (args.output_dir / "repository_metadata.json").write_text(
        json.dumps(document, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
