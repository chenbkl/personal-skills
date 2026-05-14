# Personal Agent Skills

Custom skills for **Claude Code** and **Codex CLI**, kept in a single repo so:

- One source file is shared between two agents — fix once, both pick it up.
- Cross-machine portable: clone on a new machine, run `./install.sh`, all skills wired up.
- Version controlled: every change is a git commit.

## Quick start

### First time on a new machine

```bash
git clone <your-repo-url> ~/code/personal-skills
cd ~/code/personal-skills
./install.sh
```

That creates symlinks:

```
~/.claude/skills/<skill-name>  → ~/code/personal-skills/<skill-name>
~/.codex/skills/<skill-name>   → ~/code/personal-skills/<skill-name>
```

Restart Claude Code / Codex CLI to pick up the skills.

### Adding a new skill

Create a directory with `SKILL.md`:

```
~/code/personal-skills/
└── my-new-skill/
    └── SKILL.md
```

Run `./install.sh` again. Idempotent — only creates / refreshes symlinks that are missing or stale.

### Editing an existing skill

Edit the `SKILL.md` inside this repo. The symlinks already point here, so next agent session sees the change. No reinstall needed.

## install.sh options

```bash
./install.sh                  # install all skills to both agents (default)
./install.sh --claude-only    # ~/.claude/skills only
./install.sh --codex-only     # ~/.codex/skills only
./install.sh --dry-run        # show what would happen, no changes
./install.sh --help
```

## Current skills

| Skill | Trigger | Both agents? |
|---|---|---|
| [init-agent-collab](./init-agent-collab/SKILL.md) | `/init-agent-collab`, "set up agent collab", "init agents" | ✅ |
| [cb-git-review-commit-push](./cb-git-review-commit-push/SKILL.md) | review changes / commit / push requests | ✅ |

## How skills are discovered

- **Claude Code**: scans `~/.claude/skills/*/SKILL.md` on every session start.
- **Codex CLI**: scans `~/.codex/skills/*/SKILL.md` on every session start.

The two agents have separate skill dirs, but `install.sh` symlinks the same source into both, so a single SKILL.md drives both.

## Cross-platform / cross-agent notes

- **Same path on every machine recommended** (e.g. clone to `~/code/personal-skills` everywhere). `install.sh` resolves the repo path from its own location, so it still works if you clone elsewhere — just rerun `install.sh` after moving the repo.
- **Tool-name compatibility**: Claude Code's tools (Bash / Read / Edit / Write / Glob / Grep) and Codex's tool set have different names. Skills that mostly describe behavior in prose (like `init-agent-collab`) are fully cross-platform. Skills that hardcode tool names may only work on one side — prefer generic verbs ("read the file", "run the command") in SKILL.md prose.
- **install.sh refuses to overwrite real directories** at the target location. If `~/.claude/skills/<name>` is a real dir (not a symlink), it's skipped — move/delete it manually first, then rerun install.
- **Pulling updates**: on any machine, `cd ~/code/personal-skills && git pull` is enough. Symlinks already point at the live files.

## Skills targeting only one agent

If a skill is Claude-only or Codex-only, options:

1. Run `install.sh --claude-only` / `--codex-only` (installs all skills to one side only — coarse).
2. After running `install.sh`, delete the unwanted symlink: `rm ~/.codex/skills/<name>`.
3. Add a per-skill marker (future enhancement) and have `install.sh` honor it.

## Recommended repo hygiene

- Commit each new skill or edit independently — easier to revert.
- Tag releases (`git tag v1`) before risky restructures.
- Push to a personal git host (GitHub / GitLab) so other machines can clone.
