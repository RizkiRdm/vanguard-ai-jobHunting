#!/usr/bin/env bash
# Run API, worker and web together. Ctrl-C stops all three.
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -f .env ]; then
  echo "scripts/dev.sh: missing .env — copy .env.example and fill in values" >&2
  exit 1
fi

pids=()
stop() {
  trap - EXIT INT TERM
  for pid in "${pids[@]}"; do
    kill -TERM -- "-$pid" 2>/dev/null || true
  done
  wait 2>/dev/null || true
}
trap stop EXIT INT TERM

# Own process group per service so descendants (tsx/vite) die with it.
run() {
  setsid "$@" &
  pids+=("$!")
}

run bun run dev:server
run bun run worker
run bun run dev:web

wait -n
