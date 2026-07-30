# Extraction Workflow

## 1. Ground The Review

Start from the available evidence, not memory alone:

- Current chat context and explicit user corrections.
- Project work records such as progress notes and research notes.
- Failure logs, suite summaries, and debugging transcripts.
- Relevant git diffs or changed files when the user asks about recent work.

Identify the development phase being reviewed: new module build, flaky-debugging session, risky-flow implementation, demo-suite run, or post-release cleanup.

## 2. Find Repeated Signals

Prioritize signals that appeared more than once or that would clearly affect future work:

- The user corrected the route, scope, or expected outcome.
- A test passed alone but failed in orchestration.
- A deep page was more valuable than restarting from the beginning.
- The same UI instability pattern reappeared.
- A risky side effect required special gating or recovery.
- A failure category was confused with a script bug.
- The same rule applied to multiple modules or both iOS and Android.

Ignore isolated backend incidents unless they reveal a reusable classification rule.

## 3. Convert Incidents Into Rules

Rewrite events as executable guidance.

Bad:

```text
The virtual card flow got stuck after choosing the second photo.
```

Good:

```text
For system pickers without stable ids, dump visible elements, select by candidate bounds only after inspection, and log candidate count, index, bounds, and upload echo state.
```

Rules should change how a future agent acts. If a statement only records what happened, classify it as project history instead.

## 4. Remove Sensitive And Local Noise

Strip:

- Credentials, tokens, SMS codes, phone numbers, identity data.
- Real account numbers, household numbers, power ids, card numbers.
- Local-only paths unless the lesson is about repository structure.
- One-time service messages that do not generalize.

Keep path patterns and module names when they are necessary to place the recommendation.

## 5. Produce Reviewable Candidates

Do not edit durable memory automatically. Present the extracted lessons as candidates with:

- Proposed destination.
- Reason for that destination.
- Suggested wording when useful.
- Questions that require user judgment before persistence.
