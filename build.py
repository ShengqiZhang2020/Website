"""Build Shengqi Zhang's bilingual academic website (Python 3.10+, no packages)."""
from pathlib import Path
from html import escape
from urllib.parse import urlsplit, urlunsplit
import argparse
import json
import posixpath
import re
import shutil

ROOT = Path(__file__).resolve().parent
P = json.loads((ROOT / 'data/profile.json').read_text(encoding='utf-8'))
PAPERS = json.loads((ROOT / 'data/publications.json').read_text(encoding='utf-8'))
CONFIG = json.loads((ROOT / 'data/site.json').read_text(encoding='utf-8'))
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--site-url', default=CONFIG.get('site_url', ''), help='Full public URL, including repository path')
args = parser.parse_args()
SITE = args.site_url.rstrip('/')
if SITE and (urlsplit(SITE).scheme not in ('http', 'https') or not urlsplit(SITE).netloc or urlsplit(SITE).query or urlsplit(SITE).fragment):
    parser.error('--site-url must be an http(s) URL without query or fragment')
BASE = urlsplit(SITE).path.rstrip('/') if SITE else ''
GENERATED = []
NAV = [('', '首页', 'Home'), ('biography', '个人简介', 'Biography'), ('research', '研究方向', 'Research'), ('publications', '论文发表', 'Publications'), ('projects', '科研项目', 'Projects'), ('activities', '学术活动', 'Activities')]


def esc(value):
    return escape(str(value), quote=True)


def tr(value, lang):
    return esc(value[lang] if isinstance(value, dict) else value)


def pick(lang, zh, en):
    return zh if lang == 'zh' else en


def target(lang, page=''):
    """Return the real file; English is the default root, Chinese uses /zh/."""
    prefix = 'zh/' if lang == 'zh' else ''
    return f'{prefix}{page + "/" if page else ""}index.html'


def route(lang, page=''):
    return target(lang, page).removesuffix('index.html')


def public_url(lang, page=''):
    return f'{SITE}/{route(lang, page)}'


def rel(current, path):
    """Resolve internal files relative to the page, hiding index.html in URLs."""
    parts = urlsplit(path)
    if parts.scheme or parts.netloc:
        return path
    is_index = parts.path == 'index.html' or parts.path.endswith('/index.html')
    destination = parts.path.removesuffix('index.html') if is_index else parts.path
    relative = posixpath.relpath(destination or '.', posixpath.dirname(current) or '.')
    if is_index:
        relative += '/'
    return urlunsplit(('', '', relative, parts.query, parts.fragment))


def a(current, path, text, cls=''):
    return f'<a class="{cls}" href="{esc(rel(current, path))}">{text}</a>'


def cv_links(lang, current, cls=''):
    labels = [('zh', '中文简历 ↓'), ('en', 'English CV ↓')]
    if lang == 'en':
        labels.reverse()
    return ''.join(a(current, f'files/cv-{locale}.pdf', label, cls) for locale, label in labels)


def academic_links(cls=''):
    return ''.join(f'<a class="{cls}" href="{esc(p["url"])}" rel="me">{esc(p["label"])} <span aria-hidden="true">↗</span></a>' for p in CONFIG['profiles'])


def paper_html(p, current, lang, selected=False):
    author_name = tr(P['name'], 'en')
    authors = esc(p['authors']).replace(author_name, f'<strong>{author_name}</strong>')
    authors = authors.replace(tr(P['name'], 'zh'), f'<strong>{tr(P["name"], "zh")}</strong>')
    links = []
    if p.get('doi'):
        links.append(f'<a href="https://doi.org/{esc(p["doi"])}" aria-label="DOI: {esc(p["title"])}">DOI ↗</a>')
    if p.get('pdf'):
        links.append(a(current, p['pdf'], 'PDF ↓'))
    elif p.get('external_pdf'):
        links.append(f'<a href="{esc(p["external_pdf"])}">{pick(lang, "期刊全文 ↗", "Publisher PDF ↗")}</a>')
    elif not p.get('doi') and p.get('external_source'):
        links.append(f'<a href="{esc(p["external_source"]["url"])}">{pick(lang, "来源 ↗", "Source ↗")}</a>')
    links.append(f'<a href="{rel(current, "files/citations/" + p["id"] + ".bib")}" download>BibTeX ↓</a>')
    title = esc(p.get('title_zh', p['title']) if lang == 'zh' else p['title'])
    title_lang = 'zh-CN' if re.search(r'[\u4e00-\u9fff]', title) else 'en'
    journal = p.get('journal_zh', p['journal']) if lang == 'zh' else p['journal']
    status = ''
    if p.get('status') == 'published-online':
        issue = esc(p.get('issue_date', '')[:7])
        status = '<span class="paper-status">' + pick(lang, '已在线发表', 'Published online') + (pick(lang, ' · 卷期 ', ' · Issue ') + issue if issue else '') + '</span>'
    if selected:
        title = f'<a href="{rel(current, target(lang, "publications"))}#{p["id"]}">{title}</a>'
    attr = '' if selected else f'id="{p["id"]}" data-publication data-year="{p["year"]}"'
    return f'''<li class="publication" {attr}>
      <h3 lang="{title_lang}">{title}</h3>
      <p class="publication-authors" lang="{p.get('language', 'en')}">{authors}</p>
      <p class="publication-citation"><em>{esc(journal)}</em>, {esc(p['details'])} ({p['year']}). {status}</p>
      <div class="publication-links">{''.join(links)}</div>
    </li>'''


def heading(text, id=''):
    return f'<h2 class="section-title"{f" id={id}" if id else ""}>{text}</h2>'


def home(lang, current):
    name = tr(P['name'], lang)
    intro_paragraphs = [tr(P[key], lang) for key in ('home_intro', 'home_research', 'home_background')]
    intro_paragraphs[0] = intro_paragraphs[0].replace(name, f'<strong>{name}</strong>')
    intro = ''.join(f'<p>{paragraph}</p>' for paragraph in intro_paragraphs)
    tags = ''.join(f'<span>{tr(t, lang)}</span>' for t in P['research_interests'])
    actions = a(current, target(lang, 'research'), pick(lang, '了解研究方向 →', 'Explore my research →')) + cv_links(lang, current)
    stats = [(len(PAPERS), '学术论文', 'Publications'), (len(P['projects']), '科研项目', 'Research projects'), (len(P['patents_software']), '专利与软件著作权', 'Patents & software copyrights')]
    stats_html = ''.join(f'<div><strong>{n}</strong><span>{pick(lang, zh, en)}</span></div>' for n, zh, en in stats)
    selected_ids = CONFIG['selected_publications']
    selected = ''.join(paper_html(next(p for p in PAPERS if p['id'] == id), current, lang, True) for id in selected_ids)
    return f'''<div class="prose">{intro}</div><div class="research-tags">{tags}</div>
    <div class="intro-actions">{actions}</div><div class="stats-line">{stats_html}</div>
    <section class="selected-section" aria-labelledby="selected-heading"><div class="section-heading"><h2 id="selected-heading">{pick(lang, '代表论文', 'Selected publications')}</h2>{a(current, target(lang, 'publications'), pick(lang, '全部论文 →', 'All publications →'), 'small-link')}</div><ol class="publications-list">{selected}</ol></section>'''


def biography(lang, current):
    edu = ''
    for item in P['education']:
        advisor = f'<p>{pick(lang, "导师：", "Advisor: ")}{tr(item["advisor"], lang)}</p>' if item.get('advisor') else ''
        edu += f'<li><span class="date">{item["start"]} – {item["end"]}</span><div><h3>{tr(item["institution"], lang)}</h3><p>{tr(item["field"], lang)} · {tr(item["degree"], lang)}</p>{advisor}</div></li>'
    honors = ''.join(f'<li><span class="date">{i["year"]}</span><div><h3>{tr(i["title"], lang)}</h3></div></li>' for i in P['honors'])
    return f'<div class="prose"><p>{tr(P["biography"], lang)}</p></div><div class="intro-actions">{cv_links(lang, current)}</div>{heading(pick(lang, "教育经历", "Education"))}<ol class="timeline">{edu}</ol>{heading(pick(lang, "奖励与荣誉", "Honors & awards"))}<ol class="timeline">{honors}</ol>'


def research(lang, current):
    topics = json.loads((ROOT / 'data/research.json').read_text(encoding='utf-8'))
    result = f'<div class="prose"><p>{pick(lang, "从流动机理到计算方法，结合理论分析、数值模拟与数据驱动建模，研究复杂流体系统中的结构、输运和控制。", "Combining theoretical analysis, numerical simulation, and data-driven modeling to study structures, transport, and control in complex fluid systems.")}</p></div><div class="selected-section">'
    for n, topic in enumerate(topics, 1):
        related = ''.join(f'<p class="related-paper">{a(current, target(lang, "publications") + "#" + id, esc(next(p["title"] for p in PAPERS if p["id"] == id)) + " ↗")}</p>' for id in topic['papers'])
        result += f'<section class="research-topic"><h2><span class="topic-index">0{n}</span>{tr(topic["title"], lang)}</h2><p>{tr(topic["description"], lang)}</p>{related}</section>'
    return result + '</div>'


def publications(lang, current):
    years = sorted({p['year'] for p in PAPERS}, reverse=True)
    notes = pick(lang, '* 表示通讯作者；姓名加粗标出本人。', '* denotes a corresponding author; my name is shown in bold.')
    fields = f'''<div class="filters"><div><label for="publication-search">{pick(lang, '检索论文', 'Search publications')}</label><input id="publication-search" type="search" placeholder="{pick(lang, '标题、作者或期刊', 'Title, author, or journal')}" autocomplete="off"></div><div><label for="publication-year">{pick(lang, '发表年份', 'Year')}</label><select id="publication-year"><option value="all">{pick(lang, '全部年份', 'All years')}</option>{''.join(f'<option value="{y}">{y}</option>' for y in years)}</select></div></div>
    <div class="filter-status"><p id="publication-count" role="status" aria-live="polite">{len(PAPERS)} {pick(lang, '篇论文', 'publications')}</p><button type="button" id="reset-filters">{pick(lang, '重置筛选', 'Reset filters')}</button></div>'''
    sections = ''.join(f'<section class="year-section" aria-labelledby="year-{y}"><h2 class="year-heading" id="year-{y}">{y}</h2><ol class="publications-list">{"".join(paper_html(p, current, lang) for p in PAPERS if p["year"] == y)}</ol></section>' for y in years)
    export_link = f'<a href="{rel(current, "files/publications.bib")}" download>{pick(lang, "下载全部引用（BibTeX）↓", "Download all citations (BibTeX) ↓")}</a>'
    return f'<p class="publication-note">{notes}</p><div class="publication-tools">{export_link}<a href="{esc(CONFIG["profiles"][1]["url"])}">Google Scholar ↗</a></div>{fields}<p id="no-publications" hidden>{pick(lang, "未找到匹配论文，请尝试其他关键词或年份。", "No matching publications. Try a different keyword or year.")}</p>{sections}'


def projects(lang, current):
    result = ''
    for item in sorted(P['projects'], key=lambda p: p['start'], reverse=True):
        amount = item['amount_original'] if lang == 'zh' else f'CNY {item["amount_cny"]:,}'
        result += f'<article class="record"><h3>{tr(item["title"], lang)}</h3><p>{tr(item["program"], lang)}</p><p class="record-meta">{item["start"]} – {item["end"]} · <span class="record-role">{tr(item["role"], lang)}</span> · {pick(lang, "项目经费：", "Project funding: ")}{esc(amount)}</p></article>'
    result += heading(pick(lang, '专利与软件著作权', 'Patents & software copyrights'))
    for item in P['patents_software']:
        result += f'<article class="record"><h3>{tr(item["title"], lang)}</h3><p>{tr(item["authors"], lang)}</p><p class="record-meta">{item["year"]} · {tr(item["type"], lang)} · {esc(item["number"])}</p></article>'
    return result


def activities(lang, current):
    result = heading(pick(lang, '邀请报告', 'Invited talks')) + '<ol class="timeline">'
    for item in P['talks']:
        result += f'<li><span class="date">{item["date"]}</span><div><h3>{tr(item["title"], lang)}</h3><p>{tr(item["event"], lang)} · {tr(item["location"], lang)}</p></div></li>'
    result += '</ol>' + heading(pick(lang, '学术服务', 'Academic service'))
    result += '<ul class="service-list">' + ''.join(f'<li>{tr(i, lang)}</li>' for i in P['service']['entries']) + '</ul>'
    result += heading(pick(lang, '期刊审稿', 'Journal reviewing'))
    return result + '<ul class="service-list" lang="en">' + ''.join(f'<li>{esc(i)}</li>' for i in P['service']['reviewer_journals']) + '</ul>'


def layout(lang, page, content):
    current = target(lang, page)
    other = 'en' if lang == 'zh' else 'zh'
    label = next(pick(lang, zh, en) for key, zh, en in NAV if key == page)
    title = (tr(P['name'], lang) + pick(lang, '学术主页', '')) if not page else label
    document_title = title if not page else f'{title} — {tr(P["name"], lang)}'
    navigation = ''.join(f'<a href="{rel(current, target(lang, key))}"' + (' aria-current="page"' if page == key else '') + f'>{pick(lang, zh, en)}</a>' for key, zh, en in NAV)
    description = tr(P['biography'], lang)
    metadata = ''
    if SITE:
        metadata += f'<link rel="canonical" href="{esc(public_url(lang, page))}">'
        for loc in ('zh', 'en'):
            metadata += f'<link rel="alternate" hreflang="{pick(loc, "zh-CN", "en")}" href="{esc(public_url(loc, page))}">'
        metadata += f'<link rel="alternate" hreflang="x-default" href="{esc(public_url("en", page))}">'
        metadata += f'<meta property="og:url" content="{esc(public_url(lang, page))}"><meta property="og:image" content="{esc(SITE)}/images/shengqi-zhang.jpg">'
    person = {'@context': 'https://schema.org', '@type': 'Person', 'name': P['name']['en'], 'alternateName': P['name']['zh'], 'jobTitle': P['title']['en'], 'affiliation': {'@type': 'Organization', 'name': P['institution']['en']}, 'sameAs': [p['url'] for p in CONFIG['profiles']]}
    if SITE:
        person['url'] = public_url(lang)
        person['image'] = f'{SITE}/images/shengqi-zhang.jpg'
    metadata += '<script type="application/ld+json">' + json.dumps(person, ensure_ascii=False).replace('<', '\\u003c') + '</script>'
    roles = P['title'][lang].rsplit('、' if lang == 'zh' else ', ', 1)
    role = esc(roles[0]).replace('、', ' · ').replace(', ', '<br>')
    supervision = esc(roles[1]) if len(roles) > 1 else ''
    return f'''<!DOCTYPE html>
<html lang="{pick(lang, 'zh-CN', 'en')}"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{document_title}</title><meta name="description" content="{description}"><meta name="theme-color" content="#f4f4f4">
<meta property="og:title" content="{title} — {tr(P['name'], lang)}"><meta property="og:description" content="{description}"><meta property="og:type" content="website">{metadata}
<link rel="icon" href="{rel(current, 'favicon.svg')}" type="image/svg+xml"><link rel="stylesheet" href="{rel(current, 'assets/site.css')}"><link rel="stylesheet" href="{rel(current, 'assets/custom.css')}">
<script src="{rel(current, 'assets/site.js')}" defer></script></head><body>
<a class="skip-link" href="#content">{pick(lang, '跳到正文', 'Skip to content')}</a>
<header class="site-header"><a class="wordmark" href="{rel(current, target(lang))}">SHENGQI ZHANG <span lang="zh-CN">章盛祺</span></a>
<nav class="desktop-nav" aria-label="{pick(lang, '主导航', 'Main navigation')}">{navigation}</nav>
<a class="language-switch" href="{rel(current, target(other, page))}" lang="{pick(other, 'zh-CN', 'en')}" hreflang="{pick(other, 'zh-CN', 'en')}" aria-label="{pick(lang, '切换本页至英文', 'Switch this page to Chinese')}">{pick(lang, 'EN', '中文')} <span aria-hidden="true">↗</span></a>
<details class="mobile-menu"><summary aria-label="{pick(lang, '打开导航', 'Open navigation')}"><span class="menu-lines" aria-hidden="true">☰</span><span>{pick(lang, '菜单', 'Menu')}</span></summary><nav aria-label="{pick(lang, '移动端导航', 'Mobile navigation')}">{navigation}</nav></details></header>
<div class="site-grid"><aside class="sidebar" aria-label="{pick(lang, '个人信息与联系', 'Profile and contact')}"><div class="profile-intro">
<a class="portrait-link" href="{rel(current, target(lang, 'biography'))}"><img class="portrait" src="{rel(current, 'images/shengqi-zhang.jpg')}" alt="{pick(lang, '章盛祺肖像', 'Portrait of Shengqi Zhang')}" width="333" height="400" fetchpriority="high"></a>
<p class="profile-kicker">{pick(lang, '流体力学 · 科学计算', 'FLUID MECHANICS · COMPUTATION')}</p><h2 class="profile-name">{tr(P['name'], lang)}</h2><p class="profile-native" lang="{pick(other, 'zh-CN', 'en')}">{tr(P['name'], other)}</p>
<p class="profile-position">{role}</p><p class="profile-academy">{supervision}</p><a class="institution" href="https://www.eitech.edu.cn/">{tr(P['institution'], lang)}</a></div>
<section class="contact-block"><h2>{pick(lang, '联系方式', 'Contact')}</h2><a class="email" href="mailto:{P['email']}">{P['email']}</a>
<a class="sidebar-link" href="https://faculty.eitech.edu.cn/mech/zsq_en/main.htm">{pick(lang, '学校个人主页', 'University profile')} <span aria-hidden="true">↗</span></a>
<div class="academic-profiles">{academic_links('sidebar-link')}</div><div class="cv-downloads">{cv_links(lang, current, 'sidebar-link')}</div></section>
<footer class="sidebar-footer"><p>© {CONFIG['content_year']} {tr(P['name'], lang)}</p><p>{pick(lang, '湍流 · 传热 · 科学计算', 'Turbulence · Transport · Computation')}</p></footer></aside>
<main id="content" class="main-content" tabindex="-1"><article class="paper-panel"><header class="page-heading"><p class="eyebrow">{pick(lang, '流体力学与科学计算', 'FLUID MECHANICS & SCIENTIFIC COMPUTING')}</p><h1>{title}</h1></header><div class="page-body">{content}</div></article>
<div class="bottom-line"><span>{tr(P['institution'], lang)}</span><a href="#content">{pick(lang, '返回顶部 ↑', 'Back to top ↑')}</a></div></main></div></body></html>'''


def write(path, text):
    dest = ROOT / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(text + '\n', encoding='utf-8')
    GENERATED.append(path)


for lang in ('zh', 'en'):
    for page, renderer in [('', home), ('biography', biography), ('research', research), ('publications', publications), ('projects', projects), ('activities', activities)]:
        current = target(lang, page)
        write(current, layout(lang, page, renderer(lang, current)))
write('404.html', f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex"><title>Page not found · Shengqi Zhang</title><style>body{{font:18px/1.8 system-ui,sans-serif;background:#f4f4f4;color:#3c3b3b;margin:12vh auto;padding:24px;max-width:600px}}a{{color:#197e76}}</style></head><body><p>404 · SHENGQI ZHANG</p><h1>Page not found</h1><p><a href="{BASE}/">Return to the English homepage →</a></p><p><a href="{BASE}/zh/">中文主页 →</a></p></body></html>''')


def bibtex(paper):
    # Preserve titles and Unicode names. Split English author names for BibTeX.
    def bib(value):
        value = str(value).replace('\\', r'\textbackslash{}')
        return value.replace('&', r'\&').replace('%', r'\%').replace('_', r'\_')
    names = []
    for author in paper['authors'].replace('*', '').replace('，', ',').split(','):
        author = author.strip()
        parts = author.rsplit(' ', 1)
        names.append(', '.join(reversed(parts)) if len(parts) == 2 else author)
    fields = {'author': ' and '.join(names), 'title': '{' + paper['title'] + '}', 'journal': paper['journal'], 'year': paper['year']}
    details = re.match(r'^(\d+)(?:\(([^)]+)\))?[:,]\s*(.+)$', paper['details'])
    if details:
        fields['number' if paper.get('publication_type') == 'education-research' else 'volume'] = details[1]
        if details[2]:
            fields['number'] = details[2]
        fields['pages'] = re.sub(r'[-–]+', '--', details[3])
    if paper.get('doi'):
        fields['doi'] = paper['doi']
        fields['url'] = 'https://doi.org/' + paper['doi']
    return '@article{ShengqiZhang' + str(paper['year']) + paper['id'].replace('-', '') + ',\n' + ',\n'.join(f'  {key} = {{{bib(value)}}}' for key, value in fields.items()) + '\n}\n'


citations_dir = ROOT / 'files/citations'
citations_dir.mkdir(parents=True, exist_ok=True)
entries = []
for paper in PAPERS:
    entry = bibtex(paper)
    entries.append(entry)
    (citations_dir / (paper['id'] + '.bib')).write_text(entry, encoding='utf-8')
for stale in citations_dir.glob('pub-*.bib'):
    if stale.stem not in {paper['id'] for paper in PAPERS}:
        stale.unlink()
(ROOT / 'files/publications.bib').write_text('\n'.join(entries), encoding='utf-8')

# Only site assets enter the Pages artifact, never source material, Git data, or tooling.
dist = ROOT / 'dist'
if dist.is_symlink() or dist.resolve() != ROOT.resolve() / 'dist':
    raise RuntimeError('Refusing to build into a linked or external dist directory.')
dist.mkdir(exist_ok=True)
manifest = dist / '.build-manifest.json'
previous_files = json.loads(manifest.read_text(encoding='utf-8')) if manifest.exists() else []
deployed = set(GENERATED) | {'favicon.svg', '.nojekyll', 'images/shengqi-zhang.jpg'}
for directory in ('assets', 'files'):
    deployed.update(path.relative_to(ROOT).as_posix() for path in (ROOT / directory).rglob('*') if path.is_file())
if SITE:
    deployed.update(('sitemap.xml', 'robots.txt'))
# Remove only obsolete files recorded by this generator; never recursively delete.
for old_path in set(previous_files) - deployed:
    old_file = dist / old_path
    if not old_file.resolve().is_relative_to(dist.resolve()):
        raise RuntimeError(f'Invalid generated-file manifest entry: {old_path}')
    old_file.unlink(missing_ok=True)
for path in GENERATED:
    dest = dist / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / path, dest)
for directory in ('assets', 'files'):
    shutil.copytree(ROOT / directory, dist / directory, dirs_exist_ok=True)
(dist / 'images').mkdir(exist_ok=True)
shutil.copy2(ROOT / 'images/shengqi-zhang.jpg', dist / 'images/shengqi-zhang.jpg')
shutil.copy2(ROOT / 'favicon.svg', dist / 'favicon.svg')
(dist / '.nojekyll').touch()
if SITE:
    urls = ''.join(f'<url><loc>{esc(public_url(lang, page))}</loc></url>' for lang in ('zh', 'en') for page, _, _ in NAV)
    (dist / 'sitemap.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>', encoding='utf-8')
    (dist / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n', encoding='utf-8')
else:
    for optional in ('sitemap.xml', 'robots.txt'):
        (dist / optional).unlink(missing_ok=True)
manifest.write_text(json.dumps(sorted(deployed), indent=2) + '\n', encoding='utf-8')
print(f'Built {len(GENERATED)} HTML files, {len(PAPERS)} publications, and {sum(bool(p.get("pdf")) for p in PAPERS)} PDFs in dist/.')
