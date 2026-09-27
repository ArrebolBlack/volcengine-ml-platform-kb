# Zenith 账户、配额、个人 API 与管理

从 [Zenith 入口](zenith.md)选择任务。以下权限和制度主要来自帮助；2026-09-22 只实看普通用户的
组织、用量及账号入口，没有修改组织、项目、配额、密钥、Token 或系统配置。
2026-09-27 已全文复核账户、协作、制度及管理员帮助；未将文档覆盖当作管理权限或实际操作验收。

## 权限与资源归属

| 维度 | 作用 |
|---|---|
| 平台角色 | `viewer < operator < admin`；读取、计算操作、全局管理分别受限 |
| 产品身份 | 普通用户、项目级管理员、运维管理员决定导航；进入页面不等于具备操作角色 |
| 项目角色 | 负责人/项目管理员/成员/只读决定某项目内协作和管理，不等于资源所有者 |
| 资源所有权 | 保护个人实例终端、文件、变配与破坏性操作；项目标签不转移所有权 |
| 厂商与环境能力 | 已授权也可能因产品、队列、镜像、网络、库存或云端 IAM 不支持而失败 |

平台是一个全局资源域，项目不是独立租户隔离。组织决定个人周期额度、逻辑规格和公共能力；
显式项目成员关系决定项目使用范围。一个人可有多个项目，但只属于一个组织；组织负责人标记不等于
有维护成员的权限。管理员调整角色/禁用账号后会撤销会话。

| 动作 | 帮助所述控制台权限边界 |
|---|---|
| 创建开发机 | operator；可不选项目；选项目须有效成员关系 |
| 创建训练任务 | 非 admin 当前须参与有效项目，且有计算操作权限 |
| 启停/重启自己的开发机 | operator + 所有者；项目负责人/管理员同时为 operator 可代管项目实例的这三项 |
| 删除/重建/变配/终端/补公钥 | operator + 实例所有者，或 admin；项目管理权不替代所有权 |
| 训练控制/停止 | operator + 创建者、项目负责人/管理员或 admin |
| 推理、厂商原生镜像库、传统迁移台账 | 当前 admin-only；个人镜像资产和 TOS 快传另有入口 |
| 个人 SSH/API Token/模型 | 个人身份下可管理自己的资产；不因此获得云资源变更权 |

运维管理员的“用户/项目管理员预览”只改变显示，**不降低服务端权限**。
上表描述控制台；个人 Token 还受后文开放端点、scope 和所有权限制，不继承控制台 admin 的全局能力。
普通用户不能用原生命令绕开 Zenith 的纳管边界；`volc` 所需火山身份不等于 Zenith 个人 Token。
这不禁止开发机使用已独立授权的 TOS 对象、已挂载 vePFS 或可拉取的镜像；
资产访问方法见[数据页](zenith-data.md#复用已有火山数据与镜像)，不能将平台 API 缺口扩大为机内访问限制。

来源：[权限](http://10.1.130.101/help/reference/permissions.html)、
[组织](http://10.1.130.101/help/account/organization.html)。Token scope 以本页较新个人 API 契约为准。

## 当前配置与用量口径

组织个人页“组织分配能力”显示当前有效规格/存储。2026-09-22 当前账号实见：
开发机合计开机上限 2 卡，A100 和 PRO6000 各 1/2 卡规格；训练可选各 1/2/4/8 卡，
不受开发机同时开机卡数上限裁剪。该观察不证明新学生制度的所有条款均已实现，也不是其他账号默认值。
组织开发机上限按所有资源区合计；可配置基础与“加入任意项目后”的上限，多项目不叠加，
也不要求开发机本身选择该项目。组织能力已启用仍需相应存储绑定、路由与实际挂载条件。

周期卡时看“我的总览”；历史实际运行消耗看“我的用量”。后者当前默认近 30 天，并显示
“本月未配置个人卡时额度”，这**只说明兼容月度限制未配置**，不否定总览中的周额度。

- 1 GPU × 1 小时＝1 卡时，所有 GPU 型号倍率 1.0；创建本身无 1 卡时起步价。
- 约每 5 秒结算已观测运行时长，按 GPU 毫秒聚合；开发机快照约 30 秒、任务约 60 秒，启停边缘会延迟。
- 项目用量扣款顺序：**本人在该项目的专属转入卡时 → 项目公共卡时 → 个人卡时**。未选项目只扣个人。
  不自动使用另一项目或另一人的专属余额，同一使用不重复扣。
- 专属转入只供接收者在对应项目使用，不加入个人余额，来源周期结束失效。
  趋势是实际运行量，“个人已用”仅含个人承担部分，两者可以不同。
- 项目无周期额度且月度未配置时没有项目公共卡时，但可用符合规则的本人转入/个人余额。
- 周/月/半年/自定义 1–3650 天按卡片时区计量；按天从保存当日当地 00:00 起。
  周额度不在月初额外重置；重置切计量窗口，不删历史、不自动启停资源。
- 周期策略存在时优先于兼容月度限制；预算主要观察/提醒，不是硬准入。
  配额/卡时不足通常拒绝新建或启动，不由此自动停止已运行资源。
- 月度借用仅管理员同时配置相邻月份并允许时可用；1.5×/2× 是借用成本，不是 GPU 型号倍率。

项目配额有“运行中”和“总提交”两组水位；总提交包括运行、启动/创建、排队。
实例数/GPU 数分别限制，个人、项目总量、项目成员同时检查。
项目详情 → 配额 → 项目总量/某成员 → 四项上限 → 保存；留空不限、`0` 禁止，删除行恢复未配置。
资源池余量不替代这些准入检查。
项目负责人/管理员配置上述项目双水位，不等于可以自行发放卡时；月度个人/项目卡时由平台管理员分配。

费用是采样卡时与管理员静态价表估算，非厂商账单/发票。
“包内”不耗现金但仍受容量/配额/卡时限制；“按量”耗现金；“计费未知”不能推断为免费。
余额接口不支持或请求失败不等于余额零。项目变更后新用量归新范围，历史口径按页面查看。
个人、项目视图可记录同一工作负载，不能简单相加当总量。

来源：[卡时与费用](http://10.1.130.101/help/projects/quotas-billing.html)、
[工作台](http://10.1.130.101/help/compute/workbench.html)。

## 学生制度：目标与已开放功能分开

[学生卡时与整节点预留](http://10.1.130.101/help/projects/student-resource-policy.html)
注明 2026-09-17 制度确认、**尚未全部上线**。以下是目标规则，不能据此声称已获容量或调用尚无入口的操作：

| 项目 | 已确认目标 |
|---|---|
| 周额度 | 无有效正式项目 168、自由探索 336、基础培育 672；只读不算资格，多项目取最高不叠加 |
| 升降档 | 加入后下次查询提高本周总额、保留已用/已划；退出/结项本周已获额保留，下周降档 |
| 周边界 | 北京时间周一 00:00，免费未用额度不结转 |
| 开发机 | 单台 1/2 卡，每人同时运行最多 2 台且合计 2 卡；此条不规定停机数量上限，其他配额另行检查 |
| 训练 | 不设个人卡数/并发硬上限，仍受额度/权限/容量；无项目只能个人低优，正式成员可普通/低优 |
| 预留对象 | 完整物理 8 卡训练节点；开发机和 1/2 卡碎片不可占用；借用也按整节点 |
| 预付 | 节点数×8×小时；1 节点 24h＝192、84h＝672；空闲也付，已付范围项目训练不重复扣运行卡时 |
| 低优借用 | 空闲预留可借，按提交者个人实际运行付费；不扣出借项目、不退预付 |
| 借用回收 | 项目需资源且不足时立即终止补足缺口的相关借用任务，无宽限；不清无关任务、不承诺自动保存/续跑 |
| 个人划入项目 | 成员主动确认才扣，管理员申请不能直接扣；确认时检查来源余额/占用，免费划入仍在来源周过期 |
| 跨周 | 本周免费额只保到周日24:00；购买额须有效覆盖，未获下周额度只是预约意向 |

例如周日 22:00 至周一 02:00 的一节点预留共 32 卡时，前后周各 16；后半段另需新周有效资金与容量。
购买价格、审批/有效期、预留期限/提前量、取消退款、故障保障、到期未完成和运行中余额耗尽处理
尚待公布，不补猜测。管理员页仍说明的可配置“两档 168/672、卡数 1→4”机制与此目标不同，实际执行看账号有效策略。

## 项目协作与成员目录

只有 admin 创建/删除项目；项目负责人/管理员按权限维护设置、成员、模板、配额、Webhook。
项目须“进行中”才能用于新请求。列表看负责人、本人角色、成员/实例数、预算与估算花费。
创建：项目 → 新建 → 名称/描述/负责人/可选预算 → 添加成员与额度；普通用户当前“组织与项目”仅查看。

成员页支持姓名/邮箱/登录名全项目搜索、角色筛选、20/50/100 分页、批量添加、改角色和移出；
负责人不能在普通成员行改角色或移出。创建资源时选项目，已有开发机可按所有权规则归入项目；
从已有项目改到另一项目只允许 admin。归档、移出成员和删除项目不自动停止云资源、不转移所有权。
删除项目清理成员/配置/Webhook/实例项目标签，运行资源另行处理。

项目存储支持多绑定，实际选择的存储决定资源区，不能跨区混挂。
项目 → 存储 → 项目成员存储：有权管理者配置成员个人目录和 `public` 访问。
常见 `/project_<identifier>/<工号>` 和 `/project_<identifier>/public`，保留工号前导零。
缺工号用“同步工号”（需钉钉资料）；冲突或变化先核对，不自动改目录名。
查看者即使开关启用仍只读。关闭权限前需停相关实例/任务并等未完成操作；保存权限不撤销现有云端挂载。
火山旧机由 admin 停机调整允许子挂载、再手动启动；无问需预建对应目录卷；天翼项目隔离挂载未开放。
旧文件不自动迁入 `public`。

项目额外卡时与成员总卡时分开；主数只参与本项目，`(+数值)` 为还参加其他项目者，周期不同分列，
不重复发个人额度；包含成员个人额度的汇总卡片不是项目可直接支出的共享资金池。
Webhook：名称、HTTPS URL、可选签名密钥和事件，不选事件表示全部。
测试仅证明当次请求，发送尽力而为、不保证重试；外部接收端自行处理重复与监控。
个人铃铛可见范围的变化不会自动改变已有项目 Webhook 订阅，不能据此认定外部投递已撤销。

来源：[项目与成员](http://10.1.130.101/help/projects/overview.html)。

## 个人 API 与 CLI

2026-09-27 全文重读[个人 API 原文](http://10.1.130.101/help/reference/personal-api.html)，并重新
取得 [OpenAPI 2.0.1](http://10.1.130.101/pt/api/openapi.json)，核对全部 29 个路径、31 个操作
（19 GET、11 POST、1 DELETE）。帮助尾部仍有 `2.0.0` 旧说明；API 版本不等于 CLI 包版本。
契约与 9 月 26 日快照完全一致。没有安装 CLI、创建 Token 或验收带凭据调用；9 月 26 日无凭据 capabilities 返回 401。

### 自动化覆盖：官方 CLI、API 与系统 SSH

以下是当前公开契约的覆盖情况，**通过 API/CLI 的资源操作仍未实测**；系统 SSH 的实测范围见下文。“未公开”仅指此次个人 API/CLI，
不否定控制台或厂商内部另有接口，也不授权复用它们绕过个人 API 边界。

| 工作 | 官方 `zenith` CLI | 个人 API / 其余路径 |
|---|---|---|
| 身份、额度、项目、规格、镜像目录、实例查询 | 已说明命令 | API 已公开；项目仅查询，镜像目录不等于资产管理 |
| 创建开发机、提交训练 | 帮助要求使用 HTTP API/生成客户端 | API 已公开，创建会启动/调度计算 |
| 实例启动、停止、重启、同型号改配 | 已有，支持回执与有限效果核对 | API 已公开；停止不等于释放 |
| 任务状态、取消、取消未返回 ID 的创建 | 取消命令已说明；状态用 API | API 已公开；取消回执成功后仍查终态 |
| 公钥管理、补注入、SSH 信息 | 已有 | API 已公开；不生成或提供私钥 |
| 非交互机内命令、文件传输 | `ssh connect` 要求 TTY | 个人 API 不执行 shell/传文件；控制台端点 + 系统 SSH 命令已实测，API 取端点和文件传输仍待验收 |
| 平台原生训练日志、事件、TensorBoard、产物下载 | 未公开对应命令 | 2.0.1 无对应端点；控制台日志或经已验证持久卷取回工作负载输出 |
| 实例删除、重建、换镜像、任务记录删除 | 未公开对应命令 | 2.0.1 无对应端点；按角色和厂商能力用控制台 |
| 已有资源手动挂载 | 明确不提供 | Token 明确禁止，包括管理员 Token；仅总管理员控制台 |
| 镜像构建/登记/分享、模型、文件分享/迁移 | 未公开对应命令 | 2.0.1 无资产写端点；按[数据与资产](zenith-data.md)使用有权入口 |
| Token 创建/换发/撤销 | login/logout 只管理本地接入 | Token 不能管理 Token；用户菜单完成平台凭据引导 |
| 项目/成员/组织/配额、推理等管理写入 | 未公开对应命令 | 2.0.1 无对应端点；控制台与管理员流程 |

Codex 可以在已授予的执行、网络及凭据权限内调用 CLI、HTTP 客户端和 OpenSSH；
[Codex 官方非交互文档](https://learn.chatgpt.com/docs/non-interactive-mode)也支持以 `codex exec`
从脚本运行任务。这只能证明客户端具备编排方式，不能补出 Zenith 缺失端点或扩大用户权限。
当前可判断“有条件实现常规研究命令行工作流”，不能判断“全平台完全 CLI”或“已无人值守验收”。

### 接入条件与 Token

已确认浏览器入口和公开 schema 可经 `http://10.1.130.101` 读取；API/CLI 文档及 schema 的
server 说明要求实际 **HTTPS origin（不带路径）**，目前地址未确认。公开 HTTP GET 成功不能证明
Bearer 请求应经 HTTP 发送，也没有实测 CLI 是否强制拒绝 HTTP。
CLI 帮助仅提平台 GitHub Release Assets，正文及链接未给具体仓库/Release URL。
接入时先取得受支持 origin；使用官方 CLI 再取得可信发布包。不要猜 `https://10.1.130.101`、
绕证书检查或从同名 npm 包猜安装来源。直接 HTTP 客户端不依赖 CLI 安装，控制台仍可按已有会话使用。

右上用户菜单 → [API Token](http://10.1.130.101/api-tokens) → 创建 Token 表单：名称、权限、过期。
本次实见默认只读、每人最多 10 枚、默认 90 天/最长 365 天；预选规格镜像、开发机、任务、操作结果、
本人额度、项目和可用挂载盘读取。只看了表单并取消，未创建凭据。
页面有“OpenAPI 文档”“接入指南”“复制 AI 接入说明”；本次最后一项提示“复制失败”，可直接读接入指南，
不要假定已复制到剪贴板。说明不含 Token；Token 明文仅创建时显示一次。

Token 用 `Authorization: Bearer ...`，默认读，写权限单独 scope；创建后 scope 不可改，要替代 Token。
Token 受账号当前角色、项目关系、禁用和到期限制，不授予平台管理权，也不代替 SSH 私钥。
Token 会话不能管理 Token。停用/删除使后续请求失败，已受理的远端操作仍可能继续。
旧权限页“无细粒度 scope”已过时；新接口不会自动授予旧 Token。

每账号、每平台进程读 120次/分、写30次/分，多个 Token 共享；429 区分请求限流与资源配额，遵循
`Retry-After`。不要把资源准入拒绝当成可通过高频重试解决。
凭据放系统凭据库或既有 Git 忽略私密配置，不放代码、命令行参数、共享说明或日志。

### 查询和写接口

以下路径均在 `/pt/api` 下，变量来自实际查询结果，不用名称猜 ID。

| 用途 | 方法与路径 |
|---|---|
| schema / 能力 | `GET /openapi.json`、`GET /ai/capabilities` |
| 本人/配额/卡时 | `GET /me`、`GET /me/quota-usage`、`GET /me/card-hours` |
| 项目 | `GET /projects`、`GET /projects/{id}` |
| 规格/镜像 | `GET /compute-offerings`、`GET /compute-offerings/{id}/images`；训练镜像加 `?workload=JOB` |
| 准入预检 | `POST /compute-offerings/{id}/admission` |
| 创建开发机/训练 | `POST /compute-offerings/{id}/instances`、`POST /compute-offerings/{id}/jobs` |
| 开发机列表/详情 | `GET /ai/instances`、`GET /ai/instances/{vendor}/{vendorInstanceId}` |
| 启动/停止/重启 | `POST /ai/instances/{vendor}/{vendorInstanceId}/start`、`/stop`、`/restart` |
| 同型号改配 | `POST /instances/{vendor}/{vendorInstanceId}/resize`，传 `offering_id` |
| 任务列表/详情 | `GET /ai/jobs`、`GET /ai/jobs/{vendor}/{jobId}`；可见范围不同，见下 |
| 取消任务 | `POST /ai/jobs/{vendor}/{jobId}/cancel` |
| 取消未获任务ID的创建 | `POST /operations/{创建操作ID}/cancel-job` |
| 回执/原键查回 | `GET /operations/{id}`、`GET /operations/by-key`（带原 `Idempotency-Key`） |
| 授权挂载盘 | `GET /me/mount-disks` |
| SSH端点/注入/状态 | `GET /instances/{vendor}/{vendorInstanceId}/ssh-access`、`POST /instances/{vendor}/{vendorInstanceId}/inject-ssh-keys`、`GET /instances/{vendor}/{vendorInstanceId}/ssh-injections` |
| 公钥管理 | `GET/POST /me/ssh-keys`、`GET/DELETE /me/ssh-keys/{id}` |

开发机默认本人，`scope=projects`扩到项目可见元数据，不开放他人终端。
个人 API 的 `GET /ai/jobs`只列本人提交任务，管理员 Token 也如此；详情则允许本人或当前管理的
活跃项目任务。列表支持 vendor/project_id/page/page_size，默认50、最多100条，不返回日志、
环境变量、挂载路径或完整云配置。不要用控制台项目可见范围推导列表范围。

开发机列表只含纳管、未删除、非 stale 的观测记录；精确详情仍可返回 stale 记录。
`last_seen_at` 是 Unix 毫秒观测时间，0/null 为未知；worker 断开可留下旧的非 stale 数据，
因此 `stale=false` 也不等于近期在线。分页和 CLI 截断规则见下。

查询常用 scope：资料/额度 `profile:read`、项目 `projects:read`、规格/镜像/准入 `catalog:read`、
实例 `instances:read`、任务 `jobs:read`、回执 `operations:read`、授权盘 `storage:read`。
capabilities 不另要求 scope，但仍需有效 Bearer。单个写请求的 scope 如下；CLI/完整工作流还需
查询与回执 scope，不能将组合需求误当成单个 POST 的要求。

| 单个请求 | 必需 scope |
|---|---|
| 实例创建/启动/停止/重启/改配 | 分别 `instances:create` / `instances:start` / `instances:stop` / `instances:restart` / `instances:resize` |
| 训练创建/取消 | `jobs:create` / `jobs:cancel` |
| 公钥登记/删除 | `ssh-keys:write` |
| 公钥补注入 | `ssh:inject` |
| SSH 端点 | `ssh:read` |
| 公钥列表/详情、注入状态 | `ssh-keys:read` |

认证声明为 `security: [{"PersonalToken": []}]`，仍要求 Bearer；精确 scope 另见各操作的 `x-required-scopes`。
`/pt/api/jobs` 和单独挂载接口属于管理员控制台，不是个人 API，Token 会报 `endpoint_not_available_for_token`；
开放接口缺 scope 报 `insufficient_scope`。

### 创建、准入和回执

开发机需要 `instances:create` 及查询/回执权限。先取 offering ID、对应镜像目录，再提交，例如：

```json
{"name":"ai-dev-01","vendor":"volcengine","execution_class":"standard"}
```

`name` 4–32 位小写字母/数字/中划线，字母开头、字母数字结尾。`project_id`可选且必须有权参与；
省略 `image_id`使用该路由标准镜像。存储按本人、项目、资源区规则自动配置，不能提交原生存储 ID 或任意路径。
成功回执含 vendor/vendor_instance_id/instance_url；创建会启动计算资源。

开发机创建及准入新增 `storage_mode: personal | without_personal`：前者约束支持个人存储的路由，
后者明确接受无个人存储，允许其他兼容区。帮助要求天翼区 1–4 网页模式使用后者；这是条件要求，
不是所有厂商全局必填。显式资源区、项目存储和镜像仍限制落点，不会跨区复制数据。
**训练创建 schema 没有 `storage_mode`，不要照搬该字段。**

训练需要 `jobs:create`、`jobs:read`、`operations:read` 和必要目录/项目权限。示意：

```json
{
  "name": "ai-train-01",
  "project_id": "<实际项目ID>",
  "entrypoint": "cd '<实际已挂载训练目录>' && python train.py",
  "image_vendor": "volcengine",
  "execution_class": "standard",
  "replicas": 1
}
```

`name` 1–63 ASCII 字母数字/点/下划线/中划线，字母数字开头；entrypoint 1–8192 字符；project_id必填。
`replicas` 1–256，默认1，总 GPU＝规格卡数×副本。可选 framework、envs字符串字典（最多64项、
每值≤4096字符，变量名匹配 `[A-Za-z_][A-Za-z0-9_]{0,127}`）、max_runtime_seconds（1–2147483647）、
description（≤1000字符）。镜像从 JOB 目录取，省略使用标准训练镜像，
image_vendor可约束其平台。代码与数据须预先在授权存储，接口不上传代码、不开放任意路径挂载。
成功回执含 vendor/job_id/job_url。

**初始挂载存在待核实的契约冲突。** 2.0.1 的两类创建 schema 均有 `mount_personal`、
`mount_project`、`mount_public`、`mount_disk_ids`；盘 ID 是已授权的平台 25 位 ID，最多20个且唯一，
不是厂商 Fileset ID。训练创建说明允许这些初始授权选择；开发机 POST 说明却同时写“禁止挂载开关/盘 ID”
和“允许已授权开关/盘 ID”。实际接受行为未验证，开发机示例省略这些字段，按平台自动配置并验证挂载。
该最小示例没有请求原项目 Fileset；需要指定盘的任务须先核实授权及被接受的参数，或走控制台已授权盘选择，
不能照抄省略字段的示例后假定数据已经挂入。
这不授予创建后手动挂载权；盘授权解释见[数据与资产](zenith-data.md)。
创建和准入 schema 均为 `additionalProperties: false`，不加入猜测的厂商字段。

准入 `POST .../admission` 需要 catalog:read，示意：

```json
{"workload_type":"job","project_id":"<实际项目ID>","resource_zone":"5","execution_class":"standard","replicas":1}
```

返回 allowed/blocked/unknown、reason_code、retryable；**不锁卡、不创建文件**。
镜像、挂载、SSH、卡时仍可能列在 unchecked，不能用预检通过替代挂载验收。
`project_reservation_blocked` 表示其他项目保障影响准入，不能原样刷请求或未经任务授权自行转低优。
`execution_class` 只接受 standard/low_priority，normal 返回400；低优要求火山。
2.0.1 的开发机创建、训练创建和准入均接受 `resource_zone` 字符串 `1/2/3/4/5/6/10`：
1–4 是天翼（ctyun）pool01–04，5 是火山（volcengine），6 是无问（lanqi），10 是百度百舸（baidu）。
这已解决旧文“区 10 参数/厂商未知”，但不证明当前账号在该区有容量或创建成功。

创建、取消、启停、重启、改配要求平台原生 `Idempotency-Key`（8–200字符，缺失可返回428）。
准入、公钥管理和注入没有这项头要求。同一意图重试必须保留原键和原内容；
同键改内容409；响应丢失先按原键找回。UNKNOWN先核实，不换键重交。
首次创建202只受理，重放可200；训练创建502也可能带回执，应先读取核实，不能据此换键重试。
约5秒查操作回执并遵循Retry-After，成功后再查机器/任务状态。
回执成功不等于运行、SSH可连或训练产物成功。取消发送 `{}` 并使用独立的取消键，
需jobs:cancel、operations:read、jobs:read；可取消本人任务或所管理项目任务，列表可见范围另按上文。
未获任务ID时用创建操作ID取消，原创建状态不明仍须等待；取消保留记录、日志和存储。
这里只解释平台现有契约，不要求项目新建另一套回执或调度系统。

解析响应时区分：操作查询包在 `operation`，开发机详情包在 `instance`，训练详情包在 `job`；
SSH 端点直接提供 `host/port/user` 等结构化字段。注入返回202的 `enqueued/status_url`，不是普通操作回执。
只有发起用户可读自己的操作回执。除执行 `state`，还需查看资源登记的 `finalization_state`
（PENDING/SUCCEEDED/RETRYING/NEEDS_RECONCILIATION）；需要核对身份时先核实原资源，不重交创建。
改配不隐式停止/启动，也不跨区迁移。

### CLI 安装与最小只读启动

预览 CLI 要求 **Node.js 24、macOS/Linux**，Windows 凭据/恢复存储不支持。
从平台 GitHub Release 获取 `zenith-cli-<版本>.tgz` 及配套安装说明/发布元数据，按官方安装说明验证来源；
实际仓库未在帮助提供。帮助里的 `0.1.0-dev.1` 只是安装示例，不能当成最新版本。
普通 CI 预览产物只保留14天，旧 Release 不自动补包。包不含 Node/Agent Skills，版本独立于平台发版。
先阅读随包安装说明并确认包来源，再按对应版本安装：

```bash
npm install --global --ignore-scripts ./zenith-cli-<实际版本>.tgz
zenith --version
zenith api operations --output json
zenith profiles create work --origin https://<实际平台域名>
zenith profiles use work
zenith auth login
zenith auth status --output json
zenith capabilities
zenith whoami
zenith quota show
zenith card-hours show
zenith projects list
zenith offerings list
zenith offerings images "$OFFERING_ID" --workload JOB
zenith instances list --output json
zenith api schema --remote
```

此块有明确占位符，不是本机直接可执行安装命令。profile优先级：`--profile` > `ZENITH_PROFILE` >
`profiles use NAME` 默认；先确认没有遗留 `ZENITH_PROFILE` 覆盖本次默认，或每次显式传 `--profile work`。
帮助没有保证 create 自动选中 profile，所以示例显式 use。`ZENITH_API_TOKEN` 优先本地凭据，不落文件；非交互认证使用
`zenith auth login --token-stdin --no-input`，从已批准的私密来源经stdin输入，不能把Token写命令参数。
POSIX本地凭据为私有明文文件（目录0700/文件0600）；logout只删当前profile本地凭据，不撤销平台Token、
不清环境变量。`profiles list`不输出凭据；`api schema`离线，`--remote`取当前文档且不发送Token。

开发机默认50条，page-size 1–100；`--all`最多100页/10000条，可用max-pages/max-items收紧。
检查JSON pagination完整性/截断、stale和last_seen_at。镜像page-size 1–50，支持q/workload，
无可靠总数/终止标记、无全量选项，不能把一页当完整目录；多厂商短页/空页也不证明全部读完。
镜像503是目录不可用，不是空目录；初页附加标准/Zenith 镜像可多于 page-size。

当前 CLI **不含创建/删除实例和手动挂载命令**；开发机及训练创建走上述HTTP API或生成客户端。
帮助称已提供认证/profile、只读、实例启停重启改配、SSH、回执恢复、准入与取消，实际安装后以help为准。

### 生命周期、取消和恢复命令

以下变更命令仅在实际任务授权后执行；目标变量取查询结果。

```bash
zenith instances get "$VENDOR" "$PROVIDER_ID"
zenith instances start "$VENDOR" "$PROVIDER_ID" --intent start-dev-session --yes --wait --timeout-ms 90000 --output json
zenith instances resize "$VENDOR" "$PROVIDER_ID" --offering-id "$OFFERING_ID" --intent resize-dev-session --yes --wait --timeout-ms 90000 --output json
zenith operations get "$OPERATION_ID" --output json
zenith operations wait "$OPERATION_ID" --timeout-ms 120000 --output json
zenith operations recover --intent start-dev-session --output json
zenith offerings admission "$OFFERING_ID" --workload job --project-id "$PROJECT_ID" --resource-zone 5 --execution-class standard
zenith jobs cancel "$VENDOR" "$JOB_ID" --intent cancel-training-01 --yes --wait
zenith jobs cancel-creation "$CREATE_OPERATION_ID" --intent cancel-pending-01 --yes --wait
```

stop/restart使用同样目标参数和各自稳定intent；动作scope加instances:read/operations:read，改配还需catalog:read。
`--dry-run`是只读预览，不需yes/intent，与wait冲突，不预留库存。
超时/失联保留同命令、参数、intent恢复；`operations recover`只查回执。
原键可由 `operations recover --key-stdin --output json` 输入，勿打印恢复键。
仅确定终态且不再需恢复才 `operations forget --intent NAME`；忘记后同名意图会生成新键，可能重新执行。

默认约5秒查询、总时限30秒；可显式增大timeout-ms。超时退出6、Ctrl-C130，均不取消远端；
UNKNOWN退出7，CLAIMED/RUNNING处理中，SUCCEEDED才回执成功。
实例生命周期命令的 `--wait` 还要求新的非stale观测；`operations wait/recover`的等待只跟进回执，
`jobs cancel --wait`也只等取消回执，仍需另查任务终态。重启只能看到后来RUNNING，可能返回verification.status=limited、
effect_verified=false，不能据此证明发生过重启；改配型号文本/恢复场景也可能验证有限。

### SSH CLI

```bash
zenith ssh keys import --public-key-file "$HOME/.ssh/zenith_work.pub" --name work-laptop --output json
zenith ssh keys list --output json
zenith ssh keys get "$KEY_ID"
zenith ssh inject "$VENDOR" "$PROVIDER_ID" --yes --wait --timeout-ms 90000 --output json
zenith ssh injection-status "$VENDOR" "$PROVIDER_ID" --wait --timeout-ms 90000 --output json
zenith ssh info "$VENDOR" "$PROVIDER_ID" --output json
zenith ssh connect "$VENDOR" "$PROVIDER_ID" --identity-file "$HOME/.ssh/zenith_work"
```

示例假定已有与.pub配对的本机私钥，没有就先按组织方式生成；不让平台代收私钥。
list/get/injection-status需ssh-keys:read；import还需ssh-keys:write；
`ssh keys remove "$KEY_ID" --yes`需ssh-keys:write；inject需ssh:inject + ssh-keys:read；
info/connect需ssh:read。只能连接本人机器。

公钥查重/响应丢失先从本人列表找回，重复API指纹409；登记不等于旧机注入。
API 注册必填 `public_key`（≤16384字符），可选 `name`（≤100），最多10把；201表示登记成功，删除204仅移除平台记录。
注入无生命周期intent记录，超时先查injection-status --wait，pending超时退出7，不能盲重注入。
info的人类输出隐藏地址/命令，JSON有私密端点，不能贴公共日志。
connect调用本地OpenSSH，StrictHostKeyChecking=ask，需独立可信来源核对主机身份；变更密钥拒绝。
不执行平台返回的任意命令文本，忽略SSH config，Host别名不生效；identity仅用于目标机，跳板使用
本机agent/default密钥，平台不提供跳板私钥。auto按proxy_hops选择代理，否则已寻址中继直连。
connect要求交互TTY，不支持JSON/no-input/非交互；timeout仅约束平台请求，不终止交互SSH。
删Token或平台公钥不会结束旧会话/清机内authorized_keys，撤销访问需另清授权。

### Codex 的非交互 SSH 路径

`zenith ssh connect` 的 TTY 限制不表示系统 SSH 不能用于 Codex。帮助明确建议脚本使用
`zenith ssh info ... --output json`，也可直接取 `ssh-access` API，然后构造本地 OpenSSH 参数。
尚未接入 API/CLI 时，可从本人开发机详情的“连接详情”获取主机、端口、用户和端点类型。
浏览器钉钉会话、API Token、SSH 密钥分别认证不同入口；已有机内 SSH 不依赖创建 Token。
前提是本人运行中开发机、公钥已注入、网络可达、配对私钥/agent 可用，并已通过独立可信渠道确认
目标及跳板主机身份。Token 不能替代 SSH 私钥。

例如直连端点完成上述引导后，在受支持的 shell 中可验证一个非交互命令：

```bash
ssh -T -o BatchMode=yes -o StrictHostKeyChecking=yes -o IdentitiesOnly=yes -o ConnectTimeout=10 \
  -i "$IDENTITY_FILE" -p "$SSH_PORT" "$SSH_USER@$SSH_HOST" 'hostname && id'
```

变量来自核对后的当前端点和本机密钥路径，示例不包含可直接使用的连接参数。存在 `proxy_hops` 时必须按
实际跳板路由与本地授权配置连接，不能套用直连示例或假定目标私钥也可认证跳板。不要 `eval`
平台返回的命令文本；不要为无人值守跳过主机身份校验。首次可信引导完成后，才验证系统 SSH/SFTP/SCP
的上传、下载、远程运行和错误退出处理。

2026-09-27 首次实测：Windows PowerShell + 系统 OpenSSH，复用用户已创建的区 10 公网直连开发机
及本机密钥。先用 `ssh-keygen -lf <本机公钥文件>` 与平台已登记公钥指纹比对，再按上述参数运行
`hostname && id`；无需交互、退出码 0，返回目标容器主机名及 `root`。严格主机校验通过，
沿用本机已有信任记录，未重新执行首次主机信任建立；私钥仅由本机 OpenSSH 用于认证，未复制到页面、文档或工具输出。
PowerShell 对应写法如下，所有占位参数从当前控制台与本机配置填写，不复用过期端点：

```powershell
$zenithKey = 'C:\Users\<USER>\.ssh\<KEY_NAME>'
$zenithServer = '<CURRENT_SSH_HOST>'
$zenithPort = '<CURRENT_SSH_PORT>'
$zenithUser = '<CURRENT_SSH_USER>'
ssh -T -o BatchMode=yes -o StrictHostKeyChecking=yes -o IdentitiesOnly=yes -o ConnectTimeout=10 -i $zenithKey -p $zenithPort "${zenithUser}@${zenithServer}" 'hostname && id'
```

随后执行 `nvidia-smi --query-gpu=name,memory.total --format=csv,noheader`，返回两张
`NVIDIA RPBZZZ6`、每张 `97887 MiB`；控制台规格名为 PRO6000 × 2。只证明驱动可见设备，
未证明 PyTorch/CUDA 运算、多卡通信或训练性能。实际挂载结果归[数据页](zenith-data.md)。
尚未验收自动获取端点、SFTP/SCP 上传下载、远程失败退出处理和停止/启动后的连接恢复。

共享持久目录可用于训练代码和输出交接，具体[日志与产物方案](zenith-compute.md)仍待验收。
SSH 只能操作已授权机内环境，不能补齐平台实例删除、手动挂载、Token 或管理员功能；
机内 shutdown 不能当作 Zenith 释放资源。首次实测范围见[入口页](zenith.md)。

来源：[API Token](http://10.1.130.101/help/account/api-tokens.html)、
[个人 API 与 AI 接入](http://10.1.130.101/help/reference/personal-api.html)。

## 通知、反馈与个人资料

铃铛汇总公告/发版、本人资源事件和项目预算；普通成员只看本人个人事件，项目负责人/管理员可看
其管理项目成员事件，admin全量。旧无法确认接收者的事件仅admin。读通知后回资源详情确认状态。
全部已读只保存当前浏览器/账号的本地已读时间，不删除通知、不改变资源；换设备/清站点数据不同步。
回收预告与额度不足等不同类型不能混读；收到预告不表示已经关机。

右上“提交反馈”：运维配置/缺陷/功能建议/其他，标题、详细说明，自动附页面路径。
本次表单实见标题上限200、详情8000字符，未提交。
运维配额/权限/规格选运维配置；附时间、资源区、资源ID、期望、复现和脱敏错误。
用户菜单“我的反馈”看编号、待处理/处理中/已解决/已关闭、管理员说明及评论；转交开发会有Issue链接。
私有Issue不可访问时看平台说明，不重复提交；追加平台说明不会自动写GitHub。
管理员反馈管理可筛选/改状态/回复/转GitHub，未配权限仍可站内处理。
个人资料用于核对显示名/登录身份与必要邮箱；邮箱不完整应先按页面补齐/管理员刷新，不能改目录标识替代迁移。

来源：[通知](http://10.1.130.101/help/account/notifications.html)、
[反馈](http://10.1.130.101/help/account/feedback.html)。

## 管理员功能路由（帮助说明，未实操）

| 入口 | 核心方法与边界 |
|---|---|
| 总览/资源全局监控 | 平台管理仅稳定所有者+Zenith 创建+启用纳管位置；全局监控还含外部只读资源。GPU/CPU/内存/存储缺项标未知，上报覆盖率不是容量保证 |
| 平台状态 | 看节点版本/心跳/声明能力/域权限探测；在线不代表 IAM/库存满足。余额只进页/手动刷，避免高频调用 |
| 纳管资源 | 厂商、类型、实时候选或核对的 ID、展示名/备注/启用/排序；无问须精确 pool_id，type:H100 只是监控聚合 |
| 用户算力规格 | 逻辑型号/卡数 → 精确纳管队列/池的原生规格/CPU/内存/顺序 → 组织分配；镜像兼容与在线状态约束路由 |
| 用户/组织 | 本地账号唯一，密码帮助要求≥8位；角色、禁用会撤销会话；转组织移出旧组织，不自动加入项目 |
| 项目子队列 | 从父队列给项目保留卡数，不增总容量、不授文件权；低优可借空闲。设为0取消保留；仅平台提交受准入控制 |
| 卡时监控 | 当前周期有效额/记账耗用；不能当 GPU 硬件利用率或现金余额。管理员低消耗提醒与开发机空闲回收不同 |
| 自助配置 | 模板仅预填、非库存预留；队列可见性非厂商授权；个人配额可覆盖默认，留空不限 |
| 审计/公告/反馈/发版 | 审计只是调查线索；公告草稿/上架/下架；反馈状态与可选 Issue 转交；发版按连接选目标并核对恢复状态 |

纳管停用退出放置范围，移除只删除平台登记、不释放云资源。显式纳管队列后，实例连接/终端可能
只对纳管队列开放，停用或移除前必须核对现有用户连接影响。规格路由参数不能覆盖平台控制的名称、
镜像、卡数、队列/池。**命令下发后超时不自动换平台**，防重复创建。
多资源池空闲量不能直接相加推算单机可用；共享已分配可能超自有容量，不直接判错。

组织可配置个人存储额度；超额暂停创建/启动，帮助还提到重启，缺采样不当零。
天翼科研目录路由保存不等于实际挂载，`/{username}`、`/public` 中间无 `users`；不自动建/搬目录，
“已配置·待挂载验证”仍需验真。

低消耗提醒默认关闭，默认参数 7天/20%，观察期可设1–365天；仅在当前周期内满足观察时长且
严格低于阈值，才每对象来源周期提醒一次管理员。观察不是跨周期滚动或按时间折算目标，
额度设置、成员加入和划转可重定起点；修改提醒设置立即适用于已满足观察的额度，不重新等待。
项目可覆盖全局配置或单独关闭，删除覆盖恢复全局。下月借用不进入本周期比例分母，
项目分给成员的额度先从共享池预留，不能把池扣减直接当作 GPU 运行消耗。
每小时检查，不发 Webhook、不改额度、不停机；历史通知不随用量改写，处理前刷新监控页。
这与[计算页](zenith-compute.md)的空闲提醒、低利用率回收和低优让出是不同机制。

用户批量操作可选当前页或全部搜索，跨页保留；先预览完整名单，部分失败不回滚已成功者。
禁止修改本人，“全部搜索”自动排除本人；成功项移出选择、失败项保留，网络中断先核对账号当前状态再重试。
迁移“需审批”开关只影响后续任务；清空可见队列配置恢复全部可见，不是撤销厂商权限。

来源：[管理员资源](http://10.1.130.101/help/admin/resources.html)、
[平台管理](http://10.1.130.101/help/admin/platform.html)、
[总览](http://10.1.130.101/help/guide/dashboard.html)。
