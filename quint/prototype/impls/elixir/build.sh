#!/bin/sh
# No-op: core.ex is loaded by `elixir -r` at startup. Compile once to surface errors.
cd "$(dirname "$0")"
mkdir -p _build
elixirc -o _build core.ex
