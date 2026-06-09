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

Put it under a category folder (organizational only — the installed symlink name is just the skill dir's basename):

```
~/code/personal-skills/
├── devtools/        # 开发 / git 工具类
├── investment/      # 投资分析类
└── third-party/     # 第三方下载的 skill（如理杏仁）
    └── my-new-skill/
        └── SKILL.md
```

Run `./install.sh` again. It auto-discovers any `SKILL.md` (case-insensitive) one or two levels deep, so category folders just work. Idempotent.

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

## Layout

```
personal-skills/
├── install.sh          # 把每个 skill 软链进 ~/.claude/skills 和 ~/.codex/skills
├── check-update.sh     # 只读：比对本地与远程 HEAD（不拉取）
├── update.sh           # git pull --ff-only --autostash + install.sh
├── devtools/           # cb-git-review-commit-push, init-agent-collab
├── investment/         # rough-valuation
└── third-party/        # lixinger-openapi（理杏仁，整份入库）
```

## Updating skills（自更新，理杏仁式）

用 git 复刻"比对版本号再更新"的思路（commit SHA = 版本号，`git pull` = 下载）：

- **一键手动**：`./update.sh` —— `git pull --ff-only --autostash` 后重建软链。`--autostash` 会吸收第三方 skill 自我更新留下的本地改动。
- **按需提示（已内置进每个自有 skill）**：每个自有 SKILL.md 开头有「Step 0 自更新检测」，调用 `check-update.sh`；若远程 HEAD ≠ 本地，agent 会告诉你并询问是否 `update.sh`。离线/失败静默跳过，绝不阻塞 skill。

## Current skills

| Skill | Category | Trigger | Step 0 自更新 |
|---|---|---|---|
| [init-agent-collab](./devtools/init-agent-collab/SKILL.md) | devtools | `/init-agent-collab`, "set up agent collab" | ✅ |
| [cb-git-review-commit-push](./devtools/cb-git-review-commit-push/SKILL.md) | devtools | review / commit / push requests | ✅ |
| [rough-valuation](./investment/rough-valuation/SKILL.md) | investment | "毛估估XX公司" / "目测XX值不值得买" | ✅ |
| [lixinger-openapi](./third-party/lixinger-openapi/skill.md) | third-party | 查 A股/港股 估值·财报·分红 等基本面数据 | 第三方自带 |

### third-party 策略（理杏仁 lixinger-openapi）
- **整份入库**，保留它自带的自动更新（步骤1：比对远程 doc-version → 自动下载覆盖 `api-docs/`）。
- 它自我更新会就地改动被跟踪文件 → `update.sh` 的 `--autostash` 吸收，不冲突；这些 diff 偶尔 commit 即可（相当于理杏仁 API 文档的版本史）。
- `token.json` 已 `.gitignore`，**不入库**；每台机器单独配（token 取自 https://www.lixinger.com/open/api/token）。
- 不给它加 Step 0（它有自己的机制）。`rough-valuation` 取数依赖它。

## How skills are discovered

- **Claude Code**: scans `~/.claude/skills/*/SKILL.md` on every session start.
- **Codex CLI**: scans `~/.codex/skills/*/SKILL.md` on every session start.
- **install.sh**: discovers any `SKILL.md` (case-insensitive — 理杏仁's lowercase `skill.md` is found too) at depth 1–2 under the repo, and symlinks each into both agents' skill dirs under the skill dir's basename.

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
