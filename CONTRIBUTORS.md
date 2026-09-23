# 贡献记录（CONTRIBUTORS）

B10 组 4 人贡献表。每人一行，**提交后必须回填 Commit SHA 与 Issue/PR 链接**；未完成的项写清未完成内容、失败原因、下一步。

| 姓名 | 负责模块 | 主要文件 | Commit SHA | Issue/PR | 验证结果 |
|------|----------|----------|------------|----------|----------|
| 组长 `<待填姓名>` | E2 DRAFT 契约确认、统一任务模型、校验脚本、仓库骨架 | `e2/contracts/dockerfile_job.*`<br>`e2/task.schema.json`<br>`e2/validate.py`<br>`e2/ADR.md`<br>`e2/Backlog.md`<br>`e2/AI_USAGE.md` | `<待填>` | `<待填>` | `<待填>` |
| 成员B `<待填姓名>` | E2 REPAIR 契约确认 | `e2/contracts/repair_job.*` | `<待填>` | `<待填>` | `<待填>` |
| 成员C `<待填姓名>` | E3 DRAFT 样本与 Docker 证据 | `e3/fixtures/draft/`<br>`e3/evidence/` | `<待填>` | `<待填>` | `<待填>` |
| 成员D `<待填姓名>` | E3 MDFixer 样本与修复验证 | `e3/fixtures/mdfixer/`<br>`e3/evidence/` | `<待填>` | `<待填>` | `<待填>` |

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
