# 章盛祺个人学术网站

仓库：[ShengqiZhang2020/shengqizhang2020.github.io](https://github.com/ShengqiZhang2020/shengqizhang2020.github.io)。网站地址：[shengqizhang2020.github.io](https://shengqizhang2020.github.io/)。本地目录为 `Website`。

英文首页直接位于 `/`，其他英文页面使用 `/biography/`、`/research/`、`/publications/`、`/projects/`、`/activities/`；中文页面位于 `/zh/` 及其子路径。页面地址均使用目录形式，不显示 `.html`，页面本身不执行 redirect。

本项目基于 [JackYansongLi/shiyi-chen-web](https://github.com/JackYansongLi/shiyi-chen-web) 完整克隆并保留 Git 历史，按本人的中英文简历、成果表格及论文 PDF 制作中英文个人学术网站。参考仓库提供的是 Astro 构建后的静态文件；本项目新增 Python 标准库生成器，维护内容无需安装 npm 依赖。

## 本地预览

建议使用 Python 3.12 或更新版本。在 `Website` 目录运行：

```powershell
python build.py --site-url=
python scripts/check_site.py --site-url=
python -m http.server 8000 --directory dist
```

打开 <http://localhost:8000/>，按 `Ctrl+C` 停止服务。根路径直接显示英文主页；`--site-url=` 将本次构建的发布网址设为空，适合在本机根路径预览。

正式构建使用配置中的 Pages 网址：

```powershell
python build.py
```

也可显式指定：

```powershell
python build.py --site-url https://shengqizhang2020.github.io
```

生成器更新根目录、`zh/` 及各页面目录下的 `index.html`，同时生成供发布使用的 `dist/`。这些文件负责响应目录网址，导航链接不会包含文件名。`dist/` 已被 Git 忽略；工作流在 GitHub 重新构建，因此无需上传它。

## 内容维护

网站以 `data/` 为内容维护入口，不直接修改生成的 HTML：

| 文件 | 用途 |
| --- | --- |
| `data/profile.json` | 中英文个人资料、教育经历、项目与学术活动 |
| `data/attendance.json` | 成果表格中明确记载本人参会的9条会议交流记录 |
| `data/publications.json` | 唯一的论文数据来源，包含作者、年份、DOI 和本地 PDF 路径 |
| `data/research.json` | 研究方向及相关论文 ID |
| `data/site.json` | 正式网址、仓库网址、三个学术主页链接、内容年份及代表论文 ID |
| `build.py` | 页面布局与中英文呈现逻辑 |
| `assets/` | 样式、交互脚本与实际使用的本地字体 |
| `images/shengqi-zhang.jpg` | 本人肖像 |
| `files/cv-zh.docx`、`files/cv-en.docx` | 中文、英文简历下载文件 |
| `files/papers/` | 已提供的论文全文 |
| `files/publications.bib`、`files/citations/` | 自动生成的全部论文及单篇论文 BibTeX 引用 |
| `CONTENT_SOURCES.md` | 资料来源及论文全文匹配记录 |

更新 JSON 或下载文件后重新构建并执行检查。新增论文使用稳定且唯一的 `id`；有 DOI 时填写 `doi`，有本地全文时填写 `pdf`。没有全文的条目保留书目信息及已有 DOI，不添加无效下载按钮。中文与英文页面共用同一论文数据集。

论文页支持下载全部引用和单篇 BibTeX。构建时直接从 `data/publications.json` 生成这些文件，更新论文后重新构建即可，不要单独编辑 `.bib` 文件。

三个个人学术主页入口为 [ORCID](https://orcid.org/0000-0001-8273-7484)、[Google Scholar](https://scholar.google.com/citations?user=BXTC31AAAAAJ&hl=en) 和 [ResearchGate](https://www.researchgate.net/profile/Shengqi-Zhang-2)，统一维护于 `data/site.json` 的 `profiles` 数组。

## GitHub Pages 发布

远端分工如下，可用 `git remote -v` 核对：

- `origin`：`https://github.com/ShengqiZhang2020/shengqizhang2020.github.io.git`，个人网站仓库。
- `upstream`：`https://github.com/JackYansongLi/shiyi-chen-web.git`，保留参考来源。

后续更新时，可在本地构建与检查通过后执行：

```powershell
git add .
git commit -m "Update Shengqi Zhang personal academic website"
git push -u origin main
```

本仓库已启用 GitHub Pages，发布来源为 **GitHub Actions**；向 `main` 推送会自动部署。需要重新发布时，可在 **Actions → Deploy personal website to GitHub Pages → Run workflow** 手动运行。部署状态见 [Actions](https://github.com/ShengqiZhang2020/shengqizhang2020.github.io/actions/workflows/pages.yml)。

若迁移到其他仓库，在 **Settings → Pages → Build and deployment → Source** 选择 **GitHub Actions**，再运行工作流。

工作流构建、检查并上传 `dist/`，然后部署到 GitHub Pages。它从 Pages 配置取得真实基础网址，不执行 Git 推送。使用 GitHub 根域名必须将仓库命名为 `shengqizhang2020.github.io`；原 `Website` 仓库已改名并保留历史。部署结果及访问网址显示在工作流和 Pages 设置中。配置方式参考 [GitHub 官方文档](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)。

## 资源来源

当前目录保留本人肖像与实际使用的五个字体文件，已清理其他成员照片、旧研究插图、旧 Astro 样式和 `people`／`gallery` 页面；完整参考历史仍保存在 `.git/` 中。字体位于 `assets/fonts/`，相关许可文本为 `OFL-Raleway.txt` 与 `OFL-SourceSans.txt`。

参考仓库未提供明确的网站代码许可证，本项目不据此声明 MIT 或其他开源授权。简历、论文、肖像及原设计资源的权利归各自权利人所有；保留来源记录，并按各自实际授权使用。
