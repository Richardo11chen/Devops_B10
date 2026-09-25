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

以下 7 条已提为 A 组仓库 Issue **[ana12-21/Devops_G10#2](https://github.com/ana12-21/Devops_G10/issues/2)**。
**B10 不直接修改 A 组仓库**，只通过该 Issue 沟通。

**最新进展（2026-09-25）**：A 组已在 `fec3fbe` 中逐条回应，**5 条已对齐**（议题 3、4、6、7，以及议题 1 的 `schema_version` 部分）。
剩余 6 点待 A 组处理，**完整裁决与执行方见 [`resolutions.md`](resolutions.md)**。

下表为初次提出时的原始记录，保留以追溯来龙去脉：

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
> **核对对象（双基线）**：任务书指定的 A 组基线 commit **`7720a30`**，以及核对时 A 组 main 的现况 **`fec3fbe`**（2026-09-24 抓取）。A 组在这两点之间**自己改过** `repair_job.*` 与 `task.schema.json`，故本节所有「A 组原样」列**并列给出两个基线的取值**，两种口径都能核对；文件级差异见 6.6。
> **说明**：A 组仓库 `e2/contracts/` 中**已存在** `repair_job.*` 三件套，故本节与第 2 节（DRAFT）同构，是**复制 → 逐条确认 → 修正**，而非凭空设计。
> **裁决状态（2026-09-25）**：6.3 的 12 条议题已由组长裁决，**完整裁决见 [`resolutions.md`](resolutions.md)**（组长维护，成员只读；独立成文以避免本节与组长同时改同一文件）。摘要：B 组侧 **6 条已执行完毕**（第 1、4、5、6、7、11 条），**6 条转 A 组**（第 2、3、8、9 的 `trace_id` 部分、10、12 条），第 9 条的 `schema_version` 部分已由 A 组解决。`task.schema.json` 相应收紧（`required` 7 → 8 项、`execution.required` 加 `attempt`、`trace_id` 加 `pattern`、产物枚举 8 → 10 项），**本组三件套无需返工**——已在合并后的最新代码上复跑确认，见 6.5 第 2 节与 6.7。

REPAIR 对应 **MDFixer（修复）** 服务，是四类任务中唯一会**改写代码**的一类。

### 6.1 B 组确认了哪些 REPAIR 字段

逐条核对 A 组仓库 `e2/contracts/repair_job.*`、`e2/contracts/full_check.req.json`、`error_codes.md`、`artifact_format.md` 与 `docs/` 原文。

| # | 字段 / 约定 | A 组约定（`7720a30` / `fec3fbe`） | B 组结论 | 依据 |
|---|-------------|----------------------------------|----------|------|
| 1 | `job_type` | `"REPAIR"`（两基线同） | ✅ 确认 | 四类枚举之一 |
| 2 | `input.repository.{url, commit}` | git URL + `<C0_FULL_40_SHA>`（两基线同） | ✅ 确认 | 与 A 组 `full_check.req.json` 的 `<C0_FULL_40_SHA>` **一致**：MD 在 C0 检出，补丁也打在 C0 |
| 3 | **`input.makefile_uri`** | `artifact://pair10/job-full01/Makefile`（两基线均有；`7720a30` 为 `…/full01/Makefile`） | ✅ 确认，**必须保留** | E3 成员D 的「固定输入四件套」含「同一源码版本的 Makefile」；缺此引用 MDFixer 无法确定该修哪个 Makefile |
| 4 | `input.build.{command, verify_command}` | `make` / `make check`（两基线同） | ✅ 确认 | 修复后必须重跑这两层判据（E3 两层成功判据） |
| 5 | `input.options.max_candidates` | `3`，位于 **`input.options` 之内**（两基线同） | ✅ 确认，**位置不改** | 与 A 组 `full_check.req.json` 把 `max_jobs` 放进 `options` 的约定一致 |
| 6 | **跨 Job 输入** `input.md_report_uri` | 引用 FULL_CHECK 的检测报告 `…/job-full01/md_report.json` | ✅ 确认 | A 组 `md_report.sample.json` 的 `_consumed_by` 明确标注「B10 MDFixer 消费」 |
| 7 | **只消费 `MISSING`** | `REDUNDANT` 不由 MDFixer 处理 | ✅ 确认 | `md_report.sample.json` 注明「B 组只应消费 type=MISSING」；`docs/practice_log.md` 约定 REDUNDANT 由 A 组处理 |
| 8 | 状态枚举六态 | `QUEUED`→`RUNNING`→`SUCCEEDED`/`FAILED`/`TIMED_OUT`/`CANCELLED` | ✅ 确认 | 与课程一致 |
| 9 | 错误对象三字段 | `code` / `message` / `detail` | ✅ 确认 | `error_codes.md`「固定字段」一节 |
| 10 | 产物元数据字段 | `artifact_id` / `type` / `uri` / `media_type` / `producer_job_id` / `sha256` | ✅ 确认 | `artifact_format.md` |
| 11 | 产物统一走 `output.artifacts[]` | `7720a30` 时**尚无** `artifacts[]`，产物是裸字段 `output.git_patch_uri`；`fec3fbe` 已改为数组 | ✅ 确认 | A 组 commit `84f892f` 按 B10 议题 4 改定；本组 REPAIR 产物一律列于 `artifacts[]` |
| 12 | 响应 `input` 填**请求副本** | `7720a30` 为占位符 `{"_echo": "请求副本或省略"}`；`fec3fbe` 已改为请求副本 | ✅ 确认 | A 组 commit `f541856` 按 B10 议题 3 改定 |
| 13 | 产物 URI 格式 | `artifact://<pair_id>/<job_id>/<relative_path>`，`pair_id = pair10` | ✅ 确认 | `artifact_format.md`；`fec3fbe` 起 `relative_path` 以 `<job_id>/` 开头（补 `job-` 前缀） |
| 14 | **REPAIR 专用失败码** | `error_codes.md` 中 `EXEC_4003` = 候选 patch 全部失败，服务列含 MDFixer（该文件**两基线完全相同**） | ✅ 确认 | 与 A 组现用样例的 `EXEC_4002` 矛盾，见 6.2 第 7 条 |
| 15 | 修复补丁产物类型 | `GIT_PATCH` | ✅ 确认 | `artifact_format.md` 中 B 组产物类型之一 |
| 16 | `output` 的修复语义键 | `patch_meta` / `applied_findings` / `rejected_candidates` / `recheck` / `stats` —— **`7720a30` 时就已存在** | ✅ 确认，全部沿用原键名 | 这五组键由 A 组原样提供，本组只在其上补充少量字段（见 6.2 第 10–13 条） |

### 6.2 B 组修改了什么

A 组现有 `repair_job.*` **不能原样搬入本仓库**：用本仓库 `task.schema.json` 与 `validate.py` 实测，三份样例共 **14 处**需要改动或补充。下表逐条列出，并**同时标注两个基线的取值**。

| # | 位置 | A 组原样（`7720a30` → `fec3fbe`） | B 组改为 | 理由 |
|---|------|-----------------------------------|----------|------|
| 1 | 请求侧公共字段 | `7720a30` 仅 `job_type` + `input` **两键**；`fec3fbe` 加了 `schema_version`，**仍无** `trace_id` / `execution` | 补 `trace_id`、`execution`（`mode` / `timeout_seconds` / `resources`） | `validate.py` 的 `check_request` 要求请求携带 `trace_id`；本组 DRAFT 请求同样携带 `execution`，四类任务保持一致 |
| 2 | 响应 / 失败侧 `execution` | `7720a30` res 与 err **均无** `execution`；`fec3fbe` res 有、**err 仍无** | 两份都补 `execution` | `task.schema.json` 把 `execution` 列入 `required`（组长定稿）；A 组失败样例因此不合规 |
| 3 | `execution.resources.cpu` | `7720a30` 无 `execution`；`fec3fbe` 为整数 `2` | 字符串 `"2"` | 本仓库 schema 定义 `cpu` 为 `string`（可表达 `"0.5"` / `"2000m"`）；A 组为 `integer`，属待议项（6.3 第 2 条） |
| 4 | `execution.timeout_seconds` | `fec3fbe`：res 为 `300`，同批 err 的 `detail.deadline_sec` 为 `600`（**A 组自不一致**） | 三件套统一 `300` | 消除 A 组样例的内部矛盾；本组 `stats.duration_sec = 229` 落在该上限内 |
| 5 | `execution.attempt` | `fec3fbe` res 为 `1` | `3` | REPAIR 的 `attempt` = **候选轮次**（ADR-002）：`3` 表示第 3 个候选才通过，与 `stats` 的 3 / 2 / 1 对应 |
| 6 | 产物 `type` | `7720a30` **无 `artifacts[]`**（产物为裸字段 `output.git_patch_uri`）；`fec3fbe` 有 `artifacts[]`，其中一项为 `VERIFY_LOG` | 该项改 `BUILD_LOG` | **理由已随裁决更新**：裁决第 1 条把 `VERIFY_LOG` 并入枚举（8 → 10 项），本项**已非合规所迫**；仍用 `BUILD_LOG` 是为与**组长定稿的 DRAFT 口径**一致（`dockerfile_job.res.json` 的 `verify.log` 亦为 `BUILD_LOG`，组长裁定其「无需改动」）。若要统一为 `VERIFY_LOG`，须 DRAFT 与 REPAIR **一并改**，故列为新待议项（6.7 第 2 条） |
| 7 | 失败码 | `EXEC_4002` + `FAILED`（**两基线同**） | `EXEC_4003` + `FAILED` | A 组**自家** `error_codes.md` 里 `EXEC_4003` 才是「候选 patch 全部失败（MDFixer）」，`EXEC_4002` 对应 `TIMED_OUT`；原样例与自家错误码表自相矛盾 |
| 8 | 失败 `detail` 结构 | `deadline_sec` / `iterations_used` / `last_failure_step` / `log_uri`（两基线同，属**超时**语义） | `candidates_generated` / `candidates_rejected` / `max_candidates` / `last_failure_step` / `exit_code` / `log_uri` | `EXEC_4003` 的触发条件是「候选全败」，detail 应回答「试了几个候选、卡在哪一层」，故以候选计数替换超时字段 |
| 9 | `input.options.style_hint` | `"preserve-tab-indent"`（两基线同） | 枚举 `"TARGET"` | A 组取值描述**缩进风格**（tab / 空格），与 E3 成员D 的四种**声明风格**（Target / Macro / Hybrid / Implicit）不是同一套分类；契约须与 E3 基线对齐 |
| 10 | `output.patch_meta` | 键 = `files_changed`（文件名数组）/ `lines_added` / `lines_removed` / `style`（两基线同） | 沿用全部键，新增 `base_commit`、`applies_cleanly` | 幂等性要求：补丁须能 `git apply --check` 到指定 commit（6.4 第 8 条），需要机器可读的基线与可应用性标记 |
| 11 | `output.rejected_candidates` | 键名两基线同，但样例中恒为空数组 `[]` | 沿用键名，样例给出 2 条记录：`candidate` / `summary` / `rejected_at` / `reason` / `log_uri` | A 组未定义非空记录的字段形态；候选迭代是本类核心语义（ADR-002），须显式定义才能评审「是否真试了多轮」 |
| 12 | `output.recheck` | 键 = `build_log_uri` / `build_exit_code` / `verify_log_uri` / `verify_exit_code`（两基线同） | 沿用全部键，新增 `behavior_changed` | 「编译过但行为没变」是 order-only 依赖的典型陷阱，须与 `verify_exit_code = 0` 分开记录 |
| 13 | `output.stats` | 键 = `duration_sec` / `candidates_generated` / `candidates_rejected`（两基线同） | 沿用全部键，新增 `candidates_accepted` | 与 `attempt` 对照即可自检「第 3 个候选被接受」，闭合 3 / 2 / 1 的计数 |
| 14 | `output.artifacts[]` 条目数 | `fec3fbe` 为 3 件（`patch-001` / `build-log-003` / `verify-log-002`） | 5 件：保留 A 组原 `artifact_id`，追加 `cand1-log-004`、`cand2-log-005` | ADR-002 第 5 条与 A 组议题 4 口径：所有产物引用统一经 `artifacts[]` 交接，`rejected_candidates[].log_uri` 指向的日志也须登记 |

> **改动构成**：14 条中 **3 条由本仓库 `task.schema.json` / `validate.py` 直接驱动**（第 1 条的 `trace_id`、第 2 条、第 3 条），其余 11 条为**取值对齐**与 **REPAIR 语义所必需的新增可选键**。后者全部落在 `input` / `output` 这两个 schema 未封闭的 `object` 内，属 ADR-001 定义的**可兼容变化**（新增可选字段）。第 6 条原先也属「schema 驱动」，裁决第 1 条后枚举已含 `VERIFY_LOG`，该条转为**口径选择**（见 6.7 第 2 条）。

> **相对本节上一版（`e74af37`）的纠正**：上一版曾把 `input` 改成 A 组没有的形态 —— 漏掉 `makefile_uri`、把 `max_candidates` 提到 `input` 顶层、新增来源不明的 `source_commit`、`repository.commit` 写成 `<C1_FULL_40_SHA>`。这四处**都不是 schema 冲突驱动的**，属越界改动，本版已全部回到 A 组口径：`makefile_uri` 恢复（6.1 第 3 条）、`max_candidates` 移回 `input.options`（6.1 第 5 条）、`source_commit` 删除并转为待议项（6.3 第 11 条）、`commit` 改回 `<C0_FULL_40_SHA>`（6.1 第 2 条）。

### 6.3 还需与 A 组 / 组长讨论什么

按优先级排列。第 1–5、9 条涉及 `task.schema.json`（**组长文件**），B 组**未自行修改**，一律走 Issue。

**2026-09-25 更新**：12 条**已全部裁决**，末列给出结果；完整裁决理由与执行方见 [`resolutions.md`](resolutions.md)（组长维护）。

| # | 问题 | 冲突点 | B 组倾向 | 裁决（2026-09-25） |
|---|------|--------|----------|--------------------|
| 1 | 产物 `type` 是否补 `VERIFY_LOG` | A 组枚举含 `VERIFY_LOG` / `ERROR_REPORT`，本仓库 8 项无 | 本组先用 `BUILD_LOG` 承载 `verify.log`，**不动 schema**；若要独立类型请组长裁决 | ✅ **采纳 A 组完整枚举（10 项）**——已由组长改 schema；本组三件套不受影响（6.2 第 6 条） |
| 2 | `execution.resources.cpu` 类型 | A 组 `integer`，本仓库 `string` | 统一为 `string`（可表达小数与 Kubernetes 风格 `"2000m"`） | ⏳ **转 A 组**：裁决统一为 `string`，理由为整数表达不了毫核值 |
| 3 | `execution` 是否进 `required` | A 组 `required` 不含 `execution`，本仓库含 | 保留本组「必填」；A 组失败样例因此缺 `execution`，需 A 组补齐 | ⏳ **转 A 组**：课程原文要求公共字段**必须包含 `execution`**，A 组需补齐 |
| 4 | `execution.attempt` 是否提必填 | A 组 `[mode, attempt]`，本仓库 `[mode]` | REPAIR 靠 `attempt` 表达候选轮次，**建议提为必填** | ✅ **提为必填**，本组已对齐 A 组的 `["mode", "attempt"]` |
| 5 | `required` 项次是否取并集 | A 组含 `created_at`，本仓库含 `execution` | 请组长裁定是否合并为 8 项；本组样例已同时携带两者，两种口径均可通过 | ✅ **取并集，8 项**（补 `created_at`）——本组样例原就携带两者，无需改动 |
| 6 | `trace_id` 是否加 `pattern` | A 组 `^trace-[a-z0-9-]+$`，本仓库仅 `minLength: 1` | 无实质冲突，本组可跟进 | ✅ **加 pattern**，与 A 组一致 |
| 7 | `artifact` 的 `media_type` / `sha256` 是否必填 | A 组两者必填，本仓库为可选 | 本组 REPAIR 产物已一律携带；是否提为 schema 必填请组长裁定 | ✅ **都提为必填**（4 → 6 项）——本组产物原就携带两者，无需改动 |
| 8 | **修复器自身崩溃**用哪个错误码 | `ANALYSIS_5001`（分析器失败）的服务列**不含 MDFixer**；`ENV_3001`（可运行镜像拉取失败）的服务列**含 MDFixer** | 仅「修复器内部异常」这一类无码可依；请 A 组把 MDFixer 写入 `ANALYSIS_5001` 该行，或新增 `ANALYSIS_5002` | ⏳ **转 A 组**：裁决**新增 `ANALYSIS_5002`**（修复器内部异常），不改 `ANALYSIS_5001` 的语义 |
| 9 | 请求侧是否携带 `schema_version` | 与第 2.3 节第 1 条同源 | 沿用 2.3 结论，等 A 组定夺 | ✅ `schema_version` **已解决**（A 组已加）；⏳ `trace_id` **仍未加，继续追** |
| 10 | REPAIR 超时样例是否另立 | A 组原样例把「候选全败」写成超时（`EXEC_4002` + 「Repair timed out」），与自家错误码表矛盾 | 本组 `repair_job_err.res.json` 只承载「候选全败」（`EXEC_4003`）；超时应为 `EXEC_4002` + `status = TIMED_OUT`，是否补一份样例请 A 组确认 | ✅ **支持成员B**——本组样例的取舍被采纳；补超时样例转 A 组 |
| 11 | `input.source_commit` 是否入契约 | **组长** `e2/validate.py` 的内置 REPAIR 请求样例（第 123–125 行）携带 `source_commit`；A 组 `repair_job.req.json` **两个基线都没有** | 本组**不采纳**：与 `input.repository.commit` 语义重复，两者取值不一致时无法确定以谁为准 | ✅ **不入契约，已从 B 组删除**；组长确认该字段系其**本人笔误**，已在 `validate.py` 留注释防止再加回 |
| 12 | `execution.timeout_seconds` 口径 | A 组 res 为 `300`，同批 err 的 `detail.deadline_sec` 为 `600`，两者自不一致 | 本组三件套统一 `300`，请 A 组同步；超时场景应另立样例（见第 10 条） | ⏳ **转 A 组**：裁决删除 `input.deadline_sec`，超时只由 `execution.timeout_seconds` 表达 |

**裁决统计**：B 组侧 **6 条已执行完毕**（第 1、4、5、6、7、11 条），**6 条转 A 组**（第 2、3、8、9 的 `trace_id` 部分、10、12 条），第 9 条的 `schema_version` 部分已解决。转 A 组的部分已写入 A 组 Issue `[B10] DRAFT 接口确认` 的第二轮回复（见 `issue_draft.md`），**本组不重复提**。

> 关于第 11 条：裁决明确记载该字段是**组长的错误**、不是 A 组的问题。本组「顶住没采纳」的判断被完整接受——这也是本轮唯一一次 AI 建议与人工判断一致的驳斥。相关记录见 `AI_USAGE.md` 的 AI-005。

### 6.4 REPAIR 与其余三类的差异点

验收要求「差异点逐条写明理由」，共 8 条。

| # | 差异点 | REPAIR | 其余三类 | 理由 |
|---|--------|--------|----------|------|
| 1 | **唯一会改写代码** | 产出 `GIT_PATCH`，是对项目的真实修改 | DRAFT 产出运行环境，检测类只读产出报告 | 修复是唯一带「副作用」的任务，补丁必须可 `git apply` 且绑定具体 commit |
| 2 | **唯一以「别的 Job 的产物」为输入** | `input.md_report_uri` 引用 FULL_CHECK 的检测报告，`input.makefile_uri` 引用同一 FULL_CHECK 上交的 Makefile | 另三类输入都是仓库 + 构建命令 | 需要跨 Job 的产物引用链，`sha256` 是这条链的完整性保证；Makefile 必须与被检测的源码**同版本**，否则修复结论无法复现 |
| 3 | **只消费 `MISSING`** | `REDUNDANT` 必须过滤掉，不进修复路径 | 检测类两类发现都产出 | 冗余依赖删除属另一类改动，A 组 `practice_log.md` 已约定由其自身处理 |
| 4 | **迭代单位不同** | 迭代的是**候选 patch**，`execution.attempt` = 候选轮次 | DRAFT 迭代的是 **Dockerfile 修订** | 同名字段在两类任务里语义不同，故用 `output.rejected_candidates` 与被接受候选对照记录 |
| 5 | **失败码不同** | `EXEC_4003`（候选全败，REPAIR 专用） | DRAFT 用 `ENV_3002`（镜像构建失败） | 「候选全败」≠「环境构建失败」，两者排查动作完全不同 |
| 6 | **双重验证** | 补丁应用后必须重跑 build + verify，结果写入 `output.recheck` | DRAFT 只有一次 `final_verify` | 修复的判据是「改完之后还成立」，不能沿用修复前的旧结论 |
| 7 | **`style_hint` 是独有维度** | 声明风格（Target / Macro / Hybrid / Implicit） | DRAFT 用 `base_image` 等环境选项 | 修复风格直接对应 E3 成员D 的四种风格与 Target 参考 Patch |
| 8 | **幂等性要求更高** | 补丁须能 `git apply --check` 到指定 commit（`patch_meta.base_commit` / `applies_cleanly`） | —— | 修复产物要能被 A 组或人工在固定版本上原样复现 |

### 6.5 验证方式

**1. 契约校验（三处 `SKIP` → `OK`）**

```bash
python3 e2/validate.py
```

运行结果（2026-09-24，**Ubuntu 22.04.5 LTS（WSL2, x86_64）** / Python 3.10.12 / jsonschema 3.2.0；**裁决前**，当时 `task.schema.json` 为 `required=7` 项 —— 裁决后的复跑见本节第 2 部分）：

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

**2. 裁决后复跑记录（合并 `origin/main` 后，`required=8`）**

组长于 2026-09-25 裁决 12 条议题并收紧 `task.schema.json`（提交 `70776a7`）。本组把 `origin/main` **合并**进 `memberB/e2-repair-contract`，在**未改动任何契约文件**的前提下复跑：

```text
$ python3 e2/validate.py
E2 契约校验（B10）
Schema: e2\task.schema.json
task.schema.json 已加载（required=8 项，properties=11 项）

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

（02–04 三节与第 1 部分逐项一致，此处略）

====================================================================
结论
====================================================================
最小检查 01–04 全部通过。
EXIT=0
```

**关键点**：`required` 由 7 项变为 8 项（补 `created_at`），而本组三件套**一行未改**即通过 —— 因为 `created_at`、`execution.attempt`、`media_type`、`sha256` 这些新收紧的必填项，本组样例**原就一律携带**。这正是裁决「无需返工」的依据，也说明 6.2 的 14 处改动并非凑数。

指纹（与 6.6 纠正后**完全一致** —— 证明本轮只动文档与测试脚本，契约零改动）：

| 文件 | sha256（前 16 位） | 字节数 | 顶层键数 |
|------|--------------------|--------|----------|
| `e2/contracts/repair_job.req.json` | `09f5da521354d26d` | 646 | 5 |
| `e2/contracts/repair_job.res.json` | `12d7b5d073e0b3fb` | 4032 | 10 |
| `e2/contracts/repair_job_err.res.json` | `c96535321092a94a` | 1307 | 10 |

> 环境说明：本次复跑在 **Windows 11 + Git Bash**（Python 3.13.12 / jsonschema 4.26.0）下取得，故 `Schema:` 一行显示 Windows 路径分隔符。**如需 Linux 侧原文**（课程要求），在 WSL 中执行下列命令后替换本段：
>
> ```bash
> cd "/mnt/c/Users/24188/Desktop/Git文件夹/Devops_B10"
> git log --oneline -1
> python3 e2/validate.py; echo "EXIT=$?"
> ```

**3. 反空壳变异测试（44 项变异 + 3 项正向对照 + 2 项已知缺口）**

沿用组长对 DRAFT 的做法，对 REPAIR 三件套逐项破坏，**每一项都必须被拒绝**，证明校验通过不是约束太松。裁决收紧 schema 后，脚本扩成**三张表**：

| 表 | 项数 | 内容 |
|----|------|------|
| 必须被拒绝 | 44 | 响应侧 26（含裁决新增的 `created_at` / `execution.attempt` / `trace_id` pattern / `media_type` / `sha256` 必填共 7 项）、失败侧 9、请求侧 9 |
| 必须被接受 | 3 | 产物 `type` 改 `VERIFY_LOG`、改 `ERROR_REPORT`、原样例不变 —— 证明裁决第 1 条的枚举扩容**真的生效**，而非「一律拒绝」的空壳 |
| 已知缺口 | 2 | `check_request` 未校验 `trace_id` 的 pattern、未校验 `execution.attempt` —— 见 6.7 第 1 条 |

完整输出：

```text
反空壳变异测试 —— 第一部分：每一项都必须被拒绝
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
  OK  已拒绝  [res] 产物 sha256 截短
  OK  已拒绝  [res] 产物 sha256 含大写
  OK  已拒绝  [res] 产物 uri 去掉 pair10
  OK  已拒绝  [res] 产物 uri 非 artifact 协议
  OK  已拒绝  [res] 产物缺 producer_job_id
  OK  已拒绝  [res] 产物 producer_job_id 非法
  OK  已拒绝  [res] 产物缺 artifact_id
  OK  已拒绝  [res] artifacts 不是数组
  OK  已拒绝  [res] 删 created_at
  OK  已拒绝  [res] 删 execution.attempt
  OK  已拒绝  [res] trace_id 改 trace020（缺连字符）
  OK  已拒绝  [res] trace_id 改 TRACE-020（大写）
  OK  已拒绝  [res] trace_id 改 trace-020_x（含下划线）
  OK  已拒绝  [res] 产物删 media_type
  OK  已拒绝  [res] 产物删 sha256
  OK  已拒绝  [res] 产物 type 改 WAT
  OK  已拒绝  [err] FAILED 删 error
  OK  已拒绝  [err] status 改 SUCCEEDED（无 output）
  OK  已拒绝  [err] error.code 改 exec4003
  OK  已拒绝  [err] error.code 改 EXEC_403
  OK  已拒绝  [err] error 缺 message
  OK  已拒绝  [err] 删 execution
  OK  已拒绝  [err] 删 created_at
  OK  已拒绝  [err] 删 execution.attempt
  OK  已拒绝  [err] trace_id 改 trace021（缺连字符）
  OK  已拒绝  [req] 请求携带 status
  OK  已拒绝  [req] 请求携带 job_id
  OK  已拒绝  [req] 请求携带 output
  OK  已拒绝  [req] 请求携带 error
  OK  已拒绝  [req] 请求删 trace_id
  OK  已拒绝  [req] 请求删 schema_version
  OK  已拒绝  [req] 请求 job_type 改 ABC
  OK  已拒绝  [req] 请求 execution.mode 改 BOGUS
  OK  已拒绝  [req] 请求 input 改字符串

第二部分：正向对照，每一项都必须被接受
========================================================================
  OK  已接受  [res] 产物 type 改 VERIFY_LOG（枚举已并入，应合法）
  OK  已接受  [res] 产物 type 改 ERROR_REPORT（枚举已并入，应合法）
  OK  已接受  [res] 未改动的原样例（应合法）

第三部分：已知缺口，预期「不被拒绝」——记录在案，不计入失败
========================================================================
  已确认缺口  [req] 请求 trace_id 改 trace020（缺连字符）
              原因：check_request 未校验 trace_id 的 pattern
  已确认缺口  [req] 请求 execution 只留 mode（缺 attempt）
              原因：check_request 未校验 execution.attempt（设计上 attempt 由执行方产生，故视为可接受）
========================================================================
合计 44 项变异：被拒绝 44，漏网 0
合计 3 项正向对照：被接受 3，误拒 0
合计 2 项已知缺口：确认 2（不影响本次交付，待组长定夺）
```

> 说明：变异分别走**两条不同校验路径** —— 响应/失败侧走 `task.schema.json` 完整校验，请求侧走 `validate.py` 的 `check_request` 请求侧规则（请求不携带服务端字段）。因此 44 项同时证明了 **schema 不是空壳** 与 **请求侧规则不是空壳**。
>
> **相对上一版（34 项）的变化**：`[res] 产物 type 改 VERIFY_LOG` 一项**由「必须被拒绝」改为「必须被接受」** —— 裁决第 1 条把 `VERIFY_LOG` 并入枚举后，该取值已合法。脚本若仍把它当反例，就会误报成漏网；这一处调整本身就是**裁决生效的直接证据**。
>
> 变异脚本位于工作目录 `.workbuddy/plans/_mutate_repair.py`。按本组约定 `.workbuddy/` **不进版本库**（存放协调文档、探针脚本与基线证据），故上表以**完整运行输出**代替脚本入库；**若组长需要把脚本纳入仓库以便独立复核，告知即可移入 `e2/tools/`**（属仓库骨架范围，成员B 不擅自新增目录）。

**4. 必要字段删除自测（`validate.py` 直报）**

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

该自测确认三件事：① 三件套**确实被脚本读取并逐份校验**，不是被 `SKIP` 跳过；② 公共字段缺失会**指名报出**，并被计入「未通过」清单；③ 报错定位到具体文件与字段，**无须改动校验脚本**。自测后文件已按 `sha256` 逐字节还原（恢复后哈希 `12d7b5d073e0b3fb` 与删除前一致），复跑 `EXIT=0`。

> 环境说明：本次自测在 Windows 11 + Git Bash（Python 3.13.12 / jsonschema 4.26.0）下取得；第 1、3 节的 Linux 实测已证明两者结论逐项一致。如需 Linux 侧原文，可在 WSL 中执行：
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

**5. 与 A 组的产物衔接**

`input.md_report_uri` 指向 FULL_CHECK 上交的 MD 检测报告（`md_report.json`），`input.makefile_uri` 指向同一 FULL_CHECK 上交的 Makefile；`output.applied_findings` 只回填 `type = "MISSING"` 的条目，与 A 组 `md_report.sample.json` 的 `findings` 逐条对应。

### 6.6 基线核对说明（`7720a30` vs `fec3fbe`）

任务书给出的只读参考基线是 **`7720a30`**，但 A 组 main 在核对时已前移到 **`fec3fbe`**。两者之间 A 组**自己改过**本轮涉及的多数文件，因此「A 组原样」若不标注 commit 就会失准。本节据此**并列两个基线**。

| 文件 | `7720a30` → `fec3fbe` | 说明 |
|------|----------------------|------|
| `e2/contracts/repair_job.req.json` | **已变化** | 新增 `schema_version`；`md_report_uri` / `makefile_uri` 路径由 `…/full01/…` 改为 `…/job-full01/…` |
| `e2/contracts/repair_job.res.json` | **已变化** | 新增 `created_at` / `updated_at` / `execution`（`cpu` 为 integer）；`input` 由占位符改为请求副本；`output` 新增 `artifacts[]`（含 `VERIFY_LOG`），原 `patch_meta` 等键保留 |
| `e2/contracts/repair_job_err.res.json` | **已变化** | 新增 `created_at` / `updated_at`；`input` 改为请求副本。**仍未加 `execution`，`error.code` 仍为 `EXEC_4002`** |
| `e2/contracts/full_check.req.json` | **已变化** | `commit` 为 `<C0_FULL_40_SHA>`，用于确认 REPAIR 打补丁的目标版本 |
| `e2/contracts/task.schema.json` | **已变化** | `required` 4 → 7 项；新增 `trace_id` / `execution`；加 `allOf` 条件约束；产物枚举扩至 10 项 |
| `e2/contracts/error_codes.md` | **完全相同** | 故 `EXEC_4003` 的判断在**两个基线上同样成立** |
| `e2/contracts/artifact_format.md` | **已变化** | 补 `job-` 前缀修订说明、`sha256` 转必需、`output.artifacts[]` 统一入口 |
| `e2/docs/practice_log.md`、`e2/docs/ADR-002.md` | **完全相同** | 6.1 第 6、7 条所引依据在两个基线上均有效 |

**结论**：本节的**字段取舍以两个基线共同成立的事实为准**（如 `makefile_uri`、`options.max_candidates`、`EXEC_4003`、五组 `output` 修复语义键），**对 A 组后续新增的内容标注为「`fec3fbe` 起」**（如 `execution`、`artifacts[]`、响应 `input` 副本），不把新值当成基线值。核对方法与命令：

```bash
curl -s https://raw.githubusercontent.com/ana12-21/Devops_G10/7720a30/e2/contracts/repair_job.req.json
curl -s https://raw.githubusercontent.com/ana12-21/Devops_G10/fec3fbe/e2/contracts/repair_job.req.json
```

### 6.7 裁决落地与新发现（2026-09-25）

#### 6.7.1 裁决落地：三件套零改动

组长裁决 12 条议题并收紧 `task.schema.json`（`70776a7`）后，本组把 `origin/main` 合并进 `memberB/e2-repair-contract`，**未改动任何契约文件**即通过全部校验：

| 收紧项 | 旧 → 新 | 本组需改否 | 原因 |
|--------|---------|-----------|------|
| 顶层 `required` | 7 → 8 项（补 `created_at`） | 否 | 两份响应样例原就携带 `created_at` |
| `execution.required` | `[mode]` → `[mode, attempt]` | 否 | 两份响应样例原就携带 `attempt` |
| `trace_id` | `minLength: 1` → `pattern: ^trace-[a-z0-9-]+$` | 否 | 三件套取值为 `trace-020` / `trace-021`，本就符合 pattern |
| `artifact.required` | 4 → 6 项（补 `media_type`、`sha256`） | 否 | 5 项产物原就都带 `media_type` 与 `sha256` |
| 产物 `type` 枚举 | 8 → 10 项（补 `ERROR_REPORT`、`VERIFY_LOG`） | 否，但见 6.7.2 第 2 条 | 本组用 `GIT_PATCH` / `BUILD_LOG`，均在枚举内 |

**结论**：收紧后的 schema 对本组产出的唯一影响，是让 6.2 第 6 条**失去了「合规所迫」这一理由**（枚举已含 `VERIFY_LOG`）。该条已按真实理由重写。

#### 6.7.2 本轮新发现（3 条，均待组长定夺）

| # | 发现 | 证据 | 建议 |
|---|------|------|------|
| 1 | **`check_request` 不校验 `trace_id` 的 pattern** | 变异测试第 3 部分：请求的 `trace_id` 改为 `trace020`（缺连字符），`check_request` **不拒绝**；同一取值放在响应侧则被 schema 拒绝 | 给 `check_request` 补 pattern 校验。schema 描述 `trace_id`「由发起方产生」，**请求侧才是能在源头拦下错误格式的唯一位置**；否则新加的 pattern 只作用于「已由服务端回填」的响应，拦截价值大打折扣 |
| 2 | **同一份 `verify.log` 在两组标为不同类型** | A 组用 `VERIFY_LOG`；B 组两处都用 `BUILD_LOG`（`dockerfile_job.res.json` 的 `verifylog-001`、`repair_job.res.json` 的 `verify-log-002`），且组长已裁定 `dockerfile_job.*`「无需改动」 | 裁决第 1 条已把枚举统一为两组并集，但**取值口径仍不一致**。若要对齐 A 组，须 **DRAFT 与 REPAIR 一并改**（只改 REPAIR 会让 B 组内部前后不一致）；若不改，建议在 `artifact_format.md` 写明「`verify.log` 允许 `BUILD_LOG` 或 `VERIFY_LOG`」 |
| 3 | **`check_request` 不校验 `execution.attempt`** | 变异测试第 3 部分：请求的 `execution` 缩减为 `{"mode": "ASYNC"}`，`check_request` **不拒绝** | 本组**倾向保持现状，且契约已如此处理**：`attempt` 是执行轮次计数，由执行方产生，请求阶段无从填写（本组请求的 `execution` 只声明 `mode` / `timeout_seconds` / `resources`）。请确认该口径，或在 `check_request` 中明确要求请求侧也带 `attempt` |

#### 6.7.3 未受影响

- `e2/task.schema.json`、`e2/validate.py`：**成员B 全程一行未动**（均为组长文件，改动一律走 Issue）。
- 三件套 sha256 与 6.6 基线纠正后**完全一致**，见 6.5 第 2 部分的指纹表。
- 转 A 组的 6 条（第 2、3、8、9 的 `trace_id` 部分、10、12 条）已由组长写入 A 组 Issue 的第二轮回复，见 `issue_draft.md`，**本组不重复提**。

### 6.8 二次同步最新 `main` 与合并冲突处理（2026-09-25）

#### 6.8.1 为什么要再同步一次

本组 PR #3 已由组长合入（`8797f08`，合入范围是本分支 `aa0ff0c` 及之前的 8 个提交），但**裁决落地后新增的 3 个提交仍滞留在本地分支**：

| commit | 内容 |
|--------|------|
| `48586d7` | 合并 `origin/main` @ `70776a7`（裁决版本） |
| `c434742` | 落地 12 条裁决、修正因枚举扩容而失效的论据 |
| `d9c49a0` | 回填裁决落地的 Commit SHA 与验证结果 |

此后 `main` 又前进了 14 个提交（成员C 的 PR #5、成员D 的 PR #7 相继合入，现为 `aad384e`）。故本组把 `origin/main` @ `aad384e` 再次合入本分支，把这 3 个提交与最新主线接上，再走一次 PR。

#### 6.8.2 冲突现场与处理

合并 `aad384e` 产生 **2 处冲突，各 1 个冲突块**，性质都是「多人并行追加/改写同一张表」，**不涉及契约文件、校验脚本或任何代码**：

| 文件 | 冲突性质 | 处理方式 | 理由 |
|------|----------|----------|------|
| `CONTRIBUTORS.md` | 双方改写了同一批行：成员B 行两边各有更新，成员C/D 行本分支仍是占位符 `<待填姓名>` | 成员B 行取**本分支新版**（含 `c434742`、44 项变异口径、PR #3 链接）；成员C/D 行取 **`main` 版**（孙正奇 `b2c38a8` Issue#4/PR#5；宋丞轩 `d3c86ca`+`aec91a4` Issue#6/PR#7） | 各行取信息更完整的一侧，双方内容都无损失 |
| `e2/AI_USAGE.md` | **编号撞车**：成员C 的记录已编为 `AI-006`，而本分支的成员B 记录也编为 `AI-006`（双方各自追加时互不可见） | 成员C/D 两行**原样保留**；本分支成员B 那行**顺延改编为 `AI-008`** | 不改动他人已合入的记录编号，只让自己的编号在 `main` 已有编号之后顺延 |

**顺带修正**：`main` 侧 `e2/AI_USAGE.md` 在 `AI-006`（成员C）与 `AI-007`（成员D）之间夹了一个空行，会把成员D 那一行切成**表格之外的普通段落**（Markdown 中空行即终止表格）。已删除该空行，使 AI-001…AI-009 连成同一张表。

#### 6.8.3 冲突处理遵循的边界

- **未硬解、未单方裁定**：冲突性质、双方原文与解法先在 PR / Issue 中说明清楚，再提交；未改动任何人的既有记录编号与内容。
- **未触碰组长文件**：本次合并 `e2/task.schema.json`、`e2/validate.py` 一行未改。
- **待组长确认 1 项**：AI 使用记录的编号分配口径（按人分配 vs 按日期排序）本组此前无明文约定。本次按「在 `main` 已有最大编号之后顺延」处理，故成员B 的两条记录落在编号尾部（`AI-008`、`AI-009`），而非紧邻其任务日期。若组长希望改按日期重排，请裁定后统一调整。

#### 6.8.4 二次同步后的复核结果

在合并后的最新代码上复跑 `python3 e2/validate.py`：

- `required=8` 项（收紧后值）被正确加载；
- 最小检查 01–04 全部通过，`EXIT=0`；
- `repair_job.*` 三处由 `SKIP` 变 `OK`，与 6.7.1 的结论一致；
- 三件套契约文件**本次一行未改**（冲突仅涉及两份文档）。
