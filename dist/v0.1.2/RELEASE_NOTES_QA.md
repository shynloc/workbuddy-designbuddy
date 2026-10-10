# DesignBuddy QA v0.1.2 — Release Notes（测试候选版，第 3 轮）

> 仅用于本地 WorkBuddy 真机测试，**不要上传到开放平台**。

| 文件 | 说明 |
|---|---|
| `designbuddy-qa-v0.1.2.zip` | QA Skill。ZIP SHA-256 `49c218b16a8568c16820323996c6d2bcf1923c0f15cfce7a5369a8043ac1b94b` |
| `PACKAGE_FINGERPRINT.txt` | package-manifest SHA-256 `c8e97bc5f9f100ff201c8f9ac5397849aea9bc49f7b3f0a6bbf25d938d249919` |
| `brand-alpha/`、`brand-beta/` | 测试品牌包。也可以直接在 H3b / H4 安装测试中使用 |

## 变更

见 `qa/FIX_REPORT.md`（FIX-07 ~ FIX-09）和 `qa/CHANGELOG.md`。

## 开发机验证

- 单元测试 19/19 通过；
- 包 lint 0 错误；
- 解压副本中 SCRIPT 用例 57/57；
- 两次构建的 ZIP 逐字节一致。

## 怎么测

1. 删除旧的 `designbuddy-qa`；
2. 安装本 ZIP；
3. 新开会话，粘贴 `qa/WORKBUDDY_QA_PROMPT.md`（不需要填写任何内容）。

## 状态

LOCAL_QA_PASSED = NO（安装链路尚未打通）· READY_FOR_PLATFORM_SUBMISSION = NO
