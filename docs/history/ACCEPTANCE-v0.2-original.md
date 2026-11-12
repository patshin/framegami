# IRO v0.2 acceptance record

Date: 2026-10-19. **Research preview only; not a completed image gallery.**

| Check | Actual result | Evidence |
|---|---|---|
| Catalog and pure logic + HTTP + deployment safety | 314 / 314 PASS | node-test-results.txt |
| Bilingual static routes | 439 built | ../dist/build-info.json |
| Root/repo-prefix static asset resolution | 439 × 2 PASS | static-route-results.json |
| Actual local HTTP requests | 895 successful assertions | http-results.json |
| Original Chromium DOM regressions | 65 / 65 PASS | browser-test-results.json |
| Added Chromium DOM regressions | 22 / 22 PASS | browser-v02-results.json |
| 320/390/768/1440px atlas overflow | PASS for exercised pages | browser-v02-results.json |
| Deployment safety exits | 5 / 5 PASS, MOCK CLI ONLY | deploy-safety-results.json |
| Standalone baseline B00 | MISSING | ../data/benchmark.json |
| Per-prompt visual examples | 0 | ../data/catalog.json |
| Formal content gate | BLOCKED (expected exit 2) | release-gate.json |
| Remote GitHub writes / deployment | NOT PERFORMED | DEPLOYMENT_CHECK.json |

The 10 HTTP groups and 5 mocked deployment checks are included in 314, not additional tests.
895 counts requests, not 895 independent UI or artistic checks. Browser tests load authored HTML
in memory because policy blocks navigation. Local storage and download capture are explicitly
instrumented in test HTML only; production files contain no test adapter. There is no live
origin, clipboard-permission, Safari/Firefox, screen-reader or physical-device certification.

Screenshots in `screenshots/` are actual Chromium renders of the implemented frontend.
Abstract covers are index art, never AI style-transfer output. A generated but rejected UI
mockup is isolated in `generation-attempts/`, not in the public gallery or generated-example count.
