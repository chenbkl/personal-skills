# iOS Adapter

## Identifier Design

- Prefer `accessibilityIdentifier` in the business app source.
- Give every automation-relevant page a root id such as `page_<module>_root` when that matches the project convention.
- Keep identifiers stable and independent from phone numbers, names, account numbers, amounts, backend marketing text, or row content.
- If a container has `isAccessibilityElement = NO`, do not rely on the container as the only anchor; detect the page through child controls or a root view that is actually exposed.
- For dynamic cells, set identifiers during cell configuration or display, using visible index or stable business id.

## Driver and Query Rules

- Avoid repeated `exists -> get/click` patterns in WDA-heavy code; prefer single-query helpers that return optional elements or click with retry.
- Cache one XML/tree snapshot only when reading many visible rows from the same screen.
- Treat stale/not-found after a successful click as possibly already-transitioned; check the expected next dialog/page before failing.
- Prefer MCP/WDA dump at the current deep state over restarting the flow.

## Business App Integration

- Put automation-only business-source changes in the auto-test worktree, not the user's active feature checkout.
- Update the module identifier document alongside source changes.
- Rebuild and install before expecting new identifiers to appear.
- Watch for Pods, WDA signing, bundle id conflicts, and device/worktree-specific local changes.

## iOS-Specific Flaky Patterns

- Some modal or risk verification flows are pre-request gated; use click-then-short-wait-retry only where source or device evidence supports it.
- Back navigation may pop to a different tab/root than Android; assert the actual returned page after success.
- For long lists, separate single-screen read, scroll-to-bottom, target search, and stable-boundary detection.
