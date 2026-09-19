# 从开发机到第一个自定义任务

先在开发环境跑通项目的最小命令，再从目标镜像启动短任务，验证任务容器里的
环境、挂载、运算和输出。开发机成功、镜像构建成功、提交成功分别证明不同的事情。

本页的 CLI 参数于 2026-09-19 由 `volc/1.2.55` 帮助确认；本库示例尚未运行云端任务。

## 准备

1. 确认所用账户、地域、队列权限、计费/容量与机构约束，见[机构入口](../institutions/INDEX.md)。
2. 在提交机完成 [CLI 安装和私密认证](cli.md)。开发机是否有 GPU 与提交机能否调用 API 是两回事。
3. 项目准备目标镜像、任务容器内的解释器与入口脚本、数据挂载、独立输出目录。
   镜像与开发机的关系见 [images.md](images.md)。
4. 开发环境用同一解释器运行少量真实数据，确认代码 import 的实际路径。
   GPU 任务至少执行真实张量运算；多卡另验证通信，不能仅检查 import 成功。

## 编写和提交

从[单机示例入口](../examples/INDEX.md)复制 YAML 到**项目自己的实验目录**。
填写所有 `__NAME__` 占位符，核对实际镜像、队列、规格、挂载路径和入口。
示例的 10 分钟时限适合短检查；训练任务应根据计划明确设置时限。

任务脚本位于挂载的项目目录，显式使用目标解释器；例如
`Entrypoint: "bash /workspace/project/run.sh"`。
`/workspace/project` 是示例的容器路径，必须与项目脚本一致。
项目若依赖已有绝对路径，就在 YAML 中保留该挂载路径，不强制迁移。

下面的 Bash 命令在**提交机**执行。`TASK_YAML` 必须指向已填写并检查的项目配置。
提交会创建实际云端任务：

```bash
: "${TASK_YAML:?Set the reviewed project YAML path}"
test -f "$TASK_YAML"
volc ml_task submit --conf "$TASK_YAML"
```

记录返回的任务 ID。不因短时没有日志而重复提交；先查询状态和排队原因。

## 查询和验收

```bash
: "${TASK_ID:?Set the returned task ID}"
volc ml_task get --id "$TASK_ID"
volc ml_task instance list --id "$TASK_ID"
```

从实例列表取实际 ID 后查询日志：

```bash
: "${INSTANCE_ID:?Set an instance ID from the list}"
volc ml_task logs --task "$TASK_ID" --instance "$INSTANCE_ID" --lines 100
```

最小成功证据：目标镜像启动、预期代码和解释器被使用、挂载可读写、真实工作负载完成、
输出在持久目录可读取、任务正常结束。将任务 ID、实际配置、命令、结果和限制写入
**项目实验文档**，不写进本库作为所有账户的默认状态。

短任务通过后再增加训练时长、卡数或机器数。需要抢占恢复时，单独验证 checkpoint
恢复语义，见 [custom-tasks.md](custom-tasks.md)。

需要终止本次任务时，核对 ID 后执行 `volc ml_task cancel --id "$TASK_ID"`。
这是停止操作；保留输出和必要日志后再清理项目资产。开发机是否停用由实际使用方决定。
