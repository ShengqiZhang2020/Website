# 内容来源与核对记录

## 本地资料

资料来自项目父目录的 `简历中文.docx`、`简历英文.docx`、`成果表格.xlsx`，以及 `个人成果/` 内的 15 份论文 PDF。网站中的姓名、联系方式、教育经历、研究方向、项目和学术活动以这些材料为依据，不额外推断未提供的经历或荣誉。

中文个人资料以中文简历为依据；英文措辞参照英文简历校正。职称采用英文原文 “Assistant Professor, PhD Supervisor”，本科为 “B.S.”，导师为 “Prof. Shiyi Chen”，研究方向使用 “AI-empowered scientific computing”。英文原简历对中文职称中的部分内容有所省略，网站保留两种语言各自的资料口径。

项目、荣誉、专利软件、邀请报告和学术服务的英文名称按英文简历核对；金额、项目起止时间、登记号与中文记录保持一致。顶尖人才项目采用 “Core member (third-listed contributor)” 兼容两份简历；企业项目中的英文占位公司名称不当作实际合作单位发布。

两处材料差异暂按中文简历口径展示，待本人确认后可在 `data/profile.json` 中统一：

| 条目 | 中文简历 | 英文简历 | 网站暂用口径 |
| --- | --- | --- | --- |
| 宁波市重点研发计划项目，2023.04–2026.04 | 主持 | co-PI | 主持 / Principal investigator |
| 2025 年浙江省人才称谓 | 浙江省高层次人才 | Young Innovative Talent, Science and Technology Department of Zhejiang | 浙江省高层次人才 / High-level Talent of Zhejiang Province |

论文统一维护在 `data/publications.json`，以成果表格的完整清单补充两份简历共同列出的论文，并以出版社及正式 PDF 的书目信息核对明确冲突。`data/profile.json` 不保存重复的论文数组。15 份 PDF 按标题和文内书目信息匹配，实际下载文件位于 `files/papers/`；没有本地全文的条目仅展示书目信息及已核实的 DOI。

最终清单包含 36 篇论文、35 个 DOI、15 份本地 PDF。原有 33 条论文的 ID 和 PDF 路径保持不变；成果表格补充了 `pub-34`、`pub-35`、`pub-36`。最后一条为工程教育研究论文，原表未提供 DOI，因此保留完整引用而不补造 DOI。新增的 `pub-34` 与 `pub-35` 另记录官方外部 PDF 链接，不冒充本地文件。

截至 2026-09-27，35 个 DOI 中，34 个已与 Crossref 的出版商登记标题匹配，另 1 个中文期刊 DOI 已通过期刊官方论文首页确认。各条目的核对方式与出处保存在 `doi_verification` 中。这是书目核对记录，不代表持续监控外部网站的可达性。

完整简历副本分别放在 `files/cv-zh.docx` 和 `files/cv-en.docx`。简历与论文 PDF 作为下载原件保留，不改写正文。网站信息反映所提供材料，不代表后续自动更新的任职或出版状态。

## 已提供的 15 份论文全文

以下名称与父目录 `个人成果/` 中的原始文件对应；完整题名是核对与匹配依据。

1. A CFD-aided Galerkin Method for Global Linear Instability Analysis
2. A two-dimensional-three-component model for spanwise rotating plane Poiseuille flow
3. Controlling flow reversal in two-dimensional Rayleigh–Bénard convection
4. Coupled modelling of turbulent forced thermal convection in anisotropic porous media
5. Enhancing large-scale motions and turbulent transport in rotating plane Poiseuille flow
6. Flow structures in spanwise rotating plane Poiseuille flow based on thermal analogy
7. Heat-fluid-solid coupling model for turbulent forced convection within porous media
8. Interpolation-based parametric reduced-order models via Galerkin projection and dynamic mode decomposition
9. Interpolation-based parametric reduced-order models with dynamic mode decomposition
10. Numerical study of methane dry reforming in an electromagnetic induction heating reactor
11. Perturbation analysis of baroclinic torque in low-Mach-number flows
12. Stabilizing & destabilizing the large-scale circulation in turbulent Rayleigh–Bénard convection with sidewall temperature control
13. Twin forces similarity between rotation and stratification effects on wall turbulence
14. Unified scaling laws in porous-medium vertical natural convection
15. Validity of the twin-force analogy in Couette flows

题名接近的两篇插值降阶模型论文分别保留，不合并为一条。

## 论文记录与全文映射

以下 15 条记录已匹配本地全文，ID 对应网站论文锚点。下载路径与 DOI 均记录在 `data/publications.json`。

| 论文 ID | 本地下载文件 | DOI |
| --- | --- | --- |
| `pub-01` | [`files/papers/twin-force-validity-2026.pdf`](files/papers/twin-force-validity-2026.pdf) | [10.1017/jfm.2026.11999](https://doi.org/10.1017/jfm.2026.11999) |
| `pub-09` | [`files/papers/porous-scaling-2026.pdf`](files/papers/porous-scaling-2026.pdf) | [10.1017/jfm.2025.11108](https://doi.org/10.1017/jfm.2025.11108) |
| `pub-11` | [`files/papers/dmd-parametric-2026.pdf`](files/papers/dmd-parametric-2026.pdf) | [10.1016/j.jcp.2025.114436](https://doi.org/10.1016/j.jcp.2025.114436) |
| `pub-12` | [`files/papers/induction-drm-2025.pdf`](files/papers/induction-drm-2025.pdf) | [10.1016/j.applthermaleng.2025.128514](https://doi.org/10.1016/j.applthermaleng.2025.128514) |
| `pub-13` | [`files/papers/anisotropic-porous-2025.pdf`](files/papers/anisotropic-porous-2025.pdf) | [10.1017/jfm.2025.10484](https://doi.org/10.1017/jfm.2025.10484) |
| `pub-14` | [`files/papers/dmd-galerkin-2025.pdf`](files/papers/dmd-galerkin-2025.pdf) | [10.1063/5.0277689](https://doi.org/10.1063/5.0277689) |
| `pub-15` | [`files/papers/heat-fluid-solid-2025.pdf`](files/papers/heat-fluid-solid-2025.pdf) | [10.1103/67vg-cfqb](https://doi.org/10.1103/67vg-cfqb) |
| `pub-23` | [`files/papers/twin-forces-2024.pdf`](files/papers/twin-forces-2024.pdf) | [10.1017/jfm.2023.1101](https://doi.org/10.1017/jfm.2023.1101) |
| `pub-24` | [`files/papers/rppf-transport-2024.pdf`](files/papers/rppf-transport-2024.pdf) | [10.1017/jfm.2023.1091](https://doi.org/10.1017/jfm.2023.1091) |
| `pub-27` | [`files/papers/rppf-structures-2022.pdf`](files/papers/rppf-structures-2022.pdf) | [10.1017/jfm.2021.1073](https://doi.org/10.1017/jfm.2021.1073) |
| `pub-28` | [`files/papers/baroclinic-2022.pdf`](files/papers/baroclinic-2022.pdf) | [10.1017/jfm.2021.896](https://doi.org/10.1017/jfm.2021.896) |
| `pub-29` | [`files/papers/sidewall-control-2021.pdf`](files/papers/sidewall-control-2021.pdf) | [10.1017/jfm.2021.58](https://doi.org/10.1017/jfm.2021.58) |
| `pub-30` | [`files/papers/cfd-galerkin-2021.pdf`](files/papers/cfd-galerkin-2021.pdf) | [10.4208/cicp.OA-2020-0041](https://doi.org/10.4208/cicp.OA-2020-0041) |
| `pub-31` | [`files/papers/flow-reversal-2020.pdf`](files/papers/flow-reversal-2020.pdf) | [10.1017/jfm.2020.210](https://doi.org/10.1017/jfm.2020.210) |
| `pub-32` | [`files/papers/rppf-2d3c-2019.pdf`](files/papers/rppf-2d3c-2019.pdf) | [10.1017/jfm.2019.715](https://doi.org/10.1017/jfm.2019.715) |

其余 21 条记录未提供本地 PDF：`pub-02`、`pub-03`、`pub-04`、`pub-05`、`pub-06`、`pub-07`、`pub-08`、`pub-10`、`pub-16`、`pub-17`、`pub-18`、`pub-19`、`pub-20`、`pub-21`、`pub-22`、`pub-25`、`pub-26`、`pub-33`、`pub-34`、`pub-35`、`pub-36`。这些条目的论文题名、作者、年份和期刊信息仍列于论文页。

维护时将新增论文放入 `data/publications.json`，通过 `pdf` 指向下载文件，通过 `source_pdf` 保留原始文件名；没有文件时省略 `pdf` 字段。

## 书目信息与日期口径

`pub-05` 的文章号由原材料的 `115118` 更正为 `115158`，依据是与标题和作者一致的 [Crossref 出版商登记](https://api.crossref.org/works/10.1016/j.jcp.2026.115158) 和 [出版商文章页](https://www.sciencedirect.com/science/article/abs/pii/S0021999126005103)。该文已有在线文章页，正式卷期安排为 2026 年 11 月，单独标记为 `published-online`，不把 DOI 登记创建时间当成正式发表时间。

成果表格中的日期保留为 `spreadsheet_date`；官方在线发表时间与卷期时间分别保留在 `published_online`、`issue_date`。论文按卷期年份归类。来源单元格记录在 `source_spreadsheet` 中，便于回查。

`pub-12` 引用采用 `280: 128514`，去掉原表的期号 `(5)`：所提供 PDF 首页与已核对的出版社登记中未找到该期号的依据。

成果表格还包含 31 条会议记录，其中 20 条的人员栏明确列有章盛祺。人员栏不等同报告人，“投稿”不等同录用，因此不据此推断本人主讲或报告已被接受。

网站新增“会议交流”栏目，使用原表类型为“参会”的9条本人记录，维护于 `data/attendance.json`。原简历中的9场邀请报告单独保留，未将会议表中的团队成员、投稿记录加入本人邀请报告，也未公开其他参加人员。会议表的香港理工大学邀请日期与简历月份不同，该条未重复纳入，网站仍按两份简历所载的2023年1月展示。

全部与单篇 BibTeX 从同一份论文数据自动生成，分别位于 `files/publications.bib` 与 `files/citations/`，不构成另一套手工维护的书目来源。

## 个人学术主页

本人提供的 [ORCID](https://orcid.org/0000-0001-8273-7484)、[Google Scholar](https://scholar.google.com/citations?user=BXTC31AAAAAJ&hl=en) 和 [ResearchGate](https://www.researchgate.net/profile/Shengqi-Zhang-2) 链接统一保存在 `data/site.json` 的 `profiles` 数组中。

## 参考网站和肖像

参考来源：[JackYansongLi/shiyi-chen-web](https://github.com/JackYansongLi/shiyi-chen-web)，本次克隆时的 `main` 提交为 `f9ea1b20ef4b83509d30bd46ac6733c66c3d7925`。

上述参考提交的中文 `zh/people/index.html` 与英文 `en/people/index.html` 均将 `images/shengqi-zhang.jpg` 明确标注为“章盛祺 / Shengqi Zhang”，因此个人网站复用该肖像。图片没有通过生成或身份推断获得。其他成员肖像、旧研究 SVG、原 Astro 样式及 `people`／`gallery` 跳转页已从当前网站目录清理，原文件可从保留的 Git 历史中查阅。

网站实际使用的五个字体文件集中在 `assets/fonts/`，保留 Raleway 与 Source Sans Pro 的字体许可文本 `OFL-Raleway.txt` 和 `OFL-SourceSans.txt`。其他未被页面使用的字体文件已清理。

原仓库没有提供明确的网站代码许可证；本项目仅记录来源，不补设许可条款。保留 Git 历史与资料来源，不代表获得了论文、肖像或原设计资源的额外授权。
