# Research ledger — 2026-10-17

## Scope actually covered

Discovery used public English, Chinese and Japanese sources: GitHub prompt collections,
creator experiments, a Reddit print-style discussion, a Hugging Face failure discussion,
official model guidance and selected museum technique references. The source ledger
contains **25 references**, including deployment sources. This is **not** 25 independently
benchmarked prompt libraries, and not proof of exhaustive coverage of the internet.

Public source retrieval and selected passages were examined; entire large repositories
were not claimed to have been reviewed item by item. Login-only posts and inaccessible
sources are not silently counted as covered. No source popularity rank or current star
count is used as a quality score.

## Discovery inputs

See `data/sources.json` and the rendered About page for exact links and roles:

- Official image editing guidance: OpenAI, Google Gemini, Black Forest Labs.
- Community discovery: awesome-gpt4o-images, AI Visual Prompt Cookbook, Blinkface,
  awesome-nanobanana-pro, Image-To-Image-Prompts, img2img-prompts.
- Japanese references: a same-input creator experiment on note.com and a Japanese
  style-name index. The creator experiment also cautions about variation.
- Chinese discovery: an illustrative oil/watercolor discussion on 优设.
- Specific community cases: limited-ink Risograph; unintended side-by-side outputs
  in a FLUX Kontext multi-reference discussion.
- Technique/taxonomy anchors: The Met watercolor materials, Tate drypoint/mezzotint,
  Japanese print museum distinctions, V&A textile/quilting, Getty cyanotype example.
- Deployment boundaries: GitHub Pages and the evaluated Astro deployment path.

These references have different evidentiary roles. A museum technique definition is
not an AI prompt, and a community example is not proof that this project's rewritten
prompt produces the same image.

## What was authored

The delivered **213 canonical recipes** are independently written IRO drafts, not
copied verbatim from those collections. Each has Chinese/English technique directions,
style-specific failure constraints, aliases, category/family, source references and
an explicit untested status. The UI compiler adds source-preservation instructions
and separately structured ChatGPT, Gemini and FLUX text variants.

**1,278 exports = 213 styles × 3 model targets × 2 languages.** This is not 1,278 styles.
The model/language variants are never added to the canonical style count.

## Deduplication performed

Two obvious overlaps from the 215-entry authoring draft were merged:

- Monochrome ASCII treatment → canonical character-cell image treatment; monochrome
  is a variant rather than a separate style count.
- Felt stop-motion material → canonical needle-felt sculpture treatment; alternate
  names remain searchable.

Exact technique duplicates and duplicate IDs are rejected by validation. Visual
near-duplicate judgement still requires generated images; it is **not complete**.
Potential visual-overlap pairs to inspect after generation include paper collage vs
picture-book collage, gouache vs outline-free picture book, flat cartoon vs flat anime,
and particular cartoon/handmade-material combinations.

## Breadth and unresolved gaps

There are 19 top-level categories and 60 populated families, including Japanese
painting/woodblock/craft and anime/manga subdivisions, Chinese painting and folk art,
world miniature/folk traditions, oil/watercolor/drawing/print, comics, animation,
pixel/game art, paper, textiles, sculpture, photographic processes, graphic design,
illustration, art movements, digital treatments and a separate transformation lab.

This is a broad candidate framework, not an assertion that every world art tradition
has been covered. Specialist primary-source review is especially needed for world
miniature/folk traditions, technical rendering claims and subtle historical differences.
No cultural technique is presented as certified authentic reproduction.

## Image evidence

No qualifying standalone B00 original was obtained. The image tool outputs retained in
`docs/design/` are interface concept art, not a usable reference benchmark. No thumbnail
was cropped out of them to manufacture a supposed test result.

Therefore: **0 generated style examples; 0 image-validated styles; 0 tested model
compatibility claims.** No inferred success rate, overall "best" score or "world's most
complete" marketing claim is used.

## Next research gate

Freeze the standalone B00 original; generate each recipe independently from B00; retain
actual prompt and output evidence; review drift and failure cases; revise and deduplicate
based on images. Only then promote qualified entries from research drafts to the tested
collection. For steps and schema, see EXAMPLE_WORKFLOW.md.
