#!/usr/bin/env bash
# Stage only cleanup outputs, including tracked deletions and new receipts.
set -euo pipefail

for target in r/ round-2/index.html round3/index.html sample-site-lifecycle.json cleanup-receipts/; do
  # After the final route deletion is committed, r/ is neither present nor
  # tracked. Still include it when tracked files were deleted in this run.
  if [[ -e "$target" ]] || [[ -n "$(git ls-files -- "$target")" ]]; then
    git add -A -- "$target"
  fi
done
