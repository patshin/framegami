# IRO · 色谱 | Image-to-Image Style Atlas

中英文图生图 Prompt 图鉴。213 种风格按 19 个分类、60 个家族收录，每种提供 ChatGPT、Gemini、FLUX 的中英文配方，共 1,278 个文本版本。网站使用静态文件，收藏、草稿和自定义配方保存在当前浏览器。

**视觉覆盖 213/213**，包括 155 张独立 AI 风格示意、30 张有原始拼图和裁切坐标的预览、28 张基于 B00 的程序化示意。严格 Prompt 验证为 **0/213**。模型选项用于切换文字配方。Batch 05 和 08 共 20 张独立 AI 示意由素材包声明来源，缺少生成编号；Batch 05 的提交语言也未知。

## 使用

1. 在图鉴按分类和家族浏览，或用中文、英文及别名搜索。
2. 打开风格详情，查看案例来源、技法、参考资料。选择模型和语言后复制 Prompt，在自己的图像工具中配合原图使用。
3. 将多个风格加入比较台，或在工作台调整背景、色彩和文字。另存自定义配方可保留编辑版本。更换浏览器前可导出备份。

## Local development

Use Node.js 22. The static build has no npm dependencies.

```sh
npm run check
npm run preview
```

Open the localhost address printed by the preview server. For a repository subpath, set SITE_BASE_PATH=/iro-style-atlas/ during build and BASE_PATH=/iro-style-atlas during preview.

## Asset maintenance

```sh
python3 -m pip install Pillow playwright
python3 scripts/import-image-pack.py /path/to/pack.zip --dry-run
python3 scripts/import-image-pack.py /path/to/pack.zip
npm run check
npm run test:import
python3 -m playwright install chromium
npm run test:browser
```

All canonical IDs currently have images. To replace an active montage or procedural preview with an independent AI showcase, add `--upgrade-preview` to both importer commands. The importer archives the previous illustration. See [image pack format](docs/IMAGE_PACK_HANDOFF.md), [coverage](evidence/image-coverage.json), [batch audit](evidence/final-integration/audit.json) and [content licensing](CONTENT-LICENSE.md).

## English guide

Browse by category or family, search by name or alias, then open a style to inspect its illustration and copy a model-specific prompt in either language. Use Compare for side-by-side review and Workbench for editable local recipes. The gallery contains 155 independent AI showcases, 30 montage crops and 28 procedural studies. All 213 styles await exact-prompt verification.

The Pages workflow builds from main using Node 22. The strict gallery and release gates remain separate from technical preview checks. Code uses the MIT license.
