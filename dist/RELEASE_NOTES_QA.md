# DesignBuddy QA v0.1.0 — Release Notes（测试候选版）

> 仅用于本地 WorkBuddy 真机测试。**不是商业版，不要上传到开放平台。**

## 文件

| 文件 | 用途 |
|---|---|
| `designbuddy-qa-v0.1.0.zip` | 安装到本地 WorkBuddy 的 QA Skill（根目录为 `designbuddy-qa/`，Skill 名为 `designbuddy-qa`，与未来的正式版 `designbuddy` 不冲突） |
| `brand-alpha/`、`brand-beta/` | 由编译器生成的虚构品牌 Brand Skill ZIP、Portable ZIP 和 Preview（也可以由 QA RUN ALL 在报告目录中重新生成） |
| `SHA256SUMS.txt` | 校验和 |

## 版本

- DesignBuddy 0.1.0
- Brand IR schema 1.0.0
- Brand Skill 1.0.0 / Design System 1.0.0（夹具品牌）

## 怎么测

见 `qa/QA_TEST_GUIDE.md`。安装后新开一个会话，粘贴 `qa/WORKBUDDY_QA_PROMPT.md` 中的提示词即可。

## 开发机已验证（证据见 `qa/TEST_REPORT_LOCAL.md`、`qa/local-evidence/`）

- 单元测试 12/12 通过。
- 包 lint：0 错误。
- 从解压后的 ZIP（路径含空格和中文）执行 QA RUN ALL：SCRIPT 用例 56/56 PASS。

## 尚未验证

所有 WorkBuddy 平台行为都还没有验证：

- Python 在真机上的可用性；
- 安装交接 H1–H4；
- 多品牌调度；
- 付费加密形态。

当前状态：

- `LOCAL_QA_PASSED` = **NO**（需要真机回填）；
- `READY_FOR_PLATFORM_SUBMISSION` = **NO**。
