# Evidence

`2026-10-26/installed-results.json` contains the eight final workload summaries. `comparison.json` and `comparison-refine.json` hold the earlier candidate sweep. `lifecycle.json` is an allowlisted summary of the installed reset/re-enable and automatic-restart checks.

`2026-10-26/selector-verification.json` records a later check of all three restored selector routes through the existing AsusPower IPC. It verifies settled profile, boost and refresh state, then returns to Balanced. It does not claim injected mouse clicks or a physical charger test.

`history-2026-10-25.json` records the separate stock/tuned CPU comparison, the direction-only RX result and the earlier lifecycle status. It is explicitly not the October 26 preset baseline.

These files omit boot/session identifiers, process environments, credentials, filesystem identifiers, user paths and private screenshots. Local high-frequency telemetry and session manifests are not dumped into the public repository.

Run `python3 tools/check_evidence.py` to recompute the comparison and check the saved test invariants. This verifies the data's internal consistency, not the hardware itself.
