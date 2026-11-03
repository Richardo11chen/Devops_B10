# 决策记录

背景与约束：E8-B轨要求基于固定MD报告生成候选补丁并验证身份前置检查；服务器仅2 vCPU/3.5GiB，四人共用，镜像构建需串行；样例项目的声明修复不得在未通过E10质量门前写回源文件。
选择与替代方案：选择手工分步路线（lab_new_run + lab_python 逐步执行）而非 `run_lab.py e8 --track B --out ...` 一键入口，以保留每一步的独立日志与判断点；身份检查验证采用"复制报告并把commit改为40个0"的方式主动触发STALE_REPORT，而不是等待错误补丁进入构建。自主任务方向选择"未知目标拒绝"（手册第9步第二个选项），因为第一个方向（REDUNDANT-only 不产生删除）已由同学241880240在PR #18中贡献并合入main，重复该用例无增量价值。
A：缓存何时失效、配置身份如何绑定——本阶段未做增量缓存改动（E9-A范围）；B：共享变量怎样处理、失败怎样保证原目录不变——本阶段补丁为direct风格（目标行直接追加），未涉及$(DEPS)变量展开（E9-B范围）；拒绝路径（STALE_REPORT/UNSUPPORTED_TARGET）经验证均不触碰源文件字节。
代价与覆盖范围：分步路线耗时长于一键入口，但获得了8个步骤的独立 STEP_EXIT_CODE 日志，排错粒度更细；固定MD输入覆盖 direct 风格与MD/RD两类发现，未覆盖变量/混合风格与远程报告接口。
验证命令与实际证据：OUT=work/e8-B-manual.0XgyC8；$OUT/steps/ 下8份日志全部 STEP_EXIT_CODE=0；$OUT/expected-failure.json 记录 STALE_REPORT；容器内 unittest discover → Ran 10 tests OK（work/unit-tests-20261103-104559.log）。
