# Zenith 可执行快速开始

适用于 Zenith 用户自己的项目，采用 **Python 3 + 个人 HTTP API + OpenSSH** 路线，不依赖官方 CLI 安装。
使用 [zenith_api.py](../scripts/zenith_api.py)，先读参数和做查询，再执行所需分支。
字段依据 2026-10-12 定向复核的 OpenAPI 3.8.0；[账户与 API](zenith-account-admin.md)解释完整权限，
[计算页](zenith-compute.md)解释 DDP/回收，[数据页](zenith-data.md)解释持久路径和大数据。

首次接入只执行第 1、2 节。第 3 节会创建或启停计算资源，按自己的任务授权选择一个分支；
本库不提供账号或项目默认值，也不要求安装 SE3-WAM、GPU Fleet 或其他项目的调度工具。

## 1. 一次性准备

需要：能访问自己平台部署的网络、有效个人 Token、Python 3.9+、一个本机私密目录。
使用 SSH 还需 OpenSSH、已登记公钥和匹配私钥。Token 不是 SSH 密钥；平台 Cookie 也不能当 Token。
本工具只用 Python 标准库。先在本人控制台的用户菜单 → API Token 创建个人凭据；
第 2 节查询需 `profile:read`、`projects:read`、`catalog:read`、`instances:read`，
后续任务/回执需 `jobs:read`、`operations:read`。只启用本次所需权限，具体 scope 见[账户页](zenith-account-admin.md#查询和写接口)。
创建或启停时再核对相应写 scope；已有 Token 可在控制台调整适用范围，以本人的 capabilities 为准。

SSH 公钥在本人控制台的 SSH 密钥入口登记；只上传 `.pub`，私钥留在本机，不传给平台或聊天。
有自己的密钥则复用；没有时用 `ssh-keygen -t ed25519 -f <本机未使用的私钥路径>` 交互创建，
不要覆盖已有密钥。加密私钥供非交互使用时先用 `ssh-add <本人私钥路径>` 加入本机 agent，
不要为了自动化取消口令。登记公钥不证明旧开发机已经注入，连接前仍需查询或在控制台核对。

### 本人端点与凭据

向部署管理员取得 origin，例如 `https://zenith.example.org`（示意地址，不可直接使用），
包含协议、主机和可选端口，不带 `/my`、`/pt/api` 等路径。本库历史验证地址是 `http://10.1.130.101`，
不是所有部署的默认值。HTTPS 使用受信任证书；只有部署明确允许且网络可信时才使用 HTTP，不绕过 TLS 校验。

凭据文件默认放在本库已忽略的 `local_private/zenith.env`。克隆用户先在知识库根目录运行
`git check-ignore local_private/zenith.env`，应返回该路径；ZIP 用户不运行 Git 命令，
以后纳入 Git 时先确认同样的忽略规则生效。不要靠忽略规则保护已经跟踪的秘密。

创建 `local_private/`，将根目录 [.env.example](../.env.example) 作为 `zenith.env` 的起点，
用本机编辑器把占位符替换为**本人** Token；已有个人配置则直接使用其绝对路径，不覆盖它。
文件严格只有一行 `ZENITH_API_TOKEN=<真实值>`，不加引号、注释、`export`、空行或第二个变量。
工具不自动加载 `.env`；需显式 `--token-file`。不要展示文件、把真实值写进命令历史或提交到 Git。
限制文件为当前用户可读；Linux/macOS 使用 `chmod 600 <凭据文件>`，Windows 按本机 ACL 限制访问。

也可由系统凭据库安全注入环境变量 `ZENITH_API_TOKEN`；非空环境值优先于文件。
旧环境值会遮蔽新文件，401 时检查其是否存在，但不要打印值。同一用户可跨项目复用自己的授权来源，
不同用户必须使用各自凭据。`ZENITH_BASE_URL` 也可提供 origin，但以下示例显式传参以避免地址混淆。

默认沿用本机代理配置。只有确认内网可直连时才在下列参数数组后追加 `--direct`：
PowerShell 用 `$ZArgs += '--direct'`，Bash 用 `Z_ARGS+=(--direct)`，在任何请求前设置。
历史工作机曾因默认代理超时而直连成功，这不是其他用户的网络默认值；必须经代理接入时不要追加。
全局选项放在 `schema/get/post/wait` **之前**；官方 CLI 的 HTTPS profile 要求另见账户页。

### PowerShell 会话

在含 README 的知识库根目录执行，先把 origin 占位符改成自己的地址；非默认凭据路径也在此修改：

```powershell
$KB = (Get-Location).Path
$ZenithOrigin = '<本人部署的 HTTP(S) origin>'
$Private = Join-Path $KB 'local_private'
New-Item -ItemType Directory -Path $Private -Force | Out-Null
$TokenFile = Join-Path $Private 'zenith.env'
$Z = Join-Path $KB 'scripts/zenith_api.py'
$ZArgs = @('--base-url',$ZenithOrigin,'--token-file',$TokenFile)
function Invoke-Zenith {
    & python $Z @ZArgs @args
    if ($LASTEXITCODE -ne 0) { throw 'Zenith request failed; inspect response and retain original operation key.' }
}
```

### Linux / macOS 会话

在知识库根目录使用 Bash；先按上文准备本人的凭据文件：

```bash
KB="$PWD"
ZENITH_ORIGIN='<本人部署的 HTTP(S) origin>'
PRIVATE="$KB/local_private"
mkdir -p "$PRIVATE"
TOKEN_FILE="$PRIVATE/zenith.env"
chmod 600 "$TOKEN_FILE"
Z_ARGS=(--base-url "$ZENITH_ORIGIN" --token-file "$TOKEN_FILE")
zenith_api() { python3 "$KB/scripts/zenith_api.py" "${Z_ARGS[@]}" "$@"; }
zenith_api schema
zenith_api get /pt/api/ai/capabilities
zenith_api get /pt/api/me
zenith_api get /pt/api/compute-offerings
```

后续 PowerShell 示例的 `Invoke-Zenith ...` 对应 Bash 的 `zenith_api ...`；
JSON 和 API 字段相同，变量、JSON 解析及文件操作须按本机 shell 改写，不把 PowerShell 整段粘贴到 Bash。

### 多账号配置与切换

每个账号使用自己的 Token 文件，不覆盖另一账号的凭据。例如在已忽略的目录中准备
`local_private/zenith/account-a/zenith.env` 和 `local_private/zenith/account-b/zenith.env`，
格式和权限沿用上文；`account-a/b` 只是本机别名，不是平台登录名或 API 参数。
请求 body、幂等 key 和回执路径也按账号分开。推荐每个账号使用独立终端会话，避免复用旧变量。
本工具没有隐式登录状态或官方 CLI profile；每次 CLI 调用按当前参数和环境读取凭据。
已经启动的 `wait` 轮询沿用启动时的 Token，不会重新读取文件。

先定义本节的工具函数，再选择目标账号。**改 `$TokenFile` 不会更新已有 `$ZArgs` 数组**，
必须同时重建参数。非空 `ZENITH_API_TOKEN` 会覆盖文件，所以切换到文件认证时先清除当前进程中的该变量。
以下只执行身份和权限查询，不创建、启停或取消资源。

PowerShell：

```powershell
$Account = 'account-b' # 改成本机已配置的账号别名
$ZenithOrigin = '<该账号的 Zenith HTTP(S) origin>'
if (Test-Path Env:ZENITH_API_TOKEN) { Remove-Item Env:ZENITH_API_TOKEN }
$Private = Join-Path $KB "local_private/zenith/$Account"
$TokenFile = Join-Path $Private 'zenith.env'
$ZArgs = @('--base-url',$ZenithOrigin,'--token-file',$TokenFile)
# 仅该部署网络确认可直连时，在首次请求前追加 --direct。
$OfferingId = $ResourceZone = $Vendor = $InstanceId = $JobId = $null
$Ssh = $Key = $BodyFile = $KeyFile = $Receipt = $Result = $null
$Me = Invoke-Zenith get /pt/api/me | ConvertFrom-Json
$Me
$Caps = Invoke-Zenith get /pt/api/ai/capabilities | ConvertFrom-Json
$Caps.scopes
```

Bash：

```bash
ACCOUNT='account-b'
ZENITH_ORIGIN='<该账号的 Zenith HTTP(S) origin>'
unset ZENITH_API_TOKEN
PRIVATE="$KB/local_private/zenith/$ACCOUNT"
TOKEN_FILE="$PRIVATE/zenith.env"
Z_ARGS=(--base-url "$ZENITH_ORIGIN" --token-file "$TOKEN_FILE")
# 仅该部署网络确认可直连时，在首次请求前追加 --direct。
zenith_api get /pt/api/me
zenith_api get /pt/api/ai/capabilities
```

确认 `/me` 返回的用户标识符合目标账号，再按第 2 节重新查询项目、配额、资源、镜像和存储授权。
身份不符或查询失败时不要 POST；不得沿用旧账号的项目 ID、实例/任务 ID、挂载 ID、镜像候选或 SSH 端点。
同一账号仅轮换 Token 时仍核对身份与 scope，不把本机文件名当成认证证明。

切换只影响当前会话后续工具调用；其他终端、已启动的监控/子进程和云端任务不会跟着切换，
也不会自动取消、转移旧账号资源或停止计费。旧操作响应不明时，用**原账号的有效凭据、原 origin 和原 key**
查询回执；不要拿新账号查不到的结果判定旧操作未创建，更不能换账号重提作为网络重试。
保留尚待核对的旧 body/key；原账号资源的处置按原任务授权另行完成。

浏览器登录、SSH 私钥/公钥注入、官方 CLI profile，以及原生 `volc`/TOS 凭据分别管理，
不会因本工具切换 Token 而改变。浏览器按本人登录流程切换，SSH 从新账号实例重新取端点并核对授权；
官方 CLI 用户另见[profile 优先级](zenith-account-admin.md#cli-安装与最小只读启动)。
给新对话提供目标账号别名、origin、Token 文件绝对路径及项目范围即可，不提供 Token 明文，
也不要让其他运行任务使用的默认凭据被覆盖。

## 2. 查询一次，选择真实参数

```powershell
$Schema = Invoke-Zenith schema | ConvertFrom-Json
$Schema.info.version
$Caps = Invoke-Zenith get /pt/api/ai/capabilities | ConvertFrom-Json
$Caps.api_version
$Caps.scopes
$Caps.job_submission
$Caps.resource_zones | Format-Table
$Me = Invoke-Zenith get /pt/api/me | ConvertFrom-Json
$Me
$Projects = Invoke-Zenith get /pt/api/projects | ConvertFrom-Json
$Projects.projects | Select-Object id,name
$Catalog = Invoke-Zenith get /pt/api/compute-offerings | ConvertFrom-Json
$Catalog.offerings | Select-Object id,name,gpu_count,available,job_available
Invoke-Zenith get /pt/api/me/quota-usage
Invoke-Zenith get /pt/api/me/card-hours
$Instances = Invoke-Zenith get '/pt/api/ai/instances?page=1&page_size=100' | ConvertFrom-Json
$Instances.instances | Select-Object id,vendor,vendor_instance_id,name,status,stale,last_seen_at
```

`schema` 匿名读取，不加载或发送 Token；成功只说明接口可达，不说明认证成功。
确认 `info.version` 与 `capabilities.api_version`，本人资料与控制台身份一致、所需 scope 存在；
返回 2xx 不代表拥有写权限或已获容量。401 查有效期、文件和旧环境变量，403 查对应 scope/所有权，
网络失败查 origin、VPN/内网路由与代理，禁止换用别人的凭据。

需要挂载时另查 `get /pt/api/me/mount-disks` 和 `get /pt/api/me/bucket-mounts`（需 `storage:read`），
不要为首次验证强制申请不需要的存储权限。

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

本分支取 SSH 端点需 `ssh:read`，查看公钥/注入状态需 `ssh-keys:read`；
启动还需 `instances:start` 和回执查询权限，不因只读接入成功就假定具备这些 scope。
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
端点和跳板需本地可达；有跳板时按实际路由配置，不能套直连。

首次连接新目标时，先通过管理员等独立可信渠道取得**服务器主机密钥**指纹，不是本人的公钥指纹。
由本人在终端交互连接，比对 SSH 提示的指纹；只有一致才接受并写入本机 `known_hosts`。
没有可信指纹或原主机密钥变化时先核实，不自动信任 `ssh-keyscan` 结果、不删除旧记录绕过告警。
直连示例（有跳板需先核对每一跳的主机身份和认证）：

```powershell
$Key = '<本机已有私钥绝对路径>'
ssh -o StrictHostKeyChecking=ask -o IdentitiesOnly=yes -o ConnectTimeout=10 -i $Key -p $Ssh.port "$($Ssh.user)@$($Ssh.host)" 'hostname && id'
if ($LASTEXITCODE -ne 0) { throw 'Initial SSH verification failed' }
```

已建立信任且私钥/agent 可用后，再执行 Codex 的严格非交互检查：

```powershell
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

准入文件使用**同一**资源区、优先级、项目关系和存储模式；将下例的 `__RESOURCE_ZONE__`
替换为本人所选 offering 的 `$ResourceZone`，并按实际情况修改其他字段：

```json
{"workload_type":"instance","resource_zone":"__RESOURCE_ZONE__","execution_class":"standard","storage_mode":"personal"}
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
短入口、ENV分片、GPFS脚本和官方对象交接的实证及长度/502边界见
[API短入口与代码交接](zenith-compute.md#api短入口与代码交接)。个人任务可省略`project_id`；
需要项目归属时显式填写，不能从某次省略成功推导项目字段会导致失败。
不传 `max_runtime_seconds`、`storage_mode`、原生 `queue_id/flavor_id`。

准入文件保存为 `$Private/admission-job.json`，参数与训练 body 一致；`__RESOURCE_ZONE__`
替换为本次训练 offering 的 `$ResourceZone`，项目、优先级和副本数按实际提交填写：

```json
{"workload_type":"job","resource_zone":"__RESOURCE_ZONE__","execution_class":"standard","replicas":1}
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

接入自己的项目时，仅记录本库路径/托管入口、所需主题和项目自己的配置/实验入口，
不复制整套指南或把个人镜像、目录、账户参数写回本库。SE3-WAM 是历史使用方示例：
该项目使用 `docs/resources/zenith_workflow.md` 和自己的提交登记；其用户按该项目入口执行，
直接调用本页 POST 不会自动写入其 Fleet ledger。其他用户不需要该仓库或调度实现。

2026-10-07 新工具已通过 12 项测试；现有 Token 的 capabilities、项目、规格、实例、任务详情/日志/副本/metrics、
开发机和训练镜像读取通过。区 10 的单卡开发机、单卡标准/低优训练、2 Worker × 8 卡低优训练
均取得只读准入 allowed，且 `reservation_created=false`；不代表已获容量或完成调度。
一次直连准入请求超时，因准入没有远端副作用，手动重查成功；创建调用不能按这种方式换键重试。
该次只读核查没有创建或启停资源。10 月 10–11 日随后完成的 HTTP helper 已有机启停、改配与数据恢复，
以及新建失败的具体边界，见[实测证据](zenith.md#实测证据与剩余边界)和其链接的项目资源文档。
10 月 11–12 日已有 HTTP API 训练创建/取消、个人镜像保存及 JOB 拉取、PFS 真实训练和多节点通信的
项目实证，范围由[实测证据](zenith.md#实测证据与剩余边界)及所属实验维护。
API 新建开发机运行成功、低优免费记账、真实抢占重排、跨 allocation 精确恢复及原生桶训练吞吐仍未验收。
