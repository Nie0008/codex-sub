# 来源、改动与依赖

Codex Sub 独立维护于 [Nie0008/codex-sub](https://github.com/Nie0008/codex-sub)，派生自 [aweiht/codex-adaptive-agents](https://github.com/aweiht/codex-adaptive-agents) 0.7.0，基线提交为 `e25998d49320234eb6f183d3bc18a6558397c907`。

保留原 [LICENSE](../LICENSE) 与 [NOTICE](../NOTICE)。修改后的上游源码标明 Codex Sub 的改动；新仓库按公开文件清单建立独立历史，本机调研、配置、运行记录及私有开发材料保留在原工作区。

## 本项目的改动

- 按需 sub 入口支持执行、并行分工、独立交叉验证、圆桌、脑暴与对抗性分析，不强制使用某个模型或固定流程。
- 独立 think 入口按需引用方法，允许调整、组合与清单外方法。
- code-record 保存实际执行方式、父子包关系和结果证据；code-shadow 仅作代码场景的 Laya 旁路观察。
- scripts/init.py 复用受管安装器安装 sub/think 和可选 Luna 配置，保留用户全局设定。
- 发布文件清单、内容检查和全新公开历史隔离本机材料；打包保留校验和与安全路径检查。

内部 Python 模块、运行入口和 Codex 目录继续沿用 codex-adaptive-agents，以兼容既有安装；本项目版本从 0.8.0 起维护。

## 依赖

Python 3.11+ 标准库和官方 Codex CLI 提供本地执行；登录、模型访问和原生 Agent 由官方客户端负责。Workbench 与 Laya 是可选的独立能力，本项目不复制其本机 Skill、依赖、权重、凭据或配置。select／refresh 的上游公开数据源仅在显式使用兼容工具时访问。

没有新装的调度服务、MCP 服务或外部框架。来源、安装、真实执行及效果分别核对，详见 [VALIDATION](VALIDATION.md)。
