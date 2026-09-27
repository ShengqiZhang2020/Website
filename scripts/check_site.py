"""Check generated HTML, assets, paper downloads, and cross-page anchors."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
errors = []


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.canonicals, self.publications = [], set(), [], []
        self.lang, self.h1s = '', 0
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if attr.get('id'):
            if attr['id'] in self.ids:
                errors.append(f'Duplicate ID: {attr["id"]}')
            self.ids.add(attr['id'])
        if tag == 'html':
            self.lang = attr.get('lang', '')
        if tag == 'h1':
            self.h1s += 1
        if 'data-publication' in attr:
            self.publications.append(attr['id'])
        if tag == 'link' and attr.get('rel') in ('canonical', 'alternate'):
            if attr['rel'] == 'canonical':
                self.canonicals.append(attr['href'])
        elif tag in ('a', 'link', 'img', 'script'):
            link = attr.get('href', attr.get('src', ''))
            if link:
                self.links.append(link)


files = list(DIST.rglob('*.html'))
assert files, 'Build the site first: python build.py'
assert len(files) == 14, 'Unexpected generated page count; check for obsolete pages'
pages = {file.resolve(): Page(file.read_text(encoding='utf-8')) for file in files}
base = ''
for file, parsed in pages.items():
    if parsed.canonicals:
        path = urlsplit(parsed.canonicals[0]).path
        relative = file.relative_to(DIST).as_posix()
        base = path[:-len(relative)].rstrip('/')
        break


def resolve(file, href):
    url = urlsplit(href)
    if url.scheme or url.netloc:
        return None, ''
    path = unquote(url.path)
    if path.startswith('/'):
        if base and path.startswith(base + '/'):
            path = path[len(base):]
        dest = DIST / path.lstrip('/')
    else:
        dest = file.parent / path if path else file
    if path.endswith('/'):
        dest /= 'index.html'
    return dest.resolve(), unquote(url.fragment)


for file, parsed in pages.items():
    if not parsed.lang:
        errors.append(f'Missing lang: {file}')
    text = file.read_text(encoding='utf-8')
    for stale in ('schen@eitech.edu.cn', 'G4cgJtgAAAAJ', '/shiyi-chen-web/', '陈十一学术主页', 'SHIYI CHEN'):
        if stale in text:
            # The requested new repo may itself have the old name in its configured canonical.
            if stale == '/shiyi-chen-web/' and base == '/shiyi-chen-web':
                continue
            errors.append(f'Stale template identity: {file}: {stale}')
    for href in parsed.links:
        dest, anchor = resolve(file, href)
        if dest is None:
            continue
        if not dest.is_relative_to(DIST.resolve()):
            errors.append(f'Link escapes deployed site: {file}: {href}')
        elif not dest.exists():
            errors.append(f'Broken local link: {file}: {href}')
        elif anchor and dest in pages and anchor not in pages[dest].ids:
            errors.append(f'Broken anchor: {file}: {href}')

for file in (DIST / 'assets').rglob('*.css'):
    for href in re.findall(r'url\([\"\']?([^\)\"\']+)', file.read_text(encoding='utf-8-sig')):
        dest, _ = resolve(file, href)
        if dest is not None and not dest.is_file():
            errors.append(f'Broken CSS asset: {file}: {href}')

papers = json.loads((ROOT / 'data/publications.json').read_text(encoding='utf-8'))
config = json.loads((ROOT / 'data/site.json').read_text(encoding='utf-8'))
expected_ids = {p['id'] for p in papers}
assert len(expected_ids) == len(papers), 'Publication IDs must be unique'
for lang in ('zh', 'en'):
    actual = pages[(DIST / lang / 'publications/index.html').resolve()].publications
    if len(actual) != len(papers) or set(actual) != expected_ids:
        errors.append(f'{lang}: missing or duplicated publication records')
    for page in ('', 'biography', 'research', 'publications', 'projects', 'activities'):
        file = DIST / lang / page / 'index.html'
        parsed = pages[file.resolve()]
        if parsed.h1s != 1:
            errors.append(f'Expected exactly one main heading: {file}')
        if not all(profile['url'] in parsed.links for profile in config['profiles']):
            errors.append(f'Missing academic profile link: {file}')
        for locale in ('zh', 'en'):
            if not any(link.endswith(f'files/cv-{locale}.docx') for link in parsed.links):
                errors.append(f'Missing {locale} CV download: {file}')
for paper in papers:
    bib = DIST / 'files/citations' / (paper['id'] + '.bib')
    if not bib.is_file() or not bib.read_text(encoding='utf-8').startswith('@article{'):
        errors.append(f'Missing or invalid BibTeX download: {bib}')
    if paper.get('pdf'):
        file = DIST / paper['pdf']
        if not file.is_file() or file.read_bytes()[:5] != b'%PDF-':
            errors.append(f'Invalid PDF: {file}')
for old in ('_astro', 'zh/people', 'zh/gallery', 'en/people', 'en/gallery'):
    if (ROOT / old).exists() or any((DIST / old).rglob('*')):
        errors.append(f'Obsolete resource remains: {old}')
if {p.name for p in (ROOT / 'images').iterdir()} != {'shengqi-zhang.jpg'}:
    errors.append('Unused images remain in the project')
if len(list((DIST / 'assets/fonts').glob('*.woff2'))) != 5:
    errors.append('Expected five actively used font files')
all_bib = (DIST / 'files/publications.bib').read_text(encoding='utf-8')
if len(re.findall(r'^@article\{', all_bib, re.M)) != len(papers):
    errors.append('Combined bibliography is incomplete')
if errors:
    raise SystemExit('\n'.join(errors))
print(f'PASS: {len(pages)} HTML pages, {len(papers)} publications per language, all local links, anchors, styles, fonts, and PDFs.')
