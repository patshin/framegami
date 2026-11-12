#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
command -v node >/dev/null || { echo 'Node.js 20+ is required. No npm install or model account is needed.'; read -r -p 'Press Return to close.' _; exit 1; }
npm run check
printf '\nOpen http://127.0.0.1:4173 in your browser. Ctrl+C stops the local server.\n'
npm run preview
