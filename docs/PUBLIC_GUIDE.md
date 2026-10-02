# Codex Sub 安装与维护

Modified from the upstream operator guide for Codex Sub.

## 初始化与验证

从当前仓库的源码或源码包运行 `python3 scripts/init.py --dry-run`，核对计划后运行 `python3 scripts/init.py --yes`。Windows 使用 `py -3`；Python 必须为 3.11+。脚本复用 `install --skill`，成功应用后执行 doctor；不运行模型任务，也不安装 Workbench、Laya 或后台服务。

需要把应用绑定到此前检查的计划时，添加 `--plan-id <预检查返回值>`。计划过期时重新检查。指定 Codex 位置使用 `--codex-home <目录>`；指定 CLI 使用 `--codex <路径>`。默认沿用 CODEX_HOME，未设置时使用当前用户的 ~/.codex。

安装管理 skills/sub、skills/think、五份 adaptive_luna_* 配置与 codex-adaptive-agents/runtime。五档配置只在宿主支持时使用；安装不会修改全局 AGENTS、默认主模型或默认子模型。同名非受管文件会阻止写入；在升级已有受管安装时，可以纳入与本版完全一致的旧手动 think 文件，其余内容仍保留。修改过的文件需先处理冲突，不能强制覆盖。

初始化输出依次给出安装结果和 doctor 结果。安装成功但 doctor 失败时，文件已经安装，按实际缺项修复后重新运行；不把安装成功当作模型已可调用。doctor 只运行 CLI 版本与本地入口检查。

## 升级

保留本地改动，从本仓库取得最新源码，在原 CODEX_HOME 运行同样的初始化命令；更新下载目录本身不会更新已复制的运行文件。上游旧全局规则安装与本项目的 Skill 安装是不同模式，安装器拒绝直接切换，需先按原模式完成卸载。

本项目版本为 0.8.0，上游基线为 0.7.0。保留原运行入口名称以兼容已有路径和记录协议。

## 下载目录移走后使用

独立运行入口位于 `<Codex目录>/codex-adaptive-agents/runtime/codex-adaptive-agents.py`。仍需保留安装使用的 Python 解释器。以该入口为 `<entry>`：

```sh
python3 <entry> --codex-home <Codex目录> doctor
python3 <entry> --codex-home <Codex目录> uninstall --dry-run
python3 <entry> --codex-home <Codex目录> uninstall --yes --plan-id <计划值>
python3 <entry> --codex-home <Codex目录> rollback --yes --backup <安装返回的备份目录>
```

卸载和回滚核对受管内容，保留无关文件与后续改动；冲突时停止。备份、安装回执、项目执行记录含本机信息，只在本地保存，不应提交到公开仓库。

上游 select、refresh、verify --live 等入口作为兼容工具保留，不是日常任务的必经步骤。plain install 会采用上游全局规则模式；使用本项目时采用 scripts/init.py 或 install --skill。`verify --live` 会使用真实账号额度，仅在明确需要该验证时使用。
