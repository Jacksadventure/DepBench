# Test-patch audit — elastic__apm-agent-java__2792

## 1. Task summary
- Folder: elastic__apm-agent-java__2792
- Ecosystem: maven
- Upgrade: jctools-core 3.3.0 -> 4.0.1
- Flagged in problematic_prs_review_2026-06-10.md: NO
- test_cmd: `mvn ... -pl apm-agent-core -am -Dtest=TestObjectPoolFactory test`

## 2. What is the breaking change?
jctools-core 4 removes the old `AtomicQueueFactory` / `ConcurrentQueueSpec.createBoundedMpmc` path used to allocate MPMC queues. The repaired code switches to `new MpmcAtomicArrayQueue<T>(maxCapacity)` and exposes `ObjectPoolFactory.createRecyclableObjectPool(...)` so plugin helpers can allocate through the tracer's factory.

## 3. What does Δt do?
Δt updates `TestObjectPoolFactory` so its override of `createRecyclableObjectPool(...)` is `public`, matching Δc's visibility change from `protected` to `public`.

## 4. Does Δt directly exercise the dependency break?
Yes, at compile level. On P⊕Δm, `apm-agent-core` still imports removed jctools APIs and fails to compile under jctools 4. With Δc, the core source compiles against `MpmcAtomicArrayQueue`, and the patched test override compiles and runs.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE — `TEST(P⊕Δm⊕Δt)` fails because production code uses removed jctools 3 APIs; `TEST(P⊕Δm⊕Δc⊕Δt)` passes after the queue factory migration.

## 6. Δc nature
REAL_SOURCE_REPAIR — production helpers are migrated from direct jctools factory calls to `ObjectPoolFactory` / `MpmcAtomicArrayQueue`.

## 7. Soundness concerns / notes
The verifier focuses on `apm-agent-core`, so it primarily witnesses the core factory API break. Several plugin helper edits in Δc are plausible follow-on repairs but are less directly covered by the selected test command.
