#!/usr/bin/env bash
# Creates ONE NEW PUBLIC repository on the currently authenticated user's account.
# Never overwrites a pre-existing repository. No model/API credentials are used.
set -euo pipefail
PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="${1:-iro-style-atlas}"
[[ "$REPO" =~ ^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$ ]] || { echo 'Invalid repository name.' >&2; exit 2; }
for cmd in gh git node npm tar; do command -v "$cmd" >/dev/null || { echo "Missing $cmd. Install it before running this script." >&2; exit 2; }; done
gh auth status >/dev/null || { echo 'Run gh auth login, then rerun. Never paste a token into this project.' >&2; exit 2; }
OWNER="$(gh api user --jq .login)"
USER_ID="$(gh api user --jq .id)"
[[ -n "$OWNER" && "$USER_ID" =~ ^[0-9]+$ ]] || { echo 'Could not resolve authenticated account.' >&2; exit 2; }
# Distinguish a genuine 404 from authentication/network errors; never assume all failures mean absent.
PROBE="$(mktemp)"
if gh api --include "repos/$OWNER/$REPO" >"$PROBE" 2>&1; then
  echo "Repository $OWNER/$REPO already exists. Stopped without modifying it." >&2
  echo 'Use a different new name, or follow docs/DEPLOYMENT.md for an intentional existing-repository update.' >&2
  rm -f "$PROBE"
  exit 3
fi
if ! grep -Eq '^HTTP/[0-9.]+[[:space:]]+404([[:space:]]|$)' "$PROBE"; then
  rm -f "$PROBE"
  echo 'Repository check failed without a confirmed HTTP 404. Resolve authentication/network access first. Nothing created.' >&2
  exit 4
fi
rm -f "$PROBE"
echo "This will create PUBLIC repository: $OWNER/$REPO"
echo 'It will publish the clearly labelled research preview, NOT a validated image gallery.'
if [[ "${IRO_CONFIRM_CREATE:-}" != 'yes' ]]; then
  read -r -p 'Type the repository name to authorize creation: ' CONFIRM
  [[ "$CONFIRM" == "$REPO" ]] || { echo 'Cancelled. No repository created.'; exit 0; }
fi
(cd "$PROJECT" && npm run check)
TMP="$(mktemp -d)"
CREATED='no'
cleanup(){
  code=$?
  rm -rf "$TMP"
  if [[ "$code" -ne 0 && "$CREATED" == 'yes' ]]; then
    echo "Stopped after creating $OWNER/$REPO. Do not rerun create blindly; see docs/DEPLOYMENT.md." >&2
  fi
  exit "$code"
}
trap cleanup EXIT
# Copy only the deliverable, not an enclosing Git repository or credentials.
tar -C "$PROJECT" --exclude=.git --exclude=node_modules --exclude=dist --exclude=IRO-preview.html --exclude=.env --exclude='.env.*' --exclude='*.log' --exclude='*.pem' --exclude='*.key' --exclude='*.p12' --exclude='*.pfx' -cf - . | tar -C "$TMP" -xf -
cd "$TMP"
git init -b main
git config user.name "$OWNER"
git config user.email "$USER_ID+$OWNER@users.noreply.github.com"
git add .
# Avoid running the Pages workflow before the Pages setting exists.
git commit -m 'Initial IRO research preview [skip ci]'
gh repo create "$OWNER/$REPO" --public --description 'IRO: bilingual image-to-image style recipes. Research preview; examples pending.' --source . --remote origin --push
CREATED='yes'
gh api --method POST "repos/$OWNER/$REPO/pages" -f build_type=workflow >/dev/null
gh workflow run pages.yml --repo "$OWNER/$REPO" --ref main
RUN_ID=''
for attempt in $(seq 1 20); do
  RUN_ID="$(gh run list --repo "$OWNER/$REPO" --workflow pages.yml --limit 1 --json databaseId --jq '.[0].databaseId // empty')"
  [[ -n "$RUN_ID" ]] && break
  sleep 3
done
[[ -n "$RUN_ID" ]] || { echo 'Workflow requested but no run ID yet. Inspect GitHub Actions; no live URL verified.' >&2; exit 4; }
gh run watch "$RUN_ID" --repo "$OWNER/$REPO" --exit-status
URL="$(gh api "repos/$OWNER/$REPO/pages" --jq .html_url)"
[[ "$URL" == https://* ]] || { echo 'GitHub did not return an HTTPS Pages URL.' >&2; exit 4; }
echo "Repository: https://github.com/$OWNER/$REPO"
echo "GitHub returned Pages URL: $URL"
# Never label a constructed URL as a verified deployment. Use only GitHub's response.
if command -v curl >/dev/null; then
  if curl --fail --silent --show-error --location --max-time 20 "$URL" | grep -q 'IRO'; then
    echo 'Live homepage HTTP/content check passed. Perform the remaining browser checks in docs/ACCEPTANCE.md.'
  else
    echo 'Workflow succeeded, but live homepage confirmation is still pending. Do not call this verified live yet.' >&2
  fi
fi
