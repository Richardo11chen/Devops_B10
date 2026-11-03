# 决策记录

背景与约束：
E8 需要在「不污染被测项目」的前提下，从一份固定 MD 报告生成候选补丁。约束有三：报告必须绑定到具体提交；只处理 MISSING，不能动 REDUNDANT；生成阶段不得写回源文件——是否接受要留到 E10 的构建/测试/重检判定。

选择与替代方案：
- **选择**：`patch()` 只做文本追加，返回统一 diff 与修改计划，不落盘；`validate()` 在副本 sandbox 中应用并逐项判定，全部通过才把 Makefile 字节写回。
- **替代方案 1**：直接 `sed` 原地修改 Makefile。被否决——生成失败会污染输入，且无法把「生成」与「接受」分离。
- **替代方案 2**：用 Git 分支隔离修改。被否决——样例内部 Git 是受测对象，在其上建分支会让「被测提交」与「修复操作」混淆，报告 commit 校验失去意义。
- B 轨道关注的两点：**共享变量怎样处理**——direct 风格直接改目标行；macro 风格改 `DEPS` 定义，此时改动会波及所有引用该宏的目标，本样例只有一个目标所以安全，但这是已知限制，E9 会显式对照三种风格；**失败怎样保证原目录不变**——`validate()` 先 `copytree` 出 sandbox，源目录只在 `accepted=True` 时写入，且写入前后用字节比较记录 `source_unchanged`。

代价与覆盖范围：
- 代价：每次验证都要复制整个项目并重建 Git，样例小所以可接受；真实项目需要硬链接或 overlay。
- 覆盖范围：仅显式规则、`-O0/-O1/-O0 -DMODE=1` 三种 flags、两个翻译单元。隐式规则、多目标宏、复杂变量展开均不支持（`declarations()` 会抛 `UNSUPPORTED_*`）。

验证命令与实际证据：
- `python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v` → 8 passed，退出 0（`work/unit-tests-with-own.log`）
- E8 六步 `STEP_EXIT_CODE=0`，`work/e8-B-manual.OII7uo/steps/` 下 6 份日志
- 补丁前后源字节比对：`assert before==(p/'Makefile').read_bytes()` 通过
- 旧报告拒绝：`STALE_REPORT`，且源字节不变
