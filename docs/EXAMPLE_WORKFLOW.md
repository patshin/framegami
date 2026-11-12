# Example workflow — strict, no fabricated evidence

1. Obtain one standalone, original photographic B00 satisfying data/benchmark.json.
   Reject UI mockups, contact sheets and already stylized results. Do not crop them into a baseline.
2. Inspect the image visually, then explicitly freeze it with:
   `node scripts/freeze-benchmark.mjs /absolute/original.png --confirm-standalone-original`.
   This is an operator declaration, not an automated artistic-quality certification.
3. `node scripts/prepare-examples.mjs chatgpt en` writes exact prompts and hashes;
   it does NOT call a model. Do not mark `singleIndependentOutput` true before a real output exists.
4. Submit each exact prompt with the same B00 to an available authorized free image-edit tool.
   Save the exact submitted prompt and returned original file. Never use yesterday's stylization
   as today's source. If the tool does not expose exact request provenance, do not invent it.
5. An accepted record must include styleId, model, lang, requestKind='image-edit',
   singleIndependentOutput=true, current promptVersion, originalSha256, outputSha256,
   promptSha256, promptPath, path (under public/), actual environment, date and reviewer.
   Review identity, composition (according to that recipe's preservation policy), visual style,
   whole-scene consistency and anatomy/structure, not merely file existence.
6. Accept only matching recorded preset prompts. Nonmatching edited prompts belong to a separate
   experimental record, not proof for the standard recipe. Changed prompt versions invalidate old
   evidence. Model and language selectors must never borrow another version's visual.
7. Update status and modelStatus only from accepted evidence. Run npm run check, then
   npm run release:check. The latter intentionally fails until ChatGPT examples cover every style.
8. Preserve failures as failures. Single examples prove existence, not universal reliability.

Current checkpoint: B00 is frozen; 57 separate AI-style showcase images exist, 10 images are provisional AI-montage crops, and 10 further images are deterministic B00 processing studies, not AI model outputs. No exact-prompt accepted outputs yet. See DELIVERY.md and evidence/image-coverage.json for up-to-date counts.
