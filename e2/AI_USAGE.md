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
| AI-005 | 2026-09-24 | 成员B | WorkBuddy / DeepSeek-V4.1-Flash | 复核 REPAIR 三件套是否忠于任务书指定基线并重做 | 任务书指定的只读参考基线是 `7720a30`，但前一版实际对照的是 A 组 main 现况 `fec3fbe`；要求逐字节比对两个基线的原文，确认偏差范围后重做 | 逐文件比对后判定：两基线之间 A 组自己改过 `repair_job.*` 与 `task.schema.json`，故前一版 README 6.2 的 7 条「A 组原样」中有 4 条在 `7720a30` 处并不存在；并指出三处越界改动 —— **漏掉 A 组两个基线都有的 `input.makefile_uri`**（MDFixer 靠它定位待修 Makefile，缺失会导致真实对接断）、把 `max_candidates` 从 `input.options` 提到 `input` 顶层、新增来源不明的 `input.source_commit`；同时修正 `repository.commit` 占位符应取 `<C0_FULL_40_SHA>`（与 A 组 `full_check.req.json` 一致） | 修改后采纳 | 比对结论与三处越界改动的判断采纳，三件套全部重写：`makefile_uri` 恢复、`max_candidates` 移回 `input.options`、`source_commit` 删除并转为待议项（6.3 第 11 条）、`commit` 改回 C0。README 6.2 改为「`7720a30` → `fec3fbe`」双基线并列，并新增 6.6 节说明两基线差异，使两种口径都能被逐行核对。**一处不采纳**：AI 曾建议把 `source_commit` 直接删掉不予讨论，人工判断应保留为待议项 —— 因为组长 `e2/validate.py` 第 123–125 行的内置 REPAIR 请求样例**确实携带** `source_commit`，删除需经组长确认，不能由成员B 单方决定 | `e2/contracts/repair_job.{req,res,_err.res}.json`、`e2/README.md` 第 6 节 @ `29b5e14`；核对基线 A 组 `7720a30` 与 `fec3fbe` 双点 |
| AI-006 | 2026-09-24 | 成员C | Antigravity / Gemini 3.8 Flash | E3 DRAFT 样本准备与 Docker 双层判据证据记录 | 要求构造 Dockerfile.broken 与 Dockerfile.reference 两个候选样本，满足两层判据，并生成规范命名的证据文件 | AI 建议在 broken 候选中使用畸变指令注入故障，且起初仅设计记录构建日志 | 修改后采纳 | 拒绝人工造假指令，严格按课程要求基于 `python:3.13-slim` 自然触发 `make: not found`；且严格落实双层判据，补充第二层容器内 `./hello` 功能验证输出与退出码证据 | `e3/fixtures/draft/*`、`e3/evidence/*` @ `b2c38a8` |
| AI-007 | 2026-09-25 | 成员D | Claude Code | 设计并实现 E3 MDFixer 固定输入与修复验证 | 按固定输入四件套 + reference.patch + 六步验证要求，规划 fixtures/evidence/work 目录与验证命令并执行 | 扁平目录布局；Target 风格 reference.patch；以第5步「不 clean 自动重建」作为 MD 已修的决定性证据；用 gcc -MMD -MP 实证 Implicit 风格；嵌套 git 仓库 + 外层 .gitignore 排除 | 采纳 | 三项决策（嵌套仓库+gitignore、README片段+Implicit实证、扁平布局）均采纳；执行中修正一处——无效候选需先 make clean 才能触发注入的失败命令 | `e3/fixtures/mdfixer/`、`e3/evidence/`、`.gitignore` @ `d3c86ca`、`aec91a4` |
| AI-008 | 2026-09-25 | 成员B | WorkBuddy / DeepSeek-V4.1-Flash | 落地组长对 12 条议题的裁决，并在收紧后的 schema 上复核交付物 | 合并 `origin/main` 后按新 schema 复核三件套，找出文档中因裁决而**失效的论据**，并为新增约束补变异用例 | 判定「三件套无需改动」（契约字节级未变）；指出 README 6.2 第 6 条「`VERIFY_LOG` 改 `BUILD_LOG`」的**理由已被裁决推翻**（枚举已补 `VERIFY_LOG`），必须重写；把变异脚本由 34 项扩为 **44 项变异 + 3 项正向对照 + 2 项已知缺口**；新增发现「`check_request` 不校验 `trace_id` 的 pattern 与 `execution.attempt`」 | 修改后采纳 | 复跑结论采纳（`required=8` 下 `EXIT=0`、44/44 被拒、三件套 sha256 不变）。**一处不采纳**：AI 一度建议把 REPAIR 的 `verify.log` 类型改回 `VERIFY_LOG` 以对齐 A 组 —— 人工判断这会**造成 B 组内部前后不一致**（组长定稿的 DRAFT 样例 `dockerfile_job.res.json` 同样用 `BUILD_LOG`，且组长已裁定其「无需改动」），故保持 `BUILD_LOG`，另把「两组取值口径不统一」列为新待议项（README 6.7.2 第 2 条）。**一处人工改判**：AI 初版变异用例把 `trace-020-x` 列为「应被拒绝」，但它其实**符合** `^trace-[a-z0-9-]+$`，人工改为 `trace-020_x`（含下划线，确实非法） | `e2/README.md` 第 6 节（6.2 第 6 条、6.3、6.5、新增 6.7）、`e2/ADR.md` ADR-002、`.workbuddy/plans/_mutate_repair.py` @ `c434742`；核对对象 B10 `main` @ `70776a7` |
| AI-009 | 2026-09-25 | 成员B | WorkBuddy / DeepSeek-V4.1-Flash | 同步成员C/D 合入后的最新 `main`，处理合并冲突并复核交付物 | 合并 `origin/main`（`aad384e`）时要求「冲突先别硬解，把现场发给我」，需要判定冲突性质、给出无损解法，并确认三件套在合并后仍通过校验 | 判定冲突仅 2 处且均为「多人并行追加同一张表」所致，不涉及契约与代码：`CONTRIBUTORS.md` 是同批行的双方改写、`e2/AI_USAGE.md` 是 `AI-006` **编号撞车**（成员C 已占用）；建议成员B 行取本分支新版（含 44 项变异）、C/D 行取 `main`、成员B 的 AI 记录顺延为 `AI-008`；另报出 `main` 侧 `e2/AI_USAGE.md` 表格内存在空行会把成员D 行切成表外段落 | 采纳 | 无损解法采纳并已提交（未单方重排他人记录编号、未改动组长文件）。**一处补正**：AI 另发现并修复 `e2/AI_USAGE.md` 表格中的空行断行；**一处存疑待裁**：AI 记录编号的分配顺序（按人 vs 按日期）本组此前无明文约定，本次按「`main` 已有编号顺延」处理，已在 PR 说明中提请组长确认 | `CONTRIBUTORS.md`、`e2/AI_USAGE.md`、`e2/README.md` 第 6 节 @ `<待填 SHA>`；核对对象 B10 `main` @ `aad384e` |

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
