# fixtures/draft — DRAFT 样本（占位）

> **负责人：成员C** ｜ 组长只建占位，**本目录内容由成员C填写**。

## 本目录放什么

**课程人工样例源码**，用于 DRAFT 服务的测试基线。人工构造的预期结果必须显式标注 `ORACLE` 来源，与真实运行日志分开。

## 交付要求（详见 `e2/issue_draft.md` 的成员C Issue）

必须包含两个候选：

| 候选 | 基础镜像 | 预期结果 |
|------|----------|----------|
| `Dockerfile.broken` | `python:3.13-slim`，直接 `RUN make` | 非零退出，日志出现 `make: not found` |
| `Dockerfile.reference` | 安装 `gcc make libc6-dev` | 构建成功，容器内输出 `hello E3` |

两层成功判据缺一不可：**第一层**构建命令退出码 0 且生成预期可执行文件；**第二层**运行 README 约定测试，检查退出码与预期输出（失败也要记录）。

## 要保存的证据

Dockerfile diff、build 退出码、构建日志、镜像 ID → 写入 `e3/evidence/`。

## 基线四要素

提交前确认已写清：固定版本与环境、本次修改/故障是什么、预期输出及依据、可重跑命令。
