# ADR：集成接口决策

编号、日期、作者：ADR-E11E12-241880171 / 2026-11-16 / 张少逸 241880171

问题：E11–E12 要把 B 轨道 DRAFT（构建环境）与 MDFixer（补丁修复）串成可复用的异步任务接口，A/B 两侧产物要能互验。

候选方案：
1. 每阶段独立命令行脚本，人工串接。
2. 单一管道 pipeline.py 串行执行 draft/full-check/incremental-check/repair/recheck，配 versioned envelope 与 job_id/trace_id。
3. 拆成微服务，各组件独立部署。

采用方案与原因：方案 2。单一管道保持阶段产物可追溯，envelope 带 schema_version/commit/status 便于消费方核对；job_id/trace_id 贯穿所有阶段，A/B 通过同一套异步 API（POST /v1/jobs）交换产物，比人工串接更可复现。

输入输出字段：
- 请求：idempotency_key、input(mode/repo/base/target/candidate/expected_output/build_timeout/subdir)
- 输出 envelope：schema_version、job_id、trace_id、kind、commit、status、data、artifacts
- 阶段产物用 artifact://job编号/相对路径 定位，附带 SHA256 供消费方核对

兼容性与测试：
- 沿用 E8–E10 的 main.c/helper.c 显式 Make 接口，通过 .lab-project.json 描述符扩展 targets/program/allowed_flags。
- 契约测试 test_contract.py 覆盖：envelope 校验（旧 commit 拒绝 STALE_REPORT、schema 不符、上游 FAILED 拒绝、产物类型不符）、幂等（同键同请求同 job、同键改 target 409）、产物哈希校验、subdir 越界拒绝。
- 自主测试：Student241880171 验证 macro 风格补丁落在 DEPS 定义行且 main.o: $(DEPS) 一字不变。
