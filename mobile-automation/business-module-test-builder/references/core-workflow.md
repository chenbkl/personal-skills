# Core Workflow

## 1. Source-First Module Survey

Before writing automation code, inspect the business source and identify:

- Module entry points from home, all-services, mine, settings, deep links, or existing lists.
- Page/controller/activity chain and transition triggers.
- New/old UI switches, feature flags, regional variants, account-type variants, and server-driven layouts.
- Form fields, dynamic lists, empty states, modal dialogs, WebView/system-picker boundaries, and result pages.
- Backend responses that mean success, processing, failure, no permission, empty data, duplicate submission, captcha, or toast-blocked state.

Output a short module map before coding: entry path, page sequence, required data, side effects, terminal states, and blockers.

## 2. Identifier-First Rule

Do not write a stable test against missing or speculative anchors.

- Add or document a page root for every page that must be detected.
- Add stable ids for buttons, inputs, list containers, list items, result labels, and close/finish/back controls.
- Dynamic list ids must use visible index or a stable business key; never use user-specific text as an identifier.
- Text assertions are allowed for business values, but text should not be the only navigation anchor when source can provide ids.
- If app-side ids are unavailable, record the fallback strategy and why it is acceptable.

## 3. Business Flow Intake

After source survey, ask only for information not discoverable from the repo:

- Exact route the user wants automated.
- Test data: account, amount, phone, enterprise/card/account selector, region, or fixture sequence.
- Expected terminal state: success page, processing page, submitted status, bound list item, removed list item, or known blocker.
- Whether real side effects are allowed.

Do not guess business routes such as which menu entry is canonical, which card to pick, or whether a request should be submitted.

## 4. Exploratory Implementation Loop

Implement and validate in small slices:

1. Add state detection for the current page.
2. Dump the live page and verify the anchors are visible.
3. Add one action for the next transition.
4. Run that transition on device.
5. Add flow orchestration for the verified transition.
6. Repeat until the terminal state is reached.

When a test fails on a deep page, inspect the current screen first. Use temporary scripts only to probe or reproduce; land the actual fix in module/common code.

## 5. Diagnostics Required in Full Tests

Full-chain tests must print enough information for a human demo/debug session:

- Initial login/app state.
- Entry target and matched route.
- Page/branch classifications.
- Key test data identifiers, masked when sensitive.
- Dialog/cashier/auth/payment/result type where relevant.
- Backend/blocker toast or captcha state.
- Terminal result and cleanup/return state.

Use Chinese output when the project convention or user demonstration audience is Chinese.
