# fixtures/mdfixer — MDFixer 固定输入（占位）

> **负责人：成员D** ｜ 组长只建占位，**本目录内容由成员D填写**。

## 本目录放什么

**课程人工样例源码**，用于 MDFixer 服务的固定输入。人工构造的预期结果必须显式标注 `ORACLE` 来源，与真实运行日志分开。

## 交付要求（详见 `e2/issue_draft.md` 的成员D Issue）

固定输入四件套：

1. 固定 MD 报告（`main.o` 缺 `config.h`）
2. 同一源码版本的 `Makefile`
3. 构建命令与行为测试
4. 预期声明风格

**四种声明风格**：Target、Macro、Hybrid、Implicit。参考 Patch 至少给出 **Target** 风格，并说明其他风格的差异。

**隐式规则与 `.d` 文件**：`%: %.c` 使用 `$(CC) -MMD -MP -c $< -o $@`，`-include main.d`；需检查 `.d` 内容，以及再次修改头文件时的行为。

## 修复验证步骤（逐条留证）

- 修复前：只改头文件，仍输出旧值
- `git apply --check reference.patch`
- `git apply reference.patch`
- `make clean && make` → 输出新值
- 再改头文件、**不 clean**，应自动重建
- **不能只靠 `make clean` 成功就证明 MD 已修好**

## 无效候选

原始副本可构建测试；候选修改加入失败命令后 `make` 非零退出；恢复原 `Makefile` 后构建和测试再次通过。

## 证据去向

实际命令与观察结果 → `e3/evidence/`；真实 Git 提交与参考修复 → `work/`。
