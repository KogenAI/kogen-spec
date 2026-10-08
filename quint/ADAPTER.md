# Conformance boundary for any implementation

The rewrite ships the fixed `kogen` CLI and a **separate private** JSON-lines replay executable, called `kogen-xspec` here. The private executable is not a `kogen` subcommand and adds nothing to [CLI-RULE.txt](../CLI-RULE.txt). It must call the same production transition functions the CLI uses. A Rust implementation can expose these as library functions and keep `kogen-xspec` in a separate binary target. The adapter contains JSON decoding, deterministic effect injection, and observation mapping; it contains no queue, approval, gate, provider, or landing policy.

## Two kinds of evidence

| Boundary | Black-box `kogen-conformance` | Quint trace replay |
|---|---|---|
| CLI grammar, help, stdout/stderr, exit, signals | Authority: run the read-only `cli` and `format` profiles. | No CLI parser model; do not use trace passes as a CLI substitute. |
| Intent files, approval hash, check execution, approval ref CAS | Authority: `state` and `approval`, with real Git and the `command` adapter. | `approve` and `intent`: order of refusals, unchanged prior ref, race/no-write invariants. |
| Queue and status | Authority: `cli`, `state`, and `build` with real processes, refs and restart. | `queue` and `status`: priority/time/slug ordering, one owner, stop semantics, status precedence. |
| Gate, candidate, landing, recovery | Authority: `build`, `custody`, and eventually promoted `ladder` cases with real Git trees and crashes. | `rebase` and `recovery` are mandatory for CAS/crash phase transitions; `gate` and `orchestration` are diagnostic until their L/E parts are settled. |
| Provider login, SSE, tool/custody effects | Authority: `provider` and `custody` with the fake HTTP/OAuth server and child processes. | `stream`: retry/fallback/wait decisions under injected clocks and provider outcomes. |
| Prompt cache wire and usage | Fake-provider request bodies/headers and journal `cached_input` check deterministic rules. A frozen feasible live replay separately checks the ≥0.95 threshold on each designated warm request. | `session`: affinity and thread identity, turn/repair stability and checkpoint boundaries. |
| Grok provider wire/account detail, setup cache, witness, edge probes | CLI-RULE admits `grok` on the existing provider verbs; §4.10 and P10 specify its behavior, but the frozen v1.1 suite lacks Grok coverage. | `accounts` remains diagnostic while its L-level precedence details are being validated; other experimental slices are diagnostic until promoted. |

The separate `kogen-conformance` repository retains a frozen historical v1.1 corpus of 244 cases. Its current default is an experimental v1.3 draft composition with v1.2 and v1.3 overlays, including prompt-cache and Grok cases. The suite pins the specification revision it tests and reports that revision with its own version; this repository does not pin a suite commit. A pass of the historical corpus alone does not establish v1.3 conformance, and a pass of the experimental composition is not a frozen v1.3 release certification. The additional wire cases in [CONFORMANCE-v1.2-CASES.md](../spec/CONFORMANCE-v1.2-CASES.md) remain useful for checking gaps.

## Minimal JSON-lines adapter, xspec/1

Launch one long-lived process per slice. The harness passes the slice through the private executable's argv, for example `kogen-xspec queue`. It writes one UTF-8 JSON object per line to stdin and reads exactly one JSON object per line from stdout. Diagnostics may go to stderr. EOF closes the process. No network, credential store, checkout, or production account is read; all outside results are explicit event fields. In production, these same decisions run around actual effects.

| Request | Required result |
|---|---|
| `{"op":"reset"}` | Reset all slice state and return the exact initial observation. |
| `{"op":"apply","event":{"tag":"Start"}}` | Call the real transition with the decoded event, persist its state in memory, return the exact observation. |
| `{"op":"apply","event":{"tag":"Enqueue","value":{"slug":"alpha","time":1,"priority":0}}}` | Same, using the event payload as effect input. |

Every slice's `xspec.json`, Quint `type Event` and `type Obs`, and checked-in `golden/hand/*.json` define its exact event/observation schema. Arrays that represent sets are canonicalized by the harness; ordered arrays remain ordered. Unknown tags or malformed input are protocol errors on stderr with a nonzero process exit, never a fabricated observation. `no_seam` is a **failure**, never a conformance result. No projection of observation fields can be called a pass. Existing `adapter/*.exs` files are historical Elixir diagnostics only.

For effectful transitions, events carry observations of **the effect**, not a suggested policy result. Examples: `approve.prefixOk` is calculated from actual `intent.md` + NUL + acceptance-source bytes; `approve.stableBeforeCas` records a second read immediately before the ref CAS; `rebase.Cas.won` is the injected result of a compare-and-swap; `stream` receives fake HTTP error class, elapsed time and usage. The adapter must not compute `prefixOk` from the supplied `sha` string alone, copy expected observations, or keep a parallel state machine. For a filesystem or Git effect that cannot be injected into the real transition layer, implement a temporary-origin effect driver and report the tested boundary explicitly.

## v1.3-draft slice schemas

`approve.Approve` requires `baseTree` in addition to the opaque `cacheKey` for effective setup/check/environment/toolchain/adapter context. `obs.cache` is the ordered pair `[baseTree, cacheKey]`, initially `["", ""]`. A changed checked tree must rerun the baseline even when setup products are reusable. Empty tree or context identity prohibits baseline reuse.

`gate.Demote` remains an advice event in the current observational profile. Every acceptance item still participates in verification and ranking; both landing policies require all required items to pass. `obs.offers` exposes the passing/blocking/diff ranking inputs so traces can assert that advice preserves them and the winner. Experimental demotion is opt-in and refused without admitted calibration; this slice admits no demotion profile.

`recovery.Put` requires `work`, `preserved`, and `preserveOk`; run observations also expose `cleanupPending`. `preserved` means a durable copy of the latest work/candidate, not an older snapshot. `PreservationResult({id, ok})` injects publication outcomes for cleanup retry after a terminal result. Preservation failure retains the workspace and sole incoming candidate, releases the owned claim, and prevents reapproval while cleanup is pending. A successful retry retains the preserved candidate and the terminal outcome. Actual file contents, modes, symlinks, create-only publication, earlier snapshots, writer shutdown and durability still require real Git/filesystem fault injection.

The retained Elixir adapters remain diagnostics: approval/recovery validate the new input fields and return `no_seam`; gate reports `not_replayed` for auditor events and preserves its selector state. These responses are conformance misses. Adapter syntax and schema decoding checks do not substitute for production replay.

## Running and acceptance

From `quint/prototype/`:

```sh
XSPEC_SLICE=../slices/queue python3 harness/xspec.py spec
XSPEC_SLICE=../slices/queue python3 harness/xspec.py gen --traces 500 --steps 25 --seed 17
XSPEC_SLICE=../slices/queue python3 harness/xspec.py conform -- /path/to/kogen-xspec queue
```

`spec` verifies hand expectations against Quint and writes their full observations. `gen` checks invariants on each generated step and writes randomized traces. `conform` requires **exact** observations at reset and every event. Its `--project` option exists solely to diagnose an old partial seam, prints `DIAGNOSTIC PROJECTION ONLY`, and exits 2 even if projected fields agree. Use distinct seeds 17, 23, and 41 before calling a guaranteed slice accepted; preserve the scenario and trace seed in the report. The private adapter and the public CLI must be built from the same revision. The user-facing release gate is the black-box suite plus the guaranteed trace slices and the live cache smoke, with version gaps reported separately.

The shell invocation uses an argv vector; no shell evaluates the adapter command. The protocol has no token, URL, or implicit environment lookup, so replay can run on a blank temporary HOME.
