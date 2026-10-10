---
title: DesignBuddy Open Questions
status: LIVING DOCUMENT
last_updated: 2026-10-10
---

# Open Questions

## 说明

- **Blocker**：不解决就无法冻结架构或开始相关实现。
- **High**：影响主路径体验，但有降级方案。
- **Normal**：可以在开发过程中解决。
- 每个问题都写明解决方式。解决后填写结论和日期，并同步更新 [`runtime-capabilities.md`](runtime-capabilities.md)。

## 平台与运行时

| ID | 问题 | 级别 | 影响 | 如何解决 | 结论 |
|---|---|---|---|---|---|
| Q-01 | DesignBuddy 作为第三方 Skill，怎样把已生成的 Brand Skill 交给原生机制安装？H1–H5 中哪些可用？ | Blocker | 安装主路径 | V-IN-01..08 实测 | — |
| Q-02 | 付费或加密状态下，Agent 能否读取自身的 references、scripts、templates？脚本能否执行？ | Blocker | 编译器实现方式（D-03 已按最坏情况设计）；DesignBuddy 能否运行 | V-PP-03/04 | — |
| Q-03 | "用户不可使用自定义模式调用"具体指什么？对 DesignBuddy 有什么限制？ | Blocker | 交互与触发方式 | V-PP-05；必要时咨询官方 | — |
| Q-04 | Windows 上 WorkBuddy 执行命令用什么 shell？常见的 Python 状态是什么（未安装 / Store 占位程序 / 已安装）？ | High | 能力分级的实际分布 | V-EN-01..03，在多台机器上采样 | — |
| Q-05 | Skill 运行时的工作目录在哪里？能否写入？用户希望 Workspace 放在哪里？ | High | Workspace 位置 | V-EN-05 | — |
| Q-06 | Skill 根目录能否包含官方结构之外的文件？包的大小、文件数上限是多少？能否包含二进制文件？ | High | 导出结构、Office 模板、字体 | V-PK-02/04、V-OF-01 | — |
| Q-07 | 安装后 references 是按需读取，还是会被整体注入上下文？ | High | Token 预算是否成立 | V-TK-01 | — |
| Q-08 | 多个 Brand Skill 共存时，模型的实际选择行为是怎样的？ | High | 消歧设计是否足够 | V-MB-* | — |
| Q-09 | Skill frontmatter 中 `category` 的可选值有哪些？是否有 `design`？ | Normal | frontmatter 生成 | V-PK-03；查看开放平台表单 | — |
| Q-10 | Agent 能否解析用户上传的 PDF、PPT、图片的视觉信息？在什么程度上可用？ | High | Existing/Partial 路径的抽取能力边界 | V-EN-07 | — |
| Q-11 | DESIGN.md（Stitch）规范的最新版本与字段约定是什么？ | Normal | Portable 导出 | 开发 Portable exporter 前查阅上游 | — |

## 产品决策（需要产品负责人确认）

| ID | 问题 | 当前提议 | 结论 |
|---|---|---|---|
| P-01 | 定价 | TBD（必须是整数，见 PRD §9） | — |
| P-02 | D-01/D-02：Brand IR 和项目元数据用 JSON 存储（需求原文写的是 project.yaml），YAML 只做导出视图 | 采用 JSON | — |
| P-03 | Workspace 的默认位置：当前工作目录下的 `designbuddy-workspace/`，还是每次询问？ | 默认当前工作目录，首次使用时告知用户并允许修改 | — |
| P-04 | 字体许可知识库的覆盖范围（首发收录多少款中英文可商用字体）以及复核周期 | 首发约 20–30 款，每季度复核 | — |
| P-05 | Visual Direction 原型库的首发数量 | 8–12 个原型，每次挑选 2–3 个呈现 | — |
| P-06 | Brand Skill 的 `author` 字段：填用户名，还是组织名？ | 默认填品牌所属主体，由用户确认 | — |
| P-07 | 是否在 Portable 包中附带 Preview 样例？ | 默认询问用户 | — |
| P-08 | 买断制下 V1 之后的更新节奏，以及未来行业包是否单独售卖 | 待定 | — |
| P-09 | 品牌名是中文时，Skill 的 slug 怎么生成（拼音 / 英文名 / 用户自定义）？ | 优先英文名，其次拼音，由用户确认 | — |

## 已关闭

| ID | 问题 | 结论 | 日期 |
|---|---|---|---|
| C-01 | WorkBuddy 是否支持在对话内生成并安装 Skill？ | 支持（OBSERVED，产品负责人实测） | 2026-10 |
| C-02 | 是否做免费版？ | 不做 | 2026-10 |
| C-03 | V1 是否包含全部应用模块？ | 包含；Office 二进制模板为 Advanced，可降级 | 2026-10 |
