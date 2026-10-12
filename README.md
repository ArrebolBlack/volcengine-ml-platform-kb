# Zenith 平台使用知识库

供 Zenith 用户和 Codex 按需读取的平台操作指南：个人 API、开发机、SSH、训练任务、存储、镜像与排障。
同时保留独立的火山引擎原生 MLP 指南；`volc` 身份和 YAML 不能直接用于 Zenith。
本库不是 Zenith 官方客户端，也不包含可复用的个人账号、凭据、配额或已部署训练环境。

## 获取知识库

云端仓库：[ArrebolBlack/volcengine-ml-platform-kb](https://github.com/ArrebolBlack/volcengine-ml-platform-kb)。
当前为私有仓库，克隆需要维护者授予读取权限；也可使用维护者提供的知识库 ZIP，无需 GitHub 登录。

```bash
git clone https://github.com/ArrebolBlack/volcengine-ml-platform-kb.git
cd volcengine-ml-platform-kb
```

ZIP 解压后，以含本 README 的目录作为知识库根目录。已有 checkout 用 `git pull --ff-only` 更新，
先处理本人尚未提交的修改；ZIP 用户通过新的发行包更新，不把自己的私密目录放进共享包。

## 首次接入

需要 Python 3.9+、可访问自己 Zenith 部署的网络和本人平台账号；SSH 另需 OpenSSH 与本人密钥。
API 路线无需安装官方 Zenith CLI、`volc` 或第三方 Python 包。

1. 向本部署管理员确认平台 origin（协议、主机及可选端口，不带路径），不要默认沿用文档中的历史地址。
2. 用自己的账号登录控制台，创建个人 API Token；先启用查询所需 scope。浏览器 Cookie、Token、SSH 密钥互不替代。
3. 按[快速开始：一次性准备](docs/zenith-quickstart.md#1-一次性准备)配置本机私密文件。根目录的 [.env.example](.env.example) 只有占位符，不能直接认证；不要把真实值写回模板、聊天或 Git。
4. 按[只读查询](docs/zenith-quickstart.md#2-查询一次选择真实参数)验证平台版本、本人身份、scope 和规格；此阶段不启动机器、不提交训练。
5. 按同页 3A / 3B / 3C 进入已有机连接、新建开发机或训练任务；只使用本人查询到且获授权的资源与项目。

## 让 Codex 使用

让 Codex 能访问本机 checkout 或解压目录，再提供平台地址、凭据文件的绝对路径和本次任务范围。
秘密由本人在本机配置；Codex 调用工具时通过文件或安全环境读取，不需要在对话中提供 Token 明文。
新对话可使用下面的接入说明，替换路径和目标即可：

```text
Zenith 知识库位于 <本机绝对路径>。先读 README.md 和 docs/zenith-quickstart.md 的第 1、2 节，
再按任务读取必要专题，不遍历整个知识库。平台 origin 为 <我的部署地址>，个人 Token 文件为
<本机私密文件绝对路径>，不要展示其内容。先只读核对本人身份、权限和资源。
本次目标与资源授权范围是 <任务、项目、卡数、预算或时限>。沿用我的项目记录入口，
操作超时保留原 key 查回执，不换 key 重建。实际配置和结果写入我的项目，不写成知识库默认值。
```

## 按需阅读

| 当前任务 | 入口 |
|---|---|
| Zenith 可执行流程与失败恢复 | [快速开始](docs/zenith-quickstart.md) |
| 选择计算、存储、权限或原生火山专题 | [平台文档索引](docs/INDEX.md) |
| 填写 Zenith JSON 或原生火山 YAML | [示例索引](examples/INDEX.md) |
| 查询特定机构的网络与使用约定 | [机构索引](institutions/INDEX.md) |
| 本地检查、维护与发布 | [工具索引](scripts/INDEX.md) · [维护说明](docs/maintenance.md) |

通用步骤与经验归本库；镜像、数据路径、训练入口、运行记录及恢复契约归各用户自己的项目。
各主题标明核验日期与证据边界，历史成功不保证当前容量、权限或其他部署行为；执行前以本人的 schema、capabilities 和实际响应核对。
