# Risky Flows

Use this reference for flows that change account, money, signing, identity, or persistent backend state.

## Confirmation and Gates

Require explicit user confirmation or an explicit environment gate before:

- Real payment or refund-like flows.
- Binding or unbinding bank cards/accounts.
- Changing, resetting, or verifying passwords beyond a non-mutating probe.
- Signing, unbinding, cancelling, deleting, clearing app data, uninstalling, reinstalling, or deleting accounts.

Default tests should skip rather than perform side effects.

## Reversible Design

Prefer self-recovering flows:

- Password changes: baseline value -> temporary value -> baseline value.
- Binding flows: create one test-owned item -> verify visible -> remove that same item.
- Signing flows: pre-clean existing fixture -> sign -> verify -> unbind/cancel.
- Payment flows: use preflight tests that stop at cashier before enabling real payment.

Persist state after each irreversible step when the project supports it. If the second half of a roundtrip fails, report the current account state and manual recovery action.

## Test Data Ownership

- Keep real credentials and fixtures in gitignored env files.
- Put only empty templates in `.env.example`.
- Use consume/persist helpers for one-time or sequential data such as card numbers, power ids, or generated accounts.
- Record the latest created item only when cleanup depends on it.
- For SMS, establish a send-before baseline and accept only a new matching code. Reload SPA-based SMS backends before reading latest records.

## Failure Classification

Classify terminal failures distinctly:

- Script bug: missing anchor, wrong branch, bad wait, stale element, unhandled keyboard.
- Test data issue: no permission, empty list, duplicate account, already signed, unsupported card.
- Backend/environment issue: query failure, service toast, delayed async result, missing SMS backend record.
- Risk control: captcha, face verification, real-name verification, server-side block.
- Expected business terminal: success, processing, submitted, rejected, cancelled.

Do not continue a suite through risky downstream steps after an unknown or dirty state.
