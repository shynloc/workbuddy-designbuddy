# DesignBuddy v1.0.0 — Release Notes

首个商业版本。

## 功能

- 三种起点：已有品牌 / 部分资料 / 从零开始；
- Brand IR（JSON，schema 1.0.0）作为唯一事实来源，带来源与置信度；
- G1–G6 确认关卡；
- 编译输出：
  - WorkBuddy 品牌 Skill：17 份规范、消歧规则、品牌 QA、自检脚本；
  - Portable Design System：DESIGN.md、DTCG tokens.json、tokens.css；
  - 离线预览；
  - 来源报告；
- WCAG AA 对比度放行关卡，字体和素材许可治理；
- 交付到下载文件夹（`DesignBuddy/<品牌>/`），附安装说明，不覆盖已有文件；
- 本地运行，不联网，只用 Python 标准库。

## 来源

由 QA 候选版 v0.1.0 → v0.1.3 演进而来，经过 3 轮修复（包括两轮 Windows 真机测试）。剔除了 QA Runner 和测试夹具。

## 校验

见 `SHA256SUMS.txt`、`PACKAGE_FINGERPRINT.txt`、`BUILD_VERIFICATION.md`。
