# Android Adapter

## Anchor Strategy

- Prefer `resource-id` for stable controls.
- Use `contentDescription` for dynamic rows, reusable upload components, checkbox lists, or controls whose `resource-id` is shared.
- Page detection may combine Activity, root id, title text, and key controls.
- Dynamic list rows need stable `contentDescription` or an index convention. If no app-side anchor exists, use visible row snapshots and bounds as a fallback.

## uiautomator2 Stability Rules

- Click and input helpers must re-query elements after `StaleObjectException`, `UiObjectNotFoundError`, transient `RPCUnknownError`, or page refresh.
- Do not keep a selector object across meaningful page transitions when the view may be recreated.
- If an id click is flaky but bounds click works, inspect for stale nodes, offscreen center, overlay, shared ids, or RecyclerView rebinds; do not blindly replace all id clicks with coordinates.
- For system photo pickers and similar system UI with no reliable ids/text, dump visible elements first and click by candidate bounds with logging.
- WebView automation needs a separate strategy; `uiautomator2` may not see H5 internals.

## Android Business App Integration

- Put automation-side business-source changes in the Android auto-test worktree.
- For reusable upload/list components, add configurable `contentDescription` prefixes instead of hard-coding one module's ids.
- After changing business source, install the rebuilt APK before validating anchors.

## Android-Specific Branching

- New and old business UI implementations often expose different ids; detect the visible implementation first and dispatch to separate code paths.
- Cashier type and payment-auth type are separate dimensions. Detect both before submitting payment.
- iProtect keyboards must be typed by the correct component: QWERTY, random numeric keypad, old/new payment dialog, or reset-password keyboard.
- Activity reads can hang under secure input. Use bounded fallbacks such as adb dumpsys only when local project patterns support it.
