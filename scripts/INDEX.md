# 维护工具

- [check.py](check.py)：检查本地链接、目录索引、体积与示例中的项目绑定；修改知识库后运行。
- [zenith_api.py](zenith_api.py)：标准库 Personal API HTTP 入口；按 [Zenith 快速启动](../docs/zenith-quickstart.md) 查询、预检、提交和追踪计算资源，不依赖官方 CLI。
- [test_zenith_api.py](test_zenith_api.py)：验证凭据读取、请求边界、项目付款字段透传、幂等键和操作回执；修改 HTTP 入口或提交示例后运行。

从仓库根执行 `python scripts/check.py`，只依赖 Python 标准库。
它不调用云 API，不验证 YAML 的完整平台 schema，也不代替真实任务 smoke。

HTTP 入口测试：`python -m unittest discover -s scripts -p test_zenith_api.py`。测试使用模拟响应，不调用平台写接口。
