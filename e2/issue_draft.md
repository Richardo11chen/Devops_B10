# Issue 草稿（e2/issue_draft.md）

本文件是 **Issue 草稿**，不是 Issue 本身。复制对应段落粘贴到 GitHub Issue 即可创建。

**建议分支名规则**：`<角色>/<范围>`，角色用 `lead` / `memberB` / `memberC` / `memberD`。

---

## Issue 1

**标题**：`[B10][组长] 初始化仓库与 DRAFT 契约确认`

**建议分支名**：`lead/e2-draft-contract`

### 目标

1. 建立 B10 独立仓库骨架，写清配对关系、分工、环境要求。
2. 从 A 组仓库复制 DRAFT 相关契约到本仓库，逐条确认字段，补齐 `execution` 等公共字段。
3. 产出统一任务模型与最小检查脚本。

### 产出文件

| 文件 | 说明 |
|------|------|
| `README.md` | 配对关系、A 组链接、B 组分工表、运行环境要求 |
| `CONTRIBUTORS.md` | 四人贡献表 |
| `e2/contracts/dockerfile_job.*` | DRAFT 请求 / 响应 / 错误三件套 |
| `e2/task.schema.json` | 统一任务模型（9 公共字段含 `execution`） |
| `e2/validate.py` | 最小检查 01–04 |
| `e2/README.md` | DRAFT 字段确认结论（确认 / 修改 / 待议三节） |
| `e2/ADR.md` | ADR-001 异步 Job 模式四段正文 |
| `e2/Backlog.md`、`e2/AI_USAGE.md` | 任务表与 AI 使用记录 |

### 验收条件

- [ ] 目录结构与课程要求一致，README 四项内容齐全
- [ ] `dockerfile_job.*` 含全部 9 个公共字段，`execution` 与 `input`/`output`/`error` 并列
- [ ] `e2/README.md` 三节无 `待填`
- [ ] ADR-001 四段（Context / Alternatives / Decision / Consequences）齐全
- [ ] `python3 e2/validate.py` 最小检查 01–04 全部通过
- [ ] 明确写出系统执行错误入 `job.error`、正常分析发现入 `ERROR_REPORT.findings` 的边界

### 备注

**不部署 API**。不修改 A 组仓库。全部命令在 Linux 下运行。

---

## Issue 2

**标题**：`[B10][成员B] E2 REPAIR 契约确认`

**建议分支名**：`memberB/e2-repair-contract`

### 目标

确认 REPAIR 任务（MDFixer）的接口契约，与组长产出的 `task.schema.json` 保持一致，并写清与其余三类任务的差异点。

### 产出文件

| 文件 | 说明 |
|------|------|
| `e2/contracts/repair_job.req.json` | REPAIR 请求样例 |
| `e2/contracts/repair_job.res.json` | REPAIR 成功响应样例 |
| `e2/contracts/repair_job_err.res.json` | REPAIR 失败响应样例 |
| `e2/README.md` | 追加 REPAIR 一节（不改动 DRAFT 已定稿部分） |

### 验收条件

- [ ] 三件套字段与 `e2/task.schema.json` 一致，含全部 9 个公共字段
- [ ] `job_type` 为 `REPAIR`；状态取自六态枚举
- [ ] 失败样例区分开：系统执行错误写 `job.error`，分析发现写 `ERROR_REPORT.findings`
- [ ] REPAIR 特有的迭代/重试语义在 `execution` 中表达清楚（`attempt` 等）
- [ ] 与其余三类任务的差异点逐条写明理由
- [ ] 自行运行的校验命令与输出写入 `e2/README.md`

### 备注

需要与组长约定 `execution` 的使用方式，冲突时先开 Issue 讨论，不要直接改 `task.schema.json`。

---

## Issue 3

**标题**：`[B10][成员C] E3 DRAFT 样本与 Docker 证据`

**建议分支名**：`memberC/e3-draft-fixtures`

### 目标

准备 DRAFT 服务的测试基线：能让工具接受的成功样本与失败样本，写出预期结果和判断依据，保留实际运行或失败记录。

### 产出文件

| 文件 | 说明 |
|------|------|
| `e3/fixtures/draft/Dockerfile.broken` | 失败候选 |
| `e3/fixtures/draft/Dockerfile.reference` | 参考成功 |
| `e3/fixtures/draft/` | 被测源码 + 运行说明 |
| `e3/evidence/` | 构建日志、退出码、镜像 ID、diff |

### 验收条件

**两层成功判据缺一不可：**

- [ ] 第一层编译通过：构建命令退出码 0，预期可执行文件生成，**保存构建日志**
- [ ] 第二层功能验证：运行 README 约定测试，检查退出码与预期输出，**测试失败也要记录**

**两个候选达标：**

- [ ] `Dockerfile.broken` 基于 `python:3.13-slim`，直接 `RUN make`，预期非零退出，日志出现 `make: not found`
- [ ] `Dockerfile.reference` 安装 `gcc make libc6-dev`，预期构建成功，容器内输出 `hello E3`

**证据齐备：**

- [ ] 保存 Dockerfile diff、build 退出码、日志、镜像 ID
- [ ] 基线四要素齐全：固定版本与环境、本次修改/故障是什么、预期输出及依据、可重跑命令
- [ ] 别人能按 `e3/fixtures/draft/README.md` 原样跑通
- [ ] 人工标注 `ORACLE` 来源，与实际运行日志分清

### 备注

全部命令在 **Linux + docker** 下运行。证据目录**每次运行新建，保留旧证据**。

---

## Issue 4

**标题**：`[B10][成员D] E3 MDFixer 样本与修复验证`

**建议分支名**：`memberD/e3-mdfixer-fixtures`

### 目标

准备 MDFixer 服务的固定输入：固定 MD 报告、同版本源码与 Makefile、构建与行为测试、预期声明风格，并验证参考 Patch 真正修好 MD。

### 产出文件

| 文件 | 说明 |
|------|------|
| `e3/fixtures/mdfixer/` | 固定输入四件套 |
| `e3/fixtures/mdfixer/reference.patch` | 参考 Patch（至少 Target 风格） |
| `work/`（仓库根） | 真实 Git 提交与参考修复 |
| `e3/evidence/` | 实际命令与观察结果 |

### 验收条件

**固定输入四件套齐备：**

- [ ] 固定 MD 报告（`main.o` 缺 `config.h`）
- [ ] 同一源码版本的 `Makefile`
- [ ] 构建命令与行为测试
- [ ] 预期声明风格

**四种声明风格：**

- [ ] Target、Macro、Hybrid、Implicit 四种风格齐备
- [ ] 参考 Patch 至少给出 **Target** 风格
- [ ] 说明其他三种风格与 Target 的差异

**隐式规则与 `.d` 文件：**

- [ ] `%: %.c` 使用 `$(CC) -MMD -MP -c $< -o $@`，`-include main.d`
- [ ] 检查 `.d` 文件内容
- [ ] 验证再次修改头文件时的行为

**修复验证逐条留证：**

- [ ] 修复前：只改头文件，仍输出旧值
- [ ] `git apply --check reference.patch` 通过
- [ ] `git apply reference.patch` 后 `make clean && make` 输出新值
- [ ] 再改头文件、**不 clean** 应自动重建
- [ ] **明确说明：不能只靠 `make clean` 成功就证明 MD 已修好**

**无效候选：**

- [ ] 原始副本可构建测试
- [ ] 候选修改加入失败命令后 `make` 非零退出
- [ ] 恢复原 `Makefile` 后构建和测试再次通过

### 备注

全部命令在 **Linux** 下运行。人工构造的预期结果标 `ORACLE`，与实际日志分清。

---

# 向 A 组提 Issue 的正文

> **目标仓库**：<https://github.com/ana12-21/Devops_G10>
> **注意**：本仓库 B10 **不直接修改 A 组仓库**，只通过 Issue 沟通。以下正文只涉及组长负责的 **DRAFT** 部分。

---

**标题**：`[B10] DRAFT 接口确认`

**正文**：

```markdown
## 背景

B10 组已克隆贵组仓库到本地只读参考（基线 commit `7720a30`），逐条确认与 DRAFT 任务相关的接口字段。
B10 负责 DRAFT + MDFixer，贵组负责 BuildChecker + EChecker。以下只涉及 DRAFT 部分，不涉及检测类任务。

## 已确认的 DRAFT 字段

（此节由 B10 组长在逐条复核 A 组原文件后回填）

## 需要贵组澄清的问题

### 1. DRAFT 请求契约缺公共字段

`e2/contracts/dockerfile_job.req.json` 目前只有 `job_type` 和 `input`：

```json
{
  "job_type": "DRAFT",
  "input": { ... }
}
```

按课程要求，请求侧应包含公共字段 `schema_version`、`trace_id`（`job_id`、`status` 由服务端生成，可不在请求中）。
另外 `e2/contracts/task.schema.json` 的 `required` 只列了 4 项，未包含 `execution`。

**请确认**：请求契约是否补齐 `schema_version`、`trace_id`？若有意省略，请说明理由。

### 2. 全库缺 `execution` 公共字段

课程要求公共字段为 9 个，`execution` 与 `input`/`output`/`error` 并列，记录执行元信息：
`execution.mode`、`execution.timeout_seconds`、`execution.started_at`、`execution.finished_at`、`execution.attempt`、`execution.command`、`execution.resources`。

当前 `task.schema.json` 与四类响应样例中均无此字段。

**请确认**：是否由双方共同在 `task.schema.json` 中新增 `execution`？是否属于「共享 Schema 同步更新」的可兼容变化？

### 3. 响应样例中的 `input` 是占位符

`e2/contracts/dockerfile_job.res.json` 中：

```json
"input": { "_echo": "请求副本或省略" }
```

这是一个**二选一的说明文字**，不是具体值。校验脚本无法据此判断。

**请确认**：响应中的 `input` 到底填**请求副本**还是**省略**？请二选一定稿并给一个具体样例。

### 4. `ENV_3002` 的语义范围

`dockerfile_job_err.res.json` 用 `ENV_3002` 表示「Docker image build failed」。

**请确认**：`ENV_3002` 是 DRAFT 专用，还是与检测类任务共用同一语义？若共用，请给出统一的触发条件定义。

### 5. DRAFT 端点与产物命名空间

课程约定 5 个端点：

```text
POST /v1/dockerfile-jobs
POST /v1/full-check-jobs
POST /v1/incremental-check-jobs
POST /v1/repair-jobs
GET  /v1/jobs/{job_id}
```

A 组现有 OpenAPI 只覆盖 `full-check` / `incremental-check` 两类。
另外产物 URI 使用 `artifact://pair10/...` 命名空间。

**请确认**：`artifact://pair10/` 是双组共用的命名空间，还是各组用各自的（如 `artifact://b10/`）？DRAFT 产物应挂在哪个前缀下？

## B10 侧的对齐动作

- B10 会在 `e2/contracts/dockerfile_job.*` 中补齐上述公共字段，并在 `e2/README.md` 记录**确认 / 修改 / 待议**三节。
- B10 的 `task.schema.json` 会包含全部 9 个公共字段，四类任务对象均可表达。
- 若贵组对上述任一项有不同意见，请在本 Issue 回复，B10 会同步调整本仓库契约。

## 期望回复

请逐条给出「同意 / 不同意 + 理由」。若涉及 schema 变更，请注明是否属于破坏兼容变化。

---

*本 Issue 由 B10 组长提出，只涉及 DRAFT 部分。B10 不会直接修改本仓库文件。*
```

---

## 使用说明

1. 4 份组内 Issue 依次复制到本仓库 Issues，指派给对应成员。
2. A 组联动正文复制到 A 组仓库 Issues，**标题严格用 `[B10] DRAFT 接口确认`**。
3. 「已确认的 DRAFT 字段」一节在 `e2/README.md` 第 2 节定稿后回填，两处内容必须一致。
4. 创建 Issue 后，把编号回填到 `CONTRIBUTORS.md` 的 Issue/PR 列。
