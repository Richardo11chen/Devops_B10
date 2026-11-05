# 决策记录

背景与约束：E8-E10三阶段共用同一镜像与仓库，服务器仅2 vCPU/3.5GiB需串行构建；B轨核心约束=候选未经E10质量门不得写回源目录；PR #20曾被CHANGES_REQUESTED（artifact未提交、报告步骤数/测试数不准），需一次性修正。
选择与替代方案：三阶段均采用手工分步路线（lab_new_run+lab_python逐段执行）而非一键run_lab入口，保留每步STEP_EXIT_CODE日志；E8身份检查用"commit改40个0"主动触发STALE_REPORT；E9按direct→macro→mixed顺序对照三份diff；E10按手册顺序执行拒绝→接受→坏Patch三次validate并保存两份源字节对照（source-before/source-after-accept）。自主测试方向：E8选"未知目标拒绝"（因REDUNDANT-only已被241880240合入）、E9选"macro补丁只动DEPS定义"（共享变量影响）、E10选"能构建但仍存在MD的候选被拒"（extra.h错加用例）。
A：缓存何时失效、配置身份如何绑定——本轨道未涉及增量缓存改动（A轨范围），身份绑定=报告commit必须等于project HEAD，STALE_REPORT拒绝路径实测不触碰源字节；B：共享变量怎样处理、失败怎样保证原目录不变——macro风格修改集中在DEPS定义行、目标引用不动（StudentE9BExtra断言）；失败（测试失败/坏Patch）时validate在sandbox进行、rollback=True且source_unchanged=True（E10三案例与StudentE10BExtra实证）。
代价与覆盖范围：分步路线耗时多但排错粒度细；固定输入未覆盖隐式规则、模式规则与跨目标共享变量的语义扩散分析（已在结论标注为扩展方向）。
验证命令与实际证据：E8 OUT=work/e8-B-manual.0XgyC8（6步全0）；E9 OUT=work/e9-B-manual.UpcRHg（4步全0）；E10 OUT=work/e10-B-manual.UvOzYM（7步全0，results.csv三行True，gate.json rows=3）；unittest discover → Ran 17 tests OK（work/unit-tests-20261105-091951.log）。
