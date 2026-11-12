# IRO v0.5｜可复核的交接验收

验证日期：2026-11-03；范围是本地代码与静态站点，**不是** GitHub 线上验收。

## 当前可交付能力

- 213 条固定风格，105 条有视觉展示（67 独立 AI / 10 拼图裁切 / 28 程序化）。108 条待生图。
- 完整中英文浏览、三级分类、搜索、详情、图片对比、风格比较、收藏、自定义 Prompt、批量文本导出与导入等原有功能。
- 无后端与用户 API Key；可通过 Node.js 20+ 静态构建，GitHub Pages 发布工作流已包含但**未远程执行**。
- 按 style ID 匹配的批量 ZIP 导入器；默认拒绝已有主图，升级程序化/拼图预览必须 `--upgrade-preview` 并归档旧图。

## 本地实际执行验证

1. `npm run check`：完成内容校验、静态构建、覆盖率和缺图队列导出；**449/449 Node 测试通过**，**439 × 2 静态路径检查通过**。
2. `npm run test:browser`：利用本机 Chromium 的离线 DOM 检查，**8/8 通过**。因为使用的是离线单文件预览，不冒充 GitHub Pages 或浏览器跨会话持久化验收。
3. `npm run test:import`：测试包只创建在临时项目中，依次验证新增独立图、拼图裁切图、旧程序化图升级归档，之后临时项目 `npm run check`，**451/451 Node 测试通过**。测试合成素材已删除，正式数据未改动。
4. 108 条缺图队列与 11 个工作批次通过 ID 完整性核对，**无缺漏或重复 ID**。
5. 完整内容准入门禁仍不通过：有 108 条缺图，且 **0** 条已完成严格逐字 Prompt 生成验证。

## 交接文件

- `CHECKPOINT-MANIFEST.json`：唯一当前 checkpoint 元数据与核心文件 SHA-256。
- `docs/IMAGE_PACK_HANDOFF.md`：图片包结构、来源类型、导入约束。
- `docs/CODEX_HANDOFF_PROMPT.md`：本地 Codex 执行说明。
- `data/image-production-queue.json`：108 条缺图清单及中英 ChatGPT Prompt。
- `production-batches/`：11 个分批工作单；ZIP 样例 manifest。
- `scripts/import-image-pack.py`：素材 ZIP 自动导入与校验。

## 未完成事项

真实的剩余 108 张风格素材尚未生产；ChatGPT/Gemini/FLUX 跨模型画质验证尚未执行；GitHub 仓库和 Pages 尚未创建/上线；尚未在 Safari/iOS 真机对页面做验收。不要将代码测试成功等同于业务内容验收成功。
