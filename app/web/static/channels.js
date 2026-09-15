(function () {
  const defaultsByPath = {
    '/': 'mamase-reel',
    '/ai': 'mamase-reel',
    '/quick-reel': 'mamase-reel',
    '/podcast': 'mamase-podcast',
    '/zodiac-weekly': 'khon-nuea-duang',
  };

  async function fetchChannels() {
    const response = await fetch('/api/channels');
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.detail?.message || 'โหลด Channel ไม่สำเร็จ');
    return data.channels || [];
  }

  function fill(select, channels, selected) {
    select.replaceChildren(...channels.map(channel => {
      const option = document.createElement('option');
      option.value = channel.id;
      option.textContent = channel.name;
      option.selected = channel.id === selected;
      return option;
    }));
    if (!select.value && channels.length) select.value = channels[0].id;
  }

  async function mount(target, options = {}) {
    const root = typeof target === 'string' ? document.querySelector(target) : target;
    if (!root) return null;
    root.classList.add('channel-picker');
    const label = document.createElement('label');
    label.textContent = 'Channel';
    const select = document.createElement('select');
    select.id = options.id || 'contentChannel';
    select.name = 'channel_id';
    select.setAttribute('aria-label', 'Channel ของ Content');
    const manage = document.createElement('a');
    manage.className = 'button secondary small';
    manage.href = '/channels';
    manage.textContent = 'จัดการ Channel';
    label.append(select);
    root.replaceChildren(label, manage);
    const channels = await fetchChannels();
    fill(select, channels, options.selected || defaultsByPath[location.pathname] || 'undefined');
    return select;
  }

  const originalFetch = window.fetch.bind(window);
  window.fetch = (input, init = {}) => {
    const url = typeof input === 'string' ? input : input?.url || '';
    const method = String(init.method || 'GET').toUpperCase();
    const selected = document.querySelector('#contentChannel')?.value || 'undefined';
    const creationEndpoints = ['/api/jobs', '/api/podcast/jobs', '/api/quick-reel'];
    if (method === 'POST' && creationEndpoints.includes(url) && init.body instanceof FormData && !init.body.has('channel_id')) {
      init.body.append('channel_id', selected);
    }
    if (method === 'POST' && ['/api/ai/projects/automatic', '/api/zodiac/batches'].includes(url) && typeof init.body === 'string') {
      try {
        const payload = JSON.parse(init.body);
        if (!payload.channel_id && !payload.channelId) payload.channel_id = selected;
        init = {...init, body: JSON.stringify(payload)};
      } catch (_) {}
    }
    return originalFetch(input, init);
  };

  window.AutoClipChannels = { fetchChannels, fill, mount };

  if (['/ai', '/zodiac-weekly'].includes(location.pathname) && !document.querySelector('#channelPicker')) {
    const host = document.createElement('section');
    host.id = 'channelPicker';
    host.className = 'tool-card';
    const anchor = document.querySelector('.hero-card, .zodiac-hero');
    anchor?.after(host);
    mount(host);
  }
})();
