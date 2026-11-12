# IRO · 色谱 — checkpoint 57 acceptance and limits

**Not final acceptance. No remote deployment or complete 213-image coverage.**

- Source & prompt catalog validation, Node unit tests, and both root/subpath static route checks must pass using `npm run check`.
- Headless Chromium gallery/source checks must pass using `npm run test:images` (current v0.4 checks).
- Source B00 is present with SHA-256 integrity; 47 separately generated image showcases remain untouched; 10 montage-derived previews are provisional and have separate source provenance and bounds.
- `scripts/gallery-coverage.mjs` reports 77 illustrated styles (57 independent AI-style showcases, 10 provisional montage crops, 10 B00 procedural studies), 136 missing, 0 exact-prompt validated. The full independent-gallery gate intentionally fails until 213 independent outputs are present.
- The exact-prompt release gate intentionally fails. No claim of visual quality, stability, suitability for all input subjects or multi-model compatibility has been established by code tests.
- Browser rendering checks use an embedded HTML preview and a test-only absolute URL base to allow URL parsing. They do not assert genuine hosted-domain localStorage/clipboard acceptance, Safari/Firefox or a physical device.

The original v0.2 acceptance record is archived at `docs/history/ACCEPTANCE-v0.2-original.md`.
