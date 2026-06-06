# 交接记录 — 061710 · claude · drafted

## 继承的上下文

见 `061652-claude-researched.md`（本次 grill-me 的前序记录）。
本文是在 grill-me 会话中达成共识后的正式落笔，包含：形式化定义、数据集范围、以及未决问题列表。

---

## 形式化定义：Breaking Change

### 符号约定

| 符号 | 含义 |
| ---- | ---- |
| `P` | base ref（PR 合入前的原始代码库状态） |
| `Δm` | manifest patch（依赖版本更新，含 lock file） |
| `Δc` | code patch（consumer 代码适配，仅 production code files） |
| `Δt` | test patch（开发者编写的测试新增/修改，hidden oracle） |
| `TEST(S)` | 在状态 S 上运行完整 CI pipeline（含 build + test runner）→ PASS / FAIL |

### 概念定义

> 依赖更新 Δm 对项目 P 构成 **breaking change**，当且仅当：在不做代码适配的情况下，Δm 破坏了 P 某个可观测的正确行为。

### 操作化定义

**前提（必要条件）：** Δc ≠ ∅ 且 Δt ≠ ∅

满足前提后，按测试套件对破坏的可见程度，分为两类：

#### Witnessed Breaking Change（可见破坏）

```
TEST(P ⊕ Δm ⊕ Δt) = FAIL
  AND
TEST(P ⊕ Δm ⊕ Δc ⊕ Δt) = PASS
```

开发者编写的测试直接见证了不兼容性：不加代码修复则失败，加上修复则通过。
这是 DepBench 的**纳入标准**。

#### Latent Breaking Change（隐性破坏）

```
TEST(P ⊕ Δm ⊕ Δt) = PASS
  AND
TEST(P ⊕ Δm ⊕ Δc ⊕ Δt) = PASS
  AND Δc ≠ ∅
```

代码适配确实存在，但测试套件灵敏度不足，无法区分"已修复"与"未修复"状态。
**不纳入 benchmark**，但在 dataset characterization 中报告数量与分布。

### 关键不对称性

```
TEST(P ⊕ Δm ⊕ Δt) = FAIL  →  breaking change 的充分证据
TEST(P ⊕ Δm ⊕ Δt) = PASS  →  inconclusive（不证明有，也不排除）
```

此不对称性是 test oracle problem 的内在性质，与测试充分性（test adequacy）直接相关，
不是研究设计缺陷，可直接用于回应审稿人质疑。

### TEST(S) 的边界

`TEST(S) = FAIL` 涵盖整个 CI pipeline 的非零退出，包括：
- **编译/构建失败**（type error、missing export、symbol removal）
- **测试 runner 失败**（assertion failure、runtime error）

编译失败是 API-level breaking change 的最强信号，优先于 test runner 触发。

---

## 数据集范围（Dataset Scope）

### 纳入标准（全部须满足）

| 条件 | 说明 |
| ---- | ---- |
| Δm ≠ ∅ | PR 包含依赖 manifest 文件变更 |
| Δc ≠ ∅ | PR 包含 production code 文件变更（非 test、非 generated/vendor） |
| Δt ≠ ∅ | PR 包含开发者编写的测试变更（有实质内容增加，非纯删除） |
| `TEST(P ⊕ Δm ⊕ Δc ⊕ Δt) = PASS` | Oracle solution 在 Harbor 中可复现通过（由 Harbor framework 保证） |
| `TEST(P ⊕ Δm ⊕ Δt) = FAIL` | 不加代码修复则失败（Witnessed Breaking Change 定义） |

### 排除标准

| 条件 | 说明 |
| ---- | ---- |
| Δt = ∅ | 无开发者测试变更；agent 可读取全部 verifier 测试，评估无信息不对称 |
| Latent only | TEST(P ⊕ Δm ⊕ Δt) = PASS，无法验证 agent 是否真正修复了不兼容 |
| Oracle 失败 | TEST(P ⊕ Δm ⊕ Δc ⊕ Δt) = FAIL，ground truth solution 本身无效 |

### 生态系统覆盖

当前支持四个生态系统（来源：Dependabot/Renovate bot PRs）：

| 生态系统 | 包管理器 | Manifest 文件 |
| -------- | -------- | ------------- |
| `npm_and_yarn` | npm / yarn / pnpm / bun | `package.json`, lock files |
| `pip` | pip / poetry / uv | `requirements*.txt`, `pyproject.toml`, `Pipfile` |
| `go_modules` | Go modules | `go.mod`, `go.sum` |
| `cargo` | Cargo | `Cargo.toml`, `Cargo.lock` |

### 文件分类规则（Patch Decomposition）

文件路径 regex 启发式分类（见 `scripts/mine_merged_dependabot_non_manifest_prs.py`）：

- **Δm**：匹配 `DEPENDENCY_FILE_RE`（manifest 及 lock 文件）
- **Δt**：匹配 `TEST_FILE_RE`（test 目录、`*test.*`、`*spec.*`、`_test.go`）
- **Δc**：匹配 `CODE_FILE_RE` 且不匹配 `GENERATED_OR_VENDOR_RE` 且不匹配 `TEST_FILE_RE` 且不是 manifest 文件

注意：`TEST_FILE_RE` 命中的文件从 Δc 中排除（`is_production_code_file = is_code_file AND NOT is_test_file`）。

---

## 未决问题（Todos for Next Agent）

- [ ] **单依赖约束**：是否要求 Δm 只更新一个依赖版本？多依赖同时 bump（如 `react@17→18` + `typescript@4→5`）时，breaking change 的归因不明确。Renovate 的 grouped update PR 是否算"一个更新事件"？需要拍板。
  - 推荐：要求单依赖，或明确定义"grouped release"的例外条件。

- [ ] **Δc 的最小阈值**：目前 Δc ≠ ∅ 仅要求有 production code file 变更。是否需要最低实质行数（如 ≥1 行非空白/注释变更）？防止只改了 import 路径或空行的 PR 混入。

- [ ] **Latent breaking change 的报告**：在 dataset characterization 章节，需要报告被排除的 latent cases 的数量和分布。考虑抽样手工验证，估计 test oracle 的 false negative rate。

- [ ] **Agent 的输入范围**：agent 看到什么？只有 P ⊕ Δm（broken state），还是也看到 Δm 本身（即知道哪个依赖从哪个版本升到哪个版本）？这影响 agent 能否查阅 changelog。

- [ ] **Δt 的质量下界**：目前只要求 `has_added_or_extended_tests`（有新增测试行）。是否需要更强的质量过滤（如：至少有一个新的 test case，而不只是 import 行变化）？

---

## 建议下一步

确认单依赖约束的处理方式（是否允许 grouped update），然后补充 dataset characterization 章节的数字（漏斗：原始 PR 数 → 有 Δc+Δt → Witnessed → 排除 oracle 失败 → 最终任务数）。
