# fixtures/draft — DRAFT 测试基线与候选样本

> **负责人：成员C** ｜ 负责 E3 DRAFT 样本准备与 Docker 构建证据记录。

本目录包含用于 DRAFT 服务的测试基线项目（Tiny Greeting）及两个对比候选 Dockerfile，提供可核验的两层成功判据、预期答案（ORACLE）与实际运行证据。

---

## 1. 被测项目概述（Tiny Greeting）

- **源码**：[`main.c`](main.c)（最小 C 语言程序，输出 `hello E3\n`）
- **构建脚本**：[`Makefile`](Makefile)（提供 `all` 与 `clean` 目标，默认构建生成可执行文件 `hello`）
- **两层判据目标**：
  1. **第一层（编译构建）**：执行 `make`，进程退出码为 `0`，且当前目录下生成可执行文件 `hello`。
  2. **第二层（功能验证）**：执行 `./hello`，进程退出码为 `0`，且标准输出精确匹配 `hello E3`。

---

## 2. 基线四要素说明

| 要素 | 说明 |
| :--- | :--- |
| **1. 固定版本与环境** | - **宿主环境**：Ubuntu 26.04.1 LTS (WSL2), x86_64, Linux kernel 6.6.87.2-microsoft-standard-WSL2<br>- **Docker 版本**：`Docker 29.1.3` (build 29.1.3-0ubuntu4.1)<br>- **基础镜像**：`python:3.13-slim` (`sha256:8d9d0b8bcf6506481eae4907c18f5e3e7902e629f5f6d684f9e7c32e85e3ddf0`)<br>- **编译器与工具**：gcc 14.2.0 / GNU Make 4.4.1 (Debian 镜像内安装版本)<br>- **固定基准 Commit**：`4090bc4` (基于 B10 仓库 main 分支基线) |
| **2. 修改与故障特征** | - **Broken 候选**：在缺乏 C 编译工具链（无 gcc、make、libc-dev）的 Python 精简镜像中直接调用 `RUN make`，触发命令缺失故障。<br>- **Reference 候选**：在执行构建前，通过 `apt-get` 补充安装 `gcc make libc6-dev` 工具链，完成修复。 |
| **3. 预期输出与依据 [ORACLE]** | - **Broken 候选 [ORACLE]**：预期第 4 步 `RUN make` 失败，进程非零退出（退出码 `127`），错误日志定位到 `/bin/sh: 1: make: not found`。<br>- **Reference 候选 [ORACLE]**：预期镜像构建成功（退出码 `0`），生成包含可执行文件 `hello` 的容器镜像；容器启动运行 `./hello` 输出精确为 `hello E3`，退出码 `0`。 |
| **4. 可重新执行命令** | 见下文复现操作指南，任何成员或下游按命令均可原样重跑验证。 |

---

## 3. 候选样本对比

### 候选 1：`Dockerfile.broken`（失败候选）
- **文件**：[`Dockerfile.broken`](Dockerfile.broken)
- **内容**：
  ```dockerfile
  FROM python:3.13-slim
  WORKDIR /work
  COPY main.c Makefile ./
  RUN make
  CMD ["./hello"]
  ```
- **特征**：预期失败样本，记录真实的非零退出日志，为 DRAFT 服务的错误诊断与迭代提供初始输入，**切勿手工修复**。

### 候选 2：`Dockerfile.reference`（参考成功）
- **文件**：[`Dockerfile.reference`](Dockerfile.reference)
- **内容**：
  ```dockerfile
  FROM python:3.13-slim
  WORKDIR /work
  RUN apt-get update && \
      apt-get install -y --no-install-recommends \
      gcc make libc6-dev && \
      rm -rf /var/lib/apt/lists/*
  COPY main.c Makefile ./
  RUN make
  CMD ["./hello"]
  ```
- **特征**：补充必要构建工具链，完整满足两层成功判据。
- **差异记录**：查看差异补丁文件 [`e3/evidence/dockerfile.diff`](../../evidence/dockerfile.diff)。

---

## 4. 复现与验证命令

在 Linux (Ubuntu 24.04 WSL2) 终端中进入本目录执行：

### 步骤 A：验证本地代码编译与功能（基准自测）
```bash
cd e3/fixtures/draft
make clean
make
./hello
# 预期输出：hello E3
make clean
```

### 步骤 B：构建失败候选（Broken）并捕获证据
```bash
docker build -f Dockerfile.broken -t b10-draft-broken:latest .
echo $?
# 预期输出：构建失败，输出 make: not found，退出码为 127
```

### 步骤 C：构建参考成功候选（Reference）并完成双层验证
```bash
# 第一层判据：构建镜像
docker build -f Dockerfile.reference -t b10-draft-reference:latest .
echo $?
# 预期输出：构建成功，镜像生成，退出码为 0

# 第二层判据：运行容器进行功能验证
docker run --rm b10-draft-reference:latest
echo $?
# 预期输出：精确输出 hello E3，退出码为 0
```

---

## 5. 证据文件清单（`e3/evidence/`）

真实运行日志与证据保存在 [`e3/evidence/`](../../evidence/) 目录下，遵循不使用时间戳的场景化命名：

| 证据文件 | 说明 | 对应判定 |
| :--- | :--- | :--- |
| [`dockerfile.diff`](../../evidence/dockerfile.diff) | Broken 与 Reference 两份 Dockerfile 的 `diff -u` 差异 | 变更分析 |
| [`draft-broken-build.log`](../../evidence/draft-broken-build.log) | Broken 候选的构建控制台日志，含 `make: not found` 报错定位 | 预期失败证据 |
| [`draft-broken-exit.txt`](../../evidence/draft-broken-exit.txt) | Broken 构建退出码（`127`） | 退出码证据 |
| [`draft-reference-build.log`](../../evidence/draft-reference-build.log) | Reference 候选的完整构建日志，通过第一层判据 | 第一层判据（构建） |
| [`draft-reference-exit.txt`](../../evidence/draft-reference-exit.txt) | Reference 构建退出码（`0`） | 退出码证据 |
| [`draft-image-id.txt`](../../evidence/draft-image-id.txt) | 构建产出的 Docker 镜像记录与镜像 ID | 镜像证据 |
| [`draft-verify.log`](../../evidence/draft-verify.log) | 容器运行 `./hello` 的标准输出（`hello E3`） | 第二层判据（功能） |
| [`draft-verify-exit.txt`](../../evidence/draft-verify-exit.txt) | 容器运行功能验证退出码（`0`） | 退出码证据 |

---

## 6. 相互检查自检

- [x] 别人能按 README 运行吗？ $\rightarrow$ 步骤清晰，输入输出与退出码完整标明。
- [x] 人工答案和实际日志分清了吗？ $\rightarrow$ 预期结果显式标有 `[ORACLE]`，日志存于 `evidence/` 独立目录。
- [x] 预期结果能说明依据吗？ $\rightarrow$ 明确指出基础镜像缺失 make 工具链与 apt-get 修复机理。
- [x] 失败记录能定位到具体版本吗？ $\rightarrow$ 标注了固定基准 commit 与完整 Docker 镜像 digest。
