# 设计工作流（为真实品牌建立设计系统）

目标：用尽量少的提问，把用户的品牌编译成 Brand Skill、Portable Design System 和 Preview。

**分工**：

- 专业设计工作由预置的编译器完成。
- Agent 负责收集信息、展示决策、执行命令。
- **不要临时编写模板或生成器**。

## 1. 判断路径（不需要问用户，根据材料判断后告知）

| 用户的情况 | 路径 |
|---|---|
| 有完整的 VI、品牌手册、设计规范 | `existing`（保留现有品牌，不重新设计） |
| 只有 Logo、主色、名字、几份旧材料 | `partial`（保留已知内容，补全缺失部分） |
| 什么都没有 | `new`（Discovery → 2~3 个方向 → 选择） |

## 2. 收集信息（一次问完，最多 5 个问题）

- 品牌名、英文名、别名；
- 做什么、面向谁、一句话定位；
- 希望给人的 3 个感觉，以及不想要的感觉；
- 已有的颜色、字体、Logo 文件（如果有）；
- `new` 路径额外问：喜欢的参考（只提炼原则，不复制资产）。

**不要直接问"你的主色是什么"**，用户没有的信息由方向库生成。

## 3. 写 brief 并初始化

1. 把收集到的信息写成 `brief.json`，格式见 @references/compiler-contract.md 。
2. 写在 Workspace 之外的用户目录中。
3. 用户提供的 Logo 等文件放在 brief 同级目录，用相对路径引用。
4. 运行初始化：

```
<PY> "<SKILL>/scripts/designbuddy.py" init --brief "<brief.json>" --workspace "<用户目录>/designbuddy-workspace/<slug>"
```

## 4. 逐个 Gate 给用户决策

1. 每个 Gate 先运行 `status`。
2. 只展示 `review_first`（INFERRED/GENERATED 的项）、`conflicts`、`candidates`，不要让用户逐条确认已经明确的事实。
3. 让用户回复 **KEEP / CHANGE / REJECT** 之一。

| Gate | 展示什么 | 常用 CHANGE |
|---|---|---|
| G1 品牌基础 | 定位、受众、性格 | `--set brand.positioning=...` |
| G2 视觉方向 | 3 个候选方向（new）或现状（existing/partial） | `--decision KEEP --set direction=<id>` |
| G3 核心系统 | 颜色、字体、对比度结果、冲突 | `--set color.primary=#RRGGBB`、`--set font.heading=...`、`--set resolve.<冲突id>=...` |
| G4 应用规则 | PPT、Word、Excel、网页、海报、社交媒体规则 | — |
| G5 Preview | `preview` 命令生成的 HTML（离线可直接打开） | 回到 G3/G4 修改 |
| G6 最终导出 | 版本号、包含的内容 | — |

### 反馈要具体

用户说"怪怪的"时，给 2~3 个具体的解释让用户选，例如：

- 标题太重？可以把字重从 700 降到 600；
- 颜色太冷？
- 间距太挤？

### 收敛

- 同一个 Gate 修改 3 轮后，给出 A/B 两个方案让用户二选一。
- 核心配色对比度不达标时，G3 会被拦截：
  - 先给出修改建议；
  - 用户坚持时，用 `--set override.<组合名>=<原因>` 记录 USER_OVERRIDE。**不要悄悄放行。**

## 5. 构建与交付

```
<PY> "<SKILL>/scripts/designbuddy.py" preview --workspace "<WS>"
<PY> "<SKILL>/scripts/designbuddy.py" gate --workspace "<WS>" --gate G5 --decision KEEP
<PY> "<SKILL>/scripts/designbuddy.py" gate --workspace "<WS>" --gate G6 --decision KEEP
<PY> "<SKILL>/scripts/designbuddy.py" build --workspace "<WS>"
```

`build` 的输出都在 `<WS>/exports/` 中：

- `<slug>-brand-system-<版本>.zip`（WorkBuddy Brand Skill）；
- `portable-design-system/` 和它的 ZIP；
- `preview/`；
- `source-report/`。

然后按 @references/installation-handoff.md 进行安装交接。

## 6. 断点续做

用户说"继续做 X 的品牌系统"时：

1. 运行 `status`；
2. 按返回的 `next.next_action_zh` 继续，不重复已经完成的 Gate。
