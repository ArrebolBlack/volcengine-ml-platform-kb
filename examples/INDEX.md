# 任务与开发机示例

## 火山原生任务 YAML

| 示例 | 用途 | 何时读取 |
|---|---|---|
| [task-single.yaml](task-single.yaml) | 一个 worker 的短任务起点 | 第一次验证镜像和挂载，或改为单机训练 |
| [task-distributed.yaml](task-distributed.yaml) | 两个 worker 的 PyTorchDDP 配置起点 | 项目确实需要跨节点训练时 |

两份文件是**待填写示例**，不是可直接提交的配置。将它们复制到项目实验目录，填写全部
`__NAME__`，准备任务容器内实际入口脚本，按 [任务说明](../docs/custom-tasks.md)核对字段。
示例不上传本地目录；代码由明确的 vePFS 子目录挂载提供。

公共字段参考 2026-09-19 实际生成的 `volc/1.2.55` 原生模板；vePFS 字段来自原知识库
2026-07-24 的 CLI 配置记录，本轮未重新提交验证。示例通过本地结构检查不等于云端运行成功。
机构/账户/镜像实际参数由项目提供，示例不预设其值。

## Zenith 个人 API 示例

- [zenith-instance.json](zenith-instance.json)：开发机创建字段，默认 `personal_first`；项目卡时选择按 [Zenith 快速开始](../docs/zenith-quickstart.md#3b-新开发机准入与创建)填写。
- [zenith-job.json](zenith-job.json)：默认低优的单 Worker 训练；标准训练使用项目卡时的字段修改见[提交步骤](../docs/zenith-quickstart.md#3c-自定义训练准备准入提交与结果)。

`__...__` 是必须替换的占位符；示例不含 Token、真实资源 ID 或已验收的训练配置。
它们是 Zenith HTTP body，不是上述原生 `volc` YAML。
