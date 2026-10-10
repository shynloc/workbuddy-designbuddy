---
name: designbuddy
display_name: "DesignBuddy 品牌设计系统"
display_name_en: "DesignBuddy Brand System Builder"
description: "当用户想为自己的公司、个人品牌、自媒体 IP 或产品建立或升级一套品牌设计系统（品牌 VI、颜色、字体、版式、Design System、Design Tokens、DESIGN.md、Word/PPT/Excel/网页/海报规范），或者想生成一个以后能自动按品牌规范做设计的品牌 Skill 时使用。日常为某个已安装品牌做 PPT、海报等物料时，应使用对应的品牌 Skill，而不是本技能。"
description_zh: "通过对话建立你的品牌设计系统，编译成可安装的品牌 Skill、可移植的 Design System（DESIGN.md + Tokens）和预览样例，全部在本地完成。"
description_en: "Build your brand design system through conversation and compile it into an installable Brand Skill, a portable design system (DESIGN.md + tokens) and previews, all locally."
version: 1.0.0
author: "DesignBuddy"
user-invocable: true
disable-model-invocation: false
---

# DesignBuddy 品牌设计系统 v1.0.0

DesignBuddy 把用户的品牌资料、现有素材和设计偏好，编译成一套**可以长期执行**的品牌设计系统：

- **品牌 Skill**：安装到 WorkBuddy 后，以后说"给 <品牌> 做一份 PPT"，就会自动按品牌规范设计；
- **Portable Design System**：DESIGN.md、Design Tokens（DTCG）、CSS，可用于其他 AI 工具和网页项目；
- **离线预览**：海报和单页样例，用于验收；
- **来源报告**：哪些是你确认的，哪些是 AI 推断或生成的，以及字体和素材的许可情况。

**工作原则**：

- 专业设计由 `scripts/` 中预置的确定性编译器完成。**不要临时编写模板或生成器，不要凭印象给出检查结论。**
- 全部在本地运行，不联网，不上传用户资料。

## 0. 找到运行方式（每个会话只做一次）

1. 确定本 Skill 目录的绝对路径（即本文件所在的目录），下文记作 `<SKILL>`。
2. 依次尝试下面的命令，取第一个能输出 JSON 的，下文记作 `<PY>`：
   - `python3 "<SKILL>/scripts/designbuddy.py" version`
   - `python "<SKILL>/scripts/designbuddy.py" version`
   - `py -3 "<SKILL>/scripts/designbuddy.py" version`
3. 如果都不可用：如实告诉用户"当前环境没有可用的 Python 3.8+，DesignBuddy 暂时无法运行"。**不要安装任何东西，也不要手工模拟编译结果。**

所有命令都输出一个 JSON 对象。退出码：0 成功；1 校验未通过；2 输入错误；3 环境不支持。

## 1. 建立品牌系统

按 @references/design-workflow.md 执行。数据格式和命令见 @references/compiler-contract.md 。

```
收集信息（一次问完）→ init → G1 品牌基础 → G2 视觉方向 → G3 核心系统 → G4 应用规则
→ preview → G5 预览验收 → G6 最终确认 → build --deliver → 用户在客户端导入
```

- 已有完整品牌：走 existing 路径，**保留现有品牌，不重新设计**。
- 只有部分资料：走 partial 路径，保留已知内容，补全缺失部分。
- 什么都没有：走 new 路径，先给 2~3 个视觉方向供选择。
- 每个 Gate 只让用户回答 KEEP / CHANGE / REJECT，并优先展示 AI 推断或生成的内容。

## 2. 交付与安装

按 @references/installation-handoff.md 执行：

- `build --deliver` 会把交付包放到**下载文件夹**下的 `DesignBuddy/<品牌>/`，内容包括：品牌 Skill ZIP、Portable ZIP、预览、来源报告、安装说明。
- 已有文件不会被覆盖。
- 用户在 WorkBuddy 客户端的技能管理中"导入本地技能"，选择这个 ZIP 即可完成安装。
- **禁止** Agent 自己把文件写入 WorkBuddy 的 Skill 目录。

## 3. 续做与升级

- 用户说"继续做 X 的品牌系统"：运行 `status`，从中断的 Gate 继续。
- 品牌发生变化：修改后重新 build。版本号会递增，旧的交付包会保留。

## 4. 安全与隐私

见 @references/safety.md 。要点：

- 不联网；
- 不读取与任务无关的文件；
- 用户的原始资料不会进入品牌 Skill；
- 不打包字体文件，也不打包未授权的素材；
- 参考品牌只提炼原则，不复制对方的资产；
- 不覆盖用户已有的文件和 Skill。

## 5. 自检

如果用户反馈异常，运行 `<PY> "<SKILL>/scripts/designbuddy.py" selftest`，核对本 Skill 是否与发布版本一致，并把结果告诉用户。
