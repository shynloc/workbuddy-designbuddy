# DesignBuddy QA v0.1.4 — Release Notes

> 测试候选版，**不要上传到开放平台**。商业版见 `dist/v1.0.0/`。

- 包结构改为两级目录（开放平台要求）：`scripts/db_*.py`、`templates/<类别>.<文件>`。生成的品牌 Skill 也改为两级。
- lint 新增层级检查。
- 开发机验证：单元测试 23/23；在解压副本中 SCRIPT 用例 59/59（见 `qa/TEST_REPORT_LOCAL.md`）。
- 校验和：`SHA256SUMS.txt`、`PACKAGE_FINGERPRINT.txt`。
