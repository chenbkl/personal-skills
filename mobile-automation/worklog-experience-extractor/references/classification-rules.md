# Classification Rules

## Write To Project Context

Choose project context for facts that are true for the current repository but not necessarily reusable elsewhere:

- Worktree paths, branch conventions, package/bundle ids.
- Current module status and known blockers.
- Project-specific test data policies.
- Local MCP/device/tool configuration.
- Current progress snapshots or historical run results.

Recommended destinations are project-specific files such as `PROJECT_GUIDE.md`, `PROGRESS.md`, or `RESEARCH_NOTES.md`, depending on the project's conventions.

## Write To Existing Skill

Choose an existing skill when the lesson changes future behavior for the same domain:

- Cross-module mobile automation workflow.
- Platform adapter rules for iOS or Android.
- Risky-flow handling.
- Demo-suite orchestration.
- UI stability heuristics.

Prefer updating a focused reference file over expanding a root `SKILL.md`.

## Create A New Skill

Recommend a new skill only when the topic has its own trigger and workflow:

- It applies beyond one existing skill's domain.
- It would be reused across multiple projects or repeated phases.
- It needs its own classification, templates, or references.
- Putting it into an existing skill would make that skill trigger too broadly.

## Keep As Prompt

Choose a prompt when the instruction is useful but not durable enough for a skill:

- One-time execution preferences.
- A module-specific task brief.
- A short review checklist for the next run.
- A command or workflow the user wants to paste manually.

## Do Not Preserve

Do not preserve:

- Sensitive values or identifiers.
- One-off backend failures without reusable lesson.
- Temporary debugging details already fixed.
- Agent mistakes that do not imply a durable rule.
- Duplicates of rules already present in an existing skill or project guide.

## Decision Test

Before recommending persistence, ask:

```text
Will this change how a future agent behaves?
Will it still be true in another module or later phase?
Is this the narrowest durable place for it?
Would storing it increase context quality more than context noise?
```
