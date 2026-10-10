---
name: dbprobe-protection
display_name: DesignBuddy 保护机制探测
display_name_en: DesignBuddy Protection Probe
description: DesignBuddy 开发测试专用。仅当用户明确说“运行 DesignBuddy 保护探测”或“run dbprobe protection”时使用。检测在当前安装形态（本地 / 市场、免费 / 付费、加密 / 未加密）下，Agent 能否读取 references、执行自带脚本、读取和输出内置资源、用生成器生成新文件。不要在其他任何场景使用。
description_zh: DesignBuddy 开发测试专用：检测付费或加密状态下 Skill 资源与脚本的可用性。
description_en: DesignBuddy test-only probe for skill resource and script availability under paid/encrypted installs.
version: 1.0.0
author: DesignBuddy Dev
user-invocable: true
disable-model-invocation: false
---

# DesignBuddy 保护机制探测（测试专用）

SKILL.md 标记：`DBP-PRO-SKL-2W6R`

## 目标

如实记录当前安装形态下各项能力的真实表现。

- 这是一个诊断任务：**看不到就说看不到，执行不了就说执行不了**。
- 不要猜测，不要编造标记。

## 纪律（必须遵守）

- 不安装任何东西。
- 只在 `dbprobe-results/protection/` 下写文件。
- 不尝试破解、解密或绕过任何保护机制。只做正常的读取和执行。
- 失败时原样记录错误，然后继续下一步。

## 步骤

| 步骤 | 内容 |
|---|---|
| T1 | 原样复述上面的 SKILL.md 标记 |
| T2 | 读取 @references/protected-reference.md ，复述其中的读取标记。读不到就写 FAIL 和原因 |
| T3 | 说明本 Skill 目录的绝对路径，以及你是如何得知的 |
| T4 | 用文件列表工具或命令列出本 Skill 目录下的所有文件（只列文件名） |
| T5 | 用你的文件读取工具，直接打开 `scripts/protect_probe.py`，只报告：能否打开、是否为可读的 Python 源码、文件中是否包含字符串 `DBP-PRO-SCR-4H8T`。**不要贴出源码内容** |
| T6 | 用第一个可用的解释器（依次尝试 `python3`、`python`、`py -3`）运行：`<python命令> "<Skill目录>/scripts/protect_probe.py"`，然后原样贴出报告块。没有可用的 Python 时记为 BLOCKED |

## 输出报告

```
## DBPROBE PROTECTION REPORT v1.0.0
测试形态（由测试者补充）: WorkBuddy版本=__ | 系统=__ | 来源=本地/市场 | 付费=是/否 | 加密=是/否 | 账号=开发者/购买者
T1 SKILL.md标记: <...> | Result
T2 references读取: <标记或错误> | Result
T3 Skill位置: <...> | 获取方式: <...>
T4 文件列表: <...> | Result
T5 Agent直接读取脚本源码: 能否打开=<..> 是否明文=<..> 含标记=<..> | Result
T6 脚本: <报告块原文>
能力汇总:
  references可读(Agent)=<..>  脚本可执行=<..>  脚本可读资源=<..>
  资源可输出到工作区=<..>  生成器可生成新文件=<..>  模板渲染可用=<..>
  源码对Agent可见=<..>
```
