# 自定义任务配置与运行

配置由项目维护。平台负责创建容器、分配资源和执行入口；代码、环境、输出与恢复逻辑
必须在这个新容器中成立。首先选择[单机或分布式示例](../examples/INDEX.md)。

证据：2026-09-19 的 `volc/1.2.55` 原生模板与 help；vePFS 示例字段来自原包
2026-07-24 CLI 配置记录，尚未用本库示例重新提交。账户权限、可用规格与实际挂载仍需现场核实。

## 配置输入

| 字段 | 含义及填写位置 |
|---|---|
| TaskName | 项目命名的任务，不用名字推断唯一性；提交后记录 ID |
| ImageUrl | 任务实际使用的镜像地址与明确版本，由项目选定 |
| ResourceQueueName | 当前账户有权使用的队列名称，不是存储桶名或计算池简称 |
| Framework | 单进程示例为 Custom；多节点 PyTorch 启动使用 PyTorchDDP |
| TaskRoleSpecs | RoleName、RoleReplicas（实例数）、Flavor（每实例规格） |
| Entrypoint | 在任务容器内执行的命令，使用容器可见绝对路径 |
| Storages | 存储源、子路径、容器挂载点和读写属性 |
| Envs | 当前模板结构为 Name/Value/IsPrivate；示例不携带真实秘密 |
| ActiveDeadlineSeconds | 原生 CLI 模板支持如 `10m`、`1h` 的时长文本；不要据此推导 API 参数类型 |
| RetryOptions | 明确是否重试；第一次 smoke 关闭，便于看到原始失败 |

`RoleReplicas: 2` 表示两台实例，不表示两张卡。总 GPU 数取决于副本数和每实例规格。
不要把 API 响应字段、SDK 构造参数和 CLI YAML 的键名混用。

## 代码与挂载

本库示例使用 vePFS 已存在的项目子目录。`VepfsId` 选择文件系统，`SubPath` 指该文件系统
中的源子目录，`MountPath` 是任务容器里的绝对路径。不能把开发机挂载路径直接当作 SubPath。
源目录要存在，账户/队列要有权限；具体字段大小写以当前导出和 CLI 为准。

示例把项目子目录读写挂到 `/workspace/project`，以便脚本写独立输出目录。
若代码/数据要只读，项目应拆分只读源与可写输出挂载；输出必须落在可写持久目录。
不要为了运行一个项目挂载整个机构共享根目录。

两种代码方式择一即可：

- 已有共享存储：脚本使用任务可见路径，运行期间不修改正在使用的源码目录。
- CLI 上传：显式设置 `UserCodePath` 和 `RemoteMountCodePath`。注意本地目录尾部 `/`
  对上传层级的影响，并在任务内核对实际路径。不要从含凭据的本机目录直接上传。

本库未重新验证上传文件数/大小限制，因此不沿用旧“10 files / 10 GB”作为当前硬限制。
TOS 挂载与数据传输见 [storage.md](storage.md)。

## 入口与日志

项目脚本使用 Bash `set -euo pipefail`，明确解释器、工作目录和输出目录。
优先用目标 venv 的绝对解释器路径。只有项目实际选择 conda 并依赖其激活行为时，才初始化 conda；
不能假设每个镜像都有 `/root/miniconda3`，也不要失败后静默切到另一个环境。

入口进程应返回实际工作负载退出码。需要管道落盘日志时保留 pipefail，避免 `tee` 成功掩盖训练失败。
TensorBoard 开启后将事件写到实际注入的 `TENSORBOARD_LOG_PATH`；普通训练产物写项目输出目录。
不打印整个 `env`，只记录诊断所需的非敏感值和实际模块路径。

## 分布式入口

以下片段放在**项目的任务容器入口脚本**，由 PyTorchDDP 的每个 worker 执行。
`PYTHON_BIN` 与 `TRAIN_SCRIPT` 由项目显式设置为容器可见绝对路径；训练参数也由项目补充。

```bash
set -euo pipefail
: "${PYTHON_BIN:?Set the project Python interpreter}"
: "${TRAIN_SCRIPT:?Set the project training script}"
exec "$PYTHON_BIN" -m torch.distributed.run \
  --nnodes="${MLP_WORKER_NUM:?}" \
  --nproc_per_node="${MLP_WORKER_GPU:?}" \
  --node_rank="${MLP_ROLE_INDEX:?}" \
  --master_addr="${MLP_WORKER_0_HOST:?}" \
  --master_port="${MLP_WORKER_0_PORT:?}" \
  "$TRAIN_SCRIPT"
```

平台 worker 变量用于配置 launcher；训练子进程的 RANK、LOCAL_RANK、WORLD_SIZE
由 launcher 建立，不要把开发机里手工设置的一组 rank 值复制到所有机器。
这里是启动方式示例，未在本轮执行多节点任务。

需要高带宽跨节点训练时，匹配支持相应网络能力的规格、镜像和队列；在两节点上跑最小通信测试。
单机 NCCL 成功或看到 RDMA 设备，不能证明跨节点通信和性能已通过。
不把某次 A100 拓扑、网卡名称或 NCCL 参数当成所有机型的默认值。

## 闲时资源与恢复

本轮原生模板明确包含 `Preemptible`，重试 `PolicySets` 示例包含 `Failed` 和
`InstanceReclaimed`。这些是当前模板证据，**不代表本轮验证了被抢占后的自动恢复**，
也不构成全部枚举的完整列表。

第一次短任务关闭抢占与自动重试。长任务确需闲时资源时，再按当前队列政策开启，
并验证：失败触发重试、checkpoint 写入完成、重新执行入口确实从已完成进度恢复。
平台重新拉起进程不等于恢复模型、优化器、随机数、数据迭代和日志步数。

checkpoint 采用训练框架支持的完整保存/加载方式。单文件可先写临时文件再在同一文件系统
重命名；分片 checkpoint 按框架同步协议完成。共享目录的创建/清理由指定进程负责，
不能让所有 rank 同时删除输出目录。恢复失败应显式报错，不能悄悄从头训练。

来源：[创建训练任务](https://www.volcengine.com/docs/6459/72350?lang=zh)、
[平台训练示例](https://www.volcengine.com/docs/6459/80586?lang=zh)、
[资源规格配置差异](https://www.volcengine.com/docs/6459/1449547)。
