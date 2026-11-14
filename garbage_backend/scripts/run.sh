#!/usr/bin/env bash
set -e
cd "$(dirname "$0")/.."

echo "Starting Garbage Collector Backend…"
uv run backend   