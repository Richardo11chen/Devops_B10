# DevOps_B10

DevOps 教学实验 **B 组（B10）** 仓库，包含 E2 接口契约与 E3 并行测试基线两部分交付物。

## 配对关系

| 组别 | 仓库 | E2 负责服务 | E3 负责内容 |
|------|------|-------------|-------------|
| **B10（本仓库）** | `DevOps_B10` | DRAFT + MDFixer | DRAFT 样本、MDFixer 固定输入 |
| A10（配对组） | [ana12-21/Devops_G10](https://github.com/ana12-21/Devops_G10) | BuildChecker + EChecker | MD/RD 故障项目、C0/C1/C2 连续提交、Linux 原始跟踪 |

- **A 组仓库地址**：<https://github.com/ana12-21/Devops_G10>
- **本地只读克隆**：`../Devops_G10_ref`，基线 commit `7720a30`。**只读参考，不修改、不 push。**
- **E2 交换方式**：双方以仓库中的契约文件作为接口约定，**不部署 API**。

## B 组分工

| 成员 | 角色 | E2 任务 | E3 任务 | 主要文件 |
|------|------|---------|---------|----------|
| 组长 | 组长 | DRAFT 契约确认、统一任务模型、校验脚本 | 仓库骨架 | `e2/contracts/dockerfile_job.*`、`e2/task.schema.json`、`e2/validate.py`、`e2/ADR.md` |
| 成员B | 组员 | REPAIR 契约确认 | — | `e2/contracts/repair_job.*` |
| 成员C | 组员 | — | DRAFT 样本与 Docker 证据 | `e3/fixtures/draft/` |
| 成员D | 组员 | — | MDFixer 样本与修复验证 | `e3/fixtures/mdfixer/` |

各成员任务详情见 [`e2/issue_draft.md`](e2/issue_draft.md)；个人贡献逐项记录见 [`CONTRIBUTORS.md`](CONTRIBUTORS.md)。

## 运行环境要求

**所有命令必须在 Linux 下运行。** 本仓库在 Ubuntu 24.04.3 LTS（WSL2, x86_64）上验证通过。

| 工具 | 验证版本 | 用途 |
|------|----------|------|
| Linux | Ubuntu 24.04.3 LTS, kernel 6.6.87.2-microsoft-standard-WSL2, x86_64 | 唯一受支持的运行平台 |
| git | 2.43.0 | 版本固定、提交追踪 |
| make | GNU Make 4.3 | 构建与 `make -pn` 原始跟踪 |
| gcc | 13.3.0 (Ubuntu 13.3.0-6ubuntu2~24.04.1) | 编译样本项目 |
| strace | 6.8 | 系统调用级原始跟踪 |
| docker | 29.7.2 | DRAFT 样本镜像构建 |
| python3 | 3.12.3 | 运行 `validate.py` 等校验脚本 |

## 目录结构

```text
DevOps_B10/
├── README.md
├── CONTRIBUTORS.md
├── e2/                      # E2 接口契约
│   ├── README.md            # DRAFT 契约确认结论
│   ├── contracts/           # dockerfile_job.*（组长负责）
│   ├── task.schema.json     # 统一任务模型（4 类 × 6 态 × 9 公共字段）
│   ├── validate.py          # 最小检查 01–04
│   ├── ADR.md               # 架构决策记录
│   ├── Backlog.md           # 任务、负责人、产物、验收条件
│   ├── AI_USAGE.md          # AI 使用记录
│   └── issue_draft.md       # 4 份组内 Issue 草稿 + 向 A 组提 Issue 正文
├── e3/                      # E3 并行测试基线
│   ├── README.md
│   ├── fixtures/            # 课程人工样例源码
│   │   ├── draft/           # 成员C负责（占位）
│   │   └── mdfixer/         # 成员D负责（占位）
│   ├── evidence/            # 实际命令与观察结果
│   └── scripts/
└── work/                    # 真实 Git 提交与参考修复
```

## 验证方式

```bash
# E2 契约最小检查：四类请求+响应有效样例通过，三个反例被拒绝
python3 e2/validate.py

# E3 基线复现：细节与命令见 e3/README.md
```

## 相互检查清单

每条交付物合入前逐项自问：

- [ ] 别人能按 README 跑起来吗？
- [ ] 人工答案（ORACLE）和实际日志分清楚了吗？
- [ ] 预期结果能说明依据吗？
- [ ] 失败记录能定位到具体版本吗？
