# Backlog — E2 任务表（B10）

每个任务写清：**任务、负责人、产物、验收条件**。完成后回填 Commit SHA，并同步 `../CONTRIBUTORS.md`。

| ID | 任务 | 负责人 | 产物 | 验收条件 | 状态 |
|----|------|--------|------|----------|------|
| T-001 | 初始化 B10 仓库骨架 | 组长 | `README.md`、`CONTRIBUTORS.md`、`e2/`、`e3/`、`work/` | 目录结构与课程要求一致；README 写清配对关系、A 组链接、分工表、环境要求 | 已完成 |
| T-002 | 确认 DRAFT 接口契约 | 组长 | `e2/contracts/dockerfile_job.*`、`e2/README.md` 第 2 节 | 逐条确认字段；9 个公共字段含 `execution` 齐全；确认/修改/待议三节均无待填 | 待办 |
| T-003 | 写统一任务模型与最小检查脚本 | 组长 | `e2/task.schema.json`、`e2/validate.py` | Schema 含全部公共字段与 `execution`，四类对象均可表达；`validate.py` 覆盖最小检查 01–04 | 待办 |
| T-004 | 确认 REPAIR 接口契约 | 成员B | `e2/contracts/repair_job.*`、`e2/README.md` REPAIR 节 | REPAIR 请求/响应/错误三件套字段齐全；与 `task.schema.json` 一致；差异点写明理由 | 待办 |
| T-005 | E3 DRAFT 样本与 Docker 证据 | 成员C | `e3/fixtures/draft/`、`e3/evidence/` | broken 与 reference 两候选齐备；两层成功判据（编译通过 + 功能验证）均有日志；保存 diff、退出码、日志、镜像 ID | 待办 |
| T-006 | E3 MDFixer 固定输入与修复验证 | 成员D | `e3/fixtures/mdfixer/`、`e3/evidence/` | 固定输入四件套齐备；Target 风格参考 Patch 可用；四种风格差异说明；`.d` 文件行为已验证 | 待办 |
| T-007 | 向 A 组提 DRAFT 接口确认 Issue | 组长 | `e2/issue_draft.md` 中的 A 组 Issue 正文 | 只涉及组长负责的 DRAFT 部分；开放问题列清；**不直接修改 A 组仓库** | 待办 |
| T-008 | 记录 AI 使用情况 | 全体 | `e2/AI_USAGE.md` | 每人至少一条记录，含提示摘要、AI 建议、人工采纳/修改/拒绝理由 | 进行中 |

## 说明

- **状态**取值：`待办` / `进行中` / `已完成` / `受阻`
- **受阻**的任务必须在备注里写清失败原因与下一步，不允许留空
- 任务拆分粒度以「一次提交能完成」为准，过大请拆成新 ID
