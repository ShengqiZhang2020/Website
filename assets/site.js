// Clean directory URLs work both at the domain root and in local subpath previews.
// Legacy aliases navigate once; real pages only replace the address in history.
if (window.location.protocol === 'http:' || window.location.protocol === 'https:') {
  const redirect = document.querySelector('meta[name="redirect-target"]');
  if (redirect) {
    const destination = new URL(redirect.content, window.location.href);
    destination.search = window.location.search;
    destination.hash = window.location.hash;
    if (destination.href !== window.location.href) window.location.replace(destination.href);
  } else if (window.location.pathname.endsWith('/index.html')) {
    const cleanPath = window.location.pathname.slice(0, -'index.html'.length);
    window.history.replaceState(window.history.state, '', cleanPath + window.location.search + window.location.hash);
  }
}

// Progressive enhancement: all publications remain readable without JavaScript.
const search = document.querySelector('#publication-search');
const year = document.querySelector('#publication-year');
const count = document.querySelector('#publication-count');
const empty = document.querySelector('#no-publications');
if (search && year && count && empty) {
  const papers = [...document.querySelectorAll('[data-publication]')];
  const sections = [...document.querySelectorAll('.year-section')];
  const update = () => {
    const terms = search.value.normalize('NFKC').trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    let visible = 0;
    for (const paper of papers) {
      const matches = terms.every(term => paper.textContent.normalize('NFKC').toLocaleLowerCase().includes(term));
      paper.hidden = !matches || (year.value !== 'all' && paper.dataset.year !== year.value);
      if (!paper.hidden) visible++;
    }
    for (const section of sections) {
      section.hidden = ![...section.querySelectorAll('[data-publication]')].some(p => !p.hidden);
    }
    count.textContent = document.documentElement.lang === 'zh-CN' ? `显示 ${visible} / ${papers.length} 篇论文` : `Showing ${visible} of ${papers.length} publications`;
    empty.hidden = visible !== 0;
  };
  search.addEventListener('input', update);
  year.addEventListener('change', update);
  document.querySelector('#reset-filters').addEventListener('click', () => {
    search.value = '';
    year.value = 'all';
    update();
    search.focus();
  });
  update();
}
