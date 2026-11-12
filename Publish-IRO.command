#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
# Uses the user's own local GitHub CLI login. This file contains no credentials.
bash scripts/deploy-github.sh framegami
