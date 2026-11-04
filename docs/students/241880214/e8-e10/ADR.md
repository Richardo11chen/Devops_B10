# 决策记录

背景与约束：B 轨道要在固定 MD 报告下，为 GCC 本地头文件项目生成最小 Makefile 候选 Patch。报告必须绑定内层 Git commit；候选只能在验证沙箱中落地，失败不得改写原项目。可用信息是声明图、实际 GCC 图、固定报告、候选 Patch 和验证证据，不接远程 MDFixer 服务。

选择与替代方案：

A：缓存何时失效、配置身份如何绑定。
- 选择：`scan()` 在输入或头文件变化时刷新目标；`patch()` 强制 `report['commit']==git rev-parse HEAD`，不匹配抛 `STALE_REPORT`。
- 替代：不校验 commit，直接按报告改文件。代价是旧报告可能改错输入，无法证明报告与当前项目同源。

B：共享变量怎样处理、失败怎样保证原目录不变。
- 选择：direct 修改目标依赖行；macro 修改 `DEPS` 定义（所有引用 `$(DEPS)` 的目标共享影响）；mixed 保留 `$(HEADERS)` 并在目标行追加 `config.h`。`validate()` 在 sandbox 中应用 Patch、构建、测试并做头文件变化重检，全部通过才写回；否则回滚并保持源字节。
- 替代：统一在目标行追加依赖，会忽略声明风格并可能与宏冲突；或直接改源目录，坏候选会污染项目。

代价与覆盖范围：只支持显式 Make 依赖、`-O0`/`-O1`/`-O0 -DMODE=1` 和单阶段项目；不支持隐式规则、模式规则和复杂 Make 语法。macro 修改变量可能扩大跨目标影响。扩展方向为声明图/DIS、`.d` 文件、LLM 路径和 BuildChecker 全量重检。

验证命令与实际证据：E8 `work/e8-B-manual.LJ7yTX`（6/6 exit 0，`candidate.patch`、`expected-failure.json=STALE_REPORT`）；E9 `work/e9-B-manual.XPBRCO`（4/4 exit 0，三份 patch/plan、`apply-demo/`）；E10 `work/e10-B-manual.th8XOI`（7/7 exit 0，`reject-test`/`accept`/`reject-patch`，`results.csv` 三行 True，`gate.json` rows=3，BuildChecker 无 MISSING）；单元测试 `work/unit-tests-20261104-204133.log`（`Ran 12 tests ... OK`）。
