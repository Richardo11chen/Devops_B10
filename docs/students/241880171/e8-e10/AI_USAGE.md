# AI 使用记录

- 是否调用模型：调用过（对话式助手用于读手册、定位报错、生成报告与 ADR 草稿）。
- 人工修改与核对：报告中的 SHA、镜像 ID、OUT 路径、steps 日志计数、测试计数均来自本人服务器实际运行输出；测试类 StudentE8B、StudentE9B、StudentE10B 按 08_个人测试编写示例.md 粘贴并逐项核对；labs/e8e10/lab.py 未修改。
- 验证方式：python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v，Ran 12 tests OK；E8/E9/E10 各 OUT 下 steps/ 日志全部 STEP_EXIT_CODE=0。
- 未由模型生成的内容：所有实验命令的实际执行结果、validation.json、results.csv、gate.json、findings.json 均为容器内真实产出。
