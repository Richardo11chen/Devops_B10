# 议题裁决记录（resolutions）

组长对**成员B 在 `e2/README.md` 第 6.3 节提出的 12 条**所作的裁决，以及 **A 组对 `[B10] DRAFT 接口确认` 的回应**现状。

- 裁决日期：2026-09-25
- A 组基线：`fec3fbe`（2026-09-24）
- B 组自基线：`4090bc4`

> 本文独立成文，**不写进 `e2/README.md`**：成员B 的分支已在 `e2/README.md` 追加整个第 6 节，
> 两边同时改同一文件会在合并时冲突。本文由组长维护，成员只读。

---

## 一、成员B 的 12 条裁决

| # | 问题 | 裁决 | 理由 | 执行方 |
|---|------|------|------|--------|
| 1 | 产物 `type` 是否补 `VERIFY_LOG` / `ERROR_REPORT` | **采纳 A 组的完整枚举（10 项）** | 枚举是两组共用的公共词表。B 组自持一套 8 项，会让同一份产物在两组解释不同 | B 组 ✅ 已改 |
| 2 | `execution.resources.cpu` 类型 | **统一为 `string`** | 整数表达不了 `"2000m"` 这类毫核值与小数核数；CPU 配额本身就有非整数语义。现在尚未部署，改动成本最低 | A 组 ⏳ |
| 3 | `execution` 是否进 `required` | **必须进** | 课程原文：「公共字段（**必须包含 execution**）：schema_version、…」。A 组失败样例缺 `execution` 是漏洞，需补齐 | A 组 ⏳ |
| 4 | `execution.attempt` 是否提必填 | **提为必填** | REPAIR 靠 `attempt` 表达候选轮次，DRAFT 靠它表达迭代轮次。有默认值 1，填写成本近乎为零。B 组已对齐 A 组的 `["mode","attempt"]` | B 组 ✅ 已改 |
| 5 | `required` 项次是否取并集 | **取并集，8 项** | A 组含 `created_at`、B 组含 `execution`，两者都不该被砍。并集 = `schema_version`、`job_id`、`trace_id`、`job_type`、`status`、`execution`、`input`、`created_at` | 两组（B 组 ✅ 已改） |
| 6 | `trace_id` 是否加 `pattern` | **加 `^trace-[a-z0-9-]+$`** | 与 A 组一致。没有 pattern 时，格式错误的 `trace_id` 无法在校验阶段被拦下 | B 组 ✅ 已改 |
| 7 | `artifact` 的 `media_type` / `sha256` 是否必填 | **都提为必填** | A 组已是 6 项必填；`sha256` 经议题 6 已定必需，`media_type` 缺失会让消费者无法解析产物 | B 组 ✅ 已改 |
| 8 | **修复器自身崩溃**用哪个错误码 | **新增 `ANALYSIS_5002`：修复器内部异常（MDFixer）** | 不改 `ANALYSIS_5001` 的语义 —— 分析器 ≠ 修复器。错误码表已有 `{模块}_{四位数字}` 命名规则，新增一位比篡改既有语义安全 | A 组 ⏳ |
| 9 | 请求侧是否携带 `schema_version` | **已解决**：A 组已在请求中加入 `schema_version`。**但 `trace_id` 仍未加**，继续追 | — | A 组 ⏳（trace_id） |
| 10 | REPAIR 超时样例是否另立 | **支持成员B**：`repair_job_err.res.json` 只承载「候选全败」（`EXEC_4003` + `FAILED`）；超时应另立样例（`EXEC_4002` + `TIMED_OUT`） | A 组原样例把「候选全败」写成超时，与自家 `error_codes.md` 矛盾 | A 组 ⏳ |
| 11 | `input.source_commit` 是否入契约 | **不入，且已从 B 组删除** | 成员B 判断正确。该字段是**组长**在 `e2/validate.py` 内置样例中擅自添加的，契约中并无定义，且与 `input.repository.commit` 语义重复，取值不一致时无法判定以谁为准 | B 组 ✅ 已删 |
| 12 | `execution.timeout_seconds` 口径 | **统一**：删除 `input.deadline_sec`，超时只由 `execution.timeout_seconds` 表达 | A 组 res 为 `300`、同批 err 的 `detail.deadline_sec` 为 `600`，自相矛盾；且 `deadline_sec` 与 `execution.timeout_seconds` 双写会让「以谁为准」无法判定 | A 组 ⏳ |

### 汇总

- **B 组已执行完毕**：第 1、4、5、6、7、11 条
- **需 A 组处理**：第 2、3、8、9（`trace_id` 部分）、10、12 条
- **已解决**：第 9 条的 `schema_version` 部分

> 第 11 条是**组长的错误**，不是 A 组的问题。已在 `e2/validate.py` 中删除并加注说明，防止后人重新加回。

### 追加裁决（2026-09-25，来自成员B 的 6.7.2 第 2 条）

成员B 在 PR #8 的 `e2/README.md` 6.7.2 第 2 条提出：**同一份 `verify.log` 在两组被标为不同类型**。

组长逐文件核实，属实：

| URI | A 组 | B 组（改前） |
|-----|------|--------------|
| `artifact://pair10/job-draft01/verify.log` | `VERIFY_LOG` | `BUILD_LOG` |
| `artifact://pair10/job-repair01/verify.log` | —（A 组无 REPAIR 样例） | `BUILD_LOG` |

**裁决：B 组统一改用 `VERIFY_LOG`**（即成员B 提出的选项 a）。

理由：`type` 是消费者查找产物的**判别键**。`BUILD_LOG`（构建日志）与 `VERIFY_LOG`（验证日志）本是两个不同语义；同一份产物在两组标不同值，等于契约在这一项上失效。选项 b（「两种都允许」）等于放弃判别能力，不可取。

**执行**（由组长一次改完，保证每个提交内部自洽；只改一处会让 B10 前后矛盾）：

| 文件 | 产物 | 改动 |
|------|------|------|
| `e2/contracts/dockerfile_job.res.json` | `verifylog-001` | `BUILD_LOG` → `VERIFY_LOG` |
| `e2/contracts/repair_job.res.json` | `verify-log-002` | `BUILD_LOG` → `VERIFY_LOG` |

其余保持 `BUILD_LOG` 不变且正确：`build-log-003`（真构建日志）、`cand1-log-004` / `cand2-log-005`（候选构建日志）。

> **这处不一致是组长造成的**：裁决第 1 条「采纳 A 组完整枚举」时，只把 `VERIFY_LOG` 加进了 schema 枚举，
> 未回头检查样例的**取值**；给 A 组的回复里「`dockerfile_job.*` 无需改动」也只验了 schema 合规、
> 未验语义取值一致。成员B 的 6.7.2 第 2 条把这个洞挖了出来。
>
> **教训**：schema 合规 ≠ 契约一致。枚举扩容后必须回头扫一遍所有样例的取值，
> 否则「类型判别键」会在两组间漂移 —— 而且 schema 校验**不会**报错，因为两种取值都合法。

---

## 二、A 组回应与最终对齐结果

A 组分两轮回应：`fec3fbe`（2026-09-24）、`462eb5e`（2026-09-25）。
**7 个议题 + 6 点后续全部解决，两组 `task.schema.json` 已逐字段比对一致。**

### 第一轮（`fec3fbe`）

| 议题 | 处理 |
|------|------|
| 1 请求带 `schema_version` | ✅ 已加（`trace_id` 留到第二轮） |
| 2 `execution` 入 schema | ⚠️ 加了但定为**可选** → 第二轮纠正 |
| 3 响应 `input` 填副本 | ✅ 定稿为请求副本 |
| 4 `output.artifacts[]` | ✅ 四类响应全改，删裸字段 |
| 5 `required` 扩容 | ⚠️ 含 `created_at` 不含 `execution` → 第二轮纠正 |
| 6 `sha256` 必需 | ✅ |
| 7 产物 URI 约定 | ✅ |

### 第二轮（`462eb5e`，针对 B10 提出的 6 点）

| # | 问题 | A 组提交 | 结果 |
|---|------|----------|------|
| 1 | `execution` 应进 `required` | `d031660` / `711ed28` | ✅ 已进 |
| 2 | `deadline_sec` 与 `timeout_seconds` 双写且值不同 | `4f3ee56` | ✅ 删除 `input.deadline_sec`，统一 `execution.timeout_seconds: 600` |
| 3 | `resources.cpu` 类型 | `4f3ee56` | ✅ 统一为 `string` |
| 4 | 修复器崩溃无错误码可依 | `feaf7cf` | ✅ 新增 `ANALYSIS_5002`，并补三方对照表（候选全败 / 超时 / 自身崩溃） |
| 5 | 候选全败与超时混写 | `462eb5e` | ✅ `repair_job_err` = `EXEC_4003`+`FAILED`；新增 `repair_job_timeout` = `EXEC_4002`+`TIMED_OUT` |
| 6 | 请求缺 `trace_id` | `98104b3` | ✅ 四个请求样例全部补齐 |

### 逐字段比对（2026-09-25，A 组 `462eb5e` vs B 组）

用脚本比对两组 `task.schema.json`：

| 检查项 | 结果 |
|--------|------|
| 顶层 `required`（8 项） | ✅ 一致 |
| 顶层 `properties`（11 项） | ✅ 一致 |
| `execution.required` = `["mode","attempt"]` | ✅ 一致 |
| `execution.properties`（7 项） | ✅ 一致 |
| `artifact.required`（6 项） | ✅ 一致 |
| 产物 `type` 枚举（10 项） | ✅ 一致 |
| `trace_id` pattern | ✅ 一致 |
| `resources.cpu` | ✅ 已抹平（B 组补 `minLength: 1` 与说明文字） |

> 配对契约收敛完成。**两组对外承诺的接口形状现在完全相同。**

---

## 三、B 组 `task.schema.json` 当前状态

已按上表更新：

| 项 | 现在 |
|----|------|
| `required` | 8 项（`schema_version`、`job_id`、`trace_id`、`job_type`、`status`、`execution`、`input`、`created_at`） |
| `execution.required` | `["mode", "attempt"]` |
| `trace_id` | `pattern: ^trace-[a-z0-9-]+$` |
| `artifact.required` | 6 项（`artifact_id`、`type`、`uri`、`media_type`、`producer_job_id`、`sha256`） |
| 产物 `type` 枚举 | 10 项，与 A 组一致 |
| `execution.resources.cpu` | `string` |

**验证结果**：

```bash
$ python3 e2/validate.py
最小检查 01–04 全部通过。
EXIT=0
```

另做 **13 项变异测试**，新增约束全部生效：

| 变异 | 结果 |
|------|------|
| 删 `created_at` | 被拒（required） |
| 删 `execution.attempt` | 被拒（required） |
| `trace_id = "trace010"` | 被拒（pattern） |
| 产物删 `media_type` | 被拒（required） |
| 产物删 `sha256` | 被拒（required） |
| 产物 `type = "WAT"` | 被拒（enum） |
| `resources.cpu = 2`（整数） | 被拒（应为 string） |
| 产物 `type = "ERROR_REPORT"` / `"VERIFY_LOG"` | **通过**（本轮新增，属预期） |

---

## 四、后续待办

| 项 | 负责 | 状态 |
|----|------|------|
| 回复 A 组 Issue #2（第二轮 6 点） | 组长 | ✅ 已作为 Issue 评论发出 |
| 12 条裁决的 B 组侧执行 | 组长 | ✅ 已改完 `task.schema.json` 与 `validate.py` |
| 三个成员分支合入 `main` | 组长 | ✅ PR #3 / #5 / #7 全部合并并推送 |
| A 组对第二轮 6 点的回应 | A 组 | ✅ 已全部改完（`462eb5e`） |
| 两组 `task.schema.json` 逐字段比对 | 组长 | ✅ 全部一致 |
| 成员B / 成员C / 成员D 的产出 | 各成员 | ✅ 均已合并（E2 REPAIR / E3 DRAFT / E3 MDFixer） |
| T-008 AI 使用记录 | 全体 | 🔄 持续追加，按设计无终点 |
