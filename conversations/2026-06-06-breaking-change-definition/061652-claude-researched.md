# 交接记录 — 061652 · claude · researched

## 继承的上下文

无前序交接文件。本次讨论源于新会话，背景是 DepBench benchmark 数据集的研究设计阶段。
现有线程见 `conversations/2026-06-05-dataset-failure-analysis/`（verifier 质量问题，独立话题）。

## 本次完成的工作

- [x] 与 hrz 讨论并形式化 breaking change 的操作化定义
- [x] 确定两级证据框架（Level 1 强证据 / Level 2 欠定）
- [x] 阐明 FAIL/PASS 不对称性的本质及其对审稿人的可防御性
- [x] 整理推荐的 paper wording 和缓解策略

## 当前状态

**无代码修改。** 以下为纯研究设计讨论，产出是概念框架。

| 文件 | 变更描述 |
| ---- | -------- |
| `handoff_breaking_change_definition.md`（根目录） | 草稿版本，格式不规范，待废弃或删除 |
| 本文件 | 正式交接记录 |

## 核心结论（锁定决策）

### 数据集每条 PR 有三个 patch

- **Δm** — manifest patch（依赖版本更新）
- **Δc** — code patch（消费者代码适配）
- **Δt** — test patch（测试新增/修改/修复）

`P` = base ref；`TEST(S)` = 在状态 S 上运行测试套件 → PASS/FAIL。

### Breaking change 操作化定义（两级框架）

**前提（必要条件）：** Δc ≠ ∅

| 条件 | 判定 | 证据级别 |
| ---- | ---- | -------- |
| `TEST(P ⊕ Δm ⊕ Δt) = FAIL` **且** `TEST(P ⊕ Δm ⊕ Δc ⊕ Δt) = PASS` | Breaking change | **Level 1 — 强**（测试直接见证不兼容） |
| `TEST(P ⊕ Δm ⊕ Δt) = PASS` **且** `TEST(P ⊕ Δm ⊕ Δc ⊕ Δt) = PASS` 且 Δc ≠ ∅ | Underdetermined | **Level 2 — 弱**（代码适配存在，但测试灵敏度不足） |

### 关键不对称性

```
TEST(P ⊕ Δm ⊕ Δt) = FAIL  →  充分证据（sufficient）
TEST(P ⊕ Δm ⊕ Δt) = PASS  →  inconclusive（既不确认有，也不排除）
```

这个不对称性是 test oracle problem 的内在性质，不是研究设计缺陷，可直接用于回应审稿人。

### 为何 PASS 不能排除 breaking change

Δt 有三种语义，无法仅凭测试结果区分：
1. **修复被破坏的测试** → 对应 FAIL 路径，Level 1
2. **更新测试以匹配新 API**（旧测试仍通过但语义过时）→ 对应 PASS，可能有 breaking change 但测试太弱
3. **为新行为添加测试** → 对应 PASS，未必是 breaking change

### 推荐 paper wording

> "We operationalize breaking changes using a two-tier evidence framework. **Level 1 (strong evidence):** `TEST(P ⊕ Δm ⊕ Δt) = FAIL` and `TEST(P ⊕ Δm ⊕ Δc ⊕ Δt) = PASS` — the test suite directly witnesses the incompatibility introduced by the dependency update. **Level 2 (underdetermined):** the above conditions do not hold, yet Δc ≠ ∅ — code adaptation was required but the existing test suite lacks the sensitivity to detect the underlying incompatibility. This asymmetry is intrinsic to test-based oracles and is not specific to our study design. Primary analyses use Level 1 cases; Level 2 distributions are reported separately and their implications discussed."

## 下一个 Agent 的待办事项

1. **确认 Level 2 的处理策略**：这些 case 是纳入主分析（标注为"潜在 breaking change"）、单独报告，还是排除？需要 hrz 拍板。
2. **已在 `061710-claude-drafted.md` 澄清 `TEST(S)` 的边界**：pre 阶段不要求一定是测试断言失败；编译型语言可表现为编译/构建错误，解释型语言可表现为运行时错误，只要 post 打入 `Δc` 后通过且失败可归因于依赖升级不兼容，即可作为 Level 1 强证据。
3. **明确 Δc ≠ ∅ 的阈值**：纯空白/注释变化算不算？建议设最低 LOC delta（如 ≥1 行实质代码变更）。
4. **处理 `TEST(P ⊕ Δm ⊕ Δc ⊕ Δt) = FAIL` 的情况**：fix 无效，这类 PR 应从数据集中排除，还是单独标注？
5. **对 Level 2 case 随机抽样手工验证**：估计 test oracle 的 false negative rate，支撑论文中 Level 2 的可信度陈述。

## 关键决策记录

| 决策 | 原因 |
| ---- | ---- |
| 采用两级而非单一二元分类 | 强行二元化会掩盖测试充分性问题，不如显式建模两种证据强度 |
| 以 Δc ≠ ∅ 作为必要条件 | 若无代码适配，即使测试失败也可能是 flaky test 而非 breaking change |
| 不对称性作为正面框架而非局限 | 这与 test oracle problem 同构，是已知文献，审稿人无法视为方法漏洞 |

## 阻塞项

- Level 2 case 的处理方式需要 hrz 决定（影响后续实验设计和分析范围）

## 建议下一步

确认 Level 2 case 是纳入主分析还是单独分析，然后开始实现 `TEST(P ⊕ Δm ⊕ Δt)` 和 `TEST(P ⊕ Δm ⊕ Δc ⊕ Δt)` 的自动化执行脚本，对接现有的 Harbor benchmark runner。
