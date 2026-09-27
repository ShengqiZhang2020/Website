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
