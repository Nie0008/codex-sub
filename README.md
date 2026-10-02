# Codex Sub

[简体中文](README.zh-CN.md)

Use `$sub` to organize execution, parallel research, independent verification, roundtables or brainstorming in Codex. Use `$think` directly for optional reasoning methods, or combine it with sub. Methods, roles and stages follow the task; they can be combined, skipped or replaced.

This is an independently maintained derivative of [Codex Adaptive Agents](https://github.com/aweiht/codex-adaptive-agents), based on upstream 0.7.0. The installer/runtime namespace remains `codex-adaptive-agents` for compatibility. See [origin and changes](docs/UPSTREAM.md).

## Initialize

Requires Python 3.11+ and an installed official Codex CLI. No Python packages are required.

```sh
git clone https://github.com/Nie0008/codex-sub.git
cd codex-sub
python3 scripts/init.py --dry-run
python3 scripts/init.py --yes
```

On Windows use `py -3` in place of `python3`. If needed, pass `--codex-home <directory>` or `--codex <CLI-path>`; otherwise the existing `CODEX_HOME`, then `~/.codex`, is used.

The initializer uses the existing planned, backed-up installer to install **sub, think, five optional Luna effort roles, and the standalone runtime**. It preserves global instructions, model defaults and unrelated configuration, then runs doctor without starting a model task. Conflicting local files stop installation. An earlier manually copied think can join an existing managed installation only when every destination matches the shipped content.

Open a new Codex chat after installation:

```text
Use sub to research this question and independently check the key claims.
Use sub to brainstorm this direction together, then compare the useful options.
Use think to examine the assumptions and failure conditions in this proposal.
```

sub and think are Skill names, not shell commands. Actual agents and models depend on the host. Main-agent coordination, verification and rework count toward total cost; installation does not demonstrate savings.

## Collaboration

The main Agent selects useful work, assigns ownership, checks decisive evidence and integrates delivery. Execution and professional verification can both be delegated. Joint exploration may share ideas early; an independent check derives its result before comparing answers. Shared writable work has one owner. Limited downstream delegation requires explicit main-agent permission within existing user authorization and host capacity.

Existing Workbench and Laya are optional integrations, configured separately. This project does not install their services, weights, private Skills or credentials. Laya's coding shadow test remains advisory and cannot authorize execution.

- [Task selection, modes and records](docs/CODE_SCENE.md)
- [Installation, upgrade and recovery](docs/PUBLIC_GUIDE.md)
- [Verification scope](docs/VALIDATION.md)
- [Contribution and package checks](CONTRIBUTING.md)

## License and privacy

[Apache-2.0](LICENSE), with the upstream [NOTICE](NOTICE) retained. Published sources are selected by [release-manifest.json](release-manifest.json); local configuration, authentication, account data, transcripts and execution records are excluded. The release builder also rejects machine paths and common credential signatures. See [security guidance](SECURITY.md).
