(() => {
  const header = document.querySelector('header');
  if (!header || header.querySelector('.app-nav')) return;
  const nav = document.createElement('nav'); nav.className = 'app-nav';
  for (const [label, href] of [['สร้างวิดีโอ','/'],['สร้างด้วย AI','/ai'],['History','/history'],['Thai TTS','/tts']]) {
    const link = document.createElement('a'); link.href = href; link.textContent = label;
    const path = window.location.pathname;
    if ((href === '/' && (path === '/' || path.startsWith('/jobs/'))) || path === href) link.className = 'active';
    nav.append(link);
  }
  header.append(nav);
})();
