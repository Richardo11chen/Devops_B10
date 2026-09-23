# E2 — 需求与接口契约（B10）

B 组负责 **DRAFT** 与 **MDFixer** 两个服务的接口约定。E2 **不部署 API**，以仓库中的契约文件作为交付物：约定微服务之间传什么数据、怎么传、失败怎么表示。

> **状态**：本文件由组长起草，其中 **2.1 / 2.2 / 2.3 三节待「复制并确认 DRAFT 契约」完成后回填**。

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

（待填 — 逐条列出确认无误的字段及确认依据）

### 2.2 B 组修改了什么

（待填 — 每处修改写：原样 → 改成什么 → 理由）

### 2.3 还需与 A 组讨论什么

（待填 — 未达成一致或需要 A 组确认的开放问题；同步写入 `issue_draft.md` 的 A 组联动正文）

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

| 编号 | 检查内容 |
|------|----------|
| 01 | 四类请求与响应有效样例全部通过 |
| 02 | `job_type` 改成 `ABC` 应被拒绝 |
| 03 | 删除增量任务的 `baseline` 应被拒绝 |
| 04 | 解释 MD 为什么不等于工具执行失败 |
