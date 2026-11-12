# IRO 素材包协议（给本地 Codex）

本版正式代码基线是 **105/213**。以后只生产**还缺少图片**的 108 个 style ID 的素材 ZIP；不要逐张修改网站。模型生成图、拼图截取与程序化示意不可混算。现有 105 图的来源：独立 AI 生成 67、拼图截取 10、程序化 B00 预览 28。严格逐字 Prompt 验证数为 0。

## 自动批量导入

```bash
cd iro-style-atlas
python3 -m pip install Pillow
python3 scripts/import-image-pack.py /absolute/path/IRO-Assets-Batch-01.zip --dry-run
python3 scripts/import-image-pack.py /absolute/path/IRO-Assets-Batch-01.zip
npm run check
npm run preview
```

首次 **必须先 `--dry-run`**。若拿到的是独立生成 AI 图，目标 ID 目前已用拼图或程序化图占位，可对两个导入命令都加 `--upgrade-preview`，导入器会归档旧文件和标记历史为非主展示。不要覆盖已有独立 AI 图或修改 canonical style ID。

素材 ZIP 必须包含根目录 `manifest.json` 及 `images/<style-id>.png` 等真实素材文件：

```json
{
  "schema": "iro-image-pack-v1",
  "batch_id": "20261103-batch01",
  "date": "2026-11-03",
  "images": [
    {
      "style_id": "rural-handdrawn",
      "file": "images/rural-handdrawn.png",
      "source_type": "independent-ai",
      "generation_id": "actual-generation-id",
      "model": "chatgpt",
      "language": "en",
      "prompt_verified": false,
      "note_zh": "真实生成结果的画风审查说明",
      "note_en": "Specific style quality observations from the actual output"
    }
  ]
}
```

每个 `style_id` 必须是 `data/catalog.json` 中实际存在且尚缺图的 ID，或通过 `--upgrade-preview` 合法升级的 ID。`generation_id` 必须填写真实的工具返回编号，不编造。实际图像需符合风格媒介，不符合的即使可裁切也不入库。同一文件不重复映射到多个 style ID。

拼图裁切图允许作为临时视觉参考（**不是独立模型输出**），但 `source_type` 必须设为 `montage-crop`，并额外提供：

```json
{
  "montage_file": "montages/source-grid.png",
  "crop_box": [0, 0, 400, 300],
  "source_panel_label": "Upper-left panel"
}
```

同时包含原始整张拼图和按该坐标裁切的画面。导入器校验裁切区是否匹配，并保存原图、来源拼图、完整 WebP、缩略 WebP 与 SHA-256 到工程。不能直接将拼图裁切冒充“B00 同原图模型生成”。

## 数据与验证口径

- 真实独立 AI 输出：`kind=same-input-showcase`，目前只是风格示意，不能声称准确使用 B00 原图或当前版本 Prompt 进行了逐字生成。
- 拼图临时预览：`kind=montage-derived-preview`，源拼图与裁切坐标必须可审计。
- 程序化预览：`kind=procedural-style-study`，来自本地代码，不是 ImageGen。
- 所有导入图 `accepted=false, promptVerified=false`；严格 Prompt 复现需另走逐条冻结证据审查，不接受素材包自称实测成功。
- `npm run check` 在构建后更新 `evidence/image-coverage.json` 和 `data/image-production-queue.json`。未来生成批次必须从当前 queue 中选择 ID，而不是使用过期编号。
- 约束：ZIP 最大 400 MB，每张素材最大 30 MB；图片尺寸至少 200×200，最多 40MP；1–120 条记录；不允许重复哈希、越界目录、Symlink 或恶意超大解压。

## 下一阶段生成策略

`production-batches/index.json` 将当前 108 个缺图 ID 划分为 11 批（前 10 批每批 10 个，最后一批 8 个）。各批完整中英文 Prompt 在 `production-batches/batch-XX-worklist.json` 中；这只是一份待生成任务队列，不是已生成文件。**新素材由助手按批生成并打成 ZIP 后，Codex 运行上面的两行命令即可全部配到前端。**

若导入中断，保留原项目备份并通过 Git 回退；不要手工清空 `illustrations` 或改已有图片哈希。

## 213/213 最终集成更新

以上 105/213 及 108 项队列为历史交接记录。当前计数见 evidence/image-coverage.json。对于确有包级独立 AI 来源声明但无生成记录的图片，规范化 manifest 使用 generation_record_status="unavailable" 和 generation_id=null；无法证实的提交语言使用 language="unknown"。保留源 manifest、包 SHA-256 与来源缺口。拼图记录仍须提供原拼图、裁切坐标及生成编号。
