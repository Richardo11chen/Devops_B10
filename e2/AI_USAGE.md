# AI 使用记录（AI_USAGE）— B10 / E2

课程要求：记录 **工具/模型与任务**、**提示摘要**、**AI 建议**、**人工采纳/修改/拒绝理由**、**关联文件版本验证**。

**每条记录必须有人工判断结论**。原样粘贴 AI 输出而不做验证，不算有效记录。

## 记录格式

| 字段 | 填写要求 |
|------|----------|
| 编号 | `AI-001` 起递增 |
| 日期 | `YYYY-MM-DD` |
| 使用人 | 组长 / 成员B / 成员C / 成员D |
| 工具与模型 | 例：`Claude Code / claude-opus-5`；写清具体型号 |
| 任务 | 这次让 AI 做什么 |
| 提示摘要 | 自己话概括的提示要点，**不要粘贴整段提示原文** |
| AI 建议 | AI 给出的关键结论或产物 |
| 人工结论 | `采纳` / `修改后采纳` / `拒绝` |
| 理由 | 为什么这么判断；拒绝和修改尤其要写清 |
| 关联文件与版本 | 受影响文件 + commit SHA，便于验证当时 AI 看到的是哪一版 |

## 记录表

| 编号 | 日期 | 使用人 | 工具与模型 | 任务 | 提示摘要 | AI 建议 | 人工结论 | 理由 | 关联文件与版本 |
|------|------|--------|-----------|------|----------|---------|----------|------|----------------|
| AI-001 | 2026-09-23 | 组长 | Claude Code | 起草 B10 仓库骨架与文档框架 | 按课程 E2/E3 要求生成目录结构、README/CONTRIBUTORS/ADR/Backlog 框架 | 给出目录结构建议，指出 A 组 `dockerfile_job.req.json` 缺 `schema_version`、`trace_id`，且全库无 `execution` 公共字段 | 修改后采纳 | 结构可用；但字段缺失结论需在 T-002 逐条复核 A 组原文件后再定稿，未直接采信 | `README.md`、`e2/README.md` @ `<待填 SHA>` |
| AI-002 | 2026-09-23 | 组长 | Claude Code | 逐条复核 A 组 DRAFT 契约并改写 `dockerfile_job.*` | 对照课程 9 个公共字段核对 A 组原文件，指出缺失与冲突 | 建议：请求侧补 `schema_version`/`trace_id`；`input.deadline_sec` 移入 `execution.timeout_seconds`；`output` 改为 `artifacts[]` 带 `sha256`；`task.schema.json` 的 `output` 补 `artifacts`/`findings` 属性声明 | 修改后采纳 | 字段补全与 `output` 约束采纳；但 AI 最初把「请求缺 `schema_version`」当成 A 组缺陷，实为 A 组 `validate.py` 的**有意设计**，已改写为冲突讨论项；`output` 改数组可能构成破坏兼容，已标注待 A 组确认 | `e2/task.schema.json`、`e2/contracts/dockerfile_job.*`、`e2/README.md` @ `<待填 SHA>` |
| AI-003 | 2026-09-23 | 组长 | Claude Code | 编写并验证 `e2/validate.py` | 覆盖课程最小检查 01–04 | 初版检查 1d 拿单个 `SUCCEEDED` 样例去要求 `error` 字段，必然误报；检查 02 的预期失败被当成真失败打印 | 修改后采纳 | 两处均为 AI 自身缺陷，人工复核运行输出后发现并修正：1d 改为检查 schema 声明的字段集并对 FAILED 样例单独验证；负例改用 `expect_reject` 分支 | `e2/validate.py` @ `<待填 SHA>` |
| AI-004 | 2026-09-24 | 成员B | WorkBuddy / DeepSeek-V4.1-Flash | 确认 REPAIR 契约，并与 A 组现有实现逐条比对 | 读本仓库与 A 组仓库，比对 `repair_job.*` 与 `task.schema.json`，给出冲突清单、落地步骤与差异点理由 | 指出 A 组三件套原样搬入会踩 7 处不合规；建议 `resources.cpu` 统一为 string、`VERIFY_LOG` 用 `BUILD_LOG` 承载、失败码改 `EXEC_4003`、`style_hint` 按 E3 口径枚举化；并建议把候选日志一并列入 `output.artifacts[]` | 修改后采纳 | 字段级比对结论采纳（已用本仓库 schema + `validate.py` 复跑验证，另做 34 项变异测试反空壳）。**三处不采纳**：① 其初判「请求样例缺 `job_id`/`status` 即不合规」——经查 `validate.py` 的 `check_request` 明确把 `job_id`/`status`/`output`/`error` 列为「请求不应携带的服务端字段」，请求本就不该有这些键，属未读脚本即下结论；② 其建议「直接把 `VERIFY_LOG` 加入产物枚举」——`task.schema.json` 是组长文件、成员B 无权修改，改用 `BUILD_LOG` 复用承载；③ 其建议「按 A 组口径把 `resources.cpu` 改成 integer」——本组 schema 定义为 string，反而应推动 A 组向 string 统一，已列为待议项 | `e2/contracts/repair_job.{req,res,_err.res}.json`、`e2/README.md` 第 6 节 @ `e74af37`；核对对象 A 组基线 `fec3fbe`；**其中「7 处」的口径已被 AI-005 修正为 14 处（双基线）** |
| AI-005 | 2026-09-24 | 成员B | WorkBuddy / DeepSeek-V4.1-Flash | 复核 REPAIR 三件套是否忠于任务书指定基线并重做 | 任务书指定的只读参考基线是 `7720a30`，但前一版实际对照的是 A 组 main 现况 `fec3fbe`；要求逐字节比对两个基线的原文，确认偏差范围后重做 | 逐文件比对后判定：两基线之间 A 组自己改过 `repair_job.*` 与 `task.schema.json`，故前一版 README 6.2 的 7 条「A 组原样」中有 4 条在 `7720a30` 处并不存在；并指出三处越界改动 —— **漏掉 A 组两个基线都有的 `input.makefile_uri`**（MDFixer 靠它定位待修 Makefile，缺失会导致真实对接断）、把 `max_candidates` 从 `input.options` 提到 `input` 顶层、新增来源不明的 `input.source_commit`；同时修正 `repository.commit` 占位符应取 `<C0_FULL_40_SHA>`（与 A 组 `full_check.req.json` 一致） | 修改后采纳 | 比对结论与三处越界改动的判断采纳，三件套全部重写：`makefile_uri` 恢复、`max_candidates` 移回 `input.options`、`source_commit` 删除并转为待议项（6.3 第 11 条）、`commit` 改回 C0。README 6.2 改为「`7720a30` → `fec3fbe`」双基线并列，并新增 6.6 节说明两基线差异，使两种口径都能被逐行核对。**一处不采纳**：AI 曾建议把 `source_commit` 直接删掉不予讨论，人工判断应保留为待议项 —— 因为组长 `e2/validate.py` 第 123–125 行的内置 REPAIR 请求样例**确实携带** `source_commit`，删除需经组长确认，不能由成员B 单方决定 | `e2/contracts/repair_job.{req,res,_err.res}.json`、`e2/README.md` 第 6 节 @ `<本轮 SHA>`；核对基线 A 组 `7720a30` 与 `fec3fbe` 双点 |

> 其余记录由各成员在完成自己任务时追加。**每人至少一条。**

## 已声明待验证事项（2026-09-23 复核完毕）

AI 提出的待验证结论，已逐条回查 A 组原文：

- [x] ~~A 组 DRAFT 请求契约缺 `schema_version`、`trace_id` 两个公共字段~~
      → **部分不成立**。缺 `schema_version`/`trace_id` 属实，但**不是疏漏**：A 组 `scripts/validate.py` 的 `check_request_envelope` 把 `schema_version` 明确列为「请求不应携带的服务端字段」，是有意为之。已改写为「课程要求与 A 组实现冲突」的讨论项（见 `issue_draft.md` 第 1 条），不再作为缺陷主张。
- [x] ~~A 组 DRAFT 响应样例中 `input` 为占位符 `{"_echo": "请求副本或省略"}`，非具体值~~
      → **成立**。已确认为真实问题，列为待议第 4 条（原 Issue 第 3 条）。
- [x] ~~A 组 `ENV_3002` 在 DRAFT 与检测类任务间是否语义共用，需与 A 组确认~~
      → **不成立，AI 判断有误**。A 组 `error_codes.md` 该行已明确标注「可能抛出的服务：DRAFT」，即 DRAFT 专用。AI 提问前未读该文件。已改为「已确认」项（2.1 第 10 条）。

> **教训**：AI 在未读完 A 组全部契约文件时就提出了问题清单。
> 其中 2 条（`ENV_3002` 语义、`pair10` 命名空间）在 A 组文档中已有明确答案，
> 属**提问前未取证**。后续任何「A 组缺失/矛盾」的判断，必须先回查 A 组 `contracts/` 与 `docs/` 原文再下结论。
