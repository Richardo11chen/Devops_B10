# work/ — 两个用途

本目录同时承载 **E4 的运行证据**与 **E3 保留下来的真实提交快照**。两者命名方式不同，互不冲突。

| 子目录 | 来源 | 命名 | 是否进仓库 |
|--------|------|------|-----------|
| `work/<时间>/` | **E4** 每次运行 `make` 生成的证据目录 | `YYYYMMDD-HHMMSS`（**由 E4 模板的 Makefile 规定**） | ❌ 被 `.gitignore` 忽略，按需挑选后 `git add -f` |
| `work/mdfixer-demo/` | **E3** 成员D 的真实 Git 提交快照（C0 / C1） | 按版本命名 | ✅ 已跟踪 |

## 时间戳的取舍（两处规则不同，别混）

- **E4 的 `work/<时间>/` 用时间戳** —— 这是课程模板 `Makefile` 里写死的（`RUN := work/$(shell date +%Y%m%d-%H%M%S)`），
  目的是「每次运行新建目录、不覆盖旧记录」。**不要改**，改了与课程验收口径对不上。
- **E3 的 `e3/evidence/` 不用时间戳** —— 按任务与场景命名（如 `mdfixer-no-clean-rebuild.log`）。

> 两条规则服务于不同实验，不矛盾。

## E4 证据目录里有什么

每次 `make all` 在同一个 `work/<时间>/` 下产出：

| 文件 | 来自 | 看什么 |
|------|------|--------|
| `env.json` | `make doctor` | `problems` 为空；Git 身份是自己学号 |
| `build.log`、`image.json`、`toolchain.lock` | `make build` | 镜像构建成功；digest、镜像 ID、工具版本 |
| `test.log` | `make test` | `4 passed` |
| `smoke.json` | `make smoke` | `passed: true`；`build_exit_code` 非 0；`make_error_line` 含 `make: not found` |
| `secret-scan.txt` | `make scan` | 「密钥检查：未发现问题」 |

**若失败后重试过，最新目录须对应成功的那次运行。**

## E3 快照是什么

`work/mdfixer-demo/C0/`、`C1/` 是成员D 的 MDFixer 样例对应的**真实 Git 提交快照**，
每个目录里 `.git_info.txt` 记有完整 40 位 SHA、作者、日期与提交信息。
用途是让「失败记录能定位到具体版本」这条验收有据可查 —— 详见
[`e3/fixtures/mdfixer/README.md`](../e3/fixtures/mdfixer/README.md)。

## 约定

- 记录时必须能回答：这次跑的是**哪个版本**（commit SHA / 文件 hash）。
- 人工构造的预期结果显式标 `ORACLE`，与实际运行输出分开写。
- `.gitignore` 里的 `work/` 不影响已跟踪的 `work/mdfixer-demo/`；E4 的新证据默认不入库。
