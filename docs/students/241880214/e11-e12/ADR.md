# ADR：集成接口决策

编号、日期、作者：ADR-E11E12-001 / 2026-11-16 / 孙正奇 241880214

问题：E11/E12 要把 DRAFT、BuildChecker、EChecker、MDFixer 串成可复验的异步任务接口，同时保证报告 commit 绑定、产物哈希、幂等键、失败回滚和真实项目适配。

候选方案：

- A：单进程直接调用四个组件，不暴露 API。实现简单，但无法满足 A/B 联调、job_id/trace_id、产物引用和异步查询。
- B：统一 envelope + 异步 job API + 四个组件适配器；每个阶段保存 artifact URI/SHA256，消费前校验 commit 和哈希；采用。
- C：只跑固定样例，不接真实项目。会缺少真实数据与 `subdir` 适配，不满足验收。

采用方案与原因：采用 B。统一 schema `e11e12-1`；每份报告带 `job_id`、`trace_id`、`kind`、`commit`、`status`、`data`、`artifacts`；`check_envelope` 校验 schema、commit、status 和 kind，`load_artifact` 校验 SHA256；`Store` 用 idempotency_key 做幂等，同键改输入返回 `IDEMPOTENCY_CONFLICT`。DRAFT 复用 `lab.py` 的两轮构建，BuildChecker 用 `full_check`，MDFixer 只修 MD、保留 RD；`validate` 在 sandbox 中应用补丁、构建、测试、修改头文件后再构建，全部 checks 通过才写回源目录，否则回滚并保持源字节。真实项目通过 `.lab-project.json` 的 targets/flags/header 和请求中的 `subdir` 适配。

输入输出字段：

- `POST /v1/jobs`：`idempotency_key`、`input{mode,repo,base,target,candidate,fixed_report,expected_output,build_timeout,subdir}` → 202 `{job_id,status,request_hash}`。
- `GET /v1/jobs/{job_id}`：状态 `QUEUED/RUNNING/SUCCEEDED/FAILED/TIMED_OUT`、`trace_id`、`error`。
- `GET /v1/jobs/{job_id}/artifacts`：阶段清单、`artifact://job编号/相对路径`、SHA256。
- `GET /v1/jobs/{job_id}/files/{相对路径}`：文件内容及 `X-Content-SHA256`。

兼容性与测试：契约基线 16 项 + 本人 mixed 1 项 = 17 项；E11-A、E11-B、E12 固定样例、E12 真实项目四条链均 SUCCEEDED；API 实测 health、提交、轮询、产物下载哈希一致；相同幂等键返回同一 job，同键改 target 返回 409；旧 commit `STALE_REPORT`、越界子目录、哈希不一致均被拒绝；已有证据目录不会被覆盖。
