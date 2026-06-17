# 交接记录 — 180039 · deepseek · complete-audit

## 继承的上下文

本次会话完成了两项工作：

1. **AGENTS.md 编写**：为 DepBench 仓库创建了操作指令文件，记录 harbor CLI 用法、v3 不预置 manifest 不变式、conversations 交接协议、canary string、禁止提交的运行产物目录等。

2. **Test-patch 质量审计（65-case）**：对所有 34 个 prior-audit 标记的 `no_code_pass` 任务 + 31 个按生态比例分层随机抽取的任务，逐一分析了 test.patch / code.patch / manifest.patch / test_cmd 的质量。

核心发现已提交至 `949f8e7`：

- `AGENTS.md` — 仓库操作指南
- `harbor_benchmark/reports/test_patch_quality_review_2026-06-17.md` — 综合报告
- `harbor_benchmark/reports/test_patch_quality_review_2026-06-17_cases/*.md` — 65 个逐案分析

重要的是：v4 分支 (`origin/v4-297-benchmark-rerun-20260615`) 的 test.patch / code.patch / manifest.patch / test_state.py 与当前 v3 分支完全相同，所有 65 个分析对 v4 同样适用。

见 prior 线程：
- `conversations/2026-06-06-breaking-change-definition/061710-claude-drafted.md` — 锁定的 breaking change 定义
- `conversations/260610-problematic-pr-review/101101-gpt-complete-pr-review.md` — 34 个 problematic PR review
- `conversations/2026-06-05-dataset-failure-analysis/070008-codex-fixed-harbor.md` — verifier 修复记录

## 本次完成的工作

- [x] 编写 AGENTS.md，推送到 origin/v3-no-manifest-preapply
- [x] 65-case test-patch 质量审计：34 flagged + 31 random，10 个并行子 agent
- [x] 逐案分析写入 `test_patch_quality_review_2026-06-17_cases/*.md`
- [x] 综合报告写入 `test_patch_quality_review_2026-06-17.md`
- [x] 提交并推送 `949f8e7`
- [x] 确认所有 65 个分析对 v4 分支同样适用
- [ ] **余下 297−65=232 个任务尚未标注**

## 当前状态

所有产物已提交。65-case 审计的结论摘要：

| Verdict | 数目 | 占比 |
|---|---:|---:|
| WITNESSES_BREAKING_CHANGE | 27 | 42% |
| UNWITNESSED | 26 | 40% |
| TESTS_OTHER_THING | 8 | 12% |
| INCONCLUSIVE | 4 | 6% |

按生态系统：

| 生态 | 抽样 | Witnessed |
|---|---:|---:|
| Cargo | 2 | 100% |
| Maven | 8 | 88% |
| Go | 6 | 67% |
| pip | 4 | 50% |
| npm/yarn | 45 | 27% |

34 个 prior-audit flagged 任务中，32/34（94%）被独立确认。

我们发现的跨领域 soundness 问题包括：lint-only test_cmd（5 个未被 prior audit 标记）、test-other-like-drive-by-feature（misattributed dep bumps）、circular oracle（Δt 直接断言 Δc 的值）、unpassable-by-design（Δc 编辑 test 文件违反 agent 约束）、empty placeholder test、以及 TypeScript type-only 变更无法被 vitest/jest runtime runner 检测。

## 标注方法论（供下一个 Agent 使用）

### 输入

对每个任务的 bundle 文件进行静态审查。bundle 文件由以下脚本从 `tasks_v4/<folder>/` 中生成：

```python
for folder in all_folders:
    # 读取:
    instruction.md / manifest.patch / code.patch / test.patch / test_state.py
    # 从 test_state.py 中提取 test_cmd:
    #    正则匹配 subprocess.run('cmd', shell=...)
    # 输出到 /tmp/opencode/bundles/<folder>.txt
```

捆绑文件格式见 `/tmp/opencode/bundles/_index.txt`（65-case sample）或可重新生成全部 297 个。

### 对每个任务回答 7 个问题

1. **升级了什么？** 依赖 + 旧版本 → 新版本。从 instruction.md + manifest.patch 中获取。当 Δm 没有因果联系时（misattributed dep bump），也要注意说明。

2. **breaking change 是什么？** 1-3 句，具体。从 code.patch + test.patch 推断。说明什么变化破坏了消费者代码（API 签名 / 行为 / 导入 / 编译 / 运行时）。

3. **Δt（test.patch）实际上做了什么？** 列出接触的测试文件，并分类：新测试用例 / 修改断言 / 夹具 / 快照 / 测试基础设施 / 无关附带改动（drive-by）。

4. **Δt 是否直接触发了 breaking change？** 精确。引用一个有代表性的测试断言或测试名称，该断言在 P⊕Δm 上可能失败，并在 P⊕Δm⊕Δc 上通过。如果找不到，说明原因。

5. **覆盖度裁决 — 五选一：**
   - `WITNESSES_BREAKING_CHANGE` — Δt 在 P⊕Δm 上会 FAIL，在 P⊕Δm⊕Δc 上会 PASS
   - `UNWITNESSED` — Δt 在单独的 P⊕Δm 上可能通过（Level 2 / no_code_pass）
   - `TESTS_OTHER_THING` — Δt 测试的是其他东西（formatter、快照、无关特性、lint），与被升级的依赖没有因果联系。**当 test_cmd 是 lint/format 检查时，始终使用此裁决**（根据锁定的 breaking-change 定义，`npm run lint`、`npx eslint .`、`npm run code:lint`、`npm run test:lint` 被排除在 Level 1 之外）
   - `INCONCLUSIVE` — 无法通过静态分析判断通过/失败（例如空的占位测试、构建工具加载失败歧义）
   - **如果 test_cmd 无法从 test_state.py 中提取，标记为 TEST_CMD_UNEXTRACTABLE 并尽最大努力分析**

6. **Δc 性质 — 选择主导类别：**
   - `REAL_SOURCE_REPAIR` — 生产源代码适配了新 API/行为
   - `FORMATTER_LINT_CHURN` — 仅 Prettier/eslint/standard/xo 风格更改
   - `CONFIG_INFRA_ONLY` — CI 工作流、tsconfig、构建脚本、.nvmrc
   - `TEST_ONLY` — Δc 本身只编辑测试文件/testdata（agent 禁止碰测试——设计的硬伤）
   - `SNAPSHOT_ONLY` — Δc 是 `*.snap` / `__snapshots__` 重新生成
   - `DOCS_EXAMPLE_ONLY` — Δc 只编辑了 `docs/` 示例
   - `MIXED` — 上述组合或多个依赖的混合体

7. **健壮性担忧 / 备注** — 特定任务的注意事项。

**对于较大的捆绑包（>500KB），不要读取每一行。** 使用 grep 查找关键部分：`^diff --git` 查看文件列表，在 test.patch 部分采样几个代码块（不是全部），查找实际的断言更改。

### 每任务输出格式

每项分析一个 markdown 文件，文件名为 `<folder>.md`：

```markdown
# Test-patch audit — <folder>

## 1. Task summary
- Folder: <folder>
- Ecosystem: <eco>
- Upgrade: <library> <old> -> <new>
- Flagged in problematic_prs_review_2026-06-10.md: YES / NO
- test_cmd: `<exact verifier command or TEST_CMD_UNEXTRACTABLE>`

## 2. What is the breaking change?
1-3 sentences, concrete.

## 3. What does Δt (test.patch) actually do?
List test files touched + summarize.

## 4. Does Δt directly exercise the breaking change?
Quote representative assertion or explain why not.

## 5. Coverage verdict
WITNESSES_BREAKING_CHANGE | UNWITNESSED | TESTS_OTHER_THING | INCONCLUSIVE
One-sentence justification.

## 6. Δc nature
REAL_SOURCE_REPAIR | FORMATTER_LINT_CHURN | CONFIG_INFRA_ONLY | TEST_ONLY | SNAPSHOT_ONLY | DOCS_EXAMPLE_ONLY | MIXED
One-sentence justification with key file paths.

## 7. Soundness concerns / notes
Any case-specific concerns.
```

## 下一个 Agent 的待办事项

### 第一阶段：生成剩余 232 个任务的 bundle 文件

```bash
python3 << 'EOF'
# 类似于在本次会话中使用的脚本
# 为所有 297 个任务生成 bundle 文件，然后过滤掉已有的 65 个
# 输出到 /tmp/opencode/bundles_all/<folder>.txt
EOF
```

### 第二阶段：将 232 个任务分派给子 agent 进行批量标注

并行策略（本次会话验证有效）：
- 将任务 bin-pack 到大约 30-35 个批次中，每批 6-8 个任务
- 每批 ~150-250KB 的捆绑内容
- 为每批生成一个带有完整标注提示词的子 agent（通用类型）
- 子 agent 将输出写入共享目录，然后返回一个简短的摘要行

分发注意事项：
- 超过 500KB 的文件单独成批，并指示子 agent 使用 grep + 定向读取
- 包含 `geotools__geotools__4212` 类似 `test_cmd` 提取失败的任务——子 agent 仍然可以分析补丁，即使不知道确切的 verifier 命令
- 在标注开始前，从 65-case 集中复制示例文件，供子 agent 参考良好/不良的范例

### 第三阶段：综合最终报告

标注完成后：
1. 解析所有 297 个判决结果
2. 按生态系统、标注日期、Δc 性质生成表格
3. 更新 `test_patch_quality_review_2026-06-17.md` 或写一个新报告
4. 对比 flagged vs random 见证率，确认 prior audit 的精确度/召回率
5. 标记高优先级修复项（test_cmd 错误指派的测试文件、不可通过的任务、循环 oracle）
6. 提交并推送

### 参考文件

- 65 个分析参考样例在：`harbor_benchmark/reports/test_patch_quality_review_2026-06-17_cases/*.md`
- 优秀见证任务范本：`determined-ai__determined__8316.md`、`geotools__geotools__4212.md`、`decaporg__decap-cms__5178.md`
- Lint-only 反例：`BrightspaceUI__intl__106.md`、`cloudant__nodejs-cloudant__400.md`
- Δt=占位符 empty test：`cdk8s-team__kubecon-2020-cdk8s__28.md`
- Unpassable 反例（Δc 编辑测试文件）：`runatlantis__atlantis__5209.md`
- 综合报告：`harbor_benchmark/reports/test_patch_quality_review_2026-06-17.md`

## 关键决策记录

| 决策 | 原因 |
| ---- | ---- |
| Lint-only 测试命令被视为 TESTS_OTHER_THING（不是见证的） | 与锁定的 breaking-change 定义一致：`conversations/2026-06-06-breaking-change-definition/` 明确指出 "not dependency-resolution/network/OOM/flaky/lint" |
| 通过 bundle 文件大小进行 bin-pack 批次，使 ~150-250KB 的上下文约束可行 | 较大的 bundle 文件（prettier 迁移 500-970KB）单独成批并教子 agent 使用 grep |
| 子 agent 将分析写入磁盘，只返回摘要 | 避免输出 token 消耗失控；65 项分析的总和超过 150KB 的 markdown |
| 对两个分支都确认分析适用性后才提交 | v4 远程镜像的 test.patch/code.patch/manifest.patch/test_state.py 与 v3 位级相同 |

## 阻塞项

- 无。

## 建议下一步

运行 bundle 生成脚本为全部 297 个任务生成输入文件，然后并行启动 30 个标注子 agent，从尚未覆盖的 232 个任务开始。已有 65 个标注案例可作为范例。
