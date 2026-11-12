# IRO 色谱 · 本地交接版 105/213

这是一次完整的源码与可发布静态网站交接，**不是正式上线**。推荐 `npm run check && npm run preview`。

现有 105 种风格有视觉示意（67 独立 AI / 10 拼图临时预览 / 28 程序化 B00），剩余 108 种未配图；仍无逐字 Prompt 验证样例。

`production-batches/` 包含 11 批缺图任务队列；`scripts/import-image-pack.py` 支持 ZIP 自动回填且有安全来源检查。`docs/CODEX_HANDOFF_PROMPT.md` 是给 Codex 的唯一执行提示词。

GitHub 仓库未创建，Pages 未实际部署。源码使用静态编译器而不是 Astro/React，原因见 `docs/ADR-001.md`。
