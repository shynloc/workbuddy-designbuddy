# 多品牌独立新会话测试（MB-003 ~ MB-005）

前提：已在用户明确确认后安装 `alpha-demo-brand-system` 和 `beta-demo-brand-system`（见 artifacts/）。
每条测试都要**新开一个会话**，粘贴提示词，记录回复中实际使用的品牌、颜色、字体。

## MB-003（只触发 Alpha）

```
给 Alpha Demo 做一份 PPT 封面页和一页内容页的版式说明。
```
PASS：回复声明使用 Alpha Demo 品牌系统；主色 #1F4FD8；标题字体 Source Han Sans SC。

## MB-004（不擅自套用品牌）

```
做一份 PPT。
```
PASS：没有套用任何品牌，或先询问用户使用哪个品牌。FAIL：直接套用了 Alpha 或 Beta。

## MB-005（品牌转换）

```
这是 Beta Demo 的一段文档：「欢迎来到周末读书会，本期主题是城市散步。」请把它改成 Alpha Demo 的风格。
```
PASS：明确 source=Beta Demo、target=Alpha Demo；输出只使用 Alpha 的颜色（#1F4FD8 等）和字体。FAIL：混用 Beta 的颜色或字体。

## 回填结果

回到 QA 会话，让 Agent 执行（示例）：
```
python <designbuddy-qa>/scripts/designbuddy.py record --run <报告目录> --id MB-003 --result PASS --actual "<实际回复摘要>" --evidence "<截图文件名>" --context "新会话 / macOS / WorkBuddy x.y"
```
