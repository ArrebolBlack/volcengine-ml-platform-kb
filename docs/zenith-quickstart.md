# Zenith 可执行快速开始

适用于本项目或新项目的 **Python 3 + 个人 HTTP API + OpenSSH** 路线，不依赖官方 CLI 安装。
使用 [zenith_api.py](../scripts/zenith_api.py)，先读参数和做查询，再执行所需分支。
字段依据 2026-10-12 定向复核的 OpenAPI 3.8.0；[账户与 API](zenith-account-admin.md)解释完整权限，
[计算页](zenith-compute.md)解释 DDP/回收，[数据页](zenith-data.md)解释持久路径和大数据。

SE3-WAM 执行对话先读项目的 `docs/resources/zenith_workflow.md`，使用其现有提交适配器登记负责对话、
逻辑 job 和 attempt 后再 POST。下文是通用 API 流程，直接执行本页 POST 示例不会自动进入项目 Fleet ledger。
其他项目继续使用自己的记录入口，不复制 SE3-WAM 调度实现。

## 1. 一次性准备

需要：能访问平台的网络、有效个人 Token、Python 3、一个已忽略的本机私密目录。
使用 SSH 还需 OpenSSH、已登记公钥和匹配私钥。Token 不是 SSH 密钥；平台 Cookie 也不能当 Token。
创建需相应 `instances:create` 或 `jobs:create`，查询/恢复需目录、资源、`operations:read` 等 scope。
已有 Token 可在控制台调整适用范围；每次以 capabilities 返回值为准，不在文档或命令行写明文。

下面命令在 **PowerShell** 执行；路径由接入项目一次性填写。Linux/macOS 可直接调用同一 Python 脚本，
通过安全环境注入 `ZENITH_API_TOKEN`，API 参数和 JSON 不变。

```powershell
$KB = 'C:\workspace\volcengine-ml-platform-kb' # 其他机器改为实际 checkout
$ProjectRoot = 'C:\workspace\se3-wam-research' # 其他项目改这里
$Private = Join-Path $ProjectRoot 'local_private'
$TokenFile = Join-Path $Private 'zenith.env'
$Z = Join-Path $KB 'scripts/zenith_api.py'
$ZArgs = @('--base-url','http://10.1.130.101','--token-file',$TokenFile,'--direct')
function Invoke-Zenith {
    & python $Z @ZArgs @args
    if ($LASTEXITCODE -ne 0) { throw 'Zenith request failed; inspect response and retain original operation key.' }
}
```

此工作机已有 `local_private/zenith.env`，格式为一行 `ZENITH_API_TOKEN=<真实值>`，仅当前用户可读，
不需要再次导出。其他项目可将 `$TokenFile` 指向这个已授权绝对路径，**无需复制秘密**；
换机器则在当地私密配置中准备。新位置先用 `git check-ignore <路径>` 确认忽略，
限制本机文件访问。也可安全注入环境变量；非空 `ZENITH_API_TOKEN` 优先于文件，失效时先检查是否被旧环境值覆盖。

`--direct` 明确绕过 HTTP 代理：本机默认请求曾超时，直连已成功。只在内网直连成立时使用；
必须经代理接入的机器省略它，不要改全局网络配置。当前用户授权的部署地址为上述 HTTP origin；
官方 CLI 的 HTTPS profile 要求另见账户页，不猜域名、不跳过 TLS 校验。

## 2. 查询一次，选择真实参数

```powershell
$Schema = Invoke-Zenith schema | ConvertFrom-Json
$Caps = Invoke-Zenith get /pt/api/ai/capabilities | ConvertFrom-Json
$Caps.api_version
$Caps.scopes
$Caps.job_submission
$Caps.resource_zones | Format-Table
$Projects = Invoke-Zenith get /pt/api/projects | ConvertFrom-Json
$Projects.projects | Select-Object id,name
Invoke-Zenith get /pt/api/me/mount-disks
Invoke-Zenith get /pt/api/me/bucket-mounts
$Catalog = Invoke-Zenith get /pt/api/compute-offerings | ConvertFrom-Json
$Catalog.offerings | Select-Object id,name,gpu_count,available,job_available
Invoke-Zenith get /pt/api/me/quota-usage
Invoke-Zenith get /pt/api/me/card-hours
$Instances = Invoke-Zenith get '/pt/api/ai/instances?page=1&page_size=100' | ConvertFrom-Json
$Instances.instances | Select-Object id,vendor,vendor_instance_id,name,status,stale,last_seen_at
```

列表超过一页按返回 total/page/page_size 继续；当前镜像 HTTP 接口也返回准确匹配 total，
按其翻页。旧服务器若缺 total 才保留完整性未知，不把一页当全目录。
名称只用于识别，目标选返回的 ID。新建开发机看 `available`，训练看 `job_available`，
再看该 offering 的 `capabilities_by_resource_zone`、对应存储预览、worker 状态和执行类别。
这些不预留 GPU。新项目没有平台项目关系时可走个人任务；不能编造 `project_id`。
学生标准任务资格、卡时、规格和低优份额仍由平台检查。正式项目成员资格可以允许个人标准任务；
任务若选择项目，还会受该项目存储的资源区约束，两者不是同一个检查。

`mount-disks` 是登记盘/数据集目录，`bucket-mounts` 是项目 TOS/BOS 候选目录；二者的 ID 不混用。
需要显式挂载时，按[挂载字段边界](zenith-data.md#挂载权限与现有机器补挂)填写创建 body；
项目桶必须匹配所选项目、厂商及资源区：火山 TOS 对应区 5，百度 BOS 对应区 10，不能混选。
列出候选不等于机内挂载已成功，也不表示火山桶可跨云挂到百度计算。

选择规格后，分别查询工作负载的镜像：

```powershell
$OfferingId = '<上表选中的 offering id>'
$ResourceZone = '<该 offering 对应的 resource_zone>'
$Workload = 'DEV_INSTANCE' # 训练改 JOB
$ImageRows = @()
$ImagePage = 1
do {
    $Images = Invoke-Zenith get "/pt/api/compute-offerings/$OfferingId/images?workload=$Workload&resource_zone=$ResourceZone&page=$ImagePage&page_size=500" | ConvertFrom-Json
    if ($null -eq $Images.total) { throw 'Image catalog completeness is unknown: total is missing.' }
    if ($Images.images.Count -eq 0 -and $ImageRows.Count -lt $Images.total) { throw 'Image catalog ended before total; inspect the response.' }
    $ImageRows += $Images.images
    $ImagePage++
} while ($ImageRows.Count -lt $Images.total)
$ImageRows | Select-Object image_id,name,resource_zone,vendor
```

选择同一资源区的精确 `image_id`，不是镜像名称或随意填完整 registry 地址；
不要把平台默认镜像视为已有项目依赖。开发机和训练的 offering/镜像可能不同，要分别查询。
当前每页最多 500 条；第一页面未出现某镜像不代表完整目录没有。筛选和翻页条件须保持一致。

## 3A. 已有开发机：启动与连接

若实例已 RUNNING，直接查询详情/SSH，不重复启动。STOPPED 实例按同一行的厂商与 ID：

```powershell
$Vendor = '<所选实例 vendor>'
$InstanceId = '<同一行 vendor_instance_id>'
Invoke-Zenith get "/pt/api/ai/instances/$Vendor/$InstanceId"
$BodyFile = Join-Path $Private 'start-dev.json'
$KeyFile = Join-Path $Private 'start-dev-session-01.key'
'{}' | Set-Content -Encoding utf8 $BodyFile
# 每个新的授权意图仅生成一次；已有文件应保留，不加 -Force。
New-Item -ItemType File -Path $KeyFile -Value ([guid]::NewGuid().ToString()) -ErrorAction Stop | Out-Null
$Receipt = Invoke-Zenith post "/pt/api/ai/instances/$Vendor/$InstanceId/start" --body-file $BodyFile --key-file $KeyFile | ConvertFrom-Json
Invoke-Zenith wait $Receipt.operation_id --timeout 300
Invoke-Zenith get "/pt/api/ai/instances/$Vendor/$InstanceId"
$Ssh = Invoke-Zenith get "/pt/api/instances/$Vendor/$InstanceId/ssh-access" | ConvertFrom-Json
```

确认新观测为 RUNNING、非 stale，公钥已注入。SSH 信息是结构化 `host/port/user/proxy_hops`，
端点和跳板需本地可达；有跳板时按实际路由配置，不能套直连。主机信任需已通过可信渠道建立。
直连非交互检查：

```powershell
$Key = '<本机已有私钥绝对路径>'
ssh -T -o BatchMode=yes -o StrictHostKeyChecking=yes -o IdentitiesOnly=yes -o ConnectTimeout=10 -i $Key -p $Ssh.port "$($Ssh.user)@$($Ssh.host)" 'hostname && id'
if ($LASTEXITCODE -ne 0) { throw 'SSH verification failed' }
```

百度动态端口停启后可能改变，每次重新取 SSH，不沿用旧 alias 端口。若密钥未注入，先看
`GET /pt/api/instances/{vendor}/{id}/ssh-injections`，按 [SSH 说明](zenith-account-admin.md)处理，
不要重复生成密钥。机内再检查 GPU、解释器和 `findmnt -T <实际持久目录>`。

## 3B. 新开发机：准入与创建

复制 [开发机 JSON](../examples/zenith-instance.json) 到 `$Private/dev.json`，替换全部
`__...__`：名称、资源区、精确镜像。默认个人付费；需要项目归属/项目付费时按账户页显式填写。
`storage_mode=personal` 只适合已支持个人持久盘的区；不要为了通过准入擅自改成无个人盘模式。

准入文件使用**同一**资源区、优先级、项目关系和存储模式，例：

```json
{"workload_type":"instance","resource_zone":"10","execution_class":"standard","storage_mode":"personal"}
```

将该 JSON 保存为 `$Private/admission-dev.json`，按实际选择修改后查询：

```powershell
$Admission = Invoke-Zenith post "/pt/api/compute-offerings/$OfferingId/admission" --body-file (Join-Path $Private 'admission-dev.json') | ConvertFrom-Json
$Admission | Select-Object status,reason_code,retryable,unchecked
if ($Admission.status -ne 'allowed') { throw 'Admission is not allowed; inspect its reason before submitting.' }
```

仅在 `status=allowed` 且已核对 `reason_code/retryable/unchecked` 后继续。挂载/镜像/SSH/卡时可列为未检查；
预检不是 Dry-run 训练、库存锁或实际挂载保证。`blocked/unknown` 查具体原因，不自行切区/降优。
得到实际创建授权后：

```powershell
$BodyFile = Join-Path $Private 'dev.json'
$KeyFile = Join-Path $Private 'create-dev-01.key'
New-Item -ItemType File -Path $KeyFile -Value ([guid]::NewGuid().ToString()) -ErrorAction Stop | Out-Null
$Receipt = Invoke-Zenith post "/pt/api/compute-offerings/$OfferingId/instances" --body-file $BodyFile --key-file $KeyFile | ConvertFrom-Json
$Result = Invoke-Zenith wait $Receipt.operation_id --timeout 300 | ConvertFrom-Json
$Result.operation | Select-Object state,finalization_state,vendor,vendor_instance_id,instance_url
```

创建会开机。用返回 vendor/vendor_instance_id 按 3A 查询状态和连接，不能因已有新机再调用 start。

## 3C. 自定义训练：准备、准入、提交与结果

复制 [任务 JSON](../examples/zenith-job.json) 到 `$Private/job.json`。选择训练 offering 和
`workload=JOB` 镜像，填写同一镜像中已验证的工作目录、绝对解释器及脚本。
入口需包含项目参数、持久输出、失败退出及所需 checkpoint 恢复；仅有仓库不等于环境已安装。
代码/数据须预先部署到该任务能访问的同区存储。不要假定开发机系统盘会传给任务。

`replicas` 为 Worker 数，总 GPU＝offering.gpu_count × replicas；先做单 Worker 短验证。
单机多卡仍须真实 `torchrun` 或其他多卡入口，多机依 [DDP 说明](zenith-compute.md)验证，
不能照搬火山 `MLP_*` 到其他厂商。API 上限 256 副本不代表当前容量/准入。
新接入通常省略 `framework/image_vendor`；确需厂商 DDP 模式时单独核对兼容字段。
不传 `max_runtime_seconds`、`storage_mode`、原生 `queue_id/flavor_id`。

准入文件保存为 `$Private/admission-job.json`，参数与训练 body 一致：

```json
{"workload_type":"job","resource_zone":"10","execution_class":"standard","replicas":1}
```

```powershell
$Admission = Invoke-Zenith post "/pt/api/compute-offerings/$OfferingId/admission" --body-file (Join-Path $Private 'admission-job.json') | ConvertFrom-Json
$Admission | Select-Object status,reason_code,retryable,unchecked
if ($Admission.status -ne 'allowed') { throw 'Admission is not allowed; inspect its reason before submitting.' }
# 此处再核对未检查项、任务入口和总卡数
$BodyFile = Join-Path $Private 'job.json'
$KeyFile = Join-Path $Private 'create-job-01.key'
New-Item -ItemType File -Path $KeyFile -Value ([guid]::NewGuid().ToString()) -ErrorAction Stop | Out-Null
$Receipt = Invoke-Zenith post "/pt/api/compute-offerings/$OfferingId/jobs" --body-file $BodyFile --key-file $KeyFile | ConvertFrom-Json
$Result = Invoke-Zenith wait $Receipt.operation_id --timeout 300 | ConvertFrom-Json
$Vendor = $Result.operation.vendor
$JobId = $Result.operation.job_id
Invoke-Zenith get "/pt/api/ai/jobs/$Vendor/$JobId"
Invoke-Zenith get "/pt/api/ai/jobs/$Vendor/$JobId/logs?log_num=100"
Invoke-Zenith get "/pt/api/ai/jobs/$Vendor/$JobId/replicas?page=1&page_size=50"
```

无 job_id 时仍是准备/Zenith 等待阶段，继续核对同一 operation/控制台 job_url，不重交新任务。
有 ID 后看实际状态、观测时间、退出与输出；日志/指标是否可得由厂商及任务决定。
`GET .../metrics?minutes=30` 查询近 30 分钟，`minutes` 范围 1–120；可选 `replica` 只能来自真实副本。
没有采样不能解释成零负载。

低优仅在授权接受抢占时选 `low_priority`，同时改准入文件，并确认当前 offering 支持。
最新规则低优训练免费但可能份额回收；重新排队会重跑原命令，入口必须恢复已保存进度。
低优免费记账与真实抢占后跨 allocation 恢复仍未验收；已有普通训练及同 allocation 的恢复证据
不能替代这两项。正式训练是否有应用时限按项目当前授权和真实平台限制判断，不能复用旧诊断窗口。

## 4. 超时、恢复与结束

HTTP 错误或超时仍可能已产生操作。工具不自动重试 POST；先用**原 key**查询：

```powershell
Invoke-Zenith get /pt/api/operations/by-key --key-file $KeyFile
# 已知原 operation_id 时
Invoke-Zenith wait '<原 operation_id>' --timeout 300
```

`UNKNOWN`、`FAILED`、等待超时均非零退出；CLI 等待结束不取消云端操作。
保存原 body/key，不能换键重建。待核实状态继续查原操作；确认可重试时仍发原路径、原 body、原 key。
`SUCCEEDED` 仅操作成功，还要看 `finalization_state` 和机器/任务真实状态；需要资源登记核对时不创建替代品。
每个新意图用新 key，网络重试始终原 key，启停和取消各有自己的 key。
按服务端 `Retry-After` 等待；不要高频重刷准入失败。

获得对应结束授权后，停止实例用 `POST /pt/api/ai/instances/{vendor}/{id}/stop`；
取消训练用 `POST /pt/api/ai/jobs/{vendor}/{jobId}/cancel`；尚无 job_id 用
`POST /pt/api/operations/{创建operation_id}/cancel-job`。body 均为 `{}`，使用独立 key，
wait 后继续查资源终态。取消不删除 checkpoint；开发机内 `shutdown` 不代替平台停止。
实例删除、改挂载、镜像资产管理仍走控制台。

## 验收与交接

成功分五层：**准入允许 → 操作成功 → 资源运行 → 机内环境/挂载正确 → 持久产物及指标正确**。
保存该项目的实际 body（不含秘密）、key 文件位置、operation/resource ID、运行命令和结果，
放在项目已有的实验记录中；不另建调度或重复状态系统。

2026-10-07 新工具已通过 12 项测试；现有 Token 的 capabilities、项目、规格、实例、任务详情/日志/副本/metrics、
开发机和训练镜像读取通过。区 10 的单卡开发机、单卡标准/低优训练、2 Worker × 8 卡低优训练
均取得只读准入 allowed，且 `reservation_created=false`；不代表已获容量或完成调度。
一次直连准入请求超时，因准入没有远端副作用，手动重查成功；创建调用不能按这种方式换键重试。
该次只读核查没有创建或启停资源。10 月 10–11 日随后完成的 HTTP helper 已有机启停、改配与数据恢复，
以及新建失败的具体边界，见[实测证据](zenith.md#实测证据与剩余边界)和其链接的项目资源文档。
10 月 11–12 日已有 HTTP API 训练创建/取消、个人镜像保存及 JOB 拉取、PFS 真实训练和多节点通信的
项目实证，范围由[实测证据](zenith.md#实测证据与剩余边界)及所属实验维护。
API 新建开发机运行成功、低优免费记账、真实抢占重排、跨 allocation 精确恢复及原生桶训练吞吐仍未验收。
