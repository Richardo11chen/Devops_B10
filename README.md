# DevOps_B10

DevOps 教学实验 **B 组（B10）** 服务仓库。

- **E4 起**：本仓库是可重复工程环境，服务代码在 `services/draft/`，一条 `make all` 完成构建、测试、留证据
- **E2 / E3 交付物**：接口契约在 `e2/`，并行测试基线在 `e3/`
- **配对组 A10**：<https://github.com/ana12-21/Devops_G10>（本地只读克隆 `../Devops_G10_ref`）

---

## 快速开始（E4）

```sh
mkdir -p ~/<学号> && cd ~/<学号>
git clone <本组仓库地址> && cd <仓库>
git config user.name  "<学号>"             # 统一用学号；服务器账号共用，不要加 --global
git config user.email "<学号>@localhost"   # E4 不推送，填本地示例值即可
make all
```

`git remote -v` 应指向真正的本组远程仓库。共享服务器上的学号目录与 Git 身份只隔离个人工作和标记未来的提交；运行 `make all` 本身不会产生 Git 提交。

### 命令

| 命令 | 作用 | 证据（`work/<时间>/`） |
| --- | --- | --- |
| `make doctor` | 服务器与 Git 身份自检 | `env.json` |
| `make build` | 构建服务镜像 | `build.log`、`image.json`、`toolchain.lock` |
| `make test` | 容器内运行单元测试 | `test.log` |
| `make smoke` | 用 E3 样例做冒烟测试 | `smoke.json` |
| `make scan` | 密钥检查（工作区、Git 历史、镜像） | `secret-scan.txt` |
| `make all` | 以上五步 | 同一个证据目录 |
| `make shell` | 进入服务容器；仓库的 `work/` 挂到容器 `/app/work` | — |
| `make lock` | 修改 `requirements-dev.in` 后重新生成锁文件 | `requirements-dev.lock` |
| `make clean` | 删除自己构建的镜像 | — |

**预期结果**

- `make doctor`：显示「环境自检：通过」，`problems: []`；Git 身份是自己学号
- `make test`：`4 passed`
- `make smoke`：`"passed": true`、`docker_server` 有版本、`build_exit_code` **非 0**、`make_error_line` 含 `make: not found`
- `make scan`：显示「密钥检查：未发现问题」

> **冒烟样例是故意构建失败的。** `Dockerfile.broken` 里执行 `make`，而基础镜像没装 `make`。`build_exit_code` 非 0 与 `passed: true` 可以同时出现：前者是样例构建失败，后者表示 DRAFT 服务成功识别并记录了预期失败。`log_tail` 只保留末尾 8 行，不保证包含关键行——**看 `make_error_line`**。E5 须重新保存完整原始构建日志与退出码。

### 约定

- **Debian apt 源已改为阿里云镜像站**（`services/draft/Dockerfile` 里一行 `sed`，见该文件注释）。原因：官方 `deb.debian.org` 在课程服务器上实测约 **30 KB/s**，apt 索引 9.6 MB 要 5 分钟以上且实测表现为卡死（45 秒零输出、无活跃连接）；换 `mirrors.aliyun.com` 后 `apt-get install git` 从「无限等待」变为 **68 秒完成**。**只改 URI，包内容与哈希校验不变**。要换回官方源：把该行的 `mirrors.aliyun.com` 改回 `deb.debian.org`。
- Python 基础镜像、Docker 客户端镜像与冒烟样例均通过镜像站按 **digest** 固定；更换时须核验 digest 与架构，并在提交说明中写明来源。服务镜像从 `docker:cli` 复制客户端，**不在容器里另装 Docker 引擎**；`docker_server` 记录的是宿主机引擎版本。
- 新增 Python 依赖：写进 `requirements-dev.in`，执行 `make lock`，两个文件一起提交。
- **密钥只放在 `.env`（权限 600），不提交、不进镜像、不打印到日志、不进 AI 使用记录。**
- E4 每名组员各自在学号目录运行一次 `make all`，记录成功的 `work/<时间>/` 与所测源码 SHA，再与另一名组员对照。`work/` 默认不提交；**E4 不要求个人创建分支、提交或合并**。
- 服务容器通过挂载的 `/var/run/docker.sock` 使用宿主机 Docker，**这等同于宿主机 root 权限**；容器的资源限制管不到它发起的构建。只构建课程指定的项目，不开放 2375/2376 端口，不清理其他组员的镜像与缓存。

---

## 运行环境要求

全部命令在 **Linux** 下运行。E2/E3 部分在 Ubuntu 24.04.3 LTS（WSL2, x86_64）上验证；E4 的目标平台是课程分配的 Linux 服务器。

| 工具 | 版本 | 用途 |
| --- | --- | --- |
| Linux | Ubuntu（x86_64） | E4 目标平台；`make doctor` 会校验 |
| Docker | host engine + CLI | E4 服务镜像与冒烟构建 |
| make / git / python3 | — | E4 一键命令与脚本 |
| gcc 13.3.0 / strace 6.8 | — | **仅 E3**；E4 的这些工具在服务镜像里 |

> E4 的构建环境由 `services/draft/Dockerfile` 固定（digest + `--require-hashes`），**宿主机只需要 Docker、Git、Make、Python3**。

## B 组分工

| 成员 | 角色 | E2 | E3 | E4 |
| --- | --- | --- | --- | --- |
| 陈奕澎 | 组长 | DRAFT 契约确认、统一任务模型、校验脚本 | 仓库骨架 | 模板入库提交、服务器 Docker 就绪确认、本地预跑 |
| 张少逸 | 组员 | REPAIR 契约确认 | — | 服务器 `make all` + **假 Key 验证 `make scan`** |
| 孙正奇 | 组员 | — | DRAFT 样本与 Docker 证据 | 服务器 `make all` + **第二人重跑对照** |
| 宋丞轩 | 组员 | — | MDFixer 固定输入与修复验证 | 服务器 `make all` + **镜像来源与 digest 核验** |

个人贡献逐项记录见 [`CONTRIBUTORS.md`](CONTRIBUTORS.md)。

## 目录结构

```text
DevOps_B10/
├── services/draft/            # E4：DRAFT 服务（Dockerfile、draft/、tests/、pytest.ini）
├── fixtures/draft/            # E4：冒烟样例（取自 E3，故意构建失败）
├── scripts/                   # E4：doctor.py、secret_scan.py
├── compose.yaml               # E4：运行限制 + docker.sock 挂载
├── Makefile                   # E4：一键命令
├── requirements-dev.in/.lock  # E4：依赖与锁文件（--require-hashes）
├── .env.example               # E4：密钥样板（真实 .env 不提交，权限 600）
├── .gitignore / .dockerignore
├── reports/                   # E4：报告输出目录（占位）
├── e2/                        # E2：接口契约、ADR、Backlog、AI_USAGE、裁决记录
├── e3/                        # E3：并行测试基线（draft 与 mdfixer 样例 + 证据）
└── work/                      # 运行证据（E4，默认忽略）+ 真实提交快照（E3）
```

> `work/` 有两个用途，互不冲突：`work/<时间>/` 是 E4 每次运行的证据目录（被 `.gitignore` 忽略）；
> `work/mdfixer-demo/` 是 E3 保留下来的**真实 Git 提交快照**（已跟踪，不忽略）。详见 [`work/README.md`](work/README.md)。

## 历史实验（E2 / E3）

- **E2 接口契约** — `e2/`。9 个公共字段（含 `execution`）、四类任务、10 项产物枚举；最小检查 `python3 e2/validate.py`（01–04 全部通过）；与 A10 逐字段比对一致。12 条议题的裁决过程见 [`e2/resolutions.md`](e2/resolutions.md)。
- **E3 并行测试基线** — `e3/`。DRAFT 两层判据样本 + MDFixer 固定输入四件套（六步修复验证、四种声明风格、`.d` 实证）。复现命令见 [`e3/README.md`](e3/README.md)。

## 相互检查清单

提交与验收前逐项自问：

- [ ] 别人**只看 README** 能重跑吗？
- [ ] 提交作者都是**学号**吗？
- [ ] 仓库、Git 历史、镜像里有 **Key** 吗？
- [ ] 证据目录能**对应到具体提交**吗？
- [ ] 人工答案（ORACLE）和实际日志分清楚了吗？
