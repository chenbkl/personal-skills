---
name: cb-mobile-automation-worklog-experience-extractor
description: Use after mobile automation testing development, debugging, or demo-suite work to extract reusable lessons from chat history, project work logs, failure logs, and code changes. Use when the user asks to review a development phase, identify repeated automation testing problems, decide what should become project context, update an existing skill, create a new skill, produce a reusable prompt, or avoid preserving one-off noise.
---

# Worklog Experience Extractor

## Operating Rule

Extract and classify lessons only. Do not directly edit project memory, prompts, or other skills unless the user separately asks for implementation after reviewing the proposed changes.

## Resource Selection

Read these references in order:

1. `references/extraction-workflow.md` for the analysis process.
2. `references/classification-rules.md` for deciding where each lesson belongs.
3. `references/review-output.md` for the required output format.

When the user names a specific project, inspect its work logs first. For the iOS/Android automation project, likely sources include `PROGRESS.md`, `RESEARCH_NOTES.md`, existing automation skills, recent failure logs, and relevant git diffs. Do not copy sensitive values from those sources into the output.

## What To Extract

Focus on repeated or transferable patterns:

- User corrections that changed how the agent should work.
- Flaky UI automation patterns that recurred across modules or platforms.
- Cases where a standalone test passed but suite orchestration failed.
- Deep-page debugging practices that preserved useful device state.
- Risky side-effect governance for payment, card binding, password changes, signing, unbinding, clearing data, uninstalling, or account deletion.
- Cross-module and cross-platform automation methods.
- Clear user preferences that should influence future agents.

## What Not To Preserve

Do not preserve raw chat logs, credentials, account numbers, phone numbers, power ids, card numbers, SMS codes, one-off backend incidents, or implementation details that cannot influence future behavior.

## Review Gate

End with candidate recommendations for human review. The user decides whether any item is written to project context, an existing skill, a new skill, or a prompt library.
