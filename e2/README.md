# E2 — 需求与接口契约（B10）

B 组负责 **DRAFT** 与 **MDFixer** 两个服务的接口约定。E2 **不部署 API**，以仓库中的契约文件作为交付物：约定微服务之间传什么数据、怎么传、失败怎么表示。

> **状态**：2.1 / 2.2 / 2.3 三节已于 2026-09-23 回填，核对对象为 A 组仓库基线 commit `7720a30`。第 2.3 节的 7 个开放问题已同步至 [`issue_draft.md`](issue_draft.md) 的向 A 组 Issue 正文。

## 1. 分工

| 组别 | 负责服务 | 契约文件位置 |
|------|----------|--------------|
| **B10（本组）** | DRAFT | `contracts/dockerfile_job.*`（组长） |
| **B10（本组）** | MDFixer | `contracts/repair_job.*`（成员B） |
| A10 | BuildChecker | A 组仓库 `e2/contracts/full_check.*` |
| A10 | EChecker | A 组仓库 `e2/contracts/incremental_check.*` |

统一任务模型（四类共用外壳）见 [`task.schema.json`](task.schema.json)；最小检查见 [`validate.py`](validate.py)。

## 2. DRAFT 契约确认结论

<!-- 组长在第 3 步填写以下三节 -->

### 2.1 B 组确认了哪些 DRAFT 字段

逐条核对 A 组仓库 `e2/contracts/` 原文（基线 commit `7720a30`）。

| # | 字段 / 约定 | A 组约定 | B 组结论 | 依据 |
|---|-------------|----------|----------|------|
| 1 | `job_type` | `"DRAFT"` | ✅ 确认 | 四类枚举之一 |
| 2 | `input.repository.url` | git URL | ✅ 确认 | 与 A 组一致 |
| 3 | `input.repository.commit` | 完整 40 位 SHA | ✅ 确认 | `data/commits.md` 回填 C0/C1/C2 完整 SHA，格式一致 |
| 4 | `input.build.command` | `make` | ✅ 确认 | E3 基线固定构建命令 |
| 5 | `input.build.verify_command` | `make check` | ✅ 确认 | 对应 E3 第二层「功能验证」判据 |
| 6 | `input.max_iterations` | `5` | ✅ 确认 | DRAFT 允许迭代，属任务语义 |
| 7 | `input.options.base_image` | `ubuntu:22.04` | ✅ 确认，且必需 | E3 实证：失败候选用 `python:3.13-slim`、参考成功用装 `gcc make libc6-dev` 的镜像，`base_image` 必须可指定 |
| 8 | `input.options.keep_intermediate_images` | `false` | ✅ 确认 | 迭代中间镜像保留策略 |
| 9 | 状态枚举六态 | `QUEUED`→`RUNNING`→`SUCCEEDED`/`FAILED`/`TIMED_OUT`/`CANCELLED` | ✅ 确认 | 与课程一致 |
| 10 | `error.code = ENV_3002` | Docker 镜像构建失败 | ✅ 确认，**DRAFT 专用** | `error_codes.md` 该行明确标注「可能抛出的服务：DRAFT」 |
| 11 | 错误对象三字段 | `code` / `message` / `detail` | ✅ 确认 | `error_codes.md`「固定字段」一节 |
| 12 | 产物元数据字段 | `artifact_id` / `type` / `uri` / `media_type` / `producer_job_id` / `sha256` | ✅ 确认 | `artifact_format.md` |
| 13 | 产物 URI 格式 | `artifact://<pair_id>/<job_id>/<relative_path>`，`pair_id = pair10` | ✅ 确认，**双组共用** | `artifact_format.md` 注明 pair10 是「配对组编号」 |
| 14 | **B 组产物类型** | `DOCKERFILE` / `IMAGE_REF` / `GIT_PATCH` | ✅ **B 组确认** | `artifact_format.md` 原标注「占位，待 B10 确认」，现予确认 |
| 15 | B 组新增产物类型 | — | ➕ 补 `BUILD_LOG` | 复用 A 组已有类型，承载 DRAFT 构建日志与 `final_verify` 日志 |
| 16 | 分析发现写法 | `MISSING` / `REDUNDANT` 写 `output.findings`，任务可 `SUCCEEDED` | ✅ 确认 | `error_codes.md` 关键原则；B 组 `task.schema.json` 已把 `findings.type` 设为枚举 |
| 17 | 反例行为 | `job_type=ABC`→`SCHEMA_1001`；缺 `baseline`→`BASELINE_2001` | ✅ 确认 | `negative/README.md`，B 组 `validate.py` 检查 02/03 复现 |

### 2.2 B 组修改了什么

| # | 位置 | A 组原样 | B 组改为 | 理由 |
|---|------|----------|----------|------|
| 1 | 三件套全部 | **无 `execution`** | 新增 `execution`，含 `mode` / `timeout_seconds` / `started_at` / `finished_at` / `attempt` / `command` / `resources` | 课程要求 9 个公共字段，`execution` 与 `input`/`output`/`error` 并列记录执行元信息 |
| 2 | `dockerfile_job.req.json` | `input.deadline_sec: 1800` | 移至 `execution.timeout_seconds: 1800` | 超时属执行元信息，不属任务输入；与 `EXEC_4002`（任务超时）语义对齐 |
| 3 | `dockerfile_job.req.json` | 只有 `job_type` + `input` | 增加 `schema_version`、`trace_id`、`execution` | 课程把 `schema_version`/`trace_id` 列为公共字段。**与 A 组 `validate.py` 冲突，见 2.3 第 1 条** |
| 4 | `dockerfile_job.res.json` | `"input": {"_echo": "请求副本或省略"}` | 填**具体请求副本** | 占位符是二选一的说明文字，不是值，校验脚本无法据此判断 |
| 5 | `dockerfile_job.res.json` | `output.dockerfile_uri`、`output.image_ref` 裸字段 | 新增 `output.artifacts[]`，按 `artifact_format.md` 元数据格式，每项带 `sha256` | 该文档要求「每一份产物必须在 `output` 里给 URI，同时配套一份元数据」；`sha256` 满足课程的完整性核验要求 |
| 6 | `task.schema.json` | `required` = 4 项 | `required` = 7 项，加 `trace_id`、`execution`、`input` | 9 个公共字段必须齐全 |
| 7 | `task.schema.json` | `output` 是空 `object` | 声明 `artifacts` / `findings` 并 `$ref` definitions | 原样**无法**校验 `findings.type` 与产物 `type` 枚举，schema 形同虚设 |
| 8 | `task.schema.json` | 无条件约束 | 增加 `if/then`：`SUCCEEDED` 必须有 `output`；`FAILED`/`TIMED_OUT` 必须有 `error`；`INCREMENTAL_CHECK` 必须有 `input.baseline` | 把口头约定变成机器可校验的约束 |

> 修改 1、2、5 属于课程定义的**可兼容变化**吗？B 组判断：1、2 是新增可选字段与字段搬家（可兼容）；5 改变了 `output` 的结构，**若 A 组已按裸字段实现解析器则为破坏兼容**——待 A 组确认。

### 2.3 还需与 A 组讨论什么

按优先级排列。以下 7 条已提为 A 组仓库 Issue **[ana12-21/Devops_G10#2](https://github.com/ana12-21/Devops_G10/issues/2)**，
正文见 `issue_draft.md` 的「向 A 组提 Issue 的正文」一节。**B10 不直接修改 A 组仓库**，只通过该 Issue 沟通。

| # | 问题 | 冲突点 | B 组倾向 |
|---|------|--------|----------|
| 1 | **请求侧是否携带 `schema_version`** | ⚠️ **直接冲突**：A 组 `scripts/validate.py` 的 `check_request_envelope` 把 `schema_version` 与 `job_id`/`status`/`output`/`error` 并列为「请求不应携带的服务端字段」；课程却把它列为公共字段 | B 组按课程在请求里加了它。需 A 组定夺以哪个为准。（`trace_id` 不在 A 组禁用列表内，无冲突） |
| 2 | `execution` 是否双方共同加入 `task.schema.json` | 属「共享 Schema 同步更新」的可兼容变化吗？ | 是。A 组是否同步在 `full_check.*` / `incremental_check.*` 补 `execution`？ |
| 3 | `trace_id` 是否进入 `required` | A 组 4 项 required，B 组 7 项 | 按课程进入 required |
| 4 | 响应中 `input` 填副本还是省略 | A 组原样未定稿 | B 组选「填具体副本」，便于校验与排障 |
| 5 | `output.artifacts[]` 数组 vs 裸字段 | 两组 `output` 结构不一致会影响产物交接解析器 | B 组已改数组，A 组是否跟进？ |
| 6 | `artifact://pair10/` 下 DRAFT 产物的 `relative_path` 约定 | 未明确 | 建议 `<job_id>/<filename>`，如 `artifact://pair10/job-draft01/Dockerfile` |
| 7 | `sha256` 是否强制 | A 组标注为「可选」 | B 组在 DRAFT 中提为**必需**，A 组是否同步 |

## 3. 公共字段（四类任务共用）

**9 个公共字段**：`schema_version`、`job_id`、`trace_id`、`job_type`、`status`、`execution`、`input`、`output`、`error`。

`execution` 与 `input` / `output` / `error` 并列，记录执行元信息：

| execution 子字段 | 说明 |
|------------------|------|
| `execution.mode` | 执行模式 |
| `execution.timeout_seconds` | 超时上限 |
| `execution.started_at` | 开始时间 |
| `execution.finished_at` | 结束时间 |
| `execution.attempt` | 第几次尝试 |
| `execution.command` | 实际执行的命令 |
| `execution.resources` | 资源限制/占用 |

**四类任务**：`DRAFT`、`FULL_CHECK`、`INCREMENTAL_CHECK`、`REPAIR`。

**状态枚举**：`QUEUED` → `RUNNING` → `SUCCEEDED` / `FAILED` / `TIMED_OUT` / `CANCELLED`。

## 4. 约定边界

### 4.1 系统执行错误 vs 正常分析发现

| 情形 | 写法 | 任务状态 |
|------|------|----------|
| 系统执行错误（镜像构建失败 `ENV_3002`、任务超时 `EXEC_4002`、分析器失败 `ANALYSIS_5001`） | 写入 `job.error` | `FAILED` / `TIMED_OUT` |
| 正常分析发现（`MISSING`、`REDUNDANT`） | 写入 `ERROR_REPORT` 的 `findings` | **可以为 `SUCCEEDED`** |

> 检测到 MD 是正常分析发现，**不是** `job.error`。

### 4.2 四创建端点 + 一查询端点

```text
POST /v1/dockerfile-jobs
POST /v1/full-check-jobs
POST /v1/incremental-check-jobs
POST /v1/repair-jobs
GET  /v1/jobs/{job_id}
```

创建返回 **HTTP 202** + `job_id` + `status=QUEUED`。

### 4.3 产物交接

Job 只保存元数据，大文件通过引用交接：

```json
{
  "artifact_id": "graph-001",
  "type": "ACTUAL_GRAPH",
  "uri": "artifact://pair10/full01/actual.json",
  "media_type": "application/json",
  "producer_job_id": "job-full01"
}
```

需约定**解析器或下载接口**，记录提交、配置、生产任务，并以 **sha256 核验完整性**。

### 4.4 版本兼容

| 类别 | 允许的变化 |
|------|-----------|
| **可兼容** | 新增可选字段、共享 Schema 同步更新、保留已有字段含义 |
| **破坏兼容** | 删除/改名/改语义、状态枚举改变、严格 Schema 拒绝新增字段 |

## 5. 验证方式

```bash
python3 e2/validate.py
```

最小检查四项：

| 编号 | 检查内容 | 实际结果 |
|------|----------|----------|
| 01 | 四类请求与响应有效样例全部通过 | ✅ 内置四类样例 + 仓库内 `dockerfile_job.*` 全部通过；9 个公共字段齐全 |
| 02 | `job_type` 改成 `ABC` 应被拒绝 | ✅ 响应侧与请求侧均被拒（`'ABC' is not one of [...]`） |
| 03 | 删除增量任务的 `baseline` 应被拒绝 | ✅ 拒绝理由为 `'baseline' is a required property`；补回后重新通过，确认拒绝原因就是 baseline 缺失 |
| 04 | 解释 MD 为什么不等于工具执行失败 | ✅ 带 `findings` 的 `SUCCEEDED` 任务合法；`error` 与 `findings` 同存判定非法 |

运行结果（2026-09-23，Python 3.12.3 / jsonschema 4.10.3）：

```text
$ python3 e2/validate.py
task.schema.json 已加载（required=7 项，properties=11 项）
...
最小检查 01–04 全部通过。
EXIT=0
```

**反空壳验证**：对 `dockerfile_job.res.json` 做 13 项变异（删 `execution`、`sha256` 位数不足、产物 `type` 越界、`error.code` 格式错、`SUCCEEDED` 缺 `output` 等），全部被 schema 拒绝 —— 证明校验不是因为约束太松而"全过"。

`repair_job.*` 已由成员B 产出，`validate.py` 自动纳入检查，无需改动脚本——原先的三处 `SKIP` 现为 `OK`，见第 6.5 节。

## 6. REPAIR 契约确认结论（成员B）

> **Issue**：[#2](../../issues/2) ｜ **分支**：`memberB/e2-repair-contract`
> **核对对象**：A 组 `ana12-21/Devops_G10` main HEAD **`fec3fbe`**（2026-09-24 抓取）。此前第 2 节记录的基线 `7720a30` 已过时，A 组 main 已前移 18 个提交。
> **说明**：A 组仓库 `e2/contracts/` 中**已存在** `repair_job.*` 三件套，故本节与第 2 节（DRAFT）同构，是**确认 / 修改**而非凭空设计。

REPAIR 对应 **MDFixer（修复）** 服务，是四类任务中唯一会**改写代码**的一类。

### 6.1 B 组确认了哪些 REPAIR 字段

逐条核对 A 组仓库 `e2/contracts/repair_job.*` 与 `docs/` 原文（基线 `fec3fbe`）。

| # | 字段 / 约定 | A 组约定 | B 组结论 | 依据 |
|---|-------------|----------|----------|------|
| 1 | `job_type` | `"REPAIR"` | ✅ 确认 | 四类枚举之一 |
| 2 | `input.repository.{url, commit}` | git URL + 完整 40 位 SHA | ✅ 确认 | 与 DRAFT 一致；补丁必须能 `git apply` 到该 commit |
| 3 | `input.build.{command, verify_command}` | `make` / `make check` | ✅ 确认 | 修复后必须重跑这两层判据 |
| 4 | **跨 Job 输入** `input.md_report_uri` | 引用 FULL_CHECK 的检测报告产物 | ✅ 确认 | A 组 `md_report.sample.json` 的 `_consumed_by` 明确标注「B10 MDFixer 消费」 |
| 5 | **只消费 `MISSING`** | `REDUNDANT` 不由 MDFixer 处理 | ✅ 确认 | A 组 `md_report.sample.json` 注明「B 组只应消费 type=MISSING」；`docs/practice_log.md` 约定 REDUNDANT 由 A 组下次处理 |
| 6 | 状态枚举六态 | `QUEUED`→`RUNNING`→`SUCCEEDED`/`FAILED`/`TIMED_OUT`/`CANCELLED` | ✅ 确认 | 与课程一致 |
| 7 | 错误对象三字段 | `code` / `message` / `detail` | ✅ 确认 | `error_codes.md`「固定字段」一节 |
| 8 | 产物元数据字段 | `artifact_id` / `type` / `uri` / `media_type` / `producer_job_id` / `sha256` | ✅ 确认 | `artifact_format.md` |
| 9 | 产物统一走 `output.artifacts[]` | A 组 commit `84f892f`：「四类任务统一通过 `output.artifacts[]` 提供产物，不再使用响应 output 中的产物裸字段」 | ✅ 确认 | A 组已按 B10 Issue 议题 4 改定；本组 REPAIR 产物一律列于 `artifacts[]` |
| 10 | 响应 `input` 填**请求副本** | A 组 commit `f541856`：「响应中的 `input` 定稿为创建请求的 `input` 副本」 | ✅ 确认 | A 组已按 B10 Issue 议题 3 改定；本组三件套按此填写 |
| 11 | 产物 URI 格式 | `artifact://<pair_id>/<job_id>/<relative_path>`，`pair_id = pair10` | ✅ 确认 | `artifact_format.md`；`relative_path` 以 `<job_id>/<filename>` 开头 |
| 12 | **REPAIR 专用失败码** | `EXEC_4003` = 候选 patch 全部失败 | ✅ 确认 | `error_codes.md` 该行标注「可能抛出的服务：MDFixer」 |
| 13 | 修复补丁产物类型 | `GIT_PATCH` | ✅ 确认 | `artifact_format.md` 中 B 组产物类型之一 |

### 6.2 B 组修改了什么

A 组现有 `repair_job.*` **不能原样搬入本仓库**：用本仓库 `task.schema.json` 与 `validate.py` 实测，三份样例共 **7 处不合规**。下表逐条列出改动与理由。

| # | 位置 | A 组原样 | B 组改为 | 理由 |
|---|------|----------|----------|------|
| 1 | `repair_job.req.json` | 仅 `schema_version` / `job_type` / `input` 三键 | 补 `trace_id`、`execution` | 本仓库 `validate.py` 的 `check_request` 要求请求携带 `trace_id`；B 组 DRAFT 请求已携带 `execution`，四类任务保持一致 |
| 2 | `execution.resources.cpu` | 整数 `2` | 字符串 `"2"` | 本仓库 `task.schema.json` 定义 `cpu` 为 `string`（可表达 `"0.5"` / `"2000m"`）；A 组为 `integer`，属待议项（6.3 第 2 条） |
| 3 | 产物 `type` | `VERIFY_LOG` | `BUILD_LOG` | 本仓库产物枚举 8 项中**无** `VERIFY_LOG`；DRAFT 契约已用 `BUILD_LOG` 承载 `verify.log`，沿用同一口径、**不动 `task.schema.json`**（6.3 第 1 条） |
| 4 | `repair_job_err.res.json` | 无 `execution` | 补 `execution`（含 `attempt: 3`） | 本仓库把 `execution` 列入 `required`；`attempt: 3` 同时表达「已试过 3 个候选」，与 6.4 第 4 条的迭代语义一致 |
| 5 | 失败码 | `EXEC_4002` + `FAILED` | `EXEC_4003` + `FAILED` | A 组**自家** `error_codes.md` 中 `EXEC_4003` 才是「候选 patch 全部失败（MDFixer）」，`EXEC_4002` 对应 `TIMED_OUT`；原样例与自家错误码表自相矛盾 |
| 6 | `options.style_hint` | `"preserve-tab-indent"` | 枚举 `"TARGET"` | A 组取值与 E3 成员D 的四种声明风格（Target / Macro / Hybrid / Implicit）**不是同一套分类**；契约须与 E3 基线对齐 |
| 7 | `output` 结构 | 无修复语义字段 | 新增 `patch_meta` / `applied_findings` / `rejected_candidates` / `recheck` / `stats` | 候选迭代与「修完必须重验」需要机器可读的表达；`output` 未封闭额外键，可安全扩展 |

> 第 6 条另需说明：A 组原值描述的是**缩进风格**（tab / 空格），而 E3 要区分的是**声明写法**（显式规则 / 宏 / 混合 / 隐式规则）。两者不是同一维度，本组按 E3 口径枚举化。

### 6.3 还需与 A 组 / 组长讨论什么

按优先级排列。第 1–5、9 条涉及 `task.schema.json`（**组长文件**），B 组**未自行修改**，一律走 Issue。

| # | 问题 | 冲突点 | B 组倾向 |
|---|------|--------|----------|
| 1 | 产物 `type` 是否补 `VERIFY_LOG` | A 组枚举含 `VERIFY_LOG` / `ERROR_REPORT`，本仓库 8 项无 | 本组先用 `BUILD_LOG` 承载 `verify.log`，**不动 schema**；若要独立类型请组长裁决 |
| 2 | `execution.resources.cpu` 类型 | A 组 `integer`，本仓库 `string` | 统一为 `string`（可表达小数与 Kubernetes 风格 `"2000m"`） |
| 3 | `execution` 是否进 `required` | A 组 `required` 不含 `execution`，本仓库含 | 保留本组「必填」；A 组失败样例因此缺 `execution`，需 A 组补齐 |
| 4 | `execution.attempt` 是否提必填 | A 组 `[mode, attempt]`，本仓库 `[mode]` | REPAIR 靠 `attempt` 表达候选轮次，**建议提为必填**（需组长改 schema） |
| 5 | `required` 项次是否取并集 | A 组含 `created_at`，本仓库含 `execution` | 请组长裁定是否合并为 8 项；本组样例已同时携带两者，两种口径均可通过 |
| 6 | `trace_id` 是否加 `pattern` | A 组 `^trace-[a-z0-9-]+$`，本仓库仅 `minLength: 1` | 无实质冲突，本组可跟进 |
| 7 | `artifact` 的 `media_type` / `sha256` 是否必填 | A 组两者必填，本仓库为可选 | 本组 REPAIR 产物已一律携带；是否提为 schema 必填请组长裁定 |
| 8 | **修复器自身崩溃**用哪个错误码 | `ANALYSIS_5001` 的「可能抛出的服务」列表**不含 MDFixer** | 本组无码可用；请 A 组把 MDFixer 写入该行，或新增 `ANALYSIS_5002` |
| 9 | 请求侧是否携带 `schema_version` | 与第 2.3 节第 1 条同源 | 沿用 2.3 结论，等 A 组定夺 |
| 10 | REPAIR 超时样例是否另立 | A 组原样例把超时与候选全败混为一谈 | 本组 `repair_job_err.res.json` 只承载「候选全败」（`EXEC_4003`）；超时应为 `EXEC_4002` + `status=TIMED_OUT`，是否补一份样例请 A 组确认 |

### 6.4 REPAIR 与其余三类的差异点

验收要求「差异点逐条写明理由」，共 8 条。

| # | 差异点 | REPAIR | 其余三类 | 理由 |
|---|--------|--------|----------|------|
| 1 | **唯一会改写代码** | 产出 `GIT_PATCH`，是对项目的真实修改 | DRAFT 产出运行环境，检测类只读产出报告 | 修复是唯一带「副作用」的任务，补丁必须可 `git apply` 且绑定具体 commit |
| 2 | **唯一以「别的 Job 的产物」为输入** | `input.md_report_uri` 引用 FULL_CHECK 的检测报告 | 另三类输入都是仓库 + 构建命令 | 需要跨 Job 的产物引用链，`sha256` 是这条链的完整性保证 |
| 3 | **只消费 `MISSING`** | `REDUNDANT` 必须过滤掉，不进修复路径 | 检测类两类发现都产出 | 冗余依赖删除属另一类改动，A 组 `practice_log.md` 已约定由其自身处理 |
| 4 | **迭代单位不同** | 迭代的是**候选 patch**，`execution.attempt` = 候选轮次 | DRAFT 迭代的是 **Dockerfile 修订** | 同名字段在两类任务里语义不同，故用 `output.rejected_candidates` 与被接受候选对照记录 |
| 5 | **失败码不同** | `EXEC_4003`（候选全败，REPAIR 专用） | DRAFT 用 `ENV_3002`（镜像构建失败） | 「候选全败」≠「环境构建失败」，两者排查动作完全不同 |
| 6 | **双重验证** | 补丁应用后必须重跑 build + verify，结果写入 `output.recheck` | DRAFT 只有一次 `final_verify` | 修复的判据是「改完之后还成立」，不能沿用修复前的旧结论 |
| 7 | **`style_hint` 是独有维度** | 声明风格（Target / Macro / Hybrid / Implicit） | DRAFT 用 `base_image` 等环境选项 | 修复风格直接对应 E3 成员D 的四种风格与 Target 参考 Patch |
| 8 | **幂等性要求更高** | 补丁须能 `git apply --check` 到指定 commit（`patch_meta.applies_cleanly`） | —— | 修复产物要能被 A 组或人工在固定版本上原样复现 |

### 6.5 验证方式

**1. 契约校验（三处 `SKIP` → `OK`）**

```bash
python3 e2/validate.py
```

运行结果（2026-09-24，**Ubuntu 22.04.5 LTS（WSL2, x86_64）** / Python 3.10.12 / jsonschema 3.2.0）：

```text
$ python3 e2/validate.py
E2 契约校验（B10）
Schema: e2/task.schema.json
task.schema.json 已加载（required=7 项，properties=11 项）

====================================================================
01  四类任务的有效请求与响应样例全部通过 task.schema.json
====================================================================
    OK    内置响应样例 DRAFT 通过（job_id=job-draft）
    OK    内置响应样例 FULL_CHECK 通过（job_id=job-fullcheck）
    OK    内置响应样例 INCREMENTAL_CHECK 通过（job_id=job-incrementalcheck）
    OK    内置响应样例 REPAIR 通过（job_id=job-repair）
    OK    内置请求样例 DRAFT
    OK    内置请求样例 FULL_CHECK
    OK    内置请求样例 INCREMENTAL_CHECK
    OK    内置请求样例 REPAIR
    OK    dockerfile_job.res.json 通过（status=SUCCEEDED）
    OK    dockerfile_job_err.res.json 通过（status=FAILED）
    OK    repair_job.res.json 通过（status=SUCCEEDED）
    OK    repair_job_err.res.json 通过（status=FAILED）
    OK    dockerfile_job.req.json
    OK    repair_job.req.json
    OK    9 个公共字段齐全：schema_version、job_id、trace_id、job_type、status、execution、input、output、error
    OK    error 字段可用：FAILED 样例携带 error 通过校验
    OK    可选字段 output / error / created_at / updated_at 均已声明
    OK    execution 时间字段均为 ISO8601 UTC

====================================================================
02  job_type 改成 ABC，应被拒绝
====================================================================
    OK    已拒绝，理由：job_type: 'ABC' is not one of ['DRAFT', 'FULL_CHECK', 'INCREMENTAL_CHECK', 'REPAIR']
    OK    job_type=ABC 请求 已被拒绝（预期）：job_type='ABC' 不在四类枚举内

====================================================================
03  删除 INCREMENTAL_CHECK 的 baseline，应被拒绝
====================================================================
    OK    已拒绝，理由：input: 'baseline' is a required property
          （被删除的 baseline 内容：{"commit": "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "configuration_id": "cc-MODE0", "actual_graph_uri": "artifact://pair10/job-fullcheck/actual.json"}）
    OK    补回 baseline 后重新通过，确认拒绝原因就是 baseline 缺失

====================================================================
04  MD ≠ 工具执行失败；error 与 findings 互斥
====================================================================

    三种情形必须分清：

    | 情形           | status      | job.error      | output.findings | 含义                     |
    |----------------|-------------|----------------|-----------------|--------------------------|
    | 检测到缺失依赖 | SUCCEEDED   | 空             | 有（MISSING）   | 工具正常完成，发现了问题 |
    | 分析器崩溃     | FAILED      | ANALYSIS_5001  | 空              | 工具失败了，结论不可信   |
    | 两者同存       | ——          | 有             | 有              | 非法：无法判断成功还是失败 |

    OK    检测出 MISSING 的任务是合法 SUCCEEDED —— 发现数 > 0 不等于任务失败
    OK    findings.type 只接受 MISSING / REDUNDANT
    OK    error 与 findings 同存已被判定非法（互斥约束生效）
    OK    只有 error、没有 findings 的失败任务是合法的

====================================================================
结论
====================================================================
最小检查 01–04 全部通过。
EXIT=0
```

> 环境说明：上述输出取自 **Linux 环境（Ubuntu 22.04.5 LTS / WSL2, x86_64）**，Python 3.10.12 + jsonschema 3.2.0，**满足课程「所有命令必须在 Linux 下运行」的要求**。
> 需注意：仓库 [`README.md`](../README.md) 记录的本组验证环境为 **Ubuntu 24.04.3 LTS（Python 3.12.3）**，第 5 节的 DRAFT 结论即出自该环境；本次 REPAIR 复跑使用的是另一台 WSL 发行版 **Ubuntu 22.04.5**。**两套 Linux 发行版下输出一致**，故本节结论不依赖具体发行版版本。
> `validate.py` 只依赖 Python 标准库与 `jsonschema`。同一套契约文件另在 Python 3.13.12 + jsonschema 4.26.0（Windows 11 + Git Bash）下复跑，结果与上表**逐项一致** —— 说明校验结论与操作系统、与 `jsonschema` 主版本（3.x / 4.x）均无关。

**2. 反空壳变异测试（34 项）**

沿用组长对 DRAFT 的做法，对 REPAIR 三件套逐项破坏，**每一项都必须被拒绝**，证明校验通过不是约束太松：

| 变异类别 | 项数 | 示例 |
|----------|------|------|
| 响应侧（完整 schema） | 19 | 删 `execution`、`status` 改 `BOGUS`、`SUCCEEDED` 删 `output`、`resources.cpu` 改整数、`attempt` 改 `0`、产物 `type` 改 `VERIFY_LOG`、`sha256` 截短/含大写、URI 非 `artifact://pair10/` 协议 |
| 失败侧 | 6 | `FAILED` 删 `error`、`error.code` 改 `exec4003`、`error` 缺 `message`、删 `execution` |
| 请求侧（`check_request` 规则） | 9 | 请求携带 `status`/`job_id`/`output`/`error`、删 `trace_id`、`job_type` 改 `ABC`、`execution.mode` 改 `BOGUS` |

完整 34 项逐条结果（同上环境）：

```text
反空壳变异测试 —— 每一项都必须被拒绝
========================================================================
  OK  已拒绝  [res] 删 execution
  OK  已拒绝  [res] status 改 BOGUS
  OK  已拒绝  [res] job_type 改 ABC
  OK  已拒绝  [res] job_id 去掉 job- 前缀
  OK  已拒绝  [res] SUCCEEDED 删 output
  OK  已拒绝  [res] schema_version 改 2.0.0
  OK  已拒绝  [res] resources.cpu 改整数
  OK  已拒绝  [res] attempt 改 0
  OK  已拒绝  [res] execution.mode 改 BOGUS
  OK  已拒绝  [res] trace_id 删空
  OK  已拒绝  [res] 产物 type 改 VERIFY_LOG
  OK  已拒绝  [res] 产物 sha256 截短
  OK  已拒绝  [res] 产物 sha256 含大写
  OK  已拒绝  [res] 产物 uri 去掉 pair10
  OK  已拒绝  [res] 产物 uri 非 artifact 协议
  OK  已拒绝  [res] 产物缺 producer_job_id
  OK  已拒绝  [res] 产物 producer_job_id 非法
  OK  已拒绝  [res] 产物缺 artifact_id
  OK  已拒绝  [res] artifacts 不是数组
  OK  已拒绝  [err] FAILED 删 error
  OK  已拒绝  [err] status 改 SUCCEEDED（无 output）
  OK  已拒绝  [err] error.code 改 exec4003
  OK  已拒绝  [err] error.code 改 EXEC_403
  OK  已拒绝  [err] error 缺 message
  OK  已拒绝  [err] 删 execution
  OK  已拒绝  [req] 请求携带 status
  OK  已拒绝  [req] 请求携带 job_id
  OK  已拒绝  [req] 请求携带 output
  OK  已拒绝  [req] 请求携带 error
  OK  已拒绝  [req] 请求删 trace_id
  OK  已拒绝  [req] 请求删 schema_version
  OK  已拒绝  [req] 请求 job_type 改 ABC
  OK  已拒绝  [req] 请求 execution.mode 改 BOGUS
  OK  已拒绝  [req] 请求 input 改字符串
========================================================================
合计 34 项：被拒绝 34，漏网 0
```

> 说明：三类变异分别走**两条不同校验路径** —— 响应/失败侧走 `task.schema.json` 完整校验，请求侧走 `validate.py` 的 `check_request` 请求侧规则（请求不携带服务端字段）。因此 34 项同时证明了 **schema 不是空壳** 与 **请求侧规则不是空壳**。

**3. 必要字段删除自测（`validate.py` 直报）**

上面 34 项走的是脚本化路径；这里再给一次**原文件级**的直白复现：从 `repair_job.res.json` 中删掉公共字段 `trace_id`（删除前取值 `"trace-020"`），直接在仓库根运行校验脚本。

```text
$ python3 e2/validate.py
    OK    dockerfile_job_err.res.json 通过（status=FAILED）
    FAIL  repair_job.res.json 未通过：["<root>: 'trace_id' is a required property"]
    OK    repair_job_err.res.json 通过（status=FAILED）
    OK    repair_job.req.json
...
结论
未通过 1 项：
  - repair_job.res.json 未通过：["<root>: 'trace_id' is a required property"]

$ echo $?
1
```

该自测确认三件事：① 三件套**确实被脚本读取并逐份校验**，不是被 `SKIP` 跳过；② 公共字段缺失会**指名报出**，并被计入「未通过」清单；③ 报错定位到具体文件与字段，**无须改动校验脚本**。自测后文件已按 `sha256` 逐字节还原（恢复后哈希与删除前一致），仓库状态仍为 `EXIT=0`。

> 环境说明：本次自测在 Windows 11 + Git Bash（Python 3.13.12 / jsonschema 4.26.0）下取得；第 1、2 节的 Linux 实测已证明两者结论逐项一致。如需 Linux 侧原文，可在 WSL 中执行：
>
> ```bash
> python3 - <<'PY'
> import json, pathlib
> p = pathlib.Path('e2/contracts/repair_job.res.json')
> d = json.loads(p.read_text(encoding='utf-8'))
> d.pop('trace_id')
> p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding='utf-8')
> PY
> python3 e2/validate.py; echo "EXIT=$?"
> git restore e2/contracts/repair_job.res.json   # 自测后还原，务必执行
> ```

**4. 与 A 组的产物衔接**

`input.md_report_uri` 指向 FULL_CHECK 的 `ERROR_REPORT`；`output.applied_findings` 只回填 `type = "MISSING"` 的条目，与 A 组 `md_report.sample.json` 的 `findings` 逐条对应。
