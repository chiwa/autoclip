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

  if (header.querySelector('.app-nav')) return;
  const nav = document.createElement('nav'); nav.className = 'app-nav';
  for (const [label, href] of [['สร้างวิดีโอ','/'],['สร้างด้วย AI','/ai'],['สร้าง Podcast','/podcast'],['คำสั่งสร้างภาพ','/antigravity'],['History','/history'],['Thai TTS','/tts']]) {
    const link = document.createElement('a'); link.href = href; link.textContent = label;
    const path = window.location.pathname;
    if ((href === '/' && (path === '/' || path.startsWith('/jobs/'))) || path === href) link.className = 'active';
    nav.append(link);
  }
  header.append(nav);
})();
