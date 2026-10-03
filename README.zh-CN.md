# Codex Sub · 子代理协作与思维方法

[English](README.md)

在 Codex 中用 `$sub` 组织执行、并行调研、独立交叉验证、圆桌或头脑风暴；用 `$think` 按需分析假设、取舍与验证盲点。方法和协作方式可以组合、跳过或替换，按任务需要决定人数、顺序和产物。

这是独立维护的开源衍生项目，基于 [Codex Adaptive Agents](https://github.com/aweiht/codex-adaptive-agents) 0.7.0。为兼容已有安装，内部模块和运行目录仍沿用 codex-adaptive-agents。来源及改动见 [UPSTREAM](docs/UPSTREAM.md)。

## 初始化

需要 Python 3.11+ 和已安装的官方 Codex CLI；无需安装 Python 第三方依赖。

```sh
git clone https://github.com/Nie0008/codex-sub.git
cd codex-sub
python3 scripts/init.py --dry-run
python3 scripts/init.py --yes
```

Windows 将 `python3` 换成 `py -3`。需要指定位置时添加 `--codex-home <目录>`；CLI 不在 PATH 时添加 `--codex <CLI路径>`。默认使用已有 `CODEX_HOME`，未设置时使用当前用户的 `~/.codex`。

初始化脚本安装 **sub、think、五个可选 Luna 推理档位与独立运行入口**，复用安装计划、备份、冲突检查和回滚。它保留全局设定、默认模型及其他配置，并运行 doctor；不会启动模型测试。已有同名文件冲突时停止。此前手动复制的 think 只有在已有受管安装、且各文件与本版内容一致时才纳入管理。

安装完成后开一个新 Codex 聊天，例如：

```text
用 sub 调研这个问题，关键结论安排独立核查。
用 sub 共同脑暴这个方向，先保留候选，再比较和验证。
用 think 分析这个方案的关键假设和失败条件。
```

sub 和 think 是 Skill 名称；实际模型与子代理能力以宿主工具为准。doctor READY 表示安装和入口检查通过，真实模型执行、任务质量和账号节约需要另外的证据。

## 怎么组织工作

主 Agent 对齐目标、安排分工、回查关键证据并整合交付；具体执行和专业核验都可以委派。独立检查先自行推导再比较，共同探索可以提前交流、接续创意。同一可写产物只有一个负责人；主控明确许可后，才在已有授权和宿主能力内进行有限再分工。

Workbench 和 Laya 是可选的已有能力，需另行配置。本项目不携带它们的本机 Skill、服务、权重或凭据。Laya 的代码旁路判断只用于观察，不决定派发、权限或验收。

- [任务选择、协作模式与记录](docs/CODE_SCENE.md)
- [安装、升级与恢复](docs/PUBLIC_GUIDE.md)
- [验证范围](docs/VALIDATION.md)
- [开发与打包检查](CONTRIBUTING.md)

## 搭配 Agent Workbench

[Agent Workbench](https://github.com/Nie0008/agent-workbench-open) 是本地多 Agent 桌面工作台，支持通过桌面界面、命令或 MCP 派发 Claude Code、Grok、DSH 和 ZCode 任务，集中管理项目背景、任务授权、执行进度与结果。

搭配使用时，Sub 帮助 Codex 安排分工与核验，Workbench 承接外部 Agent 的执行和任务管理。需要不同执行器或模型、续办已有任务，或统一查看任务状态时，可以组合使用。Workbench 需单独安装并配置执行器和模型；Sub 也可以只使用 Codex 的原生子代理。

[了解 Agent Workbench 与接入方式](https://github.com/Nie0008/agent-workbench-open#安装与初始化)。

## 来源与发布范围

沿用 [Apache-2.0](LICENSE)，保留上游 [NOTICE](NOTICE)。公开源码按 [release-manifest.json](release-manifest.json) 的文件清单生成；本机文档、绝对路径、认证、配置、会话、账号数据和运行记录不进入公开版本。打包时检查所有文件中的机器路径与常见凭据特征，安全问题报告见 [SECURITY](SECURITY.md)。
