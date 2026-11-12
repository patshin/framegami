# Official documentation recheck — 2026-10-19

These references were opened during v0.2 implementation. They support build/deployment
configuration choices, not prompt quality or claims of a completed online deployment.

- GitHub Pages custom workflows: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
  The current guide shows checkout v6, configure-pages v5, upload-pages-artifact v4 and deploy-pages v4; deploy requires pages write and id-token write.
- setup-node maintained repository: https://github.com/actions/setup-node
  Current README shows v7 and package-manager-cache=false when caching is unnecessary.
- gh repo create: https://cli.github.com/manual/gh_repo_create
- GitHub Pages REST: https://docs.github.com/en/rest/pages/pages
- Google image editing/style transfer: https://ai.google.dev/gemini-api/docs/image-generation
- Community prompt source re-opened: https://github.com/xcc3641/blinkface/blob/main/prompts.md

The actual GitHub connector was also invoked for the authenticated login and target
repository lookup; it did not expose repository-create, push or Pages-write operations.
No source-star counts, current best-model rankings or 'full-web completeness' claims were added.
