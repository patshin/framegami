# IRO v0.1 delivery status

## 中文

本轮交付的是**可操作、可构建的研究预览前端**，不是已经完成全部内容与部署的正式成品。

已完成：213 条独立编写的风格草案、19 个门类、60 个家族、25 项来源台账；中英双语界面与提示词；ChatGPT / Gemini / FLUX 三组文字适配；分类搜索、详情、比较、工作台、收藏、自定义、导入导出；静态页面、发布脚本、验证机制与开发文档。

未完成：合格的独立基准原图、逐条生成例图、模型效果验证、真实 GitHub 仓库创建与 Pages 部署。因此目前**真实对应生成例图为 0**。封面明确标记为抽象索引图形，不能用于声称提示词效果。

技术实现有一项明确调整：实际使用原生 JavaScript/CSS 与零依赖 Node 静态构建，并未使用先前推荐的 Astro/React。原因、收益与代价见 ADR-001；没有把未安装或未运行的框架代码伪装成完成。

本轮不增加付费服务、不收集 API Key、不调用用户的生图账号。当前 GitHub 连接未提供新建仓库或开启 Pages 的写入能力，现有其他仓库没有被修改。可在自己的终端运行已附的发布脚本完成新建和发布；远端执行仍需真实验证。

## English

This is an implemented research preview, not the content-complete deployed product.
There are 213 authored untested styles, 19 categories, 60 families, 25 recorded sources,
439 static routes and 1,278 text adaptations. Qualifying generated examples: **0**.

The actual stack is browser JavaScript/CSS plus a zero-dependency Node static compiler,
not the earlier recommended Astro/React stack. No remote repository or Pages deployment
has been performed. See ACCEPTANCE.md for the exact tests and remaining gates.
