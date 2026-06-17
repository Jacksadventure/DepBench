# Test-patch audit — nextcloud__spreed__9915

## 1. Task summary
- Folder: nextcloud__spreed__9915
- Ecosystem: npm_and_yarn
- Upgrade: webdav 4.11.2 -> 5.2.2
- test_cmd: `npx jest src/store/fileUploadStore.spec.js --colors=false`

## 2. What is the breaking change?
webdav v5 changes the client/request integration and upload payload expectations. The repair stops patching webdav's request layer with axios, creates the client with request-token headers, and converts `File`/`Blob` uploads to `ArrayBuffer` before calling `putFileContents`.

## 3. What does Δt (test.patch) actually do?
The file upload store test now mocks `DavClient` explicitly, builds expected `ArrayBuffer` values from the uploaded files, and asserts that `putFileContents` receives those buffers. It also adds a `webdav` mock module.

## 4. Does Δt directly exercise the breaking change?
Yes. Without Δc, `fileUploadStore` passes the `File` object directly to `putFileContents`; the hidden test expects the new ArrayBuffer payload required by the upgraded webdav client behavior.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — Δt directly checks the new upload payload contract that Δc implements.

## 6. Δc nature
MIXED — real production repairs in `DavClient.js`, `fileUploadStore.js`, and `VideoBackgroundEditor.vue`, plus a test-environment polyfill in `src/test-setup.js`.

## 7. Soundness concerns / notes
- The verifier targets only `fileUploadStore.spec.js`, so the `VideoBackgroundEditor.vue` half of the repair is not directly exercised.
- The store upload path is a direct and sufficient witness for the webdav payload change.

