# ADR：集成接口决策

编号、日期、作者：ADR-241880237-01 / 2026-11-17 / 宋丞轩 241880237

问题：
E11-A、E11-B、E12 三段服务之间如何交接 MD 报告与候选补丁，才能既让下游独立复验，又不把上游状态耦合进来。

候选方案：
1. 同进程函数调用：三段写在一个进程里直接传对象。最省事，但服务重启即丢，且无法体现"独立服务"的边界。
2. 共享数据库（SQLite/Postgres）存报告与补丁 blob：查询方便，但要额外维护 schema 与迁移，跨机复验还得导出。
3. 文件系统 artifact + JSON envelope（选中）：每段把结构化结果写成 JSON，二进制与补丁作为文件，通过 `artifact://<job_id>/<相对路径>` 引用，并附 `sha256`。

采用方案与原因：
选 3。理由有三点：①复验只需文件，不依赖服务存活，重启后仍能重放；②`sha256` 让"内容有没有被改"可判定，比数据库行更难被悄悄篡改；③阶段产物天然就是可归档证据，交作业/复盘直接打包。
代价也说清楚：需要约束路径（只允许 `data/` 与任务输出目录内，拒绝 `..` 越界）、需要 envelope 校验（schema 版本、commit 是否过期），磁盘占用随任务数线性增长，需要人工清理策略。

输入输出字段：
envelope：`schema_version`、`job_id`、`trace_id`、`kind`、`commit`、`status`、`data`、`artifacts[]`（`uri`、`sha256`、`bytes`）。
`data.findings[]`：`type`（MISSING/REDUNDANT）、`target`、`dependency`、`evidence[]`、`declared_dependencies`。
补丁计划：`target`、`dependency`、`style`（direct/macro/mixed）。

兼容性与测试：
`check_envelope` 强制校验 `schema_version`、`commit` 与期望一致、`kind` 匹配、`status` 为 SUCCEEDED，任一不符即失败（旧 commit 报 `STALE_REPORT`）。
`test_contract.py` 19 项覆盖：envelope 四类拒绝、artifact 哈希与相对 URI、已存在结果不覆盖、幂等同 key 同 job、仓库越界拒绝、macro/mixed 补丁位置、以及本人的同目标双 MD 顺序稳定性。
