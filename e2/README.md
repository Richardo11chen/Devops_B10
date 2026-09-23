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

`repair_job.*` 由成员B 产出后，`validate.py` 会自动纳入检查（现以 `SKIP` 跳过），无需改动脚本。
