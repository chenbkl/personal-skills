---
name: business-module-test-builder
description: Use when building or extending iOS or Android automation tests for a new business module, including source-code analysis, stable accessibility identifiers/resource ids, state/actions/flow/test layering, real-device exploration with MCP or native drivers, risky-flow handling for payment/binding/password/signing flows, and demo suite integration.
---

# Business Module Test Builder

## Operating Rule

Build a business-module test as a small engineering project, not as a recorded click path. Use one cross-platform workflow, then load the platform adapter that matches the user's target.

## Resource Selection

Read only the references needed for the current task:

- Start every new module with `references/core-workflow.md`.
- For iOS modules, also read `references/ios-adapter.md`.
- For Android modules, also read `references/android-adapter.md`.
- For Android emulator startup, ADB repair, `adb devices` failures, or mobile-MCP/uiautomator2 device reachability issues, read `references/android-emulator-runbook.md`.
- For payment, card binding, password changes, signing, unbinding, clearing data, uninstall/reinstall, account deletion, or other state-changing flows, read `references/risky-flows.md`.
- For suite runners, TUI/demo scripts, or presentation-ready regression ordering, read `references/demo-suite.md`.

If the user asks for a cross-platform plan, read both platform adapters. If the platform is not stated, inspect the repository first; ask only if both platforms are plausible and the answer changes the work.

## Mandatory Development Loop

1. Read the business app source before writing tests.
2. Identify entry points, pages, UI branches, dynamic lists, dialogs, backend terminal states, and known blockers.
3. Design stable identifiers/resource ids before consuming them in automation.
4. Ask the user for the exact business route, test data, expected terminal state, and real side effects when these cannot be derived from source.
5. Verify anchors on a real device or emulator with MCP/page dump before adding them to state/actions modules.
6. Implement one segment at a time: state detection, action, flow transition, pytest assertion.
7. Run the segment before writing the next segment.
8. Preserve deep failure state for debugging; do not restart from home unless the current state is no longer useful.
9. Promote only full business chains into demo orchestration.

## Code Organization Contract

Use this layering unless the existing project has a stronger local convention:

- `*_state.py`: constants, enums, page detection, read-only state, result classification.
- `*_actions.py`: one-screen operations, robust click/input/scroll helpers, no full business chain.
- `*_flow.py`: cross-page orchestration and branch selection.
- `tests/<module>/test_*.py`: environment gates, setup, flow call, diagnostic prints, assertions.
- `common/`: shared device, navigation, dialogs, toast, loading, keyboard, scrolling, and element primitives.

Keep pytest files thin. Reusable behavior belongs in module flow/actions or common helpers.

## Definition of Done

A module is not done when an entry page opens. It is done when the intended business terminal state is asserted, failure classes are explainable, side effects are controlled, and the test ends in a known state that can feed the next suite item.
