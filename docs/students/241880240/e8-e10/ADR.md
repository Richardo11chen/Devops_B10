# 决策记录

背景与约束：
E8/E9 要在「不污染被测项目」的前提下，从固定 MD 报告生成候选补丁。约束有三：报告必须绑定具体提交；只处理 MISSING、不动 REDUNDANT；生成阶段不写回源文件——是否接受留给 E10 的构建/测试/重检判定。

选择与替代方案：
- **选择**：`patch()` 只做文本追加，返回统一 diff 与修改计划，不落盘；`validate()` 在副本 sandbox 中应用并逐项判定，全部通过才把 Makefile 字节写回。
- **替代方案 1**：`sed` 原地修改。否决——生成失败会污染输入，且无法把「生成」与「接受」分离。
- **替代方案 2**：在样例内部 Git 上建分支隔离。否决——内部 Git 是受测对象，建分支会让「被测提交」与「修复操作」混淆，报告 commit 校验失效。
- **B 轨道的共享变量问题**：direct 直接改目标行；macro 改 `DEPS` 定义，此时改动会波及所有引用该宏的目标。本样例只有一个目标所以安全，但这是已知限制，E9 用三种风格并排对照把它显式化。真正的解需要依赖图分析，超出教学范围。
- **失败时如何保证原目录不变**：`validate()` 先 `copytree` 出 sandbox，源目录只在 `accepted=True` 时写入，写入前后用字节比较记录 `source_unchanged`。

E9 追加的决策：补丁生成的幂等性。
- 背景：同一 MISSING 在报告中重复出现（合并多份报告、或人工编辑）时，原实现会重复追加；对同一报告重复调用 `patch()` 也一样。
- 选择：在追加前先把目标行按已有变量展开，若依赖已存在则跳过。
- 替代方案：在 `scan()` 出口对 findings 去重。否决——那条路径之外仍可能传入手写报告，守卫放在 `patch()` 才能覆盖所有调用者。
- 代价：每次追加多一次变量解析（`re.findall` + 至多 8 轮宏展开），对样例规模可忽略。覆盖范围：只处理「依赖已在目标行（含宏展开）中」这一种情况；若依赖是通过隐式规则提供，仍不受支持（`declarations()` 会先抛 `UNSUPPORTED_*`）。

验证命令与实际证据：
- `python3 -m unittest discover -s labs/e8e10 -p test_profile.py -v` → 9 passed，退出 0（`work/unit-tests-e9-own.log`）
- E8 六步 `STEP_EXIT_CODE=0`（`work/e8-B-manual.OII7uo/steps/`）
- E9 四步 `STEP_EXIT_CODE=0`，三个 `STYLE_PASS`（`work/e9-B-manual.HaZcxJ/steps/`）
- 修复前后三份 patch 逐字节一致：`diff work/e9-B-manual.AmkL0w/{direct,macro,mixed}.patch work/e9-B-manual.HaZcxJ/...` 无输出
- 变异验证：删除幂等守卫后 `test_duplicate_missing_entries_added_once` 失败（`2 != 1`）
