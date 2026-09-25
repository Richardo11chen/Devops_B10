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

---

## 二、A 组对 7 个议题的回应现状

A 组在 `fec3fbe` 中逐条回应：

| 议题 | A 组处理 | 状态 |
|------|----------|------|
| 1 请求带 `schema_version` | ✅ 已加 | **部分解决** —— `trace_id` 仍未加 |
| 2 `execution` 入 schema | ⚠️ 加了，但定为**可选** | **与课程冲突**，见裁决第 3 条 |
| 3 响应 `input` 填副本 | ✅ 定稿为请求副本 | ✅ 已对齐 |
| 4 `output.artifacts[]` | ✅ 四类响应全改，删裸字段 | ✅ 已对齐 |
| 5 `required` 扩容 | ⚠️ 扩到 7 项，含 `created_at`、**不含 `execution`** | 见裁决第 5 条 |
| 6 `sha256` 必需 | ✅ | ✅ 已对齐 |
| 7 产物 URI 约定 | ✅ `artifact://<pair_id>/<job_id>/<relative_path>` | ✅ 已对齐 |

**新发现的 A 组自相矛盾处：**

1. `dockerfile_job.req.json` 同时存在 `input.deadline_sec: 1800` 与 `execution.timeout_seconds: 600` —— 同一个超时写了两处，且值不同（裁决第 12 条）
2. `execution.resources.cpu` 为整数 `2`，B 组为字符串 `"2"`（裁决第 2 条）
3. A 组失败样例缺 `execution`（裁决第 3 条）

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
| 回复 A 组 Issue #2（裁决第 2、3、8、10、12 条） | 组长 | ✅ 已完成，已作为 Issue 评论发出 |
| `dockerfile_job.*` 三件套是否需跟着改 | 组长 | ✅ 已确认无需改动（本已满足新约束） |
| 成员B 的 `repair_job.*` 是否满足新约束 | 成员B | ✅ 已复跑，三处由 `SKIP` 变 `OK` |
| 两个成员分支合入 `main` | 组长 | ✅ 已合并（PR #3 / PR #5），冲突已手工解决 |
| 等 A 组对第二轮 6 点的回应 | A 组 | ⏳ 等待中 |
| 成员D 的 E3 MDFixer 固定输入 | 成员D | ⏳ **尚未开始**（当前唯一缺口） |
