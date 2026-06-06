# DepBench 数据集失败根因分析报告

生成时间：2026-06-05 15:17  
分析对象：`harbor_benchmark/tasks_v4`  
主要依据：最新 oracle job `jobs/2026-06-04__22-45-54`

## 结论摘要

最新 oracle 验证中，217 个任务通过 209 个，失败 8 个。失败并不都是“解法 patch 错误”。按根因看，主要分成四类：

| 类型 | 数量 | 任务 |
| --- | ---: | --- |
| 真实 solution/test mismatch | 1 | `eakmanrq__sqlframe__533` |
| 测试已通过但 verifier 因 worker teardown 返回非零 | 3 | `graphql-hive__graphql-config__1481`, `nuxt__fonts__601`, `owncloud__web__11511` |
| Jest/Vitest 被 kill 或超时，疑似资源/并发/open handle 问题 | 3 | `inrupt__solid-client-authn-js__3129`, `oceanprotocol__market__1687`, `odanado__cloud-cryptographic-wallet__672` |
| verifier 命令过宽，跑完整测试导致超时 | 1 | `typescript-eslint__tslint-to-eslint-config__1192` |

最明确的问题不是 agent 能力，而是 verifier 质量：多个任务的业务测试已经全部通过，但 Harbor 最终 reward 仍为 0，因为 Node 测试进程退出阶段失败。

## 逐任务分析

### 1. `eakmanrq__sqlframe__533`

相关文件：

- `harbor_benchmark/tasks_v4/eakmanrq__sqlframe__533/tests/test_state.py`
- `harbor_benchmark/tasks_v4/eakmanrq__sqlframe__533/tests/test.patch`
- `harbor_benchmark/tasks_v4/eakmanrq__sqlframe__533/solution/code.patch`

Verifier 命令：

```bash
/usr/local/bin/python -m pip install pytest-xdist databricks-sql-connector && \
/usr/local/bin/python -m pytest "tests/integration/engines/test_int_functions.py::test_pi[duckdb]" -x -q
```

失败位置：

- `test_state.py` 中 subprocess 返回 `exit code 1`
- pytest 目标测试：`tests/integration/engines/test_int_functions.py::test_pi[duckdb]`
- hidden test 将断言从严格 `math.pi` 放宽为 `in (math.pi, 3.141592654)`，但 oracle solution 仍无法通过。

具体原因判断：

这是 8 个失败里唯一明确不是 teardown/timeout 的 case。`solution/code.patch` 将 `pi()` 从 anonymous function 改成 `expression.Pi`：

```python
return Column.invoke_expression_over_column(None, expression.Pi)
```

失败说明在升级到 `sqlglot >=24.0.0,<27.27` 后，当前 oracle patch 生成的 DuckDB SQL 或返回值仍不符合 hidden test。日志只保留了 `result.stdout[-2000:]`，导致内部 traceback 被截断成 `Att...`，无法从现有 artifact 看到完整异常。

建议修复：

1. 先复现该单测，并把 stdout 截断改大，拿到完整 traceback。
2. 检查 `expression.Pi` 在当前 `sqlglot` 版本对 DuckDB 的生成结果。
3. 若 `expression.Pi` 不稳定，改回 DuckDB 兼容的表达式生成方式，或者在 sqlframe 中为 DuckDB 添加专门 override。

### 2. `graphql-hive__graphql-config__1481`

相关文件：

- `harbor_benchmark/tasks_v4/graphql-hive__graphql-config__1481/tests/test_state.py`
- `harbor_benchmark/tasks_v4/graphql-hive__graphql-config__1481/solution/code.patch`

Verifier 命令：

```bash
pnpm exec vitest run test/loaders.spec.ts
```

失败位置：

- Vitest 业务测试全部通过：`Test Files 1 passed`, `Tests 4 passed`
- 进程退出阶段失败：`Error: Failed to terminate worker`
- 错误来自 `tinypool@1.0.0`

具体原因判断：

这是 verifier false negative。任务 solution 已经让测试通过，但 Vitest worker pool 在退出阶段没有正常 terminate，导致 subprocess exit code 为 1，Harbor reward 变成 0。

建议修复：

1. 修改 `tests/test_state.py` 的命令，不改 solution。
2. 优先尝试：

```bash
pnpm exec vitest run test/loaders.spec.ts --pool=forks
```

3. 如果该 Vitest 版本不支持 `--pool=forks`，尝试 `--threads=false` 或在 Vitest config 中禁用 threaded pool。
4. 验证标准：输出仍为 `4 passed`，且 subprocess returncode 为 0。

### 3. `inrupt__solid-client-authn-js__3129`

相关文件：

- `harbor_benchmark/tasks_v4/inrupt__solid-client-authn-js__3129/tests/test_state.py`
- `harbor_benchmark/tasks_v4/inrupt__solid-client-authn-js__3129/task.toml`
- `harbor_benchmark/tasks_v4/inrupt__solid-client-authn-js__3129/tests/test.patch`

Verifier 命令：

```bash
npx jest --selectProjects node --no-coverage
```

失败位置：

- subprocess 返回 `exit code 137`
- stderr 只有 `Killed`
- task 环境资源为 `cpus = 2`, `memory_mb = 4096`

具体原因判断：

`137` 通常是进程被 SIGKILL，结合 Jest 项目级运行和 4GB 内存限制，最可能是 OOM 或并发 worker 过多。这里不是断言失败，日志中没有出现具体 failed assertion。

另外，`test.patch` 中包含 e2e/node 相关测试改动；如果完整 node project 被 Jest 拉起，可能触发较重的网络/浏览器/异步资源路径。

建议修复：

1. 先把 verifier 命令改为低并发：

```bash
npx jest --selectProjects node --no-coverage --runInBand
```

或：

```bash
npx jest --selectProjects node --no-coverage --maxWorkers=2
```

2. 如果仍被 kill，再把 `task.toml` 的 `memory_mb` 从 4096 提到 8192。
3. 如果仍不稳定，进一步缩小 Jest 目标到 hidden patch 涉及的 spec 文件，而不是整个 node project。

### 4. `nuxt__fonts__601`

相关文件：

- `harbor_benchmark/tasks_v4/nuxt__fonts__601/tests/test_state.py`
- `harbor_benchmark/tasks_v4/nuxt__fonts__601/tests/test.patch`

Verifier 命令：

```bash
pnpm dev:prepare && pnpm exec vitest run test/basic.test.ts -t "adds preload links to the HTML with global CSS"
```

失败位置：

- 目标测试通过：`Test Files 1 passed`, `Tests 1 passed | 15 skipped`
- stdout 显示测试期间启动了服务：`Listening on http://127.0.0.1:42851`
- 退出阶段失败：`Error: Failed to terminate worker`
- 错误来自 `tinypool@1.1.1`

具体原因判断：

业务断言已经通过，失败发生在 Vitest/Nuxt 测试环境 teardown。最可疑的 open handle 是测试启动的本地 server 或 Vitest worker pool。当前 verifier 把“测试通过但退出异常”当作失败。

建议修复：

1. 首选修测试 cleanup：确保启动的 Nuxt server 在测试结束后关闭。
2. 若只想提高 verifier 稳定性，可尝试：

```bash
pnpm exec vitest run test/basic.test.ts -t "adds preload links to the HTML with global CSS" --pool=forks
```

3. 如果 Vitest 3.2.6 支持 pool 配置，应优先使用 fork pool，避免 tinypool threaded teardown。

### 5. `oceanprotocol__market__1687`

相关文件：

- `harbor_benchmark/tasks_v4/oceanprotocol__market__1687/tests/test_state.py`
- `harbor_benchmark/tasks_v4/oceanprotocol__market__1687/tests/test.patch`
- `harbor_benchmark/tasks_v4/oceanprotocol__market__1687/task.toml`

Verifier 命令：

```bash
npx jest -c .jest/jest.config.js --ci
```

失败位置：

- subprocess 返回 `exit code 137`
- stderr 中有多个 `PASS ...`，说明已有大量测试通过
- Jest 明确提示：`A worker process has failed to exit gracefully... Active timers can also cause this`
- 最后被 `Killed`
- task 资源为 `memory_mb = 4096`

具体原因判断：

这是资源/worker 泄漏问题，不是明确的业务断言失败。`test.patch` 删除了 storyshots，并新增一批 render tests；verifier 命令却跑整个 Jest config，因此会启动大量测试 worker。worker 未退出 + 4GB 内存限制共同导致进程被 kill。

建议修复：

1. 缩小 verifier 命令，只跑 hidden patch 相关新增/修改测试，不要跑整套 Jest config。
2. 或先尝试：

```bash
npx jest -c .jest/jest.config.js --ci --runInBand --detectOpenHandles
```

3. 若 `--runInBand` 能稳定通过，再移除 `--detectOpenHandles` 保留低并发。
4. 如果低并发仍被 kill，再提高 `memory_mb`。

### 6. `odanado__cloud-cryptographic-wallet__672`

相关文件：

- `harbor_benchmark/tasks_v4/odanado__cloud-cryptographic-wallet__672/tests/test_state.py`
- `harbor_benchmark/tasks_v4/odanado__cloud-cryptographic-wallet__672/tests/test.patch`

Verifier 命令：

```bash
npx vitest run packages/web3-provider-adapter/src/get-common.spec.ts --reporter=verbose
```

失败位置：

- subprocess 在 240 秒超时
- stdout 只有 `RUN v0.23.2 /app`，没有测试通过/失败明细
- hidden test 只修改 `get-common.spec.ts` 中 chainId 断言，理论上不应该跑 4 分钟。

具体原因判断：

这是测试进程启动后挂住，未进入或未完成目标测试。由于 Vitest 版本较旧（v0.23.2），常见原因是 worker threads、mock server、异步句柄或 ESM 加载卡住。该任务不是断言失败，而是 verifier 命令无法在 240 秒内收敛。

建议修复：

1. 先用老 Vitest 兼容参数禁用线程：

```bash
npx vitest run packages/web3-provider-adapter/src/get-common.spec.ts --reporter=verbose --threads=false
```

2. 检查 `get-common.spec.ts` 中的 server 是否在 `afterAll` 中同步关闭，并确保没有 pending request/promise。
3. 如果禁用线程后可通过，应只改 verifier 命令；如果仍挂住，再检查 test patch 是否引入了无法完成的 RPC mock。

### 7. `owncloud__web__11511`

相关文件：

- `harbor_benchmark/tasks_v4/owncloud__web__11511/tests/test_state.py`
- `harbor_benchmark/tasks_v4/owncloud__web__11511/tests/test.patch`

Verifier 命令：

```bash
pnpm exec vitest run <12 个指定 spec> --no-coverage
```

失败位置：

- 12 个 test files 全部通过
- 155 个 tests 全部通过
- 退出阶段失败：`Error: Failed to terminate worker`
- 错误来自 `tinypool@1.0.0`

具体原因判断：

这是最清楚的 false negative：测试全绿，只有 worker pool 退出失败。当前 verifier 命令覆盖 12 个 spec，transform/collect 时间很长，也会增加 worker teardown 风险。

建议修复：

1. 优先改 verifier 命令为 fork/single-thread pool：

```bash
pnpm exec vitest run ... --no-coverage --pool=forks
```

2. 如果不支持，尝试 `--threads=false`。
3. 如果仍失败，按 test.patch 分组拆成多个更小的 verifier subprocess，避免一个 Vitest worker pool 承载 12 个 spec。

### 8. `typescript-eslint__tslint-to-eslint-config__1192`

相关文件：

- `harbor_benchmark/tasks_v4/typescript-eslint__tslint-to-eslint-config__1192/tests/test_state.py`
- `harbor_benchmark/tasks_v4/typescript-eslint__tslint-to-eslint-config__1192/tests/test.patch`
- `harbor_benchmark/tasks_v4/typescript-eslint__tslint-to-eslint-config__1192/task.toml`

Verifier 命令：

```bash
npm test
```

失败位置：

- subprocess 在 600 秒超时
- stdout 只显示：

```text
> tslint-to-eslint-config@2.9.2 test /app
> jest
```

- hidden test 只新增 `src/utils.test.ts` 里的 `asError` 用例。

具体原因判断：

这里的 verifier 命令范围明显过大。任务只需要验证 `src/utils.ts` 的新增 `asError` 行为，但 `npm test` 会跑完整 Jest suite，导致 600 秒仍未结束。这个失败不说明 solution 错，而说明 verifier 没有聚焦 hidden patch。

建议修复：

1. 把 verifier 命令改成定向测试，例如：

```bash
npx jest src/utils.test.ts --runInBand
```

2. 保留 `timeout=600` 没问题，但关键是不要跑完整 `npm test`。
3. 修完后再跑 oracle；如果定向测试通过，应视为该任务恢复。

## 横向根因

### A. Node 测试 worker teardown 是主要问题

以下任务均表现为“测试已 passed，但进程退出失败”：

- `graphql-hive__graphql-config__1481`
- `nuxt__fonts__601`
- `owncloud__web__11511`

共同症状：

```text
Error: Failed to terminate worker
```

共同修复方向：

- 对 Vitest 使用 fork/single-thread pool。
- 修复测试中的 server/open handle cleanup。
- 对超大 spec list 拆分 verifier 命令。

### B. 4GB 内存对部分 Jest 项目不足

以下任务有 `Killed` 或 exit 137：

- `inrupt__solid-client-authn-js__3129`
- `oceanprotocol__market__1687`

共同修复方向：

- Jest 加 `--runInBand` 或 `--maxWorkers=2`。
- 必要时把 `task.toml` 的 `memory_mb = 4096` 提到 `8192`。
- 避免 verifier 跑整套 project。

### C. verifier 命令过宽

最明显的是：

- `typescript-eslint__tslint-to-eslint-config__1192`: hidden patch 只改 `src/utils.test.ts`，但 verifier 跑 `npm test`。
- `oceanprotocol__market__1687`: hidden patch 新增/修改一批组件测试，但 verifier 跑完整 Jest config。

建议：生成任务时，verifier 命令应尽量精确到 hidden patch 影响的 spec 文件。

### D. 输出截断阻碍定位

`eakmanrq__sqlframe__533` 的内部失败在 Harbor artifact 中被截断，只看到 `Att...`。原因是 `tests/test_state.py` 只输出 `result.stdout[-2000:]`。对于 Python/pytest 项目，这会吞掉关键 traceback。

建议：失败报告中至少保留 `stdout[-8000:]` 或同时写入完整 command stdout/stderr artifact。

## 修复优先级

| 优先级 | 任务 | 原因 |
| --- | --- | --- |
| P0 | `graphql-hive__graphql-config__1481` | 测试全过，只需修 worker teardown，收益最快 |
| P0 | `owncloud__web__11511` | 测试全过，只需修 worker teardown，但 spec 多 |
| P0 | `nuxt__fonts__601` | 测试全过，疑似 server/open handle 未清理 |
| P0 | `typescript-eslint__tslint-to-eslint-config__1192` | verifier 命令明显过宽，改为定向 Jest |
| P1 | `inrupt__solid-client-authn-js__3129` | exit 137，需要低并发或内存调整 |
| P1 | `oceanprotocol__market__1687` | exit 137 + worker leak，需要缩小测试范围 |
| P1 | `odanado__cloud-cryptographic-wallet__672` | Vitest 启动后挂住，需要禁用线程/排查 server |
| P2 | `eakmanrq__sqlframe__533` | 需要重新复现拿完整 traceback，可能要改 solution |

## 建议执行方案

1. 先批量修 4 个 verifier 明显问题：`graphql-hive`, `nuxt`, `owncloud`, `typescript-eslint`。
2. 然后对 `inrupt`, `oceanprotocol`, `odanado` 做低并发/线程禁用实验。
3. 最后进入 `eakmanrq__sqlframe__533` 环境单独复现，拿完整 traceback 后决定改 solution 还是 hidden test。
4. 每修一个任务，立即跑：

```bash
harbor trials start -p harbor_benchmark/tasks_v4/<task>
```

5. 8 个任务都通过后，再跑一次 oracle sweep：

```bash
harbor run -p harbor_benchmark/tasks_v4 -a oracle -n 4 -o jobs
```

验收标准：latest oracle reward 全部为 1；真实 agent 的 timeout 再作为第二阶段质量优化处理。
