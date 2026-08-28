# Installing LeanClarity

LeanClarity is one plugin for Claude Code and Codex, installed from this repository through each host's marketplace mechanism. `node` must be on the PATH that the host uses to run hooks. Product behavior, the three control prompts, and the saved setting are described in [README.md](README.md).

While the repository is private, the host's `git` must be able to authenticate to GitHub (for example after `gh auth login`).

## Claude Code

```text
/plugin marketplace add wotjr1649/leanclarity
/plugin install leanclarity@leanclarity
```

Send the two commands as separate prompts. The same steps work from a terminal:

```text
claude plugin marketplace add wotjr1649/leanclarity
claude plugin install leanclarity@leanclarity --scope local
```

`--scope local` enables the plugin only for the current project (`.claude/settings.local.json`); `--scope project` or `--scope user` widen it. Start a new session after installing.

## Codex

```text
codex plugin marketplace add wotjr1649/leanclarity
codex plugin add leanclarity@leanclarity
```

Codex needs `[features] hooks = true` in `~/.codex/config.toml`, and it asks you to review and trust the plugin hooks (`/hooks`) before they run. Restart the Codex desktop app after installing so it picks up the plugin. Codex has no per-project plugin enablement: the plugin is enabled for the whole user profile until you remove it.

## Update and uninstall

```text
claude plugin marketplace update leanclarity
claude plugin update leanclarity@leanclarity
claude plugin uninstall leanclarity@leanclarity

codex plugin marketplace upgrade
codex plugin add leanclarity@leanclarity
codex plugin remove leanclarity
```

For Codex, `codex plugin marketplace upgrade` refreshes the git snapshot and `codex plugin add` installs the refreshed version. Uninstalling removes the plugin files; the saved setting stays in the host's plugin data directory (`state.json`). LeanClarity never deletes it itself, and deleting it resets the setting to ON.
