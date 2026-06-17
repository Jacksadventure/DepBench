# Test-patch audit — nearform__brokeneck__820

## 1. Task summary
- Folder: nearform__brokeneck__820
- Ecosystem: npm_and_yarn
- Upgrade: react-router-dom 5.2.0 -> 6.4.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `npx jest --ci`

## 2. What is the breaking change?
react-router-dom 6 removes/replaces v5 APIs such as `Switch`, `Redirect`, `useHistory`, `useRouteMatch`, and route render-props. Route params are read through `useParams`, navigation through `useNavigate`, and nested routes use `Routes`/`Route element`.

## 3. What does Δt (test.patch) actually do?
`Group.test.js` and `User.test.js` update the React Router mocks and expectations: `useHistory().goBack()` becomes `useNavigate()(-1)`, `useParams()` supplies ids, and components are rendered without explicit `groupId` / `userId` props. Imports are also reordered.

## 4. Does Δt directly exercise the breaking change?
Yes. With react-router-dom 6 installed, the old source still imports removed v5 APIs and expects route ids via props; the updated tests now exercise the v6 hook-based implementation. Δc migrates the components to `Routes`, `Navigate`, `useNavigate`, `useParams`, relative links, and a trailing-slash helper.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — P⊕Δm⊕Δt fails against the v5 router source and passes after Δc's v6 source migration.

## 6. Δc nature
REAL_SOURCE_REPAIR — production React components are migrated from react-router-dom v5 APIs to v6 APIs, including routing declarations, navigation, params, links, and trailing-slash redirect behavior.

## 7. Soundness concerns / notes
- Δt is primarily a test compatibility migration, but it directly follows the same v6 API surface that Δc repairs.
