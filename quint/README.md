# Quint models

The slices in this directory model selected Kogen state transitions in Quint. Each slice has an event type, state transition, observation, hand-authored scenarios, expected traces, and an xspec configuration. The harness checks scenario expectations against the model and explores generated traces while checking invariants.

The 13 core slices are accounts, approve, gate, intent, orchestration, queue, rebase, recovery, resilience, session, setup-cache, status, and stream. Slice boundaries and the adapter protocol are described in [ADAPTER.md](ADAPTER.md). Commitment levels and their rationale are in [CLASSIFICATION.md](CLASSIFICATION.md). The retained landing prototype has its own [protocol](prototype/PROTOCOL.md).

The `resilience` slice retains historical v1.1 provider policy; use `stream` for the current §4.5 request policy. Its checks demonstrate only the historical model's internal consistency.

The approval and resilience slices also include prose source material and protocol notes. These files describe slice inputs and event/observation shapes; they do not supersede the core specification.

## Run the model checks

Prerequisites: Node.js, npm, and Python 3. Install the Quint dependency from the prototype directory's package manifest:

~~~sh
npm --prefix quint/prototype install
~~~

From the repository root, typecheck every core model, run each slice's hand scenarios, and generate 500 invariant-checked traces at seeds 17, 23, and 41:

~~~sh
set -e
quint=quint/prototype/node_modules/.bin/quint
for slice in quint/slices/*; do
  [ -f "$slice/xspec.json" ] || continue
  model=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["spec"])' "$slice/xspec.json")
  "$quint" typecheck "$slice/$model"
  "$quint" test "$slice/$model"
  XSPEC_SLICE="$slice" python3 quint/prototype/harness/xspec.py spec
  for seed in 17 23 41; do
    XSPEC_SLICE="$slice" python3 quint/prototype/harness/xspec.py gen --traces 500 --steps 25 --seed "$seed"
  done
done
~~~

The `spec` command rewrites `golden/hand` files. Set `XSPEC_BUILD` and `XSPEC_GOLDEN` to temporary directories for a read-only check. Generated traces are model self-checks. Implementation conformance requires a separate adapter backed by the production transition code and full observation comparison.
