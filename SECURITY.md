# Security policy

Modified from the upstream security policy for Codex Sub.

Report vulnerabilities through GitHub private vulnerability reporting when available, or contact the repository maintainer privately. Avoid publishing credentials or private evidence in an issue.

Do not attach auth.json, API keys, access tokens, cookies, config.toml, sessions, account information, machine paths, installation backups or unredacted model output. Provide the version, platform, affected command and a minimal redacted reproduction.

The initializer uses a scoped installation plan, private backup, atomic writes and content checks. It preserves unrelated configuration and stops on conflicts. Public packages use an explicit allowlist with path, credential-signature, link and checksum checks; this does not guarantee that every possible secret is recognized.

Agent scope instructions are not an operating-system sandbox. Actual tool permissions and user authorization remain authoritative. Optional integrations retain their own credentials and state; this repository does not collect them.
