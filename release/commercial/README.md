# 这里不是安装包

本目录只存放构建商业版时使用的**替换件**：`SKILL.md`。它会替换 QA 版的 SKILL.md。它不能单独上传。

**上传开放平台请使用完整的 ZIP：**

```
dist/v1.0.0/designbuddy-v1.0.0.zip
```

ZIP 内的结构如下（共 28 个文件，符合 WorkBuddy Skill 规范）：

```
designbuddy/
├── SKILL.md                    # 就是本目录中的这个文件
├── references/  (4)            # design-workflow · compiler-contract · installation-handoff · safety
├── scripts/     (12)           # designbuddy.py + dbcore/ 编译器
└── templates/   (11)           # 品牌 Skill 模板、预览 / 可移植模板、方向库、字体库、package-manifest
```

ZIP 由 `python3 tools/build_commercial.py` 从 `designbuddy-qa/` 的源码和本目录的 SKILL.md 生成。
