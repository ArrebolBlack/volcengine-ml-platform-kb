# Zenith 平台入口与 Agent 快速开始

Zenith 是 `http://10.1.130.101` 上的多云算力平台，具有独立账号、资源归属、配额和个人 API。
**创建/启动开发机或提交训练，先读 [可执行快速开始](zenith-quickstart.md)。**
原生火山 `volc` 的身份、YAML、队列和资源 ID 不可直接套用到 Zenith。

## 按任务阅读

| 任务 | 入口 |
|---|---|
| 新项目接入、查询、创建/启动开发机、提交任务、恢复回执 | [可执行快速开始](zenith-quickstart.md) |
| SSH、DDP、训练排队、抢占、回收与推理 | [计算与训练](zenith-compute.md) |
| 区 10 PFS、TOS、500 GiB 数据、镜像、数据集 | [数据与资产](zenith-data.md) |
| API 字段、官方 CLI、Token、项目、卡时与角色 | [账户与 API](zenith-account-admin.md) |

SE3-WAM 的新执行对话从项目 `docs/resources/zenith_workflow.md` 进入实际流程；
该页串起现有实验、提交登记、连续训练、监控和结果验收，本库维护其中的平台共性。

控制台：[总览](http://10.1.130.101/my)、[开发机](http://10.1.130.101/my/instances)、
[任务](http://10.1.130.101/my/jobs)、[文件与存储](http://10.1.130.101/my/storage)、
[组织与项目](http://10.1.130.101/my/organization)、[Token](http://10.1.130.101/api-tokens)。
帮助中心支持搜索及 `Ctrl+K`。钉钉扫码由用户完成；浏览器 Cookie、API Token 和 SSH 密钥是三套认证。

其他项目记录本库 checkout 路径、链接所需主题，并维护自己的镜像、命令、数据路径和结果。
不要复制整套知识库。GPU Fleet 只读监控；启动看板不会创建资源，也不会给另一个终端自动配置凭据。

## 2026-10-12 定向复核

本轮匿名 [OpenAPI](http://10.1.130.101/pt/api/openapi.json) 仍为 **3.8.0、60 个路径、63 个操作**；
capabilities 的已验证版本来自 10 月 11 日查询，本轮没有调用个人 Token 或创建计算资源。
相较 3.7.0，两类创建的 `bucket_mount_ids` 更新了新挂载点规则，旧挂载和已保存操作的路径保留；
具体路径统一见[数据与资产](zenith-data.md#挂载权限与现有机器补挂)。未新增启停或改配字段。
前次存储帮助的 `Last-Modified` 为 `2026-10-10 15:50:46 GMT`
（北京时间 23:50:46），不是逐篇正文修改时间。

镜像目录当前允许每页最多 500 条，须按 `total` 读取完整目录；开发机存储模式新增 `auto`，
训练契约仍不接受 `storage_mode`。项目 TOS/BOS 挂载目录与 `bucket_mount_ids`，以及登记盘和数据集
的选择边界见[数据与资产](zenith-data.md#挂载权限与现有机器补挂)；查询步骤见[快速开始](zenith-quickstart.md)。
10 月 11 日已用现有 Token 只读查询项目、授权盘、桶挂载候选、镜像目录并执行准入预检；
这轮只读查询本身不证明原生桶挂载、镜像拉取或训练创建；后续真实执行证据见下表。
账号授权与瞬时容量由使用方项目记录。

## 2026-10-07 更新核查（历史）

通过帮助导航和正文链接取得 **35 页（首页 + 34 篇专题）**，页面集合未比 10 月 3 日增加。
帮助 HTML 的 `Last-Modified` 为 `2026-10-05 17:24:56 GMT`（北京时间 10 月 6 日 01:24:56）；
这是站点部署时间，不等于每篇正文修改时间。旧平台标签页曾显示“页面资源加载失败”；
保存未提交内容后刷新加载新版本，不能把该提示当作 Token 失效。

当时匿名 [OpenAPI](http://10.1.130.101/pt/api/openapi.json) 为 **3.1.0、59 个路径、62 个操作**
（1 个为匿名文档读取）；该次 Token 的 `capabilities.api_version` 同为 `3.1.0`。
原 2.0.1/29 路径和 2.19.0/57 路径均是历史基线。

| 变化 | 应对 |
|---|---|
| 训练 API 3.0 起移除 `max_runtime_seconds`，包括 null 都拒绝 | 删除旧字段；需要时限时由工作负载处理保存和退出 |
| 训练 `image_vendor`、`framework` 标为兼容字段 | 新接入优先资源区与精确镜像 ID；分布式框架仅在目标厂商已验证时选择 |
| 低优训练不扣个人/项目卡时，仍计量 GPU 用量 | 费用与运行量分开；不推导低优开发机免费 |
| 百度/火山标准训练默认每人每队列 64 卡，超额可进入 Zenith 等待 | 管理员可改；API 256 副本不是可用节点保证 |
| 低优按用户份额调度，份额回收后整任务自动重新排队 | 入口自行恢复 checkpoint，不会自动缩小申请卡数 |
| 新增训练指标查询，训练终端仅总管理员 | `jobs:read` 可读指标，不授予训练终端 |
| 开发机低 GPU 回收不再因 CPU、显存或进程存在而豁免 | 正式批量训练优先使用任务 |
| 本人可在控制台调整同区项目/公共盘；百度可能动态分配 SSH 端口 | 停启后重新取端点；个人 Token 仍不能手动挂载 |
| Token 可在控制台调整适用范围，CLI 文档已有官方仓库链接 | 按 capabilities 核对 scope；不再按旧说明反复搜索包源 |

来源：[个人 API](http://10.1.130.101/help/reference/personal-api.html)、
[训练](http://10.1.130.101/help/workloads/training.html)、
[实例](http://10.1.130.101/help/compute/instances.html)、
[卡时](http://10.1.130.101/help/projects/quotas-billing.html)、
[CLI](http://10.1.130.101/help/guide/cli-workflows.html)。

帮助内部仍有旧文字：API 页总版本写 2.11.0，CLI 页同时出现 2.17.0/2.14.0；
训练页仍有最长运行时间、旧个人任务资格和“活动保护”；部分挂载段仍称仅总管理员。
执行以当前 schema、专题新规则及实际响应核对，不把控制台管理员能力套入个人 Token。

## 自动化结论

可复用路线是 **个人 HTTP API + 系统 OpenSSH + 项目训练入口**。
本库的小型 Python 标准库请求工具串起参数发现、准入、提交、回执恢复和查询；
不改变平台协议、不自动选择资源区或重试创建，不引入调度器。

官方 `zenith` CLI 仍未实现创建开发机、创建/读取训练任务和日志等命令，Windows 尚未获官方验收。
不要把 `NOT_IMPLEMENTED` 当作网络错误反复 debug。HTTP API 不依赖 CLI；
SSH 私钥、公钥引导及首次可信主机确认仍需准备。

删除/重建、手动挂载、镜像资产、Token 和管理功能仍走对应控制台流程。
因此可简化常规研究启动，不能声称全平台完全 CLI 或所有项目零调试：
依赖、数据位置、checkpoint 恢复与分布式通信仍须最小实测。

## 实测证据与剩余边界

| 日期 | 已验证范围 |
|---|---|
| 2026-09-27 | 区 10 双 PRO6000：Windows OpenSSH 非交互连接、GPU 和 GPFS/PFS 核查；用户已有公钥/私钥 |
| 2026-10-03 | 控制台区 10 单卡标准个人任务 `codex-zenith-smoke-20261003`（`job-9uj1k1efxlgf`）成功；任务写个人 PFS 后开发机停启仍可读，SSH 复连通过；临时文件已清理 |
| 2026-10-03 | Token 只读 API：本人资源、目录、项目、状态/日志/副本；GPU Fleet 只读集成 |
| 2026-10-07 | 当前帮助、OpenAPI、capabilities、本人资源和目录的只读核查；新工具的验证范围见快速开始 |
| 2026-10-10–11 | HTTP helper 已用于区 10 现有开发机启停、单/双卡改配和停机确认；新建请求经历厂商分配失败，没有运行成功；TOS 完整数据副本恢复及核验范围见 [SE3-WAM 项目资源文档](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/resources/volcengine_custom_tasks.md) |
| 2026-10-11 | 区 10 个人镜像保存、目录登记和单卡 JOB 实际拉取；该 JOB 在继承 rank 环境检查处失败，取消回执及 FAILED 终态已确认。后续七组 JOB 使用同一镜像加独立源码/deps 实际训练，见项目资源文档，不等于镜像内 E-only 全功能验收。 |
| 2026-10-11–12 | 区 5/10 JOB 原生训练、PFS checkpoint/日志读回、单机及多节点通信与部分完整状态恢复已有实证；具体拓扑、数值与科学验收范围见 [历史编码实验](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/experiments/DB0-TRAIN0/results/history_encoding_fresh_20261010/interruption-report.md)及[四臂部署](https://github.com/ArrebolBlack/se3-wam-research/blob/main/docs/experiments/DB0-TRAIN0/results/object_reconstruction_late_fresh_20261011/pro6000/deployment.md)。 |

10 月 3 日控制台任务没有可见日志/副本行；API 读取成功不等于已取得完整应用日志。
已有机操作不证明 API 新建开发机运行成功、实例 reboot 或官方 CLI 写入已验收。
低优免费记账、真实回收重排及跨 allocation 精确恢复、其他厂商/未测拓扑、STS 和原生桶训练吞吐仍未验证。
区 5 原生桶实际挂载和小块读取已有项目证据，不代表对象挂载具有完整 POSIX 替换语义；
TOS 缓存/容量与长期吞吐的限制见[数据页](zenith-data.md)。
真实实验在使用方的唯一主文档记命令和结果；本库不保存瞬时余卡、
余额、排队状态或凭据。历史短任务不证明长训练稳定。

## 最短排障

| 现象 | 先检查 |
|---|---|
| 请求超时但浏览器能开 | 内网路由和代理；本机已验证显式直连，见快速开始 `--direct` |
| 401 / 403 | Token 有效期、scope、所有权、端点是否向个人 Token 开放 |
| 已受理却无资源 ID | 保留原 key/body 查询原操作，不能改名或换 key 重建 |
| 有余卡却排队 | 节点碎片、并发上限、低优份额、项目准入、镜像及存储 |
| SSH 停启后失联 | 当前运行态、公钥注入、最新结构化端点，尤其百度动态端口 |
| 有目录却找不到数据 | 用 `findmnt` 核对来源、资源区、用户卷；同路径不保证同存储 |
| 单进程入口报告 DDP / CUDA 设备不可见 | 查继承的 rank 变量及 CUDA/NVML/EGL 设备身份，见[计算页](zenith-compute.md) |
| 保存失败但 df 有空闲 | 查 Fileset/用户/组配额、写入身份与原始保存异常，见[数据页](zenith-data.md) |
| 完成却无结果 | 真实退出、持久输出及指标；平台完成不等于科学验收 |

## 帮助原文路由

以下范围已获取核查；后续 Agent 按主题阅读，不必每次遍历全站。

| 分组 | 原文 |
|---|---|
| 开始 | [简介](http://10.1.130.101/help/guide/platform-overview.html)、[登录](http://10.1.130.101/help/guide/getting-started.html)、[总览](http://10.1.130.101/help/guide/dashboard.html)、[快速开始](http://10.1.130.101/help/guide/quick-start.html)、[资源](http://10.1.130.101/help/resources/overview.html) |
| 计算 | [工作台](http://10.1.130.101/help/compute/workbench.html)、[实例](http://10.1.130.101/help/compute/instances.html)、[连接](http://10.1.130.101/help/compute/connection.html)、[训练](http://10.1.130.101/help/workloads/training.html)、[推理](http://10.1.130.101/help/workloads/inference.html) |
| 资产 | [镜像](http://10.1.130.101/help/assets/images.html)、[模型](http://10.1.130.101/help/assets/models.html)、[广场](http://10.1.130.101/help/assets/plaza.html) |
| 数据 | [存储](http://10.1.130.101/help/data/storage.html)、[数据集](http://10.1.130.101/help/data/datasets.html)、[换机迁移](http://10.1.130.101/help/data/storage-migration.html)、[分享](http://10.1.130.101/help/data/file-shares.html)、[跨云迁移](http://10.1.130.101/help/data/file-migrations.html) |
| 项目 | [项目](http://10.1.130.101/help/projects/overview.html)、[卡时](http://10.1.130.101/help/projects/quotas-billing.html)、[学生制度](http://10.1.130.101/help/projects/student-resource-policy.html)、[组织](http://10.1.130.101/help/account/organization.html) |
| 账户 | [SSH](http://10.1.130.101/help/account/ssh-keys.html)、[Token](http://10.1.130.101/help/account/api-tokens.html)、[个人 API](http://10.1.130.101/help/reference/personal-api.html)、[CLI](http://10.1.130.101/help/guide/cli-workflows.html)、[通知](http://10.1.130.101/help/account/notifications.html)、[反馈](http://10.1.130.101/help/account/feedback.html) |
| 管理 | [纳管](http://10.1.130.101/help/admin/resources.html)、[平台管理](http://10.1.130.101/help/admin/platform.html)、[权限](http://10.1.130.101/help/reference/permissions.html)、[厂商](http://10.1.130.101/help/reference/vendors.html)、[排障](http://10.1.130.101/help/troubleshooting/common.html)、[FAQ](http://10.1.130.101/help/troubleshooting/faq.html) |
