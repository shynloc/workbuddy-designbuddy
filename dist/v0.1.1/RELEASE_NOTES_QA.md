# DesignBuddy QA v0.1.1 — Release Notes（测试候选版，第 2 轮）

> 仅用于本地 WorkBuddy 真机测试。**不是商业版，不要上传到开放平台。**

| 文件 | 说明 |
|---|---|
| `designbuddy-qa-v0.1.1.zip` | QA Skill（根目录 `designbuddy-qa/`）。SHA-256 见 `SHA256SUMS.txt` |
| `PACKAGE_FINGERPRINT.txt` | ZIP 和 package-manifest 的 SHA-256。用于确认测试报告对应的是这个包 |
| `brand-alpha/`、`brand-beta/` | 由 v0.1.1 编译器生成的测试品牌包（generated_at 固定为 2026-01-01，便于复现） |

## 相对 v0.1.0 的变更

修复了真机报告中的 1 个 P0、2 个 P1、2 个 P2、1 个 P3。详见 `qa/FIX_REPORT.md`、`qa/CHANGELOG.md`。

## 开发机验证（证据：`qa/TEST_REPORT_LOCAL.md`、`qa/local-evidence/`）

- 单元测试 17/17 通过；
- 包 lint 0 错误；
- 在解压副本中（路径含空格和中文，并模拟写入 `_user_meta.json`），SCRIPT 用例 57/57 PASS；
- 两次构建的 ZIP 逐字节一致。

## 怎么测

1. 先删除 v0.1.0 版本的 `designbuddy-qa`、`alpha-demo-brand-system`、`beta-demo-brand-system`；
2. 安装本 ZIP；
3. 新开会话，粘贴 `qa/WORKBUDDY_QA_PROMPT.md`。

## 状态

- `LOCAL_QA_PASSED` = NO（需要真机回填）
- `READY_FOR_PLATFORM_SUBMISSION` = NO
