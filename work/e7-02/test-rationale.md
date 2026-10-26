# 新增测试说明（C04）

**测试**：`services/draft/tests/test_output_dir_guard.py::OutputDirectoryGuardTests::test_non_empty_output_directory_is_rejected`

**检查内容**：`auto_build()` 在 `--out` 指向已有文件的目录时，必须拒绝执行并报 `Use a fresh empty output directory`，不得把新证据写入旧目录。

**不加会漏掉的 bug**：重跑时若允许复用非空输出目录，`iter-02/result.json`、`verify-container-id.txt` 等文件可能与上一次运行的候选或容器错配，E6 证据就无法证明「本次构建确实来自本次候选」，证据的可复现性被破坏。

**计数说明**：任务卡写「24 → 25」，但 main（`11b26d4`）已包含 PR #9 合入的 `test_ci_reject_demo.py`，实际基线是 25 项；本 PR 新增 1 项后为 **26 passed**（见 `work/build-02/unit-tests/stdout.log`）。
