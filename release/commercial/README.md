# 这里不是安装包

本目录只存放构建商业版时使用的**替换件**：`SKILL.md`。它会替换 QA 版的 SKILL.md。它不能单独上传。

**上传开放平台请使用完整的 ZIP：**

```
dist/v1.0.0/designbuddy-v1.0.0.zip
```

ZIP 内的结构如下（共 27 个文件；开放平台只接受**两级目录**：根目录/二级目录/文件）：

```
designbuddy/
├── SKILL.md                    # 就是本目录中的这个文件
├── references/  (4)            # design-workflow · compiler-contract · installation-handoff · safety
├── scripts/     (11)           # designbuddy.py + db_*.py 编译器模块
└── templates/   (11)           # brand-skill.* / preview.* / portable.* 模板、data.* 方向库与字体库、package-manifest
```

ZIP 由 `python3 tools/build_commercial.py` 从 `designbuddy-qa/` 的源码和本目录的 SKILL.md 生成。
