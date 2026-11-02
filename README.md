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


## 日常维护：只改 JSON

1. 编辑 `content.json`，保存为 UTF-8。`publications` 是论文数组，`news` 是新闻数组，最新条目放最前。
2. 双击 `update.cmd`，或运行 `python update.py`。不需要额外 Python 包。
3. 刷新浏览器。提交发布时包含更新后的 index.html、content.json 和 assets 文件。

### 论文字段

必填：id（唯一）、title、authors（完整姓名数组）、year、type、venue、url、teaser。
可选：summary、pdf、code、project、keywords（自定义关键词数组）、spotlight（布尔值）、bibtex（可粘贴官方引用，覆盖自动生成的简要引用）。

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
{"date": "2026-11", "label": "Nov 2026", "text": "Your news text.", "tag": "UPDATE"}
```

带链接的新闻使用 parts 数组，每段都有 text，可加 url 或 bold: true。参照已有新闻。若同时填写 parts 和 text，优先显示 parts。

settings.publications_per_page 控制每页论文数（当前为 4）；settings.news_per_page 控制每页新闻数（当前为 3）。两者独立分页，只有一页时不显示翻页条。关闭 JavaScript 时显示完整列表，保证内容仍然可读。

JSON 使用双引号，不支持尾随逗号。脚本会先验证，再更新页面；错误时保留原页面。个人简介和教育经历不受影响。论文、新闻以 JSON 为准。

## GitHub Pages 兼容性

这是纯静态网站，不需要 Node、Hugo 或服务器后端。页面使用相对资源路径，既支持 username.github.io，也支持 username.github.io/repository/ 子路径。所有图像和 PDF 都在本地 assets 中；无在线字体或前端依赖。

将本目录的内容放到仓库发布目录（index.html 位于根目录，包含 .nojekyll）。在 GitHub 仓库 Settings → Pages 选择 Deploy from a branch，选定分支和根目录即可。更新前本地运行 update.cmd，然后一起提交 content.json、生成的 index.html 及新增素材。GitHub Pages 不会运行 Python，浏览器直接读取已生成的 HTML。

目前仅本地准备，未推送或发布。
