# IRO · 色谱 — B00 程序化风格实验（研究素材）

本轮用户要求继续向图库添加风格视觉案例。图像生成工具在本轮重复输出了旧人物的多风格拼图，未交付任何能够对应所选目标风格的独立图像。**那些拼图没有被当作新增模型生成图入库。**

为了继续完善已批准的「风格图鉴＋提示词工作台」，本轮针对最适合算法转换的十类数字视觉风格，用同一张 B00 原图生成了十张 **local deterministic visual study（本地图像处理视觉示意）**：

- `pixel-1bit`, `pixel-cga`, `pixel-ascii-mosaic`
- `cmyk-halftone`, `line-density`, `contour-topography`
- `thermal-palette`, `chromatic-glitch`, `pixel-sorting`, `op-art-contours`

以上采用 Python/Pillow/OpenCV/NumPy，对固定 B00 原图做限色、网点、字符化、等值线和数字故障等处理。每个风格有独立的完整 WebP、缩略 WebP、输出 SHA-256、来源脚本 SHA-256 和风格 ID。源码在 `scripts/generate-procedural-studies.py`，运行所需 Python 依赖只服务于素材制作，**不参与 GitHub Pages 的站点构建与运行**。

**非常重要**：这些图不是 ImageGen 或图像编辑模型输出，不证明配套 ChatGPT/Gemini/FLUX Prompt 能重现这些效果。网站内已明确标注“程序化预览”，和既有的独立 AI 风格示意、拼图裁切临时示意分别计数；`modelStatus` 保持 `untested`，`accepted examples` 仍为 0。

数据完整性可以通过 `npm run check` 和 `npm run test:images` 检查。需真正完成 213 条模型图生图案例，还应日后逐条用具体 Prompt 和图像编辑工具对统一原图重新生成，记录输入、提示词和输出证据。
