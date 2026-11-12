# IRO · 色谱 | Image-to-Image Style Atlas

Open-source, bilingual (中文 / English), **static** image-to-image prompt atlas and editing workspace for GitHub Pages. No backend, user account, embedded API key, or online generation service.

## Verified local handoff — 2026-11-03

- **213** canonical styles, **19** categories, **60** families.
- **105** styles have displayed images: **67** individually generated AI showcases, **10** labeled montage crops, **28** deterministic B00 processing studies.
- **108** styles have no image; **0** exact-prompt validated outputs. Different image provenance types are explicitly disclosed.
- **439** statically generated routes, **1,278** model-language prompt text variants (ChatGPT, Gemini, FLUX × Chinese/English). No model-compatibility claim.
- GitHub source and GitHub Pages deployment **not yet performed**.

## Run the site locally

Requires Node.js 20+. No npm dependencies are needed for the site build:

```bash
cd iro-style-atlas
npm run check
npm run preview
```

Open the local URL shown by the preview server. Use the served site rather than opening the large `IRO-preview.html` directly: the single-file backup embeds all showcase images and can be slow.

## For the remaining 108 styles

Image generation is performed externally; Codex imports completed ZIP packs using the included script. No manual placement into HTML is required.

```bash
python3 -m pip install Pillow
python3 scripts/import-image-pack.py /absolute/path/IRO-Assets-Batch-01.zip --dry-run
python3 scripts/import-image-pack.py /absolute/path/IRO-Assets-Batch-01.zip
npm run check
npm run preview
```

For an *individually generated AI image* replacing an existing montage/procedural preview, use `--upgrade-preview` on both importer commands. Existing images are archived and their history retained. Previously covered independent AI entries are not overwritten.

- **[Image pack contract](docs/IMAGE_PACK_HANDOFF.md)**: required manifest and provenance rules.
- **[Codex continuation instructions](docs/CODEX_HANDOFF_PROMPT.md)**: one-time copy/paste handoff.
- **[Remaining prompt queue](data/image-production-queue.json)**: exact IDs, full Chinese and English ChatGPT prompts for 108 missing styles.
- **[`production-batches/`](production-batches/)**: 11 ready-to-generate worklists of 10 or fewer styles, plus manifest example.
- **[Source audit](evidence/image-coverage.json)**: active example kinds and image status for every style.

Import smoke test (requires Python Pillow and Node.js):

```bash
npm run test:import
```

This creates synthetic test images only in a disposable temporary copy, testing fresh import, montage import, provenance and upgrade/archive. It never adds fabricated examples to the website.

## Release and provenance boundaries

Code is MIT and independently authored style prompt text is described in `CONTENT-LICENSE.md`. The full content gate (`npm run gallery:check`) intentionally fails while styles are missing individual AI showcases, and exact-prompt verification remains unfinished. Use the included GitHub Pages workflow after the site is ready, with no server-side image generation.
