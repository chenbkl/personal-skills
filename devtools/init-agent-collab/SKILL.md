---
name: init-agent-collab
description: Initialize or retrofit multi-agent collaboration files (PROJECT_GUIDE.md + per-agent entry points like CLAUDE.md / AGENTS.md) for a project. Use when the user wants to set up agent collaboration conventions, asks to "init agents", "set up agent collab", "create AGENTS.md and CLAUDE.md", or wants both Claude Code and Codex (or other agents) to share the same project rules. Works both for new projects and for retrofitting existing projects that already have CLAUDE.md / AGENTS.md.
---

# Multi-Agent Collaboration Init

This skill sets up a **shared single-source-of-truth document** (`PROJECT_GUIDE.md`) plus thin per-agent entry files (`CLAUDE.md` for Claude Code, `AGENTS.md` for Codex / OpenAI agents) so that:

- Both agents auto-load the same shared rules on session start
- Shared content (conventions, doc map, progress) is edited in **one place**
- Per-agent specifics (MCP configs, agent-only quirks) stay in each agent's entry file
- Onboarding any future agent is a matter of adding one more entry file

## 0. Self-update check (do this first, once)

This skill is managed by the git repo `personal-skills`. Before anything else, silently check for a newer version (Lixinger-style on-demand self-update):

```bash
d="$(readlink "$HOME/.claude/skills/init-agent-collab" 2>/dev/null || readlink "$HOME/.codex/skills/init-agent-collab" 2>/dev/null)"
[ -n "$d" ] && bash "$(git -C "$d" rev-parse --show-toplevel)/check-update.sh"
```

- Output `up-to-date` or offline → say nothing, just continue.
- Output `⚠ update-available` → tell the user "your personal-skills has a newer version, run `update.sh` now?"; only run `update.sh` if they agree, otherwise continue. Never block on a failed check.

## When to invoke

Trigger this skill when the user:

- Says explicitly: `/init-agent-collab`, "init agents", "set up agent collab", "initialize project for Claude and Codex"
- Describes the pain: "I keep telling agents the same rules over and over", "every project I have to redo this", "I want both Claude and Codex to read the same conventions"
- Starts a brand new project and mentions multiple agents
- Asks how to manage CLAUDE.md / AGENTS.md sprawl across many projects

Do **not** trigger for: pure CLAUDE.md init (use the built-in `init` skill instead), or for editing a single file's content unrelated to multi-agent setup.

## Workflow

Follow these steps in order. Always prefer asking the minimum number of questions; default to sensible choices and let the user override.

### Step 1 — Detect current state

Run these checks before asking anything:

1. List the project root contents. Look specifically for: `CLAUDE.md`, `AGENTS.md`, `PROJECT_GUIDE.md`, `README.md`, `.git`, `package.json`, `requirements.txt`, `Podfile`, `Cargo.toml`, `go.mod`, `pyproject.toml`.
2. Classify the project as one of:
   - **fresh**: no `CLAUDE.md` or `AGENTS.md` exists.
   - **partial**: one of `CLAUDE.md` / `AGENTS.md` exists.
   - **retrofit**: both exist (or `PROJECT_GUIDE.md` already exists).
3. For partial / retrofit cases, **read the existing files in full** before proceeding.

### Step 2 — Ask only what you must

Use `AskUserQuestion` for the few decisions that cannot be inferred. **Skip questions whose answer you can infer** (e.g., if a `Podfile` is present, the project is iOS).

Necessary questions:

- **Which agents will collaborate on this project?** — Default: Claude Code + Codex. Other options: + Gemini CLI, + Aider, custom.
- **Project type / domain** (if not inferable from files) — picks the right convention template.

Recommended-but-optional questions (offer one combined question with multiselect):

- **Which hard conventions to pre-seed in PROJECT_GUIDE.md?**
  - Forbid AI markers in commit messages (Co-Authored-By, Generated with X, model names)
  - Forbid force-push to protected branches
  - Required reading order on session start
  - "Run before paper-design" dev rhythm preference

If the user does not have a strong opinion, default to all of the above.

### Step 3 — For retrofit projects: propose a merge plan before writing

If `CLAUDE.md` / `AGENTS.md` already exist:

1. Summarize what each file currently contains (sections, line counts).
2. Classify each section into:
   - **shared** (project overview, doc map, conventions, progress) → goes to `PROJECT_GUIDE.md`
   - **agent-specific** (MCP configs, plugin specifics, agent-only workflow tweaks) → stays in `CLAUDE.md` / `AGENTS.md`
3. Show the proposed split to the user (filenames + section list, no full content yet).
4. Get explicit approval before writing.

For fresh projects, skip this step.

### Step 4 — Generate files

Write three files at the project root:

**`PROJECT_GUIDE.md`** — shared source of truth. Structure:

```markdown
# <Project Name> 项目指南（共享）

> 本文件是 <agent list> 共同遵守的项目说明与协作约定。任一 agent 启动后应先读完本文件。Agent 个性化内容（如 Codex 的 MCP 配置、Claude 的特殊偏好）见各自入口文件。

## Project Overview
<inferred from README / file structure / user input>

## Directory Notes
<inferred from top-level dirs>

## Agent 协作约定

### 提交信息禁止 AI 标识（如果用户选了）
<one-paragraph rule>

### 风险动作前需先确认
<force-push / rm -rf / destructive ops list>

### 开发节奏：边跑边调（如果用户选了）
<short paragraph>

### 文档维护规则
- 共享内容改 PROJECT_GUIDE.md
- 各 agent 个性化改对应入口文件
- 延迟拆分：单节超过 ~80 行时拆出独立文件，不预先拆分

## 项目进度（跨会话恢复语境）

> 用户或 agent 在阶段性节点更新本节。

- <ISO date>：初始化 agent 协作文档
```

**`CLAUDE.md`** — Claude Code entry:

```markdown
# Claude Code 入口

> 本工程的共享项目说明与协作约定见 `PROJECT_GUIDE.md`，下面直接导入到当前上下文。Claude 特定的偏好/工具说明可加在文件末尾。

@PROJECT_GUIDE.md

## Claude 特定

<empty placeholder, or migrated Claude-specific content from old CLAUDE.md>
```

**`AGENTS.md`** — Codex entry (OpenAI / agents.md convention):

```markdown
# Codex Agent 入口

> 本工程的共享项目说明与协作约定见 `PROJECT_GUIDE.md`，**Codex 启动后请优先阅读该文件**，再继续读本文件中 Codex 特定的配置。

## Startup（Codex 特定）
1. 阅读 PROJECT_GUIDE.md（共享）
2. 阅读本文件（Codex 个性化配置）

## Codex 特定

<migrated Codex-specific content from old AGENTS.md, or empty placeholder>
```

For additional agents (Gemini, Aider, etc.), create analogous thin entry files.

### Step 5 — Auxiliary suggestions

After writing the files, surface (but do not force) these follow-ups:

- If `.env` is referenced anywhere in the project, suggest adding it to `.gitignore`.
- If README.md exists, suggest adding a short "Agent collaboration" section pointing humans at `PROJECT_GUIDE.md`.
- If the project has a `.git` and the user mentioned future commits, surface the pre-seeded conventions (e.g., no AI markers in commit messages) so they know we have already wired this rule in.

### Step 6 — Summary report

End with a concise table:

| File | Action | Lines | Role |
| --- | --- | --- | --- |
| `PROJECT_GUIDE.md` | created / updated | N | shared source of truth |
| `CLAUDE.md` | created / updated | N | Claude Code entry |
| `AGENTS.md` | created / updated | N | Codex entry |

Plus a one-line "next session, any agent starting in this directory will auto-load PROJECT_GUIDE.md."

## Constraints

- **Non-destructive**: never silently overwrite existing files. Always read first, propose, get approval.
- **Idempotent**: rerunning the skill on an already-initialized project should be an "upgrade / sync" action, not a redo. Detect already-present sections and skip recreating them; offer to add missing pieces only.
- **Minimal prompts**: ≤3 questions in the happy path. Use defaults aggressively. Multi-select for combinable choices.
- **Language-aware**: if the existing project uses Chinese (e.g., Chinese READMEs, Chinese commit messages), generate Chinese content. Detect from existing files; do not ask.
- **No AI markers in generated content**: PROJECT_GUIDE.md / CLAUDE.md / AGENTS.md must not contain Co-Authored-By trailers, model names, or "generated by" attributions. The skill is invisible.
- **Delayed split awareness**: write the "延迟拆分" rule into PROJECT_GUIDE.md so future agents know when to suggest splitting.

## Anti-patterns to avoid

- Don't create a `MEMORY.md` or memory-style file alongside PROJECT_GUIDE.md — the shared document IS the memory. Duplication causes drift.
- Don't put project conventions in `~/.claude/projects/<encoded-path>/memory/` (Claude's global auto-memory). Keep everything project-local so Codex / Gemini / future agents can see it.
- Don't import `@PROJECT_GUIDE.md` in AGENTS.md — Codex's AGENTS.md spec does not formally support that directive. Use a plain instruction "请先阅读 PROJECT_GUIDE.md".
- Don't pre-split PROJECT_GUIDE.md by content type (CONVENTIONS.md / PROGRESS.md / REFERENCE.md). Single file until a section actually outgrows the rest (>~80 lines).

## Example invocation flow (fresh iOS project)

```
User: /init-agent-collab
Claude: [detects: empty project, has Podfile and Swift files, has .git but no commits]
Claude: [infers: iOS project, no existing CLAUDE/AGENTS.md, fresh init]
Claude: AskUserQuestion ×1 combined:
        - Which agents? [default: Claude Code + Codex] (multi-select)
        - Hard conventions to seed? [defaults all checked] (multi-select)
User: [confirms defaults]
Claude: [writes PROJECT_GUIDE.md, CLAUDE.md, AGENTS.md]
Claude: [summary table + next-session note]
```

## Example invocation flow (retrofit existing project)

```
User: /init-agent-collab
Claude: [detects: existing CLAUDE.md 200 lines, existing AGENTS.md 120 lines, no PROJECT_GUIDE.md]
Claude: [reads both files]
Claude: [analyzes: 80% overlap between CLAUDE.md and AGENTS.md — that's the shared content;
                  the remaining 20% in each is agent-specific]
Claude: Proposes split plan (table: section name → target file). Shows it to user.
User: [approves with minor edits, e.g., "MCP config should stay in AGENTS.md"]
Claude: [creates PROJECT_GUIDE.md with shared content; slims CLAUDE.md and AGENTS.md to agent-specific]
Claude: [summary + tip: "if old CLAUDE.md had session memory, consider deleting ~/.claude/projects/.../memory/ to avoid duplicate loading"]
```
