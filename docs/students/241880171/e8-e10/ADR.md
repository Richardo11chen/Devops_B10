# 决策记录

## 背景与约束

本次 E8—E10 按 B 轨道执行，目标是在受限 Make 配置下完成三件事：E8 生成固定 MD 报告与候选补丁；E9 对 direct / macro / mixed 三种声明风格分别生成补丁；E10 把补丁生成与接受分开，验证“拒绝、接受、回滚”三条路径，并保证失败时源目录不被破坏。

约束：

- 只在 labs/e8e10/lab.py 和 labs/e8e10/test_profile.py 范围内改动，不改动参考实现以外的课程文件；
- 所有实验在 course-e8e10:241880171 镜像内运行，禁网，通过 lab_python 挂载仓库到 /course；
- 每个实验独立新建 OUT，不复用上一次 OUT，避免证据覆盖；
- 失败路径必须和成功路径一样有可核对证据，不能只记录“通过”。
## 选择与替代方案

### B 轨道 vs A 轨道

选择 B 轨道。A 轨道侧重从真实 BuildChecker 执行中建立历史图并做增量复用；B 轨道侧重“固定 MD 报告 → 候选补丁 → 质量验证”的闭环，更贴近“补丁是否可接受”这一交付问题。B 轨道的输出直接对应 fixed-md-report.json、candidate.patch、validation.json、results.csv、gate.json，便于在 PR 中逐项核对。

替代方案：选 A 轨道可以更早接触 BuildChecker 的真实 trace，但 E10 的动态重检仍要回到“接受/拒绝”判定，B 轨道把这条路径提前到 E8/E9/E10 全程。
### 共享变量怎样处理（E9）

三种声明风格分别处理：

- direct：直接修改 main.o 的目标依赖行，增加 config.h。最直接，但若该目标行引用了共享变量，修改可能扩大影响范围。
- macro：修改 DEPS 变量定义，增加 config.h，目标行仍写 $(DEPS)。集中管理，但所有引用 DEPS 的目标都会受影响。
- mixed：保留 $(HEADERS) 宏引用，只修改 main.o 的目标行。折中，既保留宏结构，又把影响限制在单个目标。

选择依据：本次样例中 main.o 依赖 $(DEPS)，helper.o 不引用同一变量，因此 macro 与 mixed 在本样例里等价；若共享变量被多个目标引用，macro 会扩大影响，direct/mixed 更安全。最终以 patch-plan.json 的 style 字段记录选择，便于复核。
### 失败怎样保证原目录不变（E10）

E10 把 validate() 设计成“沙箱内尝试、成功才写回”：

1. patch_applies：git apply --check 先检查补丁格式与上下文；
2. build：在沙箱副本中构建，失败则记录 COMMAND_FAILED；
3. test：运行程序并比较预期输出，fail_test=True 时故意把预期改成 99，制造测试失败；
4. header_change：修改沙箱中的 config.h，确认增量扫描能重新编译 main.o；
5. no_missing：重检后无 MISSING。

任一项为 False，accepted=False，rollback=True，source_unchanged=True，源 Makefile 字节不变。只有全部为 True 才写回源目录。

替代方案：直接写回再回滚。风险是回滚失败会污染源目录；沙箱方案把失败隔离在副本内，源目录只在成功时被修改。

### 验证顺序（E10）

选择“先错误测试拒绝 → 正常接受 → 坏 Patch 拒绝”：

- 先证明拒绝路径有效，避免“接受路径能跑但拒绝路径失效”的假阳性；
- 再证明接受路径在正确预期下写回源目录；
- 最后证明接受后的版本仍受保护，坏 Patch 不会破坏已接受的 Makefile。

替代方案：先接受再拒绝。风险是若拒绝路径有 bug，已接受的源目录可能被后续坏 Patch 破坏，证据顺序也不利于定位问题。

## 代价与覆盖范围

- 覆盖范围：E8 覆盖 MD 报告、候选补丁、STALE_REPORT 拒绝；E9 覆盖 direct/macro/mixed 三种声明风格；E10 覆盖错误测试拒绝、正常接受、坏 Patch 拒绝三条路径，并用真实 BuildChecker 交叉核对。
- 未覆盖：隐式规则、复杂 Make 语法、跨目标共享变量的完整影响分析。这些在 E9 结论中明确标为“需要扩展分析”，不在本次参考路线内。
- 代价：每个实验独立新建 OUT，证据目录较多；沙箱方案在 E10 多一次构建与重检，耗时略高，但换来源目录在失败时不被破坏。
- 测试：原包 9 项 + 新增 3 项（StudentE8B、StudentE9B、StudentE10B）= 12 项，全部通过。

## 验证命令与实际证据

E8：$E8_OUT 下 9 项齐套，steps/ 7 份日志全部 STEP_EXIT_CODE=0；expected-failure.json 记录 STALE_REPORT，源 Makefile 字节未变。

E9：$E9_OUT 下 direct/macro/mixed 三个项目与三份 patch/plan 齐套，apply-demo 验证 macro.patch 可应用，steps/ 4 份日志全部 STEP_EXIT_CODE=0。

E10：$E10_OUT 下 results.csv 三行 passed=True，gate.json passed=true rows=3，recheck-buildchecker/findings.json 无 MISSING；AFTER_REJECTION_CMP_EXIT=0。

单元测试：Ran 12 tests，OK，TEST_EXIT_CODE=0。
