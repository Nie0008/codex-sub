# Codex Sub 验证范围

Modified from the upstream validation document for this independent project.

本版的公开检查入口：

```sh
python3 -m unittest discover -s tests_python -p 'test_*.py'
python3 scripts/release_python.py --output-dir release-check
```

源码测试覆盖安装、升级、冲突保护、恢复、记录、进程管理与打包。初始化应在独立的 CODEX_HOME 中检查预览、安装 sub/think、重复运行、doctor 和卸载，确认全局设定与无关文件保留。

发布脚本按固定文件清单收集源码，拒绝链接、越界路径、私有配置文件、机器路径及常见凭据特征，核对 Markdown 引用、源码包和 SHA-256 清单。这些检查覆盖本次发布范围，不检查使用者全部硬盘或保证识别所有秘密。

CI 配置 Python 3.11／3.13 和 macOS、Ubuntu、Windows，实际结果以 [对应提交的运行记录](https://github.com/Nie0008/codex-sub/actions) 为准；配置存在不等于 CI 已通过。上游的历史测试和模型执行结果不能当作本项目本版的验收。

Skill 的规则已经用隔离案例试用过接续创意、独立复算和一次明确许可的有限再分工。实际模型未由宿主披露；不能据此认定 Luna 或 Workbench 已验证。课堂效果、真实业务质量提升、跨通道收益和账号额度节约尚无测量，不能由安装或案例成功推断。

Laya 与 Workbench 由使用者自行配置，正向模型执行、任务结果与成本需要各自的实际证据。公开仓库不携带本机试用日志、账号资料或模型缓存。
