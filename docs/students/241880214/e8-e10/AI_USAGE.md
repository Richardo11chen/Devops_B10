# AI使用记录

工具/模型/日期：Claude Code / DeepSeek-V4.1-Flash-1017 / 2026-11-04。

输入上下文与问题：按 E8–E10 B 轨道手册完成固定 MD 报告、三种声明风格 Patch、E10 的拒绝/接受/坏 Patch 与 BuildChecker 重检；合并 main 后补充一条自设计测试并填写报告/ADR/AI 记录。

模型建议：辅助执行课程参考流程、整理证据和起草文档；没有让模型生成或修改 `labs/e8e10/lab.py` 的核心算法，也没有用模型生成实验数据。main 中的 `StudentE8B`/`StudentE9B`/`StudentE10B` 三个示例测试来自课程 `08_个人测试编写示例.md`，不作为本人新增贡献。

采纳/拒绝及理由：采纳自设计测试 `Student241880214.test_macro_plus_direct_dependency_is_mixed`（macro 风格 + 目标行额外直接依赖 → 预期 style=mixed），因为该预期可由 `patch()` 的风格分支独立推导并在容器内复现；拒绝把示例测试重复算作个人贡献，也拒绝改写参考实现或伪造证据。

人工修改：本人在 `labs/e8e10/test_profile.py` 末尾新增 1 个自设计测试类（约 20 行）；三份文档由本人审核；实验命令、OUT 和预期由本人确认。

实际验证命令/输入/结果：`python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v` → `Ran 13 tests ... OK`（`work/unit-tests-20261104-205504.log`）；E8/E9/E10 的 `lab_python` 分别执行 6/4/7 次，全部 `STEP_EXIT_CODE=0`。

未调用模型时写明未调用：本轮未让模型参与实验数据生成或 `lab.py` 修改；所有构建、扫描、Patch、验证和 BuildChecker 结果均来自容器内实际执行。参考实现来自课程 `labs/e8e10/lab.py` 与 `08_个人测试编写示例.md`；本人贡献为自设计测试、证据整理和文档。
