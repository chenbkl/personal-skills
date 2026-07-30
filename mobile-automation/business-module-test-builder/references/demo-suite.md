# Demo Suite

## Inclusion Rules

A demo suite should contain complete business chains only. Exclude entry-only, page-only, half-chain, and exploratory tests unless the user explicitly asks for them.

Good demo items:

- Cold start to known app state.
- Login.
- Full payment to result page.
- Full application/signing submission.
- Bind then unbind owned data.
- Logout or cleanup.

Poor demo items:

- Open entry page only.
- Click into a form then stop without a business terminal state.
- Tests requiring manual intervention without a clear success signal.
- Known unstable backend/data cases mixed into a green-line demo.

## Suite State Contract

- Define the suite start state, usually cold-start logged out.
- Each item must end in a state the next item can use: home, mine, module home, or logged-out home.
- If a business stack cannot be backed out reliably, use the project's accepted restart-to-home helper and log that choice.
- Login tests inside a suite should not perform an extra cold start if the suite already did it.
- Cleanup/logout should tolerate being launched from a deep page by returning to a main tab first.

## Output Contract

Each item must print:

- Display name and pytest path.
- PASS/FAIL/SKIP/MIXED.
- Elapsed time.
- pytest passed/failed/skipped/error counts.
- Important business diagnostics emitted by the test.

The final summary must print total elapsed time and counts by status.

## Failure Handling

- Stop immediately when a critical setup item fails, such as cold start or login.
- For non-critical business items, continue only if the app has been restored to a known state.
- Report known blockers clearly: captcha, empty fixture list, service toast, no permission, backend query failure.
- Do not hide a script bug as skip.

## Performance and Demonstration Quality

- Prefer measured waits on state changes over fixed sleeps.
- Add stage timings for slow flows when useful: cold start, entry, query, submit, result, cleanup.
- Avoid repeated full-suite reruns while debugging; create temporary focused suites and delete or clearly mark them after use.
- Use concise, audience-readable logs. For Chinese demos, print Chinese branch labels and result labels.
