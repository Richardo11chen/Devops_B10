# 贡献记录（CONTRIBUTORS）

B10 组 4 人贡献表。每人一行，**提交后必须回填 Commit SHA 与 Issue/PR 链接**；未完成的项写清未完成内容、失败原因、下一步。

| 姓名 | 负责模块 | 主要文件 | Commit SHA | Issue/PR | 验证结果 |
|------|----------|----------|------------|----------|----------|
| 陈奕澎（组长） | E2 DRAFT 契约确认、统一任务模型、校验脚本、仓库骨架 | `e2/contracts/dockerfile_job.*`<br>`e2/task.schema.json`<br>`e2/validate.py`<br>`e2/ADR.md`<br>`e2/Backlog.md`<br>`e2/AI_USAGE.md` | `7ff92ae`<br>`c370828`<br>`685f034` | [#1](../../issues/1) | 最小检查 01–04 全部通过（exit 0）；13 项变异测试全部被 schema 拒绝 |
| 张少逸（成员B） | E2 REPAIR 契约确认 | `e2/contracts/repair_job.*`<br>`e2/README.md` 第 6 节<br>`e2/ADR.md` ADR-002 | `e74af37` | [#2](../../issues/2) | `python3 e2/validate.py` → 最小检查 01–04 全部通过（EXIT=0），`repair_job.*` 三处由 `SKIP` 变 `OK`；34 项变异测试全部被 schema 拒绝 |
| 成员C `<待填姓名>` | E3 DRAFT 样本与 Docker 证据 | `e3/fixtures/draft/`<br>`e3/evidence/` | `<待填>` | `<待填>` | `<待填>` |
| 成员D `<待填姓名>` | E3 MDFixer 样本与修复验证 | `e3/fixtures/mdfixer/`<br>`e3/evidence/` | `<待填>` | `<待填>` | `<待填>` |

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
| 成员B/C/D 的贡献行 | 待其本人完成 | 各自完成后回填 SHA 与验证结果 |
| 分支 / PR 流程 | 暂缓决定 | 成员分支名已写在 `e2/issue_draft.md` |

---

## 成员B 完成记录（张少逸）

**已完成内容**：E2 REPAIR（MDFixer）契约确认 —— 新增 `repair_job.req.json` / `repair_job.res.json` / `repair_job_err.res.json`，并在 `e2/README.md` 第 6 节写清确认 / 修改 / 待议与 8 条差异点，补 ADR-002。

| commit | 内容 |
|--------|------|
| `e74af37` | e2: 确认 REPAIR 契约并补 trace_id / execution / 产物枚举对齐 |

**验证结果**（Ubuntu 22.04.5 LTS（WSL2）/ Python 3.10.12 / jsonschema 3.2.0）：

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

另做 **34 项变异测试**（删 `execution`、`resources.cpu` 改整数、产物 `type` 改 `VERIFY_LOG`、`sha256` 截短、`FAILED` 删 `error`、请求携带 `status` 等），**全部被 `task.schema.json` / `check_request` 拒绝**。

**未完成项 / 下一步**：

| 项 | 原因 | 下一步 |
|----|------|--------|
| ~~本行姓名与 Commit SHA~~ | 已解决 | 已回填姓名「张少逸」与 `e74af37` |
| 与 A 组 / 组长的 10 条待议项 | 涉及 `task.schema.json`（组长文件）与 A 组仓库，成员B 无权单方面修改 | 见 `e2/README.md` 第 6.3 节 |
| ~~Linux 环境复跑~~ | 已解决 | 已在 **Ubuntu 22.04.5 LTS（WSL2）/ Python 3.10.12 / jsonschema 3.2.0** 下复跑，`validate.py` 与 34 项变异测试结果与 Windows 侧逐项一致；`e2/README.md` 6.5 的环境标注已同步更新为 Linux |
| 请求侧 `schema_version` 冲突 | 与 A 组实现直接冲突 | 沿用 `e2/README.md` 2.3 第 1 条，等 A 组定夺 |

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
