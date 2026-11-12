# Acceptance record

Date: 2026-10-17
Release decision: **RESEARCH PREVIEW — NOT CONTENT COMPLETE — NOT DEPLOYED**

## Completed technical checks

| Check | Result | Evidence |
|---|---|---|
| Catalog schema, IDs, localization, constraints and source URLs | PASS | `npm run validate` |
| Pure-logic / content / import / security regression tests | 266 / 266 PASS | `docs/node-test-results.txt` |
| Static build | 439 routes, 1,278 text exports | `dist/build-info.json` |
| Root and repository-prefix asset resolution | 439 × 2 PASS | `docs/static-route-results.json` |
| Chromium DOM and interaction regression | 65 / 65 PASS | `docs/browser-test-results.json` |
| Desktop and 390px mobile overflow checks | PASS for exercised pages | Browser report and screenshots |
| Deployment shell syntax | PASS | `bash -n scripts/deploy-github.sh` |
| API key collection / model requests | Not present | Browser source, CSP and tests |

## Important test qualifications

The environment rejected browser HTTP and file navigation with an administrator
policy. The generated standalone HTML was therefore rendered in real Chromium using
`page.set_content`, without changing or disabling those policies. This is a DOM and
rendering test, **not a live-host navigation test**.

Persistence tests use an explicitly documented test-only localStorage adapter because
in-memory pages do not supply the production HTTP origin. Export checks inspect the
actual Blob payload. Native clipboard permissions and final download behavior are
not claimed as verified on the user's browser. Node URL resolution verifies generated
asset locations for root and `/iro-style-atlas/`, not network deployment success.

No Safari, Firefox, physical phone, keyboard-only exhaustive audit, screen-reader
audit or complete WCAG certification has been performed. Reduced-motion preference,
native mobile dialog behavior, keyboard search, accessible labels on exercised controls
and viewport overflow were checked.

## Issues found and fixed in this pass

- Standalone preview without a hash incorrectly fell into static-path parsing when
  hosted over HTTP. The preview parser now preserves its configured initial route.
- Workbench drafts could be lost when browser storage was unavailable. Session-memory
  fallback now retains them for the current page session and warns about backup needs.
- Manual prompt edits needed protection from control changes. Recomposition now requires
  confirmation; unedited text updates directly from controls.
- A new custom prompt initially contained instruction text instead of being blank.
  It now opens a genuinely empty editor with a placeholder.
- Lab prompts inherited a blanket ban on frames that contradicted card/box recipes.
  The compiler now permits only the specifically requested transformation container.
- An initial search test demanded a nonexistent combined style. It was corrected to
  test a real Japanese woodblock combination; another test explicitly confirms that
  the search does not invent a missing Japanese-watercolor match.

## Required content gates — not passed

- Approved standalone B00 original: PENDING.
- Independent same-input style outputs: 0 / 213.
- Per-example visual review and actual-model record: PENDING.
- Cross-model validation: PENDING.
- Visual near-duplicate review: PENDING.
- A source-backed claim of exhaustive world coverage: NOT MADE.

## Required publishing gates — not passed

- New public GitHub repository: NOT CREATED.
- Repository upload and Actions run: NOT EXECUTED.
- Pages enablement and real returned site URL: NOT VERIFIED.
- Live root/nested-page/clipboard/storage/mobile checks: PENDING.

Passing schema tests must never be reported as passing art, model or deployment gates.
