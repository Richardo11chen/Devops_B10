# Issue 草稿（e2/issue_draft.md）

本文件是 **Issue 草稿**，不是 Issue 本身。复制对应段落粘贴到 GitHub Issue 即可创建。

**建议分支名规则**：`<角色>/<范围>`，角色用 `lead` / `memberB` / `memberC` / `memberD`。

> Issue 1 的组长工作**未开分支**，直接提交到 `main`。Issues 2 / 3 / 4 是待办任务，
> 其中的分支名是成员需要**新建**的分支。

---

## Issue 1

**标题**：`[B10][组长] 初始化仓库与 DRAFT 契约确认`

**状态**：✅ **已完成**（2026-09-23）。未开分支，直接提交到 `main`。
**已创建为本仓库 Issue #1**，可直接 Close 作为完成记录留档。

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

- [x] 目录结构与课程要求一致，README 四项内容齐全
- [x] `dockerfile_job.*` 含全部 9 个公共字段，`execution` 与 `input`/`output`/`error` 并列
- [x] `e2/README.md` 三节无 `待填`
- [x] ADR-001 四段（Context / Alternatives / Decision / Consequences）齐全
- [x] `python3 e2/validate.py` 最小检查 01–04 全部通过
- [x] 明确写出系统执行错误入 `job.error`、正常分析发现入 `ERROR_REPORT.findings` 的边界

### 完成情况

**分支**：未开分支，直接提交到 `main`。

| commit | 内容 |
|--------|------|
| `7ff92ae` | init: 建立 B10 仓库骨架与 E2/E3 文档框架 |
| `c370828` | e2: 确认 DRAFT 契约并补齐 execution 公共字段 |

**验证结果**：`python3 e2/validate.py` → 最小检查 01–04 全部通过，退出码 0。
另做 13 项变异测试（删 `execution`、`sha256` 位数不足、产物 `type` 越界、`SUCCEEDED` 缺 `output` 等），
全部被 schema 拒绝，确认校验不是因为约束太松而全过。

### 备注

**不部署 API**。不修改 A 组仓库。全部命令在 Linux 下运行。
后续待议项（与 A 组）：见 `e2/README.md` 第 2.3 节，共 7 条。

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
**状态**：✅ **已完成**（2026-09-24）。已正式创建为本仓库 Issue [#4](../../issues/4) 与 PR [#5](../../pull/5)。

### 目标

准备 DRAFT 服务的测试基线：能让工具接受的成功样本与失败样本，写出预期结果和判断依据，保留实际运行或失败记录。

### 产出文件

| 文件 | 说明 |
|------|------|
| `e3/fixtures/draft/Dockerfile.broken` | 失败候选 |
| `e3/fixtures/draft/Dockerfile.reference` | 参考成功 |
| `e3/fixtures/draft/main.c`、`Makefile` | 被测源码与构建规则 |
| `e3/fixtures/draft/README.md` | 测试基线说明与两层判据复现命令 |
| `e3/evidence/` | 构建日志、退出码、镜像 ID、diff、功能验证日志 |

### 验收条件

**两层成功判据缺一不可：**

- [x] 第一层编译通过：构建命令退出码 0，预期可执行文件生成，**保存构建日志**
- [x] 第二层功能验证：运行 README 约定测试，检查退出码与预期输出，**测试失败也要记录**

**两个候选达标：**

- [x] `Dockerfile.broken` 基于 `python:3.13-slim`，直接 `RUN make`，预期非零退出，日志出现 `make: not found`
- [x] `Dockerfile.reference` 安装 `gcc make libc6-dev`，预期构建成功，容器内输出 `hello E3`

**证据齐备：**

- [x] 保存 Dockerfile diff、build 退出码、日志、镜像 ID
- [x] 基线四要素齐全：固定版本与环境、本次修改/故障是什么、预期输出及依据、可重跑命令
- [x] 别人能按 `e3/fixtures/draft/README.md` 原样跑通
- [x] 人工标注 `ORACLE` 来源，与实际运行日志分清

### 完成情况

**分支**：`memberC/e3-draft-fixtures`

| commit | 内容 |
|--------|------|
| `b2c38a8` | e3: 添加 DRAFT 失败与参考成功样本及构建证据 |

**验证结果**：
1. **第一层判据**：
   - Broken 候选：构建退出码 127，日志定位到 `/bin/sh: 1: make: not found`。
   - Reference 候选：构建退出码 0，成功生成镜像 `b10-draft-reference:latest`（ID: `eca1d90eb03f`）。
2. **第二层判据**：
   - 容器内运行 `./hello`，退出码 0，标准输出 `hello E3`。
3. **证据文件**：
   - `e3/evidence/` 下包含 diff、退出码、构建日志、镜像 ID 及功能验证日志。

### 备注

全部命令在 **Linux + docker** 下运行。证据目录**每次运行新建场景文件，保留旧证据**。

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
> **状态**：✅ 已提交为 **[ana12-21/Devops_G10#2](https://github.com/ana12-21/Devops_G10/issues/2)**
> **注意**：本仓库 B10 **不直接修改 A 组仓库**，只通过 Issue 沟通。以下正文只涉及组长负责的 **DRAFT** 部分。

---

**标题**：`[B10] DRAFT 接口确认`

**正文**：

```markdown
## 背景

B10 组已克隆贵组仓库到本地只读参考（基线 commit `7720a30`），逐条确认与 DRAFT 任务相关的接口字段。
B10 负责 DRAFT + MDFixer，贵组负责 BuildChecker + EChecker。以下只涉及 DRAFT 部分，不涉及检测类任务。

## 已确认的 DRAFT 字段（B10 逐条复核后）

以下字段已核对无误，B10 原样采纳：

| # | 字段 / 约定 | 结论 |
|---|-------------|------|
| 1 | `job_type = "DRAFT"` | ✅ 确认 |
| 2 | `input.repository.{url, commit}`（commit 用完整 40 位 SHA） | ✅ 确认 |
| 3 | `input.build.{command, verify_command}` | ✅ 确认 |
| 4 | `input.max_iterations = 5` | ✅ 确认 |
| 5 | `input.options.{base_image, keep_intermediate_images}` | ✅ 确认，且 `base_image` 必须可指定 |
| 6 | 状态枚举六态 | ✅ 确认 |
| 7 | `error.code = ENV_3002` 为 **DRAFT 专用** | ✅ 确认（依 `error_codes.md` 该行标注「可能抛出的服务：DRAFT」） |
| 8 | 错误对象固定字段 `code` / `message` / `detail` | ✅ 确认 |
| 9 | 产物元数据字段与 `artifact://<pair_id>/<job_id>/<relative_path>` 格式 | ✅ 确认 |
| 10 | `pair_id = pair10` 为**双组共用**命名空间 | ✅ 确认（依 `artifact_format.md`「配对组编号」） |
| 11 | **B 组产物类型占位** `DOCKERFILE` / `IMAGE_REF` / `GIT_PATCH` | ✅ **B10 予以确认**；另补复用贵组已有的 `BUILD_LOG` |
| 12 | `MISSING` / `REDUNDANT` 写 `output.findings`，任务可为 `SUCCEEDED` | ✅ 确认 |
| 13 | 反例行为（`ABC`→`SCHEMA_1001`；缺 `baseline`→`BASELINE_2001`） | ✅ 确认 |

## 需要贵组澄清的问题

### 1. ⚠️ 请求侧是否携带 `schema_version` —— 课程要求与贵组现有实现冲突

贵组 `e2/scripts/validate.py` 的 `check_request_envelope` 中写着：

```python
# 请求不应携带服务端字段
for k in ("schema_version", "job_id", "status", "output", "error"):
    if k in doc:
        passed &= fail(f"请求样例不应携带 {k}", str(src))
```

即贵组把 `schema_version` 归入「请求不应携带的服务端字段」。

但课程对 E2 的要求是：

> 公共字段（必须包含 execution）：schema_version、job_id、trace_id、job_type、status、execution、input、output、error

`schema_version` 位列公共字段。B10 因此在 `dockerfile_job.req.json` 中加入了它。

**请确认以哪个为准**：

- **(a)** 请求侧也携带 `schema_version`（B10 现状），贵组相应放宽 `check_request_envelope`；
- **(b)** 请求侧不携带（贵组现状），则请在贵组文档中说明课程该条如何满足。

注：`trace_id` 不在贵组禁用列表内，无冲突。

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

### 4. `output` 结构：`artifacts[]` 数组 vs 裸字段

贵组 `artifact_format.md` 要求：

> 每一份产物必须在 `output` 字段里给一个 URI，同时配套一份元数据

但贵组 `dockerfile_job.res.json` 用的是 `output.dockerfile_uri` / `output.image_ref` 两个**裸字段**，未配套元数据。

B10 已改为 `output.artifacts[]` 数组，每项按元数据格式并带 `sha256`。

**请确认**：两组 `output` 结构是否需要统一？若贵组已按裸字段实现解析器，B10 的改动对贵组构成**破坏兼容变化**，需要重新对齐。

### 5. `task.schema.json` 的 `required` 与 `output` 约束

贵组 `task.schema.json` 当前 `required` 只有 4 项（`schema_version` / `job_id` / `job_type` / `status`），`trace_id`、`execution`、`input` 均未列入；`output` 声明为空 `object`，导致 `findings.type` 与产物 `type` 枚举**实际未被校验**。

B10 已提到 7 项 required 并补上 `output` 的属性声明。**请确认**贵组是否同步。

### 6. `sha256` 是可选还是必需

贵组 `artifact_format.md` 标注 `sha256` 为「可选，完整性校验时使用」。B10 在 DRAFT 契约中提为**必需**（课程要求「sha256 核验完整性」）。**请确认**贵组是否同步。

### 7. DRAFT 产物 `relative_path` 约定

`artifact://pair10/` 已确认为双组共用。**请确认** DRAFT 产物的路径约定，B10 建议 `<job_id>/<filename>`，例如 `artifact://pair10/job-draft01/Dockerfile`。

## B10 侧已做的对齐动作

- B10 已在 `e2/contracts/dockerfile_job.*` 三件套中补齐 `execution`，并在 `e2/README.md` 记录**确认 / 修改 / 待议**三节（2.1 / 2.2 / 2.3）。
- B10 的 `e2/task.schema.json` 含全部 9 个公共字段，四类任务对象均可表达，并已通过 `e2/validate.py` 的最小检查 01–04。
- 若贵组对上述任一项有不同意见，请在本 Issue 回复，B10 会同步调整本仓库契约。

## 期望回复

请逐条给出「同意 / 不同意 + 理由」。若涉及 schema 变更，请注明是否属于破坏兼容变化。

---

*本 Issue 由 B10 组长提出，只涉及 DRAFT 部分。B10 不会直接修改本仓库文件。*
```

---

# A 组 Issue #2 的第二轮回复正文

> **发到**：[ana12-21/Devops_G10#2](https://github.com/ana12-21/Devops_G10/issues/2)（作为 Issue 评论）
> **针对**：A 组 commit `fec3fbe`（2026-09-24）的逐条回应

```markdown
## B10 对贵组 fec3fbe 回应的确认与后续

感谢逐条处理。B10 已核对全部 7 个议题的改动，其中 **5 条已对齐**（议题 3、4、6、7，以及议题 1 的 schema_version 部分）。

以下 6 点仍需贵组确认或处理。

### 1. ⚠️ `execution` 应进 `required`，不能是可选

贵组 `task.schema.json` 现为：

    "required": ["schema_version", "job_id", "job_type", "status", "trace_id", "input", "created_at"]

`execution` 只出现在 `properties` 里，未进 `required`；贵组的失败样例也因此缺 `execution`。

但课程对 E2 的原文是：

> 公共字段（**必须包含 execution**）：schema_version、job_id、trace_id、job_type、status、execution、input、output、error

「必须包含」是硬要求。B10 建议：

- `required` 取**并集 8 项**：schema_version、job_id、trace_id、job_type、status、execution、input、created_at
- 贵组的失败样例补齐 `execution`

（B10 已按此改完本仓库 schema。）

### 2. `dockerfile_job.req.json` 里超时写了两处，且值不同

    "input":      { ..., "deadline_sec": 1800, ... }
    "execution":  { "timeout_seconds": 600, ... }

同一个超时两处表达，`1800` 与 `600` 不一致，消费者无法判定以谁为准。

**请贵组删除 `input.deadline_sec`**，超时只由 `execution.timeout_seconds` 表达。

另外贵组同批次内也自相矛盾：`dockerfile_job.res.json` 的 `execution.timeout_seconds` 为 `300`，
而 `dockerfile_job_err.res.json` 的 `detail.deadline_sec` 为 `600`。请一并统一。

### 3. `execution.resources.cpu` 类型

贵组为整数 `2`，B10 为字符串 `"2"`。**建议统一为 `string`** ——
整数表达不了 `"2000m"` 这类毫核值与小数核数。

### 4. 修复器自身崩溃：错误码无处可依

贵组 `error_codes.md` 中：

- `ANALYSIS_5001`（分析器内部异常）的服务列为 `BuildChecker / EChecker`，**不含 MDFixer**
- `ENV_3001`（可运行镜像拉取失败）的服务列**含 MDFixer**，但语义是镜像拉取失败，不是「修复器内部异常」

MDFixer 自身崩溃目前无码可用。**请贵组二选一**：

- **(a)** 在 `ANALYSIS_5001` 的服务列加入 `MDFixer`（语义放宽为「分析器/修复器内部异常」）
- **(b)** 新增 `ANALYSIS_5002`：修复器内部异常（`MDFixer`）

B10 倾向 **(b)** —— 分析器与修复器是两类服务，合并语义会让排查时无法区分。

### 5. REPAIR「候选全败」与「超时」是两种情形，不应混写

贵组原有 `repair_job_err.res.json` 把「候选 patch 全部失败」写成超时
（`EXEC_4002` + "Repair timed out"），与贵组自家 `error_codes.md` 矛盾：

- `EXEC_4003` = 候选 patch 全部失败，REPAIR 拒绝
- `EXEC_4002` = 任务执行超时

**请拆成两份样例**：候选全败用 `EXEC_4003` + `status = FAILED`；超时用 `EXEC_4002` + `status = TIMED_OUT`。

### 6. 请求侧仍未携带 `trace_id`

议题 1 的处理（统一请求必须携带正确的 `schema_version`）B10 已采纳，感谢。
但**请求侧仍无 `trace_id`**。

`trace_id` 的定义是「一次平台流程的串联 ID，跨 A/B 两组任务保持不变」。
若发起方不把它传进来，服务端只能自行生成，「同一流程内多个任务共享一个 trace_id」就无法实现。
**请在请求样例中补上 `trace_id`。**

---

## B10 侧已完成的改动

按贵组回应，B10 已更新本仓库 `e2/task.schema.json`：

| 项 | 现在 |
|----|------|
| `required` | 8 项（并集） |
| `execution.required` | `["mode", "attempt"]` |
| `trace_id` | `pattern: ^trace-[a-z0-9-]+$` |
| `artifact.required` | 6 项（对齐贵组） |
| 产物 `type` 枚举 | 10 项（对齐贵组） |
| `execution.resources.cpu` | `string` |

`python3 e2/validate.py` 最小检查 01–04 全部通过；另做 13 项变异测试确认新增约束全部生效。

---

**期望回复**：对第 1–6 条逐条给「同意 / 不同意 + 理由」。
第 1 条（`execution` 进 `required`）关系到课程明确要求，希望优先确认。

---

*本评论由 B10 组长提出，只涉及 DRAFT 部分。B10 不会直接修改本仓库文件。*
```

---

## 使用说明

1. 4 份组内 Issue 依次复制到本仓库 Issues，指派给对应成员。
2. A 组联动正文复制到 A 组仓库 Issues，**标题严格用 `[B10] DRAFT 接口确认`**。
3. 「已确认的 DRAFT 字段」一节已与 `e2/README.md` 第 2.1 节核对一致（2026-09-23）。两处内容若日后调整必须同步。
4. 创建 Issue 后，把编号回填到 `CONTRIBUTORS.md` 的 Issue/PR 列。
5. **A 组 Issue #2 的第二轮回复**（本文件上方「A 组 Issue #2 的第二轮回复正文」一节）作为 **Issue 评论**发出，不要新开 Issue。
   发出前先看 [`resolutions.md`](resolutions.md) 第一节，那是 12 条裁决的完整依据。
