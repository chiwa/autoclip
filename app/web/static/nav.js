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

    // เสียงสำเร็จ: "ตึง-ตึง-ตึง-ตึ๊งงง" (Long, rich resonant 4-note chime with sustained bell decay ~2.5s)
    function playSuccess() {
      if (!isEnabled()) return;
      try {
        const ac = getAudioContext();
        if (!ac) return;
        const t = ac.currentTime;

        const master = ac.createGain();
        master.gain.setValueAtTime(0.48, t);
        master.connect(ac.destination);

        // 4 notes sequence: C5 (523.25 Hz), E5 (659.25 Hz), G5 (783.99 Hz), C6 (1046.50 Hz)
        const notes = [
          { freq: 523.25, time: 0.00, dur: 0.50, gain: 0.55 }, // ตึง 1
          { freq: 659.25, time: 0.22, dur: 0.50, gain: 0.60 }, // ตึง 2
          { freq: 783.99, time: 0.44, dur: 0.55, gain: 0.65 }, // ตึง 3
          { freq: 1046.50, time: 0.68, dur: 1.85, gain: 0.75 }, // ตึ๊งงง (หางเสียงยาวกังวาน)
        ];

        notes.forEach(({ freq, time, dur, gain }) => {
          const noteTime = t + time;
          const osc = ac.createOscillator();
          const oscGain = ac.createGain();
          const harmonic = ac.createOscillator();
          const harmonicGain = ac.createGain();

          osc.type = 'sine';
          osc.frequency.setValueAtTime(freq, noteTime);
          oscGain.gain.setValueAtTime(0.0001, noteTime);
          oscGain.gain.exponentialRampToValueAtTime(gain, noteTime + 0.015);
          oscGain.gain.exponentialRampToValueAtTime(0.0001, noteTime + dur);

          // Harmonic for rich crystal chime sound
          harmonic.type = 'sine';
          harmonic.frequency.setValueAtTime(freq * 2, noteTime);
          harmonicGain.gain.setValueAtTime(0.0001, noteTime);
          harmonicGain.gain.exponentialRampToValueAtTime(gain * 0.22, noteTime + 0.012);
          harmonicGain.gain.exponentialRampToValueAtTime(0.0001, noteTime + Math.min(dur * 0.6, 0.6));

          osc.connect(oscGain);
          oscGain.connect(master);
          harmonic.connect(harmonicGain);
          harmonicGain.connect(master);

          osc.start(noteTime);
          harmonic.start(noteTime);
          osc.stop(noteTime + dur + 0.05);
          harmonic.stop(noteTime + dur * 0.6 + 0.05);
        });
      } catch (e) {
        console.warn('AutoClipSound: Failed to play success chime', e);
      }
    }

    // เสียงไม่สำเร็จ / เกิดข้อผิดพลาด: 5 จังหวะเตือนชัดเจน (5-pulse distinct error warning)
    function playError() {
      if (!isEnabled()) return;
      try {
        const ac = getAudioContext();
        if (!ac) return;
        const t = ac.currentTime;

        const master = ac.createGain();
        master.gain.setValueAtTime(0.42, t);
        master.connect(ac.destination);

        const filter = ac.createBiquadFilter();
        filter.type = 'lowpass';
        filter.frequency.setValueAtTime(950, t);
        filter.connect(master);

        // 5 pulses of warning tone (E4 -> Eb4 -> D4 -> C#4 -> C4 with longer tail)
        const pulses = [
          { freq: 329.63, offset: 0.00, dur: 0.14 }, // Pulse 1
          { freq: 311.13, offset: 0.18, dur: 0.14 }, // Pulse 2
          { freq: 293.66, offset: 0.36, dur: 0.14 }, // Pulse 3
          { freq: 277.18, offset: 0.54, dur: 0.14 }, // Pulse 4
          { freq: 261.63, offset: 0.72, dur: 0.42 }, // Pulse 5 (ยาวชัดเจน)
        ];

        pulses.forEach(({ freq, offset, dur }) => {
          const startTime = t + offset;
          const osc = ac.createOscillator();
          const gain = ac.createGain();

          osc.type = 'triangle';
          osc.frequency.setValueAtTime(freq, startTime);

          gain.gain.setValueAtTime(0.0001, startTime);
          gain.gain.linearRampToValueAtTime(0.85, startTime + 0.015);
          gain.gain.exponentialRampToValueAtTime(0.0001, startTime + dur);

          osc.connect(gain);
          gain.connect(filter);

          osc.start(startTime);
          osc.stop(startTime + dur + 0.05);
        });
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
