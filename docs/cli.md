# volc 命令与配置

以下命令形态于 2026-09-19 在 Linux `volc/1.2.55` 上核查。
初次核查仅执行版本、各子命令 `--help` 和 `ml_task template`。后续项目短任务实际验证了 submit、cancel、get/list JSON 查询及正常退出；未验证通用示例本身或配置导出。项目任务与计算证据由所属实验保存。
`volc` 是 veMLP 工具；不要用通用云 CLI `ve` 代替，也不要拼成 `vloc`。

## 安装与认证

从[官方 CLI 安装说明](https://www.volcengine.com/docs/6459/72394)选择当前操作系统和架构的安装方式。
本库不携带可执行文件，不固定旧下载地址。安装完成后，在**提交机 Bash**检查：

```bash
command -v volc
command -v mlp
volc version
volc ml_task --help
```

在本轮机器上，`volc` 会调用 `mlp`。仅使用 `volc` 绝对路径仍可能报
`exec: "mlp": executable file not found in $PATH`。将实际安装目录加入 PATH：

```bash
: "${VOLC_BIN_DIR:?Set the directory containing volc and mlp}"
export PATH="$VOLC_BIN_DIR:$PATH"
volc ml_task --help
```

这一步尤其适用于非交互 SSH。PowerShell 使用
`$env:PATH = "$env:VOLC_BIN_DIR;$env:PATH"`，事先设置该变量为实际 Windows 安装目录。
不要在 PowerShell 原样使用 Bash 的 `export`、单引号包裹脚本或反斜杠续行。
本轮未安装或运行 Windows 版 CLI；可从 Windows SSH 到已有 Linux 提交机执行。

首次认证在自己的私密终端运行 `volc configure`，交互输入账户的 AK/SK 与地域。
Linux 配置位于 `~/.volc/config`、`~/.volc/credentials`，不要打印其内容。
用 `umask 077` 创建私密文件；认证后可对现有两文件执行 `chmod 600`。
这些文件不得复制进任务源码、共享数据盘或镜像。

## 命令速查

表中大写名称为需替换的值；`INSTANCE_ID` 取实际实例列表，不推测名称。

| 操作 | 命令 | 说明 |
|---|---|---|
| 看当前任务 | `volc ml_task list` | 默认只含 Queue/Staging/Running/Killing，不代表完整历史 |
| 看完成与失败任务 | `volc ml_task list --status Success,Failed,Killed --limit 20 --output json` | 帮助确认这些参数；需自行翻页时用 offset |
| 查询详情 | `volc ml_task get --id TASK_ID` | 查询响应不等同于提交 YAML |
| 列实例 | `volc ml_task instance list --id TASK_ID` | 是 instance list，不是 instances |
| 读日志 | `volc ml_task logs --task TASK_ID --instance INSTANCE_ID --lines 100` | 追加 `-f` 持续读取，Ctrl-C 只结束读取 |
| 导出配置 | `volc ml_task export --task TASK_ID --config` | 写入当前目录；使用私密工作目录，再选择所需非敏感字段 |
| 原生模板 | `volc ml_task template --path task.template.yaml --example=false` | 本地写文件；path 应选新文件，避免覆盖自己的配置 |
| 提交 | `volc ml_task submit --conf task.yaml` | 创建云任务 |
| 停止 | `volc ml_task cancel --id TASK_ID` | 停止精确任务；不是删除数据 |

当前顶层帮助没有 `ml_task delete`。不要从 `DeleteJob` 等 OpenAPI 名称猜 CLI 命令。
2026-09-19 Linux 1.2.55 实测：不带 `--output` 的 `get` 会进入交互界面，非交互 SSH 应使用 `get --id TASK_ID --output json`。`list --name` 实测匹配任务名称，传任务 ID 得到空列表时不能据此判定任务不存在；已知 ID 用 `get --id`。JSON 摘要不包含完整排队原因，必要时查官方 GetJob 的 Status.Message。 多个监控同时调用 GetJob 曾触发 `AccountFlowLimitExceeded`，属于账户API限流，不能解释为训练失败或无任务。应串行查询并间隔请求；本次约2秒间隔可读回，非平台承诺的固定QPS。`-o yaml` 尚未验证为可提交格式；导出使用上表的 `export`。

## 提交字段与覆盖

实际生成的 1.2.55 模板使用 `TaskName`、`ImageUrl`、`ResourceQueueName`、
`Framework`、`TaskRoleSpecs[].Flavor`、`Entrypoint`。
它还生成了过时的示例镜像与示例规格，不能把生成成功当成这些资源仍可用。
模板注释中的部分命令缺少 `submit`；实际命令以本页经 help 核对的形态为准。

`submit --help` 确认：

- `--resource_queue_name` 优先于 `--resource_queue_id`；旧 `--resource_group_id` 已弃用。
- `--set` 可以替换模板变量或覆盖配置项，其优先级低于相应专用 flags。
- `--preemptible` 为提交参数；默认 false。
- `--priority` 完整范围为1–9，按数值从高到低调度；提交者只能使用其中获准档位。2026-09-20在1.2.55实测：同一账户在不同队列对9可接受或以“user is not queue admin”明确拒绝，6可接受。项目按授权选择最高可用档位；明确拒绝且未创建任务后才降低，不因超时或排队重复提交。实际值从GetJob的`ResourceConfig.Priority`核对，不能读顶层Priority。

日常先保持一份可审阅的完整项目 YAML，再用标准 submit 命令。需要批量覆盖时才使用
`--set TaskName=...`；包含逗号、引号、Shell 变量或嵌套结构时先检查解析行为，
不要同时混用多种覆盖方式而使最终配置不明。

本轮没有发现并验证 submit 的 `--dry-run`；不能自行添加这个 flag。
生成模板、语法解析通过、读帮助都不能证明服务器会接受配置。

## 版本变化

当前安装提示存在 1.2.57 更新，但本库只声明 1.2.55 的核查结果。
不为阅读知识库自动升级共享安装。需要升级时先在选定安装中核对版本、help、原生模板，
再更新受影响的例子；旧任务的 API 响应、CLI 输入和 Python SDK 参数不能机械互换。

官方入口：[CLI](https://www.volcengine.com/docs/6459/72394)、
[创建任务](https://www.volcengine.com/docs/6459/72350?lang=zh)。
部分官网页面在自动读取时可能只有 JavaScript 壳；遇到这种情况记录未核验项，使用实际安装的 help 对账。
