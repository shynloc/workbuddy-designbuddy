# DesignBuddy Probe 测试指南（第一轮）

> 你只需要：WorkBuddy 客户端 + 5 个现成的 ZIP。
> 不需要配置任何开发环境，也不需要安装 Python 或 Node。没有 Python 本身就是要记录的测试结果之一。

## 0. 开始前（5 分钟）

### 0.1 下载测试包

从仓库 `tests/probes/dist/` 下载以下 5 个 ZIP（`SHA256SUMS` 文件里有校验值）：

| ZIP | 用途 | 测试编号 |
|---|---|---|
| `dbprobe-environment-1.0.0.zip` | 运行环境探测 | T-ENV |
| `dbprobe-protection-1.0.0.zip` | 加密 / 保护探测 | T-PRO |
| `dbprobe-installation-1.0.0.zip` | 安装链路探测 | T-INS |
| `alpha-demo-brand-system-1.0.0.zip` | 虚构品牌 Alpha | T-MB |
| `beta-demo-brand-system-1.0.0.zip` | 虚构品牌 Beta | T-MB |

### 0.2 安全说明

- 所有测试包都不包含真实品牌、账号或凭据，也不联网。
- 测试包只会在当前工作目录下新建 `dbprobe-results/` 文件夹，不会修改其他文件。
- 测试包被明确禁止直接写入 WorkBuddy 的 Skill 目录。

### 0.3 准备测试文件夹

新建一个空文件夹作为测试工作区，例如 `桌面/DesignBuddy-Probe`。如果 WorkBuddy 支持选择工作目录，请选这个文件夹。

### 0.4 每台机器先记下这些信息

后面填写报告时要用：

- WorkBuddy 版本号（在"关于"或"设置"中查看）；
- 操作系统和版本（macOS 15.x / Windows 11 等）；
- 这台机器在系统终端中是否装过 Python。不确定就写"不确定"。

### 0.5 安装测试包的方法

安装测试包本身也是一个测试点。请记下你用了哪种方式、是否成功：

| 方式 | 操作 |
|---|---|
| 方式 A（优先） | 在 WorkBuddy 对话中发送 ZIP 文件，并输入：`请把这个 ZIP 原样安装为 Skill，不要修改任何文件内容。` |
| 方式 B | 如果客户端有"导入 Skill / 上传 Skill"的入口，用它导入 ZIP，并截图记录入口位置 |

### 0.6 通用规则

- 每个测试都在**新对话**中开始。
- 要求你"原样复制"的报告块，请完整复制，不要删减。
- 截图包括：触发语句、完整的回复，以及任何报错或权限弹窗。
- 你可以直接把报告文字粘贴回来给我，我负责整理到 `docs/runtime-validation-results.md`。

---

## T-ENV：运行环境探测（P0）

**目标**：在 WorkBuddy 真实的 Skill 执行环境中（不是系统终端），确认以下内容：

- 能用哪些 Python / Node / Shell；
- 工作目录在哪里；
- 能否读写文件、能否读取 Skill 自带的文件。

**机器矩阵**：每台机器都跑一次。

| 编号 | 环境 |
|---|---|
| ENV-1 | macOS |
| ENV-2 | Windows（没装过 Python 的机器，如果有的话） |
| ENV-3 | Windows（装过 Python 的机器） |

**步骤**：

1. 用 0.5 的方式安装 `dbprobe-environment-1.0.0.zip`。
2. 新对话，输入：

   ```
   运行 DesignBuddy 环境探测
   ```

3. 如果出现执行命令的权限确认，选择允许，并截图记录。
4. 等待回复中出现 `## DBPROBE ENVIRONMENT REPORT v1.0.0`。

**需要保存**：

- 整段报告文字；
- 截图；
- 工作目录中 `dbprobe-results/` 文件夹里的 `env-*.json`（如果生成了）。

**判断**：

| 项目 | PASS | FAIL / BLOCKED |
|---|---|---|
| A2 references 读取 | 复述出 `DBP-ENV-REF-5K2P` | 读不到或复述错误 |
| A4 解释器 | 至少一个返回了版本号 | 全部报错（不算失败，属于需要记录的事实，A5 会记为 BLOCKED） |
| A5 脚本 | 出现报告块，且 `ENV-WRITE`、`ENV-SELFREAD` 均为 PASS | 脚本无法运行，或这两项 FAIL |
| 结果文件 | `dbprobe-results/` 中出现了 json 文件 | 没有生成文件 |

**注意**：Agent 回复说"成功"不算数，以报告块中的 PASS / FAIL 为准。

---

## T-PRO：保护机制探测（P0）

**目标**：确认在不同安装形态下，以下能力是否可用：

- 读取 references；
- 执行脚本；
- 脚本读取内置资源；
- 把资源输出到工作区；
- 用生成器生成新文件；
- 源码对 Agent 是否可见。

### 必须区分的形态（不能用一种形态的结果代替另一种）

| 形态 | 来源 | 付费 | 加密 | 账号 | 现在能做吗 |
|---|---|---|---|---|---|
| PRO-L | 本地安装 | 否 | 否 | 开发者 | ✅ 现在就做（基线） |
| PRO-M1 | 市场 | 是 | 是 | 开发者本人 | ⛔ **需要你先批准**发布付费测试包 |
| PRO-M2 | 市场 | 是 | 是 | 另一个普通购买者账号 | ⛔ **需要你先批准**购买测试 |

PRO-M1 和 PRO-M2 在你批准之前一律记为 **BLOCKED**，不会用 PRO-L 的结果代替。发布付费测试包属于公开且不可逆的操作，我不会替你执行。

**步骤（PRO-L）**：

1. 安装 `dbprobe-protection-1.0.0.zip`。
2. 新对话，输入：

   ```
   运行 DesignBuddy 保护探测
   ```

3. 回复的报告第一行"测试形态"由你补充：WorkBuddy 版本、系统、本地、否、否、开发者。

**需要保存**：

- 整段报告；
- 截图；
- `dbprobe-results/protection/` 整个文件夹。

### 可选的人工检查

这一步回答"用户自己能否在电脑上找到原文"。在系统终端执行，只读、不修改任何东西。如果不方便，可以跳过，记为 NOT_TESTED。

- macOS：

  ```
  grep -rl "DBP-PRO-REF-7Q3K" ~/Library/Application\ Support ~/.workbuddy 2>/dev/null | head
  ```

- Windows PowerShell：

  ```
  Get-ChildItem $env:APPDATA,$env:LOCALAPPDATA -Recurse -File -ErrorAction SilentlyContinue | Select-String -Pattern "DBP-PRO-REF-7Q3K" -List | Select-Object -First 10 Path
  ```

找到的路径就是 Skill 在本地的存放位置，同时说明该文件以明文存储。

**判断（每一项分别记 PASS / FAIL）**：

| 能力 | 报告中对应的项 | PASS 条件 |
|---|---|---|
| Agent 读取 references | T2 | 复述出 `DBP-PRO-REF-7Q3K` |
| 脚本可执行 | T6 中的 `P-EXEC` | PASS |
| 脚本读取资源 | `P-RES-READ` | PASS |
| 资源可输出到工作区 | `P-RES-EXPORT` | PASS |
| 生成器生成新文件 | `P-GEN-EMBED`、`P-GEN-RENDER` | PASS |
| 源码对 Agent 可见 | T5 | 只记录事实：在加密形态下，"不可见"是我们希望看到的结果 |

### 结论怎么用

最关键的组合是：在加密形态下，`P-EXEC`、`P-GEN-RENDER` 为 PASS，同时 T5 显示源码不可见。如果是这样，就说明完整的 Compiler 架构可以保留。

---

## T-INS：安装链路探测（P0）

**目标**：打通至少一条可以**重复成功**的路径：

```
生成 Brand Skill → 原生安装交接 → 用户确认 → 安装 → 核对
```

**步骤**：

1. 安装 `dbprobe-installation-1.0.0.zip`。
2. 新对话，输入：

   ```
   运行 DesignBuddy 安装探测
   ```

3. Agent 会先生成一个测试 Skill `dbprobe-generated-hello`，列出可用的安装方式（H1–H4），然后停下来等你确认。
4. 回复 `确认安装 H1`（如果列出了 H1），按提示完成。
5. **新对话**，输入：

   ```
   运行 DesignBuddy 安装验证
   ```

6. 查看报告中 `selfcheck: overall`。

**每种方式单独测一轮**：

- 测完一轮后，先在 WorkBuddy 中删除 `dbprobe-generated-hello`。
- 然后从第 2 步重新开始，依次测 H2、H3、H4（只测 Agent 列出的、确实存在的方式）。
- H3 是由你亲自复制并发送 Agent 给出的那句安装指令。
- H4 是你用 0.5 的方式 B 手动导入 ZIP。

**升级测试**（任选一种已经成功的方式）：

1. 在 `dbprobe-generated-hello` 1.0.0 仍然安装着的情况下，新对话输入：

   ```
   运行 DesignBuddy 安装探测，版本 1.1.0
   ```

2. 安装后，用"运行 DesignBuddy 安装验证"核对。
3. 记录平台的行为：覆盖、并存，还是报错。

**判断**：

| 结果 | 条件 |
|---|---|
| PASS | 安装成功；验证报告显示 `overall: MATCH`；`build_id` 与生成时一致；`MUST-COLOR-01` 的值正确（1.0.0 为 `#2F6FEB`，1.1.0 为 `#0F7B5F`） |
| PARTIAL | 安装成功，但出现 `MISMATCH-NEWLINE-ONLY`（只有换行符被改动），或出现 `EXTRA` 文件 |
| FAIL | 安装失败、`MISMATCH`、`MISSING`，或者 `build_id` 不一致（说明安装的不是这次生成的版本，或者被重新生成了） |

**需要保存**：探测报告、验证报告、每一步的截图，以及平台的提示原文。

---

## T-MB：多品牌消歧（P1）

**目标**：记录 WorkBuddy 调度品牌 Skill 时的**真实行为**。我们不能只因为 description 写得好，就宣称消歧一定有效。

**怎么判断触发了哪个品牌**：每个品牌 Skill 被使用时，回复第一行必须是 `【品牌系统】Alpha Demo v1.0.0（…）` 或 `【品牌系统】Beta Demo v1.0.0（…）`。没有这一行，就说明没有触发任何品牌 Skill。

### 第一组：只安装 Alpha

每条都在新对话中测试。

| 编号 | 输入 | 期望 |
|---|---|---|
| MB-1 | `给 Alpha Demo 做一份 3 页的产品介绍 PPT 大纲和版式说明` | 触发 Alpha |
| MB-2 | `帮阿尔法示例设计一张小红书封面，文案：秋季新品发布` | 触发 Alpha |
| MB-3 | `做一份 3 页的 PPT，主题是团队周报` | 不触发 Alpha；如果触发了，必须先问用户用哪个品牌 |

### 第二组：同时安装 Alpha 和 Beta

| 编号 | 输入 | 期望 |
|---|---|---|
| MB-4 | `做一份 PPT。` | 不随机选品牌；先询问，或不套用任何品牌 |
| MB-5 | `给 Alpha 做一份 PPT 封面页和一页内容页的版式。` | 只触发 Alpha |
| MB-6 | `给贝塔示例做一张活动海报，标题：周末读书会` | 只触发 Beta |
| MB-7 | `这是 Beta Demo 的一页文档内容：「欢迎来到周末读书会，本期主题是城市散步。」请把它改成 Alpha Demo 的风格。` | 识别出 source = Beta、target = Alpha；输出只使用 Alpha 的颜色和字体（标题字体为思源黑体，主色为 #1F4FD8） |
| MB-8 | 同一对话中先完成 MB-5，再输入 `再做一张海报` | 可以继续沿用 Alpha，但必须声明使用的是 Alpha |

### 判断

| 结果 | 条件 |
|---|---|
| PASS | 行为与"期望"一致 |
| PARTIAL | 选对了品牌，但缺少第一行声明；或者先问了用户，但问得不清楚 |
| FAIL | 用错品牌、随机套用品牌、两种品牌规则混用；或者在 MB-7 中输出了 Beta 的颜色或字体 |

### 需要保存

每条测试的截图，以及第一行和回复中的颜色值、字体名、QA 报告行。

如果时间允许，MB-1 到 MB-3 可以各重复一次。同一提示词两次结果不同，本身就是需要记录的重要信息。

---

## 清理（全部测试完成后）

1. 在 WorkBuddy 中删除以下 Skill：
   - `dbprobe-environment`
   - `dbprobe-protection`
   - `dbprobe-installation`
   - `dbprobe-generated-hello`
   - `alpha-demo-brand-system`
   - `beta-demo-brand-system`
2. 保存需要的证据后，删除测试工作区中的 `dbprobe-results/` 文件夹。
3. 如果做过付费测试（PRO-M1/M2）：由你决定是否下架测试包。下架、退款等操作都需要你亲自执行。
4. 这些测试不会修改你已有的正式 Skill 和专家。如果发现有被修改的迹象，请立即告诉我。

---

## 人工验证清单

| ✔ | 编号 | 内容 | 机器 | 优先级 | 需要你批准 |
|---|---|---|---|---|---|
| ☐ | ENV-1 | 环境探测 | macOS | P0 | 否 |
| ☐ | ENV-2 | 环境探测 | Windows（无 Python） | P0 | 否 |
| ☐ | ENV-3 | 环境探测 | Windows（有 Python） | P0 | 否 |
| ☐ | PRO-L | 保护探测：本地未加密基线 | macOS（Windows 可选） | P0 | 否 |
| ☐ | PRO-M1 | 保护探测：市场付费加密 + 开发者账号 | 任一 | P0 | **是**（发布付费测试包） |
| ☐ | PRO-M2 | 保护探测：市场付费加密 + 普通购买者账号 | 任一 | P0 | **是**（另一个账号购买） |
| ☐ | INS-H1..H4 | 安装交接：每种可用方式各一轮 + 安装验证 | macOS + Windows | P0 | 否 |
| ☐ | INS-UP | 1.0.0 → 1.1.0 升级 | 任一 | P0 | 否 |
| ☐ | MB-1..3 | 只装 Alpha | 任一 | P1 | 否 |
| ☐ | MB-4..8 | 同时装 Alpha 和 Beta | 任一 | P1 | 否 |

### 每条结果需要回传的信息

```
测试编号 · 机器/系统 · WorkBuddy 版本 · Skill 来源（本地/市场）
· 是否加密 · 账号类型 · 报告原文 · 截图
```
