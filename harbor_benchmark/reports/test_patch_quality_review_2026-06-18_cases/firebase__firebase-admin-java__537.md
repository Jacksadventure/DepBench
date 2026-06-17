# Test-patch audit - firebase__firebase-admin-java__537

## 1. Task summary
- Folder: firebase__firebase-admin-java__537
- Ecosystem: maven
- Upgrade: google-api-client-bom 1.30.10 -> 1.31.4
- test_cmd: Maven test command selecting Firebase Admin Java unit tests such as `OutgoingHttpRequestTest`, `FirebaseCustomTokenTest`, auth/page tests, messaging tests, and remote-config tests.

## 2. What is the breaking change?
The BOM upgrade changes the Google API client defaults enough that Firebase stops using direct `com.google.api.client.googleapis.util.Utils` calls. Delta c introduces `ApiClientUtils`, forcing `NetHttpTransport` and `JacksonFactory`, and routes production JSON/transport construction through that helper.

## 3. What does Delta t (test.patch) actually do?
It updates a broad set of Firebase tests to import and use `com.google.firebase.internal.ApiClientUtils` instead of `Utils.getDefaultJsonFactory()` / `Utils.getDefaultTransport()`.

## 4. Does Delta t directly exercise the breaking change?
Yes. The patched tests compile against and use the new internal helper added by Delta c, and the selected test suite covers JSON parsing/serialization and HTTP-client setup paths that formerly used `Utils` directly. Without Delta c, the tests fail at compile time because `ApiClientUtils` is absent; with Delta c, the tests validate the new default parser/transport path.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE - the evidence is a source/API compile and behavior witness inside the Java test suite, not lint or dependency resolution.

## 6. Delta c nature
REAL_SOURCE_REPAIR - production Java source changes replace direct API-client utility calls and add the internal helper; minor whitespace cleanup is incidental.

## 7. Soundness concerns / notes
- The hidden tests are tightly coupled to the helper introduced by the oracle repair, but that helper is the intended compatibility layer for the dependency upgrade.
