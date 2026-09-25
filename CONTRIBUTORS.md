# 贡献记录（CONTRIBUTORS）

B10 组 4 人贡献表。每人一行，**提交后必须回填 Commit SHA 与 Issue/PR 链接**；未完成的项写清未完成内容、失败原因、下一步。

| 姓名 | 负责模块 | 主要文件 | Commit SHA | Issue/PR | 验证结果 |
|------|----------|----------|------------|----------|----------|
| 陈奕澎（组长） | E2 DRAFT 契约确认、统一任务模型、校验脚本、仓库骨架 | `e2/contracts/dockerfile_job.*`<br>`e2/task.schema.json`<br>`e2/validate.py`<br>`e2/ADR.md`<br>`e2/Backlog.md`<br>`e2/AI_USAGE.md` | `7ff92ae`<br>`c370828`<br>`685f034` | [#1](../../issues/1) | 最小检查 01–04 全部通过（exit 0）；13 项变异测试全部被 schema 拒绝 |
| 张少逸（成员B） | E2 REPAIR 契约确认 | `e2/contracts/repair_job.*`<br>`e2/README.md` 第 6 节<br>`e2/ADR.md` ADR-002 | `e74af37`<br>`29b5e14`<br>`c434742` | [#2](../../issues/2)<br>[PR #3](../../pull/3) | `python3 e2/validate.py` → 最小检查 01–04 全部通过（EXIT=0），`repair_job.*` 三处由 `SKIP` 变 `OK`；**44 项变异全部被拒绝**（另 3 项正向对照被接受、2 项已知缺口已上报） |
| 孙正奇（成员C） | E3 DRAFT 样本与 Docker 证据 | `e3/fixtures/draft/`<br>`e3/evidence/` | `b2c38a8` | [#4](../../issues/4)<br>[#5](../../pull/5) | 两层成功判据均达成；Broken 构建失败（exit 127，make: not found）；Reference 构建成功（exit 0）且容器运行输出 hello E3（exit 0） |
| 宋丞轩（成员D） | E3 MDFixer 样本与修复验证 | `e3/fixtures/mdfixer/`<br>`e3/evidence/`<br>`work/mdfixer-demo/` | `d3c86ca`<br>`aec91a4` | [#6](../../issues/6)<br>[#7](../../pull/7) | 六步修复验证通过（第5步不 clean 自动重建输出 v3）；无效候选三步反向验证通过；.d/-include 隐式规则验证通过。证据见 `e3/evidence/` |

## 组长完成记录

**已完成内容**：仓库骨架、DRAFT 契约确认、统一任务模型、最小检查脚本、ADR-001、成员任务模板与 Issue 草稿。

| commit | 内容 |
|--------|------|
| `7ff92ae` | init: 建立 B10 仓库骨架与 E2/E3 文档框架 |
| `c370828` | e2: 确认 DRAFT 契约并补齐 execution 公共字段 |

**验证结果**：

```bash
$ python3 e2/validate.py
task.schema.json 已加载（required=7 项，properties=11 项）
...
最小检查 01–04 全部通过。
EXIT=0
```

另做 **13 项变异测试**（删 `execution`、`sha256` 位数不足、产物 `type` 越界、`SUCCEEDED` 缺 `output`、`error.code` 格式错、`execution.attempt=0` 等），**全部被 `task.schema.json` 拒绝** —— 证明校验通过不是因为约束太松，schema 不是空壳。

**未完成项 / 下一步**：

| 项 | 原因 | 下一步 |
|----|------|--------|
| ~~「Issue/PR」列待填~~ | 已解决 | 已回填本仓库 Issue [#1](../../issues/1) |
| 与 A 组的 7 条待议项 | 等待对方回复 | 已提 [ana12-21/Devops_G10#2](https://github.com/ana12-21/Devops_G10/issues/2)；见 `e2/README.md` 第 2.3 节 |
| 成员B/D 的贡献行 | 待其本人完成 | 各自完成后回填 SHA 与验证结果 |
| 成员C 的贡献行 | 已完成 | 已回填 SHA `b2c38a8` 与两层判据结果 |
| 分支 / PR 流程 | 暂缓决定 | 成员分支名已写在 `e2/issue_draft.md` |

## 成员C完成记录

**已完成内容**：DRAFT 测试基线项目（Tiny Greeting `main.c` / `Makefile`）、两层判据候选（`Dockerfile.broken` 与 `Dockerfile.reference`）、场景化证据记录（构建日志、退出码、镜像 ID、diff、功能验证日志）。

| commit | 内容 |
|--------|------|
| `b2c38a8` | e3: 添加 DRAFT 失败与参考成功样本及构建证据 |

**验证结果**：
1. **第一层判据（编译构建）**：
   - Broken 候选：`docker build -f Dockerfile.broken` 失败，退出码 127，日志精准定位 `/bin/sh: 1: make: not found`。
   - Reference 候选：`docker build -f Dockerfile.reference` 成功，退出码 0，镜像 `b10-draft-reference:latest`（ID: `eca1d90eb03f`）正常生成。
2. **第二层判据（功能验证）**：
   - Reference 容器内执行 `./hello`，退出码 0，标准输出精准匹配 `hello E3`。
3. **证据齐备**：
   - 包含 `dockerfile.diff`、`draft-broken-build.log`、`draft-broken-exit.txt`、`draft-reference-build.log`、`draft-reference-exit.txt`、`draft-image-id.txt`、`draft-verify.log`、`draft-verify-exit.txt`。

**未完成项 / 下一步**：
无未完成项。所有两层判据与基线四要素均已完备落地。

---

## 成员B 完成记录（张少逸）

**已完成内容**：E2 REPAIR（MDFixer）契约确认 —— 新增 `repair_job.req.json` / `repair_job.res.json` / `repair_job_err.res.json`，并在 `e2/README.md` 第 6 节写清确认 / 修改 / 待议与 8 条差异点，补 ADR-002。

| commit | 内容 |
|--------|------|
| `e74af37` | e2: 确认 REPAIR 契约并补 trace_id / execution / 产物枚举对齐（初版） |
| `29b5e14` | e2: 按双基线（`7720a30` / `fec3fbe`）重做三件套与第 6 节 —— 恢复 `input.makefile_uri`、`max_candidates` 移回 `input.options`、删除来源不明的 `source_commit`、`commit` 占位符改回 `<C0_FULL_40_SHA>` |
| `48586d7` | Merge `origin/main`（`70776a7` 裁决提交）—— 零冲突合入，三件套未改动 |
| `c434742` | e2: 落地 12 条裁决并修正因枚举扩容而失效的论据 —— README 6.2 第 6 条重写理由、6.3 加裁决列、6.5 扩为 44+3+2、新增 6.7 |

**验证结果**：

**（1）裁决前** —— 2026-09-24，Ubuntu 22.04.5 LTS（WSL2）/ Python 3.10.12 / jsonschema 3.2.0，当时 `task.schema.json` 为 `required=7` 项：

```bash
$ python3 e2/validate.py
...
    OK    repair_job.res.json 通过（status=SUCCEEDED）
    OK    repair_job_err.res.json 通过（status=FAILED）
    OK    repair_job.req.json
...
最小检查 01–04 全部通过。
EXIT=0
```

**（2）裁决后** —— 2026-09-25，合并组长裁决提交 `70776a7` 并按收紧后的 schema 复跑：

```bash
$ python3 e2/validate.py
task.schema.json 已加载（required=8 项，properties=11 项）
...
最小检查 01–04 全部通过。
EXIT=0
```

`required` 由 7 项增至 8 项（补 `created_at`）、`execution.required` 加 `attempt`、`trace_id` 加 `pattern`、`artifact.required` 加 `media_type`/`sha256`、产物枚举 8 → 10 项 —— **本组三件套一行未改即全部通过**，且 sha256 与裁决前**完全一致**。

**反空壳共 49 项**：44 项变异**全部被拒绝**（含裁决新增的 `created_at`、`execution.attempt`、`trace_id` pattern、`media_type`、`sha256` 共 7 项）；另设 **3 项正向对照全部被接受**（产物 `type` 用 `VERIFY_LOG` / `ERROR_REPORT` 应合法 —— 证明裁决第 1 条的枚举扩容真的生效）；**2 项已知缺口**已确认并作为新发现上报（`check_request` 未校验 `trace_id` 的 pattern、未校验 `execution.attempt`，见 `e2/README.md` 6.7.2）。

**未完成项 / 下一步**：

| 项 | 原因 | 下一步 |
|----|------|--------|
| ~~本行姓名与 Commit SHA~~ | 已解决 | 已回填姓名「张少逸」与提交 SHA |
| ~~与 A 组 / 组长的 12 条待议项~~ | 已解决 | 组长 2026-09-25 已**全部裁决**（见 `e2/resolutions.md`）：B 组侧 6 条已落地，6 条转 A 组处理，本组不重复提 |
| ~~基线口径（`7720a30` vs `fec3fbe`）~~ | 已解决 | 三件套已按 A 组**两个基线共同成立**的事实重做；`e2/README.md` 6.2 改为双基线并列，新增 6.6 节给出逐文件差异与可复现核对命令 |
| ~~Linux 环境复跑~~ | 已解决 | 裁决前已在 **Ubuntu 22.04.5 LTS（WSL2）** 下复跑，结果与 Windows 侧逐项一致；裁决后复跑记录见 `e2/README.md` 6.5 第 2 部分（含 WSL 侧复现命令） |
| ~~请求侧 `schema_version` 冲突~~ | 已解决 | 裁决第 9 条：A 组已加入 `schema_version`；`trace_id` 部分转 A 组继续追 |
| **分支推送与 PR** | 本地凭据助手为 `helper-selector`，需交互式登录，无法在脚本中完成 | 由本人在终端执行 `git push -u origin memberB/e2-repair-contract`，再开 PR 到 `main`（正文见 `.workbuddy/plans/pr_body.md`） |
| 本轮新发现 3 条 | 涉及 `e2/validate.py`（组长文件）与两组 `verify.log` 取值口径 | 见 `e2/README.md` 6.7.2，待组长定夺 |

---

## 成员D 完成记录

**已完成内容**：MDFixer 固定输入四件套（固定 MD 报告 / 同一源码版本 Makefile / 构建命令与行为测试 / 预期声明风格）、`reference.patch`（Target 风格）、修复验证六步、无效候选三步反向验证、`.d` 隐式规则验证。

| commit | 内容 |
|--------|------|
| `d3c86ca` | e3: 添加 MDFixer 固定输入四件套与 reference.patch |
| `aec91a4` | e3: 添加 MDFixer 修复验证证据（六步 + 无效候选 + .d 隐式规则） |

**验证结果**：六步修复验证通过（第 5 步不 clean 自动重建输出 v3 为决定性证据）；无效候选三步反向验证通过（注入失败命令后 `make` 非零退出 `Error 1`）；`.d`/`-include main.d` 隐式规则验证通过（`main.d` 含 `config.h`，改头文件自动重建）。证据见 `e3/evidence/`。

**未完成项 / 下一步**：

| 项 | 原因 | 下一步 |
|----|------|--------|
| 提 PR 合入 main | 分支已变基到 main，尚未创建 PR | 创建 PR 请求合并到 main |

---

## 填写要求

- **姓名**：填真实姓名，与 Issue 指派人一致。
- **Commit SHA**：填完整 40 位或至少 7 位短 SHA，**必须是本人提交**，便于追溯个人贡献。
- **Issue/PR**：填本仓库 Issue 编号或 PR 链接。Issue 草稿见 [`e2/issue_draft.md`](e2/issue_draft.md)。
- **验证结果**：写**实际跑出来的结论**（可复现命令 + 观察到的输出），不要写"应该没问题"。
- **未完成项**：写清未完成内容、失败原因、下一步计划。

## 提交规范

每个提交对应一条可追溯的贡献，建议格式：

```text
<module>: <做了什么>

- 产出/验证要点
- 复现命令
```

示例：`e2: 确认 DRAFT 契约并补 execution 公共字段`、`e3: 添加 DRAFT broken 失败样本与构建日志`。
