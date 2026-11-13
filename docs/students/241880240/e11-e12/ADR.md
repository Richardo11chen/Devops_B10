# ADR：集成接口决策

编号、日期、作者：ADR-E11E12-01 / 2026-11-13 / 陈奕澎（241880240）

问题：E11/E12 要求把 DRAFT、BuildChecker、EChecker、MDFixer 串成一条链，并把本组真实 C/Make 项目接入。参考实现假设：项目即仓库根、两个源文件 `main.c`/`helper.c`、程序名 `app`、输出 `1`、`CFLAGS=-O0`。本组真实项目只有一个源文件、程序名 `main`、输出 `v1`、`CFLAGS=-I.`，且位于仓库子目录 `e3/fixtures/mdfixer`。

候选方案：

1. **把真实项目复制到仓库根**，使其符合参考实现假设。——否决：会与仓库现有结构冲突，且「项目在子目录」是常见形态，迁就一次等于掩盖接口缺陷。
2. **新建一个符合假设的 C 项目**当作"真实项目"。——否决：新造的项目没有历史，与 `prepare` 生成的样例性质相同，手册明确「生成的双文件项目不计为外部真实项目验证」。
3. **描述文件 + 子目录字段**：项目根放 `.lab-project.json` 声明目标映射与验证参数，请求 JSON 增加 `subdir`。

采用方案与原因：方案 3。理由有三：现有 `lab.py` 的全部假设都能收敛到一份声明里；缺省值与原行为逐字一致，E8–E10 的 17 项测试无需改动即可通过；`subdir` 使真实的仓库结构（项目在子目录）得以保留，两个提交 SHA 仍指向本组仓库的真实历史。

输入输出字段：

- `.lab-project.json`：`targets[{object,source}]`、`program`、`build_target`、`allowed_flags`、`header`、`expected_output`、`header_edit{from,to}`、`header_output`。
- 请求 JSON 新增可选 `subdir`：只接受克隆内部的相对路径，越界或不存在时抛 `UNSUPPORTED_PROJECT`。

兼容性与测试：缺省值 `targets=[main.o←main.c, helper.o←helper.c]`、`program=app`、`expected_output=1`、`allowed_flags=[-O0,O1,-O0 -DMODE=1]`，与改前逐字等价。`test_contract.py` 新增 6 项：缺省等价、描述覆盖、按描述扫描、macro 风格补丁位置、subdir 越界拒绝、`STALE_REPORT` 错误码。

代价与已知限制：`allowed_flags` 目前是白名单，换成别的编译参数需显式声明（这是有意的——静默接受未知 flags 会让增量判定失真）。`validate()` 的 `header_edit` 采用「整串替换」，若目标头文件写法与声明不符会抛 `HEADER_EDIT_PATTERN_MISSING`，不会静默跳过。
