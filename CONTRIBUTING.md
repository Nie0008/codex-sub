# Contributing to Codex Sub

Modified from the upstream contribution guide.

Use Python 3.11+ and keep changes small. Reuse the existing installer, runtime and record protocol. Agent methods should serve actual tasks; preserve user authorization, evidence and ownership while leaving methods flexible.

```sh
python3 -m unittest discover -s tests_python -p 'test_*.py'
python3 scripts/release_python.py --output-dir release-check
```

The manifest is the public allowlist. Tests and the archive build reject unsafe paths, credentials, local configuration, missing links and checksum mismatches. Build output must be new; existing archives are not overwritten. Use an isolated CODEX_HOME for initialization tests. Keep secrets, local paths, transcripts, account data, execution records and private materials out of commits and issues.

Update usage, package files and validation scope with implementation changes. Report source checks, installation, CI, actual model execution and cost separately. Workbench and Laya remain optional, separately managed integrations. Respect the upstream LICENSE and NOTICE and mark modified upstream files.
