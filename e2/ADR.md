# ADR — 架构决策记录（B10 / E2）

每条决策按 **Context / Alternatives / Decision / Consequences** 四段写。编号后不再改写，被推翻时新增一条并注明 `Supersedes`。

| 编号 | 标题 | 负责人 | 状态 |
|------|------|--------|------|
| ADR-001 | 采用异步 Job 模式表达四类任务 | 组长 | 已定稿 |
| ADR-002 | 以候选轮次表达 REPAIR 的迭代语义 | 成员B | 已定稿 |

---

## ADR-001：采用异步 Job 模式表达四类任务

**状态**：已定稿（2026-09-23）

**Supersedes**：无

### Context

B 组负责 DRAFT（环境生成）与 MDFixer（修复），A 组负责 BuildChecker 与 EChecker，四类任务共用一套外壳。四类任务的耗时特征差异极大：

| 任务 | 耗时来源 |
|------|----------|
| DRAFT | 迭代构建镜像：拉基础镜像 → 试构建 → 读失败日志 → 改 Dockerfile → 再试 |
| FULL_CHECK | 全量依赖图构建（编译 + 静态分析） |
| INCREMENTAL_CHECK | 从 C0 到 C1/C2 的增量比对 |
| REPAIR | 多候选 patch 逐个尝试 |

DRAFT 请求里的 `max_iterations: 5` 与 `timeout_seconds: 1800` 直接说明：**单次任务可能跑几十分钟**。

同步请求-响应会带来三个具体问题：

1. **必然被切断** —— 常见网关/负载均衡超时在 30–60 秒量级，1800 秒的任务跑不完，且被切断后客户端无从得知任务是否还在执行。
2. **状态丢失** —— 连接一断就没有句柄，无法续查结果，也无法把产物关联回这次调用。
3. **失败说不清** —— 单一 HTTP 状态码区分不了「镜像构建失败」（`ENV_3002`）、「任务超时」（`EXEC_4002`）、「分析器崩溃」（`ANALYSIS_5001`），而这三者的排查动作完全不同。

课程不要求部署 API，但要求写清「传什么数据、怎么传、失败怎么表示」。以上三点正是异步 Job 模式要解决的。

### Alternatives

| 方案 | 说明 | 为什么不选 |
|------|------|-----------|
| A. 同步请求-响应 | POST 阻塞到任务结束，一次返回最终结果 | 承载不了 1800 秒级任务；网关超时后状态丢失；失败只能靠 HTTP 状态码区分，表达不了 `TIMED_OUT` 与 `FAILED` 的差别；DRAFT 的每轮迭代、REPAIR 的每个候选 patch 无处安放 |
| **B. 异步 Job + 轮询查询** | POST 立即返回 `202` + `job_id`，客户端轮询 `GET /v1/jobs/{job_id}` | **选中** |
| C. 异步 Job + 回调 / webhook | POST 返回 `job_id`，完成后服务端回调客户端 | 需要双方都部署可达的 HTTP 端点。E2 明确不部署 API，回调地址无处可配；两组之间没有常驻服务，联调成本高 |
| D. 消息队列 + 事件流 | 任务投递队列，结果经事件流推送 | 契约要回答的是「数据长什么样」，不是「用什么中间件传」。引入 MQ 会把契约绑死在具体基础设施上，而 A/B 两组可能选不同实现 |

### Decision

**采用方案 B：异步 Job + 轮询查询。** 配套约定如下。

**1. 四个创建端点 + 一个查询端点**，创建返回 **HTTP 202** + `job_id` + `status=QUEUED`：

```text
POST /v1/dockerfile-jobs            POST /v1/repair-jobs
POST /v1/full-check-jobs            GET  /v1/jobs/{job_id}
POST /v1/incremental-check-jobs
```

用 `202 Accepted` 而非 `200 OK`，语义上明确「已受理、未完成」。

**2. 统一状态机**：`QUEUED` → `RUNNING` → `SUCCEEDED` / `FAILED` / `TIMED_OUT` / `CANCELLED`。四个终态不可回退，任务不可重跑，重跑即新建 `job_id`。

**3. 9 个公共字段**：`schema_version`、`job_id`、`trace_id`、`job_type`、`status`、`execution`、`input`、`output`、`error`。

其中 `execution` 与 `input`/`output`/`error` **并列**，专门承载执行元信息（`mode` / `timeout_seconds` / `started_at` / `finished_at` / `attempt` / `command` / `resources`）。并列而非嵌套的理由：

- `input` 描述**任务要什么**，`execution` 描述**这次是怎么跑的**。超时上限、执行模式、尝试次数属于后者，塞进 `input` 会使「同样的任务输入产生不同结果」无法解释。
- `attempt` 与 `started_at`/`finished_at` 是失败归因的关键：定位「哪个版本的哪次尝试」需要它们，而它们既不是输入也不是产出。
- 与 `input`/`output`/`error` 平级，四类任务可以在不改动业务字段的前提下共享同一套执行语义。

**4. 失败怎么表示**：`job.error` **只**承载系统执行错误（`ENV_3002` / `EXEC_4002` / `ANALYSIS_5001`）；正常分析发现（`MISSING` / `REDUNDANT`）写入 `ERROR_REPORT` 的 `findings`，任务状态**仍为 `SUCCEEDED`**。两者互斥，不得同存。

**5. 产物怎么传**：Job 只保存元数据，大文件通过 `artifact://<pair_id>/<job_id>/<relative_path>` 引用交接，元数据含 `artifact_id`/`type`/`uri`/`media_type`/`producer_job_id`/`sha256`。DRAFT 额外在 `output.artifacts[]` 中以数组形式列出，`sha256` 用于完整性核验。

### Consequences

**正面：**

- 长任务不再被网关超时切断；`job_id` 使任务可续查、可关联产物、可经 `trace_id` 串联成一次平台流程。
- 失败原因从单一状态码细化为错误码，`TIMED_OUT`（`EXEC_4002`）与 `FAILED`（`ENV_3002`）可区分，排查方向不同。
- 中间过程有地方记录：DRAFT 的每轮迭代、REPAIR 的每个候选 patch 都能写进 `output`。
- `execution` 让「这次跑的是哪个版本、哪条命令、第几次尝试」可追溯，满足 E3 基线「失败记录能定位到具体版本」的要求。

**负面 / 代价：**

- 客户端必须实现轮询；轮询间隔与退避策略本契约未定义，属实现层，两组可能不一致。
- 服务端必须维护任务状态存储与状态机，实现复杂度明显高于同步方案。
- 响应中 `input` 是否回填请求副本需要定稿（B 组选「填副本」，见 `README.md` 2.3 第 4 条），否则抽查失败时缺少现场。
- 新增 `execution` 使请求样本比 A 组原样更大，**且与 A 组 `validate.py` 现有规则冲突**（它禁止请求携带 `schema_version`，见 `README.md` 2.3 第 1 条）—— 这是本决策落地前必须与 A 组解决的问题。

**需要额外约定的点：**

- 幂等：重复创建同 `trace_id` 的 job 返回 `CONFLICT_7001`。
- 查询不存在的 `job_id` 返回 `NOT_FOUND_6001`。
- 版本兼容判定：新增可选字段（如 `execution`）属**可兼容变化**；状态枚举改变、删除或改名字段、严格 Schema 拒绝新增字段属**破坏兼容**。

---

## ADR-002：以候选轮次表达 REPAIR 的迭代语义

**状态**：已定稿（2026-09-24）

**Supersedes**：无

### Context

四类任务中，DRAFT 与 REPAIR 都会「反复试」，但试的对象不同：

| 任务 | 每一轮改的是什么 | 轮次之间是否互相影响 |
|------|------------------|----------------------|
| DRAFT | Dockerfile 的修订 | 是，后一轮基于前一轮的失败日志 |
| REPAIR | **候选 patch**（对源码的修改方案） | 否，候选彼此独立，逐个试用 |

REPAIR 的输入来自 FULL_CHECK 的检测报告，输出是一份能真正修好缺失依赖的补丁。多候选逐个尝试意味着契约必须同时回答两个问题：**试到第几轮了**、**被淘汰的候选为什么不行**。

`execution.attempt` 在 A、B 两组实现中都被解释为「第几次尝试」，可直接复用；但 REPAIR 的一轮尝试 = 一个候选 patch，语义与 DRAFT 不同，需要显式定义。

### Alternatives

| 方案 | 说明 | 为什么不选 |
|------|------|-----------|
| A. 只记录 `execution.attempt` | 用整数表示试到第几轮 | 能回答「试了几轮」，但回答不了「为什么前几轮不行」，排障时仍需翻日志 |
| **B. `execution.attempt` + `output.rejected_candidates[]`** | 轮次用 `attempt`，被淘汰候选逐条记录摘要、失败阶段与理由 | **选中** |
| C. 每个候选开一个独立 Job | 一个候选一个 `job_id`，任务链经 `trace_id` 串联 | 单次修复被拆成多个 Job，`max_candidates` 失去意义；产物交接复杂化，且与「四类任务共用一套外壳」的设计冲突 |
| D. 不记录被淘汰的候选 | 只保留最终成功的补丁 | 修复过程不可追溯，评审无法判断是「真试了多轮」还是第一次就恰好命中 |

### Decision

**采用方案 B。** 约定如下。

**1. `execution.attempt` 在 REPAIR 中的语义是「候选轮次」**，从 1 起递增：成功时等于最终被接受候选的序号，失败时等于已尝试的候选总数。

**2. `output.rejected_candidates[]`** 逐条记录被淘汰的候选：

```json
{ "candidate": 1, "summary": "…", "rejected_at": "build|verify", "reason": "…", "log_uri": "artifact://…" }
```

`rejected_at` 取值限定 `build` / `verify`，对应 E3 要求的两层成功判据。

**3. `output.applied_findings[]` 只回填 `type = "MISSING"` 的条目**，与检测报告的 `findings` 逐条对应；`REDUNDANT` 不进修复路径。

**4. `output.recheck`** 记录补丁应用后重跑的 build 与 verify 退出码 —— 修复成立的判据是「改完之后两层仍通过」，不能沿用修复前的结论。

**5. 候选日志一并列入 `output.artifacts[]`**，遵循 A 组议题 4 的口径：所有产物引用统一经 `artifacts[]` 交接。

### Consequences

**正面：**

- 「试了几轮」与「每轮为什么被否」都可机器读取，修复过程可复现、可评审。
- `rejected_at` 直接区分「编译就不过」与「编译过但行为没变」，与 E3 的两层判据对应。
- 复用已有的 `execution.attempt`，不需要新增公共字段，属 ADR-001 定义的**可兼容变化**。

**负面 / 代价：**

- `attempt` 在 DRAFT（Dockerfile 修订轮次）与 REPAIR（候选序号）中语义不同，**必须在文档中显式说明**，否则会被误读。
- 与 A 组的差异：A 组 `execution.required = [mode, attempt]`，本仓库为 `[mode]`。本组样例始终携带 `attempt`，但**是否提为 schema 必填需组长裁决**（见 `e2/README.md` 6.3 第 4 条）。
- `rejected_candidates` / `applied_findings` 是 B 组在 `output` 下的自定义键。`task.schema.json` 的 `output` 未封闭额外键，故当前合法；若日后收紧为 `additionalProperties: false`，需同步登记这两个键。

---

## 待补充的决策位

<details>
<summary>成员B / 成员C / 成员D 如遇到需要记录的决策，在此追加 ADR-002 及以后</summary>

- ~~ADR-002：REPAIR 任务的迭代语义（成员B）~~ —— 已定稿，见上
- ADR-003：DRAFT 样本的构建环境固定策略（成员C）
- ADR-004：MDFixer 声明风格的选择依据（成员D）

需要决策时请复制 ADR-001 的四段结构，**不要只写结论**。
</details>
