# AI使用记录

工具/模型/日期：WorkBuddy AI 助手，2026-11-03。
输入上下文与问题：提供E8-E10实验材料路径、操作手册（8_E8_B组.md、07_提交与排错.md、08_个人测试编写示例.md）、lab.py源码与既有测试；请求协助按手册逐步执行E8-B轨、设计自主任务测试、填写报告并完成GitHub提交。
模型建议：按手册顺序执行8个步骤并核对每步通过条件；自主任务避免与同学已合入main的REDUNDANT-only用例重复，改选"未知目标拒绝"方向；补充参考测试StudentE8B（配方字节保持）；发现首版测试缺setUp后建议修复。
采纳/拒绝及理由：全部采纳。拒绝重复同学用例的理由是保证个人贡献的独立性与增量价值；采纳参考测试是为覆盖配方字节保持这一B轨核心保证。
人工修改：自主测试的输入构造、断言内容（ValueError正则UNSUPPORTED_TARGET、字节比较、git status干净断言）及报告/ADR/AI记录的填写均由本人确认与调整；报告中对参考代码与自研部分的边界已如实标注。
实际验证命令/输入/结果：OUT=work/e8-B-manual.0XgyC8 各步STEP_EXIT_CODE=0；unittest discover → Ran 10 tests, OK，TEST_EXIT_CODE=0。
