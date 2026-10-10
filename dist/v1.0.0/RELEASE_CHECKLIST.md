# RELEASE_CHECKLIST — DesignBuddy v1.0.0

> 上传、定价、提交审核都由**你本人**在 WorkBuddy 开放平台操作。我没有、也不会执行任何发布动作。

## A. 上传前必须确认（5 项）

| ✔ | 项 | 说明 |
|---|---|---|
| ☑ | **发布主体与 author** | 已改为认证主体名 `"ShyNloc"`（2026-10-11 重新打包）。之前 author="DesignBuddy" 的构建已作废，不要上传 |
| ☐ | **价格** | 买断制，价格**必须是 1–9999 的整数**（开放平台 UI 文案，OBSERVED）。付费方式上架后不能更改，改价次数每年有限 |
| ☐ | **服务类目**（个人主体） | 建议：工具 → 办公；辅类目：工具 → 图片处理。提交当天请重新核对官方类目页 |
| ☐ | **市场分类** | 设计 |
| ☐ | **图标** | `marketplace/designbuddy-icon-512.png`（另有 256 尺寸和 SVG 源文件）。以上传位的尺寸和格式要求为准 |

## B. 包信息

| 项 | 值 |
|---|---|
| 文件 | `designbuddy-v1.0.0.zip`（根目录 `designbuddy/`，28 个文件，约 150KB） |
| SHA-256 | 见 `SHA256SUMS.txt` |
| 包指纹 | 见 `PACKAGE_FINGERPRINT.txt` |
| 本地验证 | `BUILD_VERIFICATION.md`：6/6 PASS，并通过 WB-OPDK `validate_skill.py` |
| 不包含 | QA Runner、测试夹具、虚构品牌、字体文件、任何凭据 |

## C. 上传后：状态逐级确认（不能互相替代）

| 状态 | 怎样才算达成 | 当前 |
|---|---|---|
| LOCAL_QA_PASSED | 本地验证 | ✅ 开发机商业包 6/6；Windows 真机 QA v0.1.1 的 SCRIPT 57/57；交付功能已在 QA v0.1.3 中实现 |
| READY_FOR_PLATFORM_SUBMISSION | 包可以交给你上传 | ✅ 本包 |
| PLATFORM_PARSE_PASSED | 开放平台上传并解析成功 | ⏳ 待你上传 |
| REVIEW_APPROVED | 平台审核通过 | ⏳ |
| PAID_ENCRYPTED_RUNTIME_VERIFIED | 付费加密后在真实环境中可用 | ⏳ 见 D |

## D. 上线后的第一件事（强烈建议，属于高风险项）

付费 Skill 会被平台**强制加密**。加密后 Agent 能否读取 references、执行 `scripts/`，**至今没有验证过**（PP-002/003）。如果不能，DesignBuddy 对购买者将**完全不可用**。

1. 审核通过后，先用**另一个普通账号**购买并安装（可以先设一个最低的整数价格，或者用平台提供的测试方式）。
2. 新开会话，说"帮我建立一套品牌设计系统"，确认能走到 G1。
3. 再说"运行 DesignBuddy 自检"，Agent 应该执行 `selftest`，并返回 `ok: true`。
4. 如果第 2 或第 3 步失败：**立即下架**，把错误信息交给我。我们按架构文档 §29 的降级顺序处理（服务端编译仍然需要你另行批准）。
5. 通过后再对外推广。即便通过，对外也只称 Paid Skill，不使用"加密"或"源码保护"的说法。

## E. 你已接受的剩余风险（产品负责人决定："其他没问题，可以发布"）

- macOS 未在真机测试；
- 多品牌自动触发（MB-003~005）没有在独立会话中测试；
- 没有用真实品牌走过完整的 Gate 交互；
- 详见 `KNOWN_LIMITATIONS.md`。
