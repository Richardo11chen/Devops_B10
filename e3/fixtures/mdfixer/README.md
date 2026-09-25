# fixtures/mdfixer — MDFixer 固定输入（成员D）

> **负责人：成员D（Song Chengxuan）** ｜ 本目录是 MDFixer 服务的**固定输入样例**（课程人工构造，`ORACLE`），
> 用于演示一个「Missing Dependency（MD）」缺陷及其参考修复。

## 1. 这是什么

一个最小单文件 C 项目：`main.c` 里 `#include "config.h"` 并打印 `MESSAGE`，但 `Makefile` 的
`main.o` 规则**漏写了 `config.h` 这个先决条件**。后果：修改 `config.h` 后 `make` 判定
`main.o` 仍是最新，不触发重编，程序继续打印旧值。

MDFixer 的输入是「固定 MD 报告 + 同一源码版本的 Makefile + 构建/行为测试 + 预期声明风格」四件套，
本目录把这四件套连同参考补丁一起给出。

> 所有人工构造的预期结果均显式标注 `ORACLE`，与 `e3/evidence/` 下的真实运行日志区分开。

## 2. 文件清单

| 文件 | 作用 |
|------|------|
| `main.c` | 源文件，`#include "config.h"`，`printf("%s\n", MESSAGE)` |
| `config.h` | 头文件，`#define MESSAGE "v1"`（基线值） |
| `Makefile` | 带 MD 缺陷的构建脚本（`main.o: main.c` 缺 `config.h`） |
| `md_report.json` | 固定 MD 报告（单条 `MISSING`，`detector=INSTRUCTOR_ORACLE`） |
| `reference.patch` | 参考修复（Target 风格：`main.o` 规则补 `config.h`） |
| `README.md` | 本说明 |

## 3. 固定输入四件套

### 3.1 固定 MD 报告（`md_report.json`）

单条 `MISSING` 发现，`target=main.o`、`dependency=config.h`，`detector=INSTRUCTOR_ORACLE`、
`confidence=1.0`、`fix_strategy=append-dep-to-prerequisite`。结构对齐 A 组 `md_report.sample.json`
的 `ERROR_REPORT` 外壳（`report_id` / `producer_service=BUILDCHECKER` / `findings[]` / `summary` /
`provenance` / `human_review`），`target_commit` 回填本仓库 C0 的完整 SHA（见第 7 节）。

### 3.2 同一源码版本的 Makefile

```makefile
CC      = gcc
CFLAGS  = -I.

main: main.o
	$(CC) -o $@ $^

main.o: main.c            # ← MD 所在：漏了 config.h
	$(CC) $(CFLAGS) -c $< -o $@

.PHONY: check clean
check: main
	./main

clean:
	rm -f main.o main main.d
```

### 3.3 构建命令与行为测试

- **构建命令**：`make`（对应 repair 契约的 `build.command`）。
- **行为测试**：`make check`（对应 `verify_command`），跑 `./main`，人肉核对输出等于当前 `MESSAGE` 值。

### 3.4 预期声明风格（四种）

| 风格 | 写法 | 特点 |
|------|------|------|
| **Target** | `main.o: main.c config.h` | 直接写死依赖；最直观、改动最小，`reference.patch` 采用 |
| **Macro** | `MAIN_DEPS = main.c config.h`<br>`main.o: $(MAIN_DEPS)` | 依赖抽变量；多处共用时少重复 |
| **Hybrid** | `HDRS = config.h`<br>`main.o: main.c $(HDRS)` | 源文件写死 + 头文件走变量 |
| **Implicit** | `%.o: %.c` + `$(CC) -MMD -MP -c $< -o $@` + `-include main.d` | 不手写头依赖，gcc 自动生成 `.d`；依赖 gcc/clang 的 `-MMD`，且 `.d` 是需清理的生成物 |

`reference.patch`（Target 风格）：

```diff
--- a/Makefile
+++ b/Makefile
@@ -4,7 +4,7 @@ CFLAGS  = -I.
 main: main.o
 	$(CC) -o $@ $^
 
-main.o: main.c
+main.o: main.c config.h
 	$(CC) $(CFLAGS) -c $< -o $@
 
 .PHONY: check clean
```

## 4. 修复验证六步（证据见 `e3/evidence/`）

| 步 | 命令 | 预期 | 证据文件 |
|----|------|------|----------|
| 1 修复前 MD | `make clean && make && ./main`；改 `config.h` v1→v2；`make && ./main` | `make` 报 "up to date"，`./main` 仍 v1 | `mdfixer-before-fix.log` |
| 2 检查补丁 | `git apply --check reference.patch` | 退出 0，无输出 | `mdfixer-apply-check.txt` |
| 3 应用补丁 | `git apply reference.patch` + `git diff` | `main.o` 规则出现 `config.h` | `mdfixer-apply.log` |
| 4 干净重建 | `make clean && make && ./main` | 重建，`./main` → v2 | `mdfixer-after-fix.log` |
| 5 不 clean 重建 | 改 `config.h` v2→v3；`make && ./main` | 出现 `gcc -c` 行，`./main` → v3 | `mdfixer-no-clean-rebuild.log` |
| 6 结论 | （原则） | 第 4 步不能证明 MD 已修（clean 会强制全量重建）；第 5 步才是决定性的 | 见本节末 |

**第 5 步为什么是关键**：修复后 `main.o` 的先决条件含 `config.h`，改 `config.h` 使其 mtime 新于
`main.o`，make 才会重跑编译配方。证据三重：`make` 输出出现 `gcc -I. -c main.c -o main.o`（而非
"up to date"）、`./main` 输出由 v2 变 v3。与第 1 步（同样的改动却 "up to date" + 旧值）形成对照。

## 5. 无效候选三步（反向验证）

证明 fixture 不是「怎么跑都坏」的假样例，且能区分「真修复」与「坏补丁」。

| 步 | 做法 | 证据文件 |
|----|------|----------|
| 原始副本可构建 | `make clean && make && make check` 全通过，`./main` → v1 | `mdfixer-invalid-candidate-baseline.log` |
| 注入失败命令 | 在 `main` 配方插入 `false`，`make clean && make` 非零退出（`Error 1`） | `mdfixer-invalid-candidate-fail.log` |
| 恢复后通过 | `git checkout -- Makefile` 后重建测试再次通过 | `mdfixer-invalid-candidate-restore.log` |

## 6. `.d` 文件与 `-include main.d`（Implicit 风格实证）

用隐式规则 Makefile（`Makefile.implicit`，见 3.4 Implicit 写法）验证「不手写依赖也能自动重建」：

1. `make -f Makefile.implicit` → `gcc -MMD -MP -c main.c -o main.o` 生成 `main.d`。
2. `cat main.d` → 内容 `main.o: main.c config.h`（gcc `-MMD` 自动算出头依赖，`-MP` 补 phony）。
3. 改 `config.h` v1→v4；`make -f Makefile.implicit`（不 clean）→ 自动重编，`./main` → v4。

证据：`mdfixer-implicit-dfile.log`、`mdfixer-implicit-rebuild.log`。

## 7. 基线四要素（版本与环境）

| 要素 | 值 |
|------|-----|
| 固定项目版本 | C0 = `16a1490984aaa3904a80b6b433dfbed47d86a6ce`（MD 潜伏）；C1 = `f58876392b157eb121f9bc2a30ca0566e69db4c2`（Target 修复）。真实提交见 `work/mdfixer-demo/`（嵌套仓库，外层 `.gitignore` 排除） |
| 运行环境 | Ubuntu 22.04（WSL2），gcc 11.4.0，GNU Make 4.3 |
| 本次修改/故障 | `Makefile` 的 `main.o` 规则漏声明 `config.h` 先决条件 |
| 预期输出及依据 | 修复前改头文件不重建（旧值）；修复后改头文件自动重建（新值）——依据是 make 的 mtime 先决条件比较 |
| 可重新执行命令 | 见第 4/5/6 节各步命令，均可复制重跑 |

## 8. 相互检查

- [x] 别人能按 README 跑起来吗？→ 复制 `main.c`/`config.h`/`Makefile` 到任意 Linux 环境即可复现。
- [x] 人工答案（ORACLE）和实际日志分清楚了吗？→ ORACLE 仅在 `md_report.json` / `reference.patch` / 本 README 的「预期」栏；实际输出全部在 `e3/evidence/`。
- [x] 预期结果能说明依据吗？→ 依据 = make 的 mtime 先决条件比较 + gcc `-MMD` 依赖推导。
- [x] 失败记录能定位到具体版本吗？→ 每条证据头部记录 `commit=16a1490...`。
