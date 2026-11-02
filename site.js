const buttons = document.querySelectorAll('[data-filter]');
const topicButtons = document.querySelectorAll('[data-topic]');
const papers = [...document.querySelectorAll('.paper')];
const paperList = document.querySelector('#paper-list');
let selectedType = 'all', selectedTopic = '', publicationPage = 1;

function paginate(items, allItems, container, page, size) {
 const pages = Math.max(1, Math.ceil(items.length / size));
 page = Math.max(1, Math.min(page, pages));
 const shown = new Set(items.slice((page - 1) * size, page * size));
 allItems.forEach(item => item.hidden = !shown.has(item));
 container.hidden = pages <= 1;
 container.querySelector('.page-position').textContent = `Page ${page} of ${pages}`;
 container.querySelector('[data-direction="previous"]').disabled = page === 1;
 container.querySelector('[data-direction="next"]').disabled = page === pages;
 return page;
}
function renderPublications() {
 const matches = papers.filter(p => (selectedType === 'all' || p.dataset.kind === selectedType) && (!selectedTopic || JSON.parse(p.dataset.keywords || '[]').includes(selectedTopic)));
 publicationPage = paginate(matches, papers, document.querySelector('#publications-pagination'), publicationPage, Number(paperList.dataset.pageSize));
 document.querySelector('.pub-count').textContent = `${matches.length} publications`;
 let empty = paperList.querySelector('.empty-result');
 if (!empty) { empty = document.createElement('p'); empty.className = 'empty-result'; empty.textContent = 'No publications match these filters.'; empty.setAttribute('role','status'); paperList.appendChild(empty); }
 empty.hidden = matches.length > 0;
}
buttons.forEach(button => button.addEventListener('click', () => {
 selectedType = button.dataset.filter; publicationPage = 1;
 buttons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
 renderPublications();
}));
topicButtons.forEach(button => button.addEventListener('click', () => {
 selectedTopic = button.dataset.topic; publicationPage = 1;
 topicButtons.forEach(item => item.setAttribute('aria-pressed', String(item === button)));
 renderPublications();
}));
document.querySelectorAll('#publications-pagination button').forEach(button => button.addEventListener('click', () => {
 publicationPage += button.dataset.direction === 'next' ? 1 : -1;
 renderPublications(); document.querySelector('#publications').scrollIntoView({block:'start'});
}));
renderPublications();
const newsList = document.querySelector('.timeline');
const newsItems = [...newsList.querySelectorAll('article')];
const newsPager = document.querySelector('#news-pagination');
let newsPage = 1;
function renderNews() { newsPage = paginate(newsItems, newsItems, newsPager, newsPage, Number(newsList.dataset.pageSize)); }
newsPager.querySelectorAll('button').forEach(button => button.addEventListener('click', () => {
 newsPage += button.dataset.direction === 'next' ? 1 : -1;
 renderNews(); document.querySelector('#news').scrollIntoView({block:'start'});
}));
renderNews();
if ('IntersectionObserver' in window) {
 const navigation = document.querySelectorAll('nav a[href^="#"]');
 const sections = document.querySelectorAll('main > section[id]');
 const observer = new IntersectionObserver(entries => { entries.forEach(entry => { if(entry.isIntersecting){ navigation.forEach(link => { const active = link.hash === '#'+entry.target.id; link.classList.toggle('active', active); if(active) link.setAttribute('aria-current','location'); else link.removeAttribute('aria-current'); }); } }); }, {rootMargin:'-10% 0px -65% 0px', threshold:0});
 sections.forEach(section => observer.observe(section));
 if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
 const reveal = new IntersectionObserver(entries => entries.forEach(entry => { if(entry.isIntersecting){ entry.target.classList.add('visible'); reveal.unobserve(entry.target); } }), {threshold:.08});
 document.querySelectorAll('.research-card,.timeline article').forEach(el=> {el.classList.add('reveal-ready'); reveal.observe(el);});
 }
}
