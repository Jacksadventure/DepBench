# 交接记录 — 101101 · gpt · complete-pr-review

## 继承的上下文

本次任务按 handoff Mode A 检查了 `conversations/`。最新线程 `260609-dependabot-maven-results` 与本次 problematic PR 数据质量审阅不匹配，因此新建线程：

`conversations/260610-problematic-pr-review/`

同时读取并继承了两个相关旧线程：

- `conversations/2026-06-05-dataset-failure-analysis/`：oracle/verifier 质量分析，关键决策是优先以 oracle/witness 证据判断 dataset blocker。
- `conversations/2026-06-06-breaking-change-definition/`：形式化定义了 witnessed breaking change，主 benchmark 应满足 `TEST(P + Delta m + Delta t) = FAIL` 且 oracle solution pass，并且 `Delta c` 应是真实 production consumer-code repair。

## 本次完成的工作

- [x] 解析 `harbor_benchmark/reports/problematic_prs_review_2026-06-08.csv` 的全部 44 行。
- [x] 对每一行检查本地 `harbor_benchmark/tasks_v4/<task_id>` 是否存在。
- [x] 对本地存在的任务检查 `solution/code.patch`、`tests/test.patch`、`environment/patches/manifest.patch` 的路径与增删规模。
- [x] 使用 `gh api` 查询每个 upstream PR 的 title、author、merged_at、commit/file 数和 changed-file 列表。
- [x] 写出完整审阅报告 `harbor_benchmark/reports/problematic_prs_review_2026-06-10.md`。

## 当前状态

| 文件 | 变更描述 |
| --- | --- |
| `harbor_benchmark/reports/problematic_prs_review_2026-06-10.md` | 新增综合报告，覆盖 CSV 中 44 个 case，分为 packaged exclude candidates、packaged Delta-c boundary cases、non-packaged vendor-only rows，并给出 root causes 和 remediation。 |
| `conversations/260610-problematic-pr-review/101101-gpt-complete-pr-review.md` | 本交接记录。 |

当前结论：

- CSV 中 44 行均为真实质量问题或历史候选过滤问题。
- 34 行仍存在于本地 `tasks_v4`，建议从 main witnessed benchmark 中 remove/quarantine。
- 10 行不在本地 `tasks_v4`，均为 Go vendor/test-tools vendor sync 类候选，已不属于当前 packaged task removal，但应保留为 mining filter 反例。
- 30 个本地 packaged case 是 `no_code_pass`，违反 witnessed-breaking-change 纳入标准。
- 4 个本地 packaged case 是 `Delta c` 边界问题：snapshot、docs example、test/testdata，不应计入 production source repair。

## 下一个 Agent 的待办事项

1. 如果用户要执行清理，先决定是直接删除 34 个任务目录，还是生成 quarantine manifest/list 供实验脚本过滤。
2. 清理后重新统计 `tasks_v4` 数量，并同步更新 paper 中任务总数、ecosystem/source 分布、实验表格。
3. 如果保留 latent/unwitnessed 子集，给这些任务加显式标签，不要混入 main witnessed benchmark。
4. 可进一步修改 mining/decomposition 脚本，排除 `vendor/`、`test/tools/vendor/`、`__snapshots__/`、`*.snap`、`*_test.go`、`testdata/`、`__test_helpers__/`、`.github/workflows/`、docs/examples 等作为 production `Delta c`。

## 关键决策记录

| 决策 | 原因 |
| --- | --- |
| 报告区分 packaged 与 non-packaged rows | CSV 中 10 个 vendor-only PR 已不在当前 `tasks_v4`，不能当作当前本地任务删除项，但仍是 candidate mining/filtering 质量问题。 |
| 建议 34 个 packaged rows 从 main witnessed benchmark 移除或隔离 | 30 个不满足 witness check；4 个不满足 production `Delta c` 边界。 |
| 未 rerun Harbor | 本轮目标是定位并审阅 CSV 中的问题；动态 `no_code_pass` 事实来自 CSV 审计结果，本轮补充了本地 patch 和 GitHub PR/file evidence。 |

## 阻塞项

- 无当前阻塞。
- 尚未实际删除或 quarantine 任务目录；这是下一步数据集变更，需要用户确认清理策略。

## 建议下一步

如果继续做数据集清理，先生成一个 34-task quarantine list，并让 Harbor/paper 统计脚本从 main witnessed corpus 中排除这些 task。
