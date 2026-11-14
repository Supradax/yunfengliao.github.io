# Yunfeng Liao — Academic Homepage

Local static website; no build or third-party dependencies.

## Preview

Double-click `preview.cmd`, then open http://127.0.0.1:8765/ . Close the preview window to stop it. You can also open `index.html` directly.

## Editing

- `index.html`: profile, interests, six papers, news, contact.
- `styles.css`: color palette, responsive layout, motion.
- `site.js`: publication filters and scroll effects.
- `assets/`: original wolf avatar, vector geometric surface, six paper PDFs and real teaser crops.

## Content sources

Profile title and interests: user-supplied November 2026. Avatar: supplied repository archive, images/avatar.jpg.

Papers: https://arxiv.org/abs/2610.36931 , https://arxiv.org/abs/2610.35952 , https://arxiv.org/abs/2610.25297 , https://arxiv.org/abs/2610.15573 , https://openreview.net/forum?id=PluDA8DEar , https://proceedings.mlr.press/v267/liao25b.html . Conference PDF copies from https://xiucheng.org/assets/pdfs/ . Teasers extracted from Figure 1 of each original paper.

NeurIPS uses conference year 2025 (Scholar indexes proceedings in 2026). Skeletons coauthor is Yucheng Wu, following the full paper. Email: NeurIPS 2025 public poster. Preprints explicitly labelled. Research descriptions paraphrase the supplied interests and paper abstracts. News dates follow arXiv submission records; no new acceptance claims are inferred.

No GitHub push, registration, or deployment performed. Original archive preserved.


## 每页显示条数

打开 `content.json`，最前面的设置就是每页数量：

```json
"settings": {
  "publications_per_page": 4,
  "news_per_page": 3
}
```

分别表示每页 4 篇论文、3 条新闻。修改为 1–100 的整数，保存后双击 `update.cmd`。脚本会显示实际每页数量与总页数。论文筛选后按同样的每页数量重新分页；新闻单独分页。只有一页时隐藏翻页按钮。发布时同时提交更新后的 `content.json` 和 `index.html`。


## 可视化内容编辑器

不需要直接编辑 `content.json`。双击 `editor.cmd` 会启动本地编辑器并打开 `http://127.0.0.1:8766/`：

- About、教育经历、Research、Publications、News 都可以用表单编辑，条目默认折叠。
- 简介和新闻使用 Markdown 文本框，支持 `**加粗**`、`[文字](https://example.com)`，不需要手动组装 `parts`。
- 点击“保存并更新本地页面”会写入 `content.json` 并运行 `update.py`。
- 确认预览后点击“保存并发布 GitHub”会调用现有 `publish.py`。
- 编辑器只监听本机 `127.0.0.1`，不会被 GitHub Pages 发布。

## 一键更新并发布

修改 `content.json` 并保存后，双击 `publish.cmd`。脚本会依次运行 `update.py`、检查引用素材、创建提交并推送到原仓库。窗口会保留结果和错误提示。

- 新图片/PDF 放入 assets，在 JSON 中填写路径后一起发布。
- 自动读取当前 Windows 系统代理；不修改 Git 或系统的全局配置。
- 使用 Git for Windows 已保存的 GitHub 登录。如果登录失效，按 Git 登录提示完成授权。
- 推送成功后，GitHub Pages 还需要完成部署；可从脚本给出的 Actions 链接查看。
- 默认复用同级 `github-publish` 仓库。若网站目录本身就是 Git 仓库，则直接使用该仓库。
- 遇到远端有更新、发布副本有未提交修改、素材缺失或 JSON 错误时会停止，不会强制覆盖或重置文件。
- 网络失败且已生成提交时，网络恢复后再次双击即可继续推送。

只想生成本地预览仍使用 `update.cmd`。也可运行 `python publish.py --check`，只更新和检查，不提交或推送。

依赖：Python 3.10+ 和 Git for Windows。当前电脑已具备。

## 日常维护：只改 JSON

1. 编辑 `content.json`，保存为 UTF-8。`publications` 是论文数组，`news` 是新闻数组，最新条目放最前。
2. 双击 `update.cmd`，或运行 `python update.py`。不需要额外 Python 包。
3. 刷新浏览器。提交发布时包含更新后的 index.html、content.json 和 assets 文件。

### 论文字段

必填：id（唯一）、title、authors（完整姓名数组）、year、type、venue、url、teaser。
可选：summary、pdf、code、project、keywords（自定义关键词数组）、labels（自定义色块标签数组，如 ["Spotlight", "Oral"]）、month、bibtex（可粘贴官方引用，覆盖自动生成的简要引用）。

type 可用 journal / conference / preprint。Journal 已预留，0 篇时自动不显示；新增 journal 条目并运行更新即可出现。一个论文可以有多个关键词，例如 "keywords": ["Walk on Spheres", "Geometry"]。关键词按钮自动生成，可以同时按论文类型和关键词筛选。

新增论文示例（用真实信息替换后放入 publications 数组）：

```json
{
  "id": "unique-id",
  "title": "Your paper title",
  "authors": ["Yunfeng Liao", "Coauthor Name"],
  "year": 2027,
  "type": "journal",
  "venue": "Journal Name, volume, pages (2027)",
  "url": "https://doi.org/your-doi",
  "teaser": "assets/your-teaser.webp",
  "pdf": "assets/your-paper.pdf",
  "keywords": ["Your Topic"],
  "summary": "A short explanation."
}
```

### 新闻与分页

简单新闻可以这样填写：

```json
{"date": "2026-11", "text": "Your news text.", "tag": "UPDATE"}
```

`date` 使用 `YYYY-MM`，页面会自动显示为 `Nov 2026` 这样的缩写；只有需要特殊显示时才填写可选的 `label`。新闻内容直接使用 `text` 字符串，支持 Markdown 的 `**加粗**` 和 `[文字](https://example.com)`。`label` 是可选覆盖项，不填时由 `date` 自动生成月份显示。

settings.publications_per_page 控制每页论文数（当前为 4）；settings.news_per_page 控制每页新闻数（当前为 3）。两者独立分页，只有一页时不显示翻页条。关闭 JavaScript 时显示完整列表，保证内容仍然可读。

JSON 使用双引号，不支持尾随逗号。脚本会先验证，再更新页面；错误时保留原页面。`site.about.description` 和新闻 `text` 都是 Markdown 字符串；`site.about.education` 是可填写多段的数组。论文、新闻、About、Research 都以 JSON 为准。

## GitHub Pages 兼容性

这是纯静态网站，不需要 Node、Hugo 或服务器后端。页面使用相对资源路径，既支持 username.github.io，也支持 username.github.io/repository/ 子路径。所有图像和 PDF 都在本地 assets 中；无在线字体或前端依赖。

将本目录的内容放到仓库发布目录（index.html 位于根目录，包含 .nojekyll）。在 GitHub 仓库 Settings → Pages 选择 Deploy from a branch，选定分支和根目录即可。更新前本地运行 update.cmd，然后一起提交 content.json、生成的 index.html 及新增素材。GitHub Pages 不会运行 Python，浏览器直接读取已生成的 HTML。

目前仅本地准备，未推送或发布。


## 旧链接跳转

redirects.json 记录最初 ZIP 中的全部旧 HTML 页面路径。对应路径已创建立即跳转页，统一跳到 https://supradax.github.io/yunfengliao.github.io/ 。404.html 兜底处理这个项目下其他不存在的路径。原图片、脚本等旧静态资源不再恢复，访问失效地址时由 Pages 的 404 页面处理。

publish.cmd 会保留并上传清单中的全部跳转页，以后更新 content.json 不会将它们移除。跳转页使用零秒 meta refresh、固定目标的 JavaScript replace 和手动链接。已知旧页面返回 200 后由浏览器跳转；未知路径仍先返回 404。这不是 HTTP 301，也不保证把旧页面排名全部转给主页。

保留 google17274b0d254d4e65.html 验证文件，不要把它改成跳转页。


## 可编辑的 About 和 Research

`content.json` 的 `site.about` 控制姓名、别名、头衔、Markdown 简介、教育经历和链接；`site.research` 控制 01 / RESEARCH 的三个卡片。修改后运行 `update.cmd` 或 `publish.cmd`，页面会按 JSON 重新生成。论文的 `month` 字段控制右侧年月框，使用缩写显示，例如 `Oct 2026`；venue 只填写会议或期刊名称。`labels` 数组中的每个字符串都会显示为独立色块。


## 可编辑的 About、Research 和论文月份

`content.json` 的 `site.about` 控制姓名、别名、头衔、Markdown 简介、教育经历和链接；`site.research` 控制 `01 / RESEARCH` 的三个卡片。论文的 `month` 字段控制右侧年月框，使用缩写显示，例如 `Oct 2026`；venue 只填写会议或期刊名称。`labels` 数组中的每个字符串都会显示为独立色块。

修改 JSON 后运行 `update.cmd` 可生成本地页面，运行 `publish.cmd` 可更新并推送。
