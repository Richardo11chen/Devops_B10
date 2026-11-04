# AI 使用记录（E8-E10 补自主用例）

## 补自主测试用例（2026-11-04）

- 使用模型：Claude Opus 4.8（通过 Claude Code）
- 使用范围：选择测试方向（Option 2：同一 target 两条 MISSING）、分析 patch() 函数行为以确定预期输出、编写  测试代码
- 人工修改：确认测试预期（plan 顺序为 config.h 再 extra.h，按字母序）、验证 14 项测试全部通过、编写本次 AI_USAGE.md 记录
- 测试设计思路由人工选定，代码逻辑由 AI 辅助编写，最终在 Docker 容器内验证通过
