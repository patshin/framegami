# IRO source rules

- Maintain 213 canonical style IDs; bilingual prompt exports do not multiply the style count.
- Keep the existing frozen B00 portrait original. Do not regenerate it to excuse missing style output.
- Keep exact-prompt evidence and generated style illustrations distinct. A real image may be useful for display without proving an unrecorded Prompt was tested.
- No repeated generated output across unrelated styles, no UI-montage crops, no CSS effects presented as AI examples.
- Never expose or request API keys in this public static product. No generation backend is part of this build.
- Never certify a Gemini or FLUX prompt from a ChatGPT style illustration.
- Run data integrity, build, tests, route checks and browser asset-decode checks after edits.
- `gallery:check` stays failed while any style lacks a case image. Other tests cannot override that content gate.
- Do not infer or fabricate deployment status.
