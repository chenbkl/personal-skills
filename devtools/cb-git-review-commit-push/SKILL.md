---
name: cb-git-review-commit-push
description: "[CB Private Skill] Review git workspace changes using the active chat context, produce a clear commit message, and complete commit plus push safely. Use when the user asks to review pending code, summarize changes for commit, write commit messages, or directly commit and push a branch."
---

# CB Git Review Commit Push

## 0. Self-update check (do this first, once)

This skill is managed by the git repo `personal-skills`. Before the main workflow, silently check for a newer version (Lixinger-style on-demand self-update):

```bash
d="$(readlink "$HOME/.claude/skills/cb-git-review-commit-push" 2>/dev/null || readlink "$HOME/.codex/skills/cb-git-review-commit-push" 2>/dev/null)"
[ -n "$d" ] && bash "$(git -C "$d" rev-parse --show-toplevel)/check-update.sh"
```

- Output `up-to-date` or offline → say nothing, just continue.
- Output `⚠ update-available` → tell the user "your personal-skills has a newer version, run `update.sh` now?"; only run `update.sh` if they agree, otherwise continue. Never block on a failed check.

## Overview

Execute a reliable workflow for code submission:
1. Review pending changes against the user request and chat context.
2. Draft a high-quality commit message.
3. Get explicit user confirmation before commit.
4. Commit and push with safe git checks.

Prefer concise, factual summaries. Prioritize correctness and safety over speed.

## Workflow

### 1) Build Review Context

- Read the latest user intent from chat history.
- Detect target scope from context:
  - specific files/modules requested by the user
  - bugfix/feature/refactor intent
  - constraints (no unrelated changes, keep behavior, etc.)
- If scope is ambiguous, default to reviewing currently staged changes first.

### 2) Inspect Workspace Changes

Run these commands in order:

```bash
git status --short --branch
git diff --staged
git diff
```

Apply this policy:
- Treat staged and unstaged changes separately.
- Do not include unrelated edits without explicit user instruction.
- Flag obvious risks before commit:
  - secrets/tokens/keys accidentally added
  - large binary or generated noise files
  - accidental lockfile or formatting-only churn unrelated to task

If needed, inspect file-level diffs for clarity:

```bash
git diff --staged -- <path>
```

### 3) Produce Commit Message

Write a message that reflects actual changes, not assumptions.

Format:
- First line: short imperative summary (<= 72 chars preferred)
- Blank line
- Body bullets for important details and behavioral impact

Message quality rules:
- Commit message must be Chinese only (subject and body).
- Do not use English words unless they are unavoidable code identifiers (file name, class name, API name).
- Never include agent-related words such as `codex`, `openai`, `chatgpt`, `ai`, `智能体`, `机器人` in commit messages.
- Mention primary user-facing or system impact.
- Mention key technical change (component/module).
- Avoid vague text like "update" or "fix issues".
- If change is small, a single-line commit message is acceptable.

### 4) Ask User Confirmation (Required)

Before any `git commit`, show the generated commit message and ask the user to choose one option:
- `是`: use the current message and continue commit + push.
- `否`: stop, do not commit and do not push.
- `修改`: let the user provide edits, regenerate message, then ask again.

Mandatory rules:
- Never run `git commit` or `git push` until user chooses `是`.
- If user chooses `否`, end workflow immediately.
- If user chooses `修改`, keep iterating until `是` or `否`.

### 5) Commit Safely

Before committing:
- Confirm branch and staged set are expected.
- If nothing is staged, stage only intended files (or ask user if scope is unclear).

Commit command:

```bash
git commit -m "<subject>" -m "<body line 1>" -m "<body line 2>"
```

Use single `-m` when no body is needed.

### 6) Push Safely

Check upstream and push:

```bash
git rev-parse --abbrev-ref HEAD
git push
```

If upstream is missing, set it explicitly:

```bash
git push -u origin <branch>
```

Safety rules:
- Do not force push unless user explicitly requests it.
- Do not amend existing commits unless user explicitly requests it.
- Do not rewrite history in this workflow.

## Output Template

After finishing, report:
- reviewed scope (staged/unstaged and notable files)
- final commit message used (Chinese-only and agent-word-free)
- user confirmation choice used (`是`/`否`)
- commit hash (if committed)
- push result (remote/branch, if pushed)
- any residual risks or skipped validation

## Failure Handling

- If commit fails: show exact git error and fix path.
- If push fails: report remote error and next safe command.
- If review finds sensitive data: stop and ask user before any push.
