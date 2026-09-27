"""Check root-based clean routes, generated content, assets and downloads."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit, unquote
import argparse
import json
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
errors = []
config = json.loads((ROOT / 'data/site.json').read_text(encoding='utf-8'))
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--site-url', default=config.get('site_url', ''),
                    help='Public site URL; pass --site-url= for a local root build')
args = parser.parse_args()
site = args.site_url.rstrip('/')
site_parts = urlsplit(site)
if site and (site_parts.scheme not in ('http', 'https') or not site_parts.netloc
             or site_parts.query or site_parts.fragment):
    parser.error('--site-url must be an http(s) URL without query or fragment')
# The configured deployment root is authoritative; it is independent of locale.
base = unquote(site_parts.path).rstrip('/') if site else ''
dist_root = DIST.resolve()
sections = ('', 'biography', 'research', 'publications', 'projects', 'activities')
content_routes = {
    ('/' if lang == 'zh' else '/en/') + (section + '/' if section else ''): lang
    for lang in ('zh', 'en') for section in sections
}
redirect_routes = {}
for section in sections:
    suffix = section + '/' if section else ''
    redirect_routes['/zh/' + suffix] = '/' + suffix
    redirect_routes['/Website/zh/' + suffix] = '/' + suffix
    redirect_routes['/Website/en/' + suffix] = '/en/' + suffix
redirect_routes['/Website/'] = '/'


def route_file(route):
    return (DIST / route.lstrip('/') / 'index.html').resolve()


def public_url(route):
    return site + route


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.canonicals, self.publications = [], set(), [], []
        self.navigation, self.alternates, self.redirects, self.refreshes = [], [], [], []
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
        if tag == 'meta':
            if attr.get('name', '').lower() == 'redirect-target':
                self.redirects.append(attr.get('content', ''))
            if attr.get('http-equiv', '').lower() == 'refresh':
                match = re.search(r'(?:^|;)\s*url\s*=\s*(.+)$', attr.get('content', ''), re.I)
                if match:
                    self.refreshes.append(match[1].strip().strip('\"\''))
        rels = attr.get('rel', '').lower().split()
        if tag == 'link' and ('canonical' in rels or 'alternate' in rels):
            if 'canonical' in rels:
                self.canonicals.append(attr.get('href', ''))
            if 'alternate' in rels:
                self.alternates.append(attr.get('href', ''))
                self.navigation.append(attr.get('href', ''))
                self.links.append(attr.get('href', ''))
        elif tag in ('a', 'link', 'img', 'script'):
            link = attr.get('href', attr.get('src', ''))
            if link:
                self.links.append(link)
                if tag == 'a':
                    self.navigation.append(link)


files = list(DIST.rglob('*.html'))
assert files, 'Build the site first: python build.py'
pages = {file.resolve(): Page(file.read_text(encoding='utf-8')) for file in files}
expected_files = {route_file(route) for route in content_routes | redirect_routes}
expected_files.add((DIST / '404.html').resolve())
for file in sorted(expected_files - pages.keys()):
    errors.append(f'Missing generated page: {file.relative_to(dist_root)}')
for file in sorted(pages.keys() - expected_files):
    errors.append(f'Unexpected generated page: {file.relative_to(dist_root)}')


def resolve(file, href):
    url = urlsplit(href)
    if url.scheme or url.netloc:
        if (url.scheme not in ('', 'http', 'https') or not site
                or url.netloc.lower() != site_parts.netloc.lower()):
            return None, ''
    path = unquote(url.path)
    if path.startswith('/'):
        if base and (path == base or path.startswith(base + '/')):
            path = path[len(base):] or '/'
        dest = DIST / path.lstrip('/')
    else:
        dest = file.parent / path if path else file
    if path.endswith('/') or dest.is_dir():
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
    for href in parsed.navigation + parsed.redirects + parsed.refreshes:
        dest, _ = resolve(file, href)
        if dest is None:
            continue
        path = unquote(urlsplit(href).path)
        if path.lower().endswith('.html'):
            errors.append(f'HTML filename in navigation: {file}: {href}')
        elif dest in pages and path and not path.endswith('/'):
            errors.append(f'Page navigation must end with a slash: {file}: {href}')

for route, lang in content_routes.items():
    file = route_file(route)
    parsed = pages.get(file)
    if parsed is None:
        continue
    if parsed.redirects or parsed.refreshes:
        errors.append(f'Content page unexpectedly redirects: {route}')
    if parsed.lang != ('zh-CN' if lang == 'zh' else 'en'):
        errors.append(f'Wrong page language: {route}: {parsed.lang}')
    expected_canonicals = [public_url(route)] if site else []
    if parsed.canonicals != expected_canonicals:
        errors.append(f'Incorrect canonical for {route}: expected {expected_canonicals}, got {parsed.canonicals}')
    if not site and parsed.alternates:
        errors.append(f'Local build should omit hreflang links: {route}')

for route, target in redirect_routes.items():
    file = route_file(route)
    parsed = pages.get(file)
    if parsed is None:
        continue
    if len(parsed.redirects) != 1 or len(parsed.refreshes) != 1:
        errors.append(f'Legacy route needs one redirect target and one noscript refresh: {route}')
    for href in parsed.redirects + parsed.refreshes:
        dest, _ = resolve(file, href)
        if dest != route_file(target):
            errors.append(f'Incorrect legacy redirect: {route}: {href}; expected {target}')
    expected_canonicals = [public_url(target)] if site else []
    if parsed.canonicals != expected_canonicals:
        errors.append(f'Incorrect legacy canonical: {route}: {parsed.canonicals}')

sitemap = DIST / 'sitemap.xml'
if site:
    if not sitemap.is_file():
        errors.append('Missing sitemap.xml for the public build')
    else:
        try:
            document = ET.fromstring(sitemap.read_text(encoding='utf-8'))
            locations = [element.text or '' for element in document.findall('{*}url/{*}loc')]
            expected_locations = {public_url(route) for route in content_routes}
            if len(locations) != len(expected_locations) or set(locations) != expected_locations:
                errors.append('Sitemap must contain exactly the 12 canonical content URLs, including the root homepage')
            if any('.html' in unquote(urlsplit(url).path).lower() for url in locations):
                errors.append('Sitemap contains an HTML filename URL')
        except ET.ParseError as exc:
            errors.append(f'Invalid sitemap.xml: {exc}')
elif sitemap.exists():
    errors.append('Local root build should omit sitemap.xml')

for file in (DIST / 'assets').rglob('*.css'):
    for href in re.findall(r'url\([\"\']?([^\)\"\']+)', file.read_text(encoding='utf-8-sig')):
        dest, _ = resolve(file, href)
        if dest is not None and not dest.is_file():
            errors.append(f'Broken CSS asset: {file}: {href}')

papers = json.loads((ROOT / 'data/publications.json').read_text(encoding='utf-8'))
expected_ids = {p['id'] for p in papers}
assert len(expected_ids) == len(papers), 'Publication IDs must be unique'
for lang in ('zh', 'en'):
    prefix = '/' if lang == 'zh' else '/en/'
    publication_page = pages.get(route_file(prefix + 'publications/'))
    actual = publication_page.publications if publication_page else []
    if len(actual) != len(papers) or set(actual) != expected_ids:
        errors.append(f'{lang}: missing or duplicated publication records')
    for page in sections:
        file = route_file(prefix + (page + '/' if page else ''))
        parsed = pages.get(file)
        if parsed is None:
            continue
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
print(f'PASS: {len(content_routes)} clean content routes, {len(redirect_routes)} legacy redirects, '
      f'{len(pages)} HTML pages, {len(papers)} publications per language, canonicals, sitemap, '
      'local links, anchors, styles, fonts, and PDFs.')
