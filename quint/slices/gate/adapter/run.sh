#!/bin/sh
cd "$(dirname "$0")"
: "${KOGEN_EBIN:?Set KOGEN_EBIN to the compiled Kogen ebin directory}"
exec elixir -pa "$KOGEN_EBIN" adapter.exs
