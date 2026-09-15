(() => {
  const header = document.querySelector('header');
  if (!header) return;

  const brand = header.querySelector('.brand');
  if (brand && !brand.querySelector('.brand-logo')) {
    const img = document.createElement('img');
    img.className = 'brand-logo';
    img.src = '/static/auto-clip-logo.png';
    img.alt = 'AutoClip Logo';
    brand.prepend(img);
  }

  const oldNav = header.querySelector('.app-nav');
  if (oldNav) oldNav.remove();
  const nav = document.createElement('nav'); nav.className = 'app-nav canonical-nav';
  const primary = document.createElement('div'); primary.className = 'app-nav-row app-nav-primary';
  const histories = document.createElement('div'); histories.className = 'app-nav-row app-nav-history';
  for (const [label, href] of [
    ['สร้างวิดีโอ','/'],
    ['Quick Reel','/quick-reel'],
    ['สร้างด้วย AI','/ai'],
    ['สร้าง Podcast','/podcast'],
    ['🔮 ดวง 12 ราศี','/zodiac-weekly'],
    ['Channels','/channels'],
  ]) {
    const link = document.createElement('a'); link.href = href; link.textContent = label;
    const path = window.location.pathname;
    if ((href === '/' && (path === '/' || path.startsWith('/jobs/'))) || path === href) link.className = 'active';
    primary.append(link);
  }
  for (const [label, href] of [
    ['Reels History','/reels-history'],
    ['Quick Reel History','/quick-reel-history'],
    ['Podcast History','/podcast-history'],
    ['ดวง History','/zodiac-history'],
  ]) {
    const link = document.createElement('a'); link.href = href; link.textContent = label;
    const path = window.location.pathname;
    if ((href === '/' && (path === '/' || path.startsWith('/jobs/'))) || path === href) link.className = 'active';
    histories.append(link);
  }
  nav.append(primary, histories);
  header.append(nav);
})();
