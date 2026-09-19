# vePFS、TOS 与数据传输

将需要共享的热数据、代码、运行环境和高频输出放到项目的 vePFS 子目录；
TOS 用于对象传输和长期归档。系统盘承载镜像与明确选择的本地依赖，不能假设它会跟随新任务。
对象存储挂载不保证所有本地文件系统语义；小文件随机训练 I/O 是否合适应测量后决定。

## 工具与地域

安装使用[官方 tosutil 入口](https://www.volcengine.com/docs/6349/148772)，本库不分发二进制。
2026-09-19 在 Linux amd64 的 `tosutil v4.1.7` 上执行了 `version`、`help cp`、
`help config`；未执行本页传输。工具安装后在传输机检查：

```bash
tosutil version
tosutil help cp
tosutil help config
```

首次在私密终端执行 `tosutil config -interactive`。
按桶的地域及网络选择 endpoint；北京示例为公网 `tos-cn-beijing.volces.com`，
可达的火山内网使用 `tos-cn-beijing.ivolces.com`。不能在普通本地网络默认使用内网 endpoint。
`tosutil` 不使用 S3 协议域名；这是与 S3 客户端配置的区别。
来源：[tosutil 常见问题](https://www.volcengine.com/docs/6349/1110757?lang=zh)。

私密配置通常是 `~/.tosutilconfig`。不要打印、上传或随镜像保存；不要通过命令行传真实 AK/SK。
需要多个账户时先查看当前 `help config` 的配置文件选项，避免覆盖其他任务使用的配置。

## 传输命令

以下为**传输机 Bash**，变量必须填写明确的本地/vePFS 路径和项目自己的 TOS 前缀。
不要将整个桶根目录作为例行传输源。

```bash
: "${LOCAL_DIR:?Set the source directory}"
: "${TOS_PREFIX:?Set tos://bucket/project-prefix/}"
# 先只查看计划；-dryRun 的大小写由当前 help 确认。
tosutil cp "$LOCAL_DIR" "$TOS_PREFIX" -r -u -flat -dryRun
# 确认目标层级后执行上传。
tosutil cp "$LOCAL_DIR" "$TOS_PREFIX" -r -u -flat
```

下载方向相反：

```bash
: "${TOS_PREFIX:?Set the source object prefix}"
: "${DEST_DIR:?Set the local or vePFS destination}"
tosutil cp "$TOS_PREFIX" "$DEST_DIR" -r -u -flat -dryRun
tosutil cp "$TOS_PREFIX" "$DEST_DIR" -r -u -flat
```

`-flat` 表示不带相对父目录，使用前以小目录预览和实际目标键确认层级。
`-u` 是增量复制，不证明所有内容相同，也不自动删除目标多余对象。
复制成功后查看失败记录，并按数据用途核对对象数、尺寸及少量实际可读样本；
不能把“命令返回 0”直接解释成数据集满足训练需求。

本轮 help 确認 `-j` 控制批量任务并发，`-p` 控制单个分片任务并发。
先测量默认配置，再针对大小文件和网络调整；旧 `-j 32 -p 16` 不是通用最优值。
需要中断续传时保留该次工具的断点记录，按当前 help 恢复；不要清掉记录后仍声称可续传。

PowerShell 中使用 `$env:LOCAL_DIR` 等 PowerShell 变量形式，或填写带引号的真实路径；
不要粘贴 Bash 的 `${VAR:?}` 检查语句。

## 数据进入训练环境

大数据先在允许的下载机器获取，再传入 TOS，按需预热到 vePFS。
数据集、模型版本、许可证与具体下载工具属于项目；本库不维护 DROID/CALVIN/HF
等全部数据集直链与容量。源数据有变化时重新确认项目选用版本。

记录 TOS 源前缀与目标 vePFS 目录的对应关系，留在项目数据说明中。
任务首次只读少量真实样本，确认格式与路径；需要解压的内容放在空间与权限合适的文件系统。
不要假设某个桶名、路径或挂载在所有账户中存在。

## 输出、备份与恢复

训练先写可恢复的持久输出目录；阶段结束后把必要产物增量复制到 TOS。
恢复到新的临时项目目录，实际加载关键产物后再清理源数据。
备份内容包括重建所需代码版本、配置、依赖说明和产物，不包括账户秘密。
仅当明确需要完整镜像同步时才使用具有删除语义的工具选项；普通归档示例不删除目标内容。

## 挂载字段范围

vePFS 配置见 [custom-tasks.md](custom-tasks.md)。本轮 CLI 原生模板中的 TOS
示例使用 `Type: Tos`、`Bucket`、`Prefix` 和 `MountPath`。
这不意味着 vePFS 的 `SubPath` 或 SDK 的同名参数可机械替换；按具体存储类型和客户端核对。
当前账户的挂载授权、加速服务和存储可用性应通过对应队列现场确认。
