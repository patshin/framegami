# Maintaining Framegami

Use Node.js 22 for the static site. Run `npm run check` to validate the catalog, build the site, run unit tests and check all routes. Use `npm run preview` for local review.

For browser and importer tests, install Pillow and Playwright in a Python virtual environment, run `python -m playwright install chromium`, then run `npm run test:import` and `npm run test:browser`.

## Images

Follow the [pack protocol](docs/IMAGE_PACK_HANDOFF.md). Start with a dry run using a canonical style ID. All 213 styles currently have illustrations. Use `--upgrade-preview` on both commands when replacing an eligible procedural or montage preview with an independent AI image.

```sh
python3 scripts/import-image-pack.py /path/to/pack.zip --dry-run --upgrade-preview
python3 scripts/import-image-pack.py /path/to/pack.zip --upgrade-preview
npm run check
```

See the [integration report](docs/STATUS.md), [batch audit](evidence/final-integration/audit.json) and [content license](CONTENT-LICENSE.md). Original manifests, hashes and IDs refer to the project name at the time of import.
