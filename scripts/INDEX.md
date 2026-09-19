# 维护工具

- [check.py](check.py)：检查本地链接、目录索引、体积与示例中的项目绑定；修改知识库后运行。

从仓库根执行 `python scripts/check.py`，只依赖 Python 标准库。
它不调用云 API，不验证 YAML 的完整平台 schema，也不代替真实任务 smoke。
