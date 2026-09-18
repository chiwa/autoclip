// AutoClip Sound Notification System
if (!window.AutoClipSound) {
  window.AutoClipSound = (() => {
    let ctx = null;
    const STORAGE_KEY = 'autoclip_sound_enabled';

    function isEnabled() {
      try {
        const v = localStorage.getItem(STORAGE_KEY);
        return v === null ? true : v === 'true';
      } catch (_) {
        return true;
      }
    }

    function setEnabled(val) {
      try {
        localStorage.setItem(STORAGE_KEY, val ? 'true' : 'false');
      } catch (_) {}
    }

    function getAudioContext() {
      if (!ctx) {
        const AC = window.AudioContext || window.webkitAudioContext;
        if (AC) ctx = new AC();
      }
      if (ctx && ctx.state === 'suspended') {
        ctx.resume().catch(() => {});
      }
      return ctx;
    }

    // Pre-unlock audio context on first user interaction to satisfy browser autoplay policy
    ['pointerdown', 'keydown', 'click'].forEach(evt => {
      window.addEventListener(evt, () => {
        const ac = getAudioContext();
        if (ac && ac.state === 'suspended') {
          ac.resume().catch(() => {});
        }
      }, { once: true, passive: true });
    });

    // เสียงสำเร็จ: "ติ้งต่อง" (Bright pleasant Ding-Dong chime)
    // Note 1 (Ding): E5 (659.25 Hz), Note 2 (Dong): C5 (523.25 Hz)
    function playSuccess() {
      if (!isEnabled()) return;
      try {
        const ac = getAudioContext();
        if (!ac) return;
        const t = ac.currentTime;

        const master = ac.createGain();
        master.gain.setValueAtTime(0.35, t);
        master.connect(ac.destination);

        // --- Note 1 ("ติ้ง"): Starts at t ---
        const ding = ac.createOscillator();
        const dingGain = ac.createGain();
        const dingHarmonic = ac.createOscillator();
        const dingHarmonicGain = ac.createGain();

        ding.type = 'sine';
        ding.frequency.setValueAtTime(659.25, t); // E5
        dingGain.gain.setValueAtTime(0.0001, t);
        dingGain.gain.exponentialRampToValueAtTime(0.55, t + 0.012);
        dingGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.38);

        dingHarmonic.type = 'sine';
        dingHarmonic.frequency.setValueAtTime(1318.5, t); // 2nd harmonic
        dingHarmonicGain.gain.setValueAtTime(0.0001, t);
        dingHarmonicGain.gain.exponentialRampToValueAtTime(0.12, t + 0.012);
        dingHarmonicGain.gain.exponentialRampToValueAtTime(0.0001, t + 0.22);

        ding.connect(dingGain);
        dingGain.connect(master);
        dingHarmonic.connect(dingHarmonicGain);
        dingHarmonicGain.connect(master);

        ding.start(t);
        dingHarmonic.start(t);
        ding.stop(t + 0.4);
        dingHarmonic.stop(t + 0.25);

        // --- Note 2 ("ต่อง"): Starts at t + 0.20s ---
        const t2 = t + 0.20;
        const dong = ac.createOscillator();
        const dongGain = ac.createGain();
        const dongHarmonic = ac.createOscillator();
        const dongHarmonicGain = ac.createGain();

        dong.type = 'sine';
        dong.frequency.setValueAtTime(523.25, t2); // C5
        dongGain.gain.setValueAtTime(0.0001, t2);
        dongGain.gain.exponentialRampToValueAtTime(0.65, t2 + 0.015);
        dongGain.gain.exponentialRampToValueAtTime(0.0001, t2 + 0.75);

        dongHarmonic.type = 'sine';
        dongHarmonic.frequency.setValueAtTime(1046.5, t2); // 2nd harmonic
        dongHarmonicGain.gain.setValueAtTime(0.0001, t2);
        dongHarmonicGain.gain.exponentialRampToValueAtTime(0.15, t2 + 0.015);
        dongHarmonicGain.gain.exponentialRampToValueAtTime(0.0001, t2 + 0.4);

        dong.connect(dongGain);
        dongGain.connect(master);
        dongHarmonic.connect(dongHarmonicGain);
        dongHarmonicGain.connect(master);

        dong.start(t2);
        dongHarmonic.start(t2);
        dong.stop(t2 + 0.8);
        dongHarmonic.stop(t2 + 0.45);
      } catch (e) {
        console.warn('AutoClipSound: Failed to play success chime', e);
      }
    }

    // เสียงไม่สำเร็จ: "Alert / เตือน" (Distinct double warning alert pulse)
    function playError() {
      if (!isEnabled()) return;
      try {
        const ac = getAudioContext();
        if (!ac) return;
        const t = ac.currentTime;

        const master = ac.createGain();
        master.gain.setValueAtTime(0.32, t);
        master.connect(ac.destination);

        const filter = ac.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(850, t);
        filter.connect(master);

        // Pulse 1: Eb4 (311.13 Hz)
        const osc1 = ac.createOscillator();
        const gain1 = ac.createGain();
        osc1.type = 'triangle';
        osc1.frequency.setValueAtTime(311.13, t);
        gain1.gain.setValueAtTime(0.0001, t);
        gain1.gain.linearRampToValueAtTime(0.75, t + 0.015);
        gain1.gain.exponentialRampToValueAtTime(0.0001, t + 0.13);

        osc1.connect(gain1);
        gain1.connect(filter);
        osc1.start(t);
        osc1.stop(t + 0.14);

        // Pulse 2: C4 (261.63 Hz) - lower tone warning
        const t2 = t + 0.15;
        const osc2 = ac.createOscillator();
        const gain2 = ac.createGain();
        osc2.type = 'triangle';
        osc2.frequency.setValueAtTime(261.63, t2);
        gain2.gain.setValueAtTime(0.0001, t2);
        gain2.gain.linearRampToValueAtTime(0.85, t2 + 0.015);
        gain2.gain.exponentialRampToValueAtTime(0.0001, t2 + 0.30);

        osc2.connect(gain2);
        gain2.connect(filter);
        osc2.start(t2);
        osc2.stop(t2 + 0.32);
      } catch (e) {
        console.warn('AutoClipSound: Failed to play error alert', e);
      }
    }

    return {
      playSuccess,
      playError,
      isEnabled,
      setEnabled,
    };
  })();
}

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
    ['Thai TTS','/tts'],
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

  // Sound notification toggle button in nav
  const soundBtn = document.createElement('button');
  soundBtn.type = 'button';
  soundBtn.className = 'nav-sound-btn';
  function updateSoundUI() {
    const on = window.AutoClipSound.isEnabled();
    soundBtn.innerHTML = on
      ? '<span class="nav-sound-icon">🔔</span><span class="nav-sound-text">เสียงเตือน</span>'
      : '<span class="nav-sound-icon">🔕</span><span class="nav-sound-text">ปิดเสียง</span>';
    soundBtn.title = on
      ? 'เสียงแจ้งเตือน: เปิดอยู่ (คลิกซ้าย: เปิด/ปิด & ทดสอบติ้งต่อง | คลิกขวา: ทดสอบเสียง Alert)'
      : 'เสียงแจ้งเตือน: ปิดอยู่ (คลิกเพื่อเปิด)';
    soundBtn.classList.toggle('sound-muted', !on);
  }
  updateSoundUI();
  soundBtn.onclick = (e) => {
    e.preventDefault();
    const next = !window.AutoClipSound.isEnabled();
    window.AutoClipSound.setEnabled(next);
    updateSoundUI();
    if (next) {
      window.AutoClipSound.playSuccess();
    }
  };
  soundBtn.oncontextmenu = (e) => {
    e.preventDefault();
    window.AutoClipSound.playError();
  };
  histories.append(soundBtn);

  nav.append(primary, histories);
  header.append(nav);
})();
