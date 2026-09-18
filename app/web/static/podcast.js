(() => {
  const $ = selector => document.querySelector(selector);

  const PODCAST_BEDTIME_STYLE_MALE = 'Speak smoothly with connected phrasing and a natural conversational rhythm. Avoid short choppy pauses between phrases. Keep sentence transitions fluid, with gentle pacing and subtle emphasis. Use brief natural pauses only at punctuation or topic changes.';

  const PODCAST_BEDTIME_STYLE_FEMALE = 'Read aloud in a calm, warm, and gently formal Thai female voice (gentle, feminine, and soothing tone) suitable for a relaxing bedtime podcast. Speak smoothly and naturally, like a thoughtful female storyteller guiding the listener through a fascinating subject late at night. Maintain a soft, even volume and a relaxed, unhurried pace. Use subtle changes in pitch to keep the narration engaging without becoming energetic or dramatic. Keep pauses natural, brief, and well placed between ideas. Avoid sudden emphasis, sharp changes in volume, exaggerated emotion, playful teasing, advertising language, and news-anchor delivery. Pronounce scientific terms, names, and numbers clearly. The overall experience should feel peaceful, reassuring, intelligent, and comfortable enough for the listener to gradually fall asleep.';

  const PODCAST_ENGLISH_STYLE_MALE = PODCAST_BEDTIME_STYLE_MALE;

  const FEMALE_VOICES = new Set(['Achernar', 'Aoede', 'Autonoe', 'Callirrhoe', 'Despina', 'Erinome', 'Gacrux', 'Kore', 'Leda']);

  function getDefaultStyleForVoice(voiceName) {
    return FEMALE_VOICES.has(voiceName) ? PODCAST_BEDTIME_STYLE_FEMALE : PODCAST_BEDTIME_STYLE_MALE;
  }

  const SAMPLE_TEXT = 'ราตรีสวัสดิ์ครับ ยินดีต้อนรับสู่ห้วงเวลาแห่งความสงบ คืนนี้เราจะพาคุณเดินทางข้ามผ่านความเงียบงัน ไปสำรวจความลับอันน่าทึ่งของจักรวาลด้วยกัน';

  // Elements
  const form = $('#podcastForm');
  const titleInput = $('#podcastTitle');
  const focusSelect = $('#podcastFocus');
  const coverInput = $('#coverImage');
  const coverInfo = $('#coverInfo');
  const coverWrap = $('#coverPreviewWrap');
  const coverImg = $('#coverPreviewImg');
  const aspectBadge = $('#aspectRatioBadge');
  const scriptInput = $('#podcastScript');
  const englishScriptInput = $('#englishPodcastScript');
  const enableEnglishAudio = $('#enableEnglishAudio');
  const tabThaiScript = $('#tabThaiScript');
  const tabEnglishScript = $('#tabEnglishScript');
  const tabImportJson = $('#tabImportJson');
  const panelThaiScript = $('#panelThaiScript');
  const panelEnglishScript = $('#panelEnglishScript');
  const panelImportJson = $('#panelImportJson');
  const podcastJsonInput = $('#podcastJsonInput');
  const btnApplyPodcastJson = $('#btnApplyPodcastJson');
  const btnClearPodcastJson = $('#btnClearPodcastJson');
  const podcastJsonStatus = $('#podcastJsonStatus');
  const statChars = $('#statCharCount');
  const statBytes = $('#statByteCount');
  const statChunks = $('#statChunkCount');
  const statDuration = $('#statEstDuration');
  const statEnglishChars = $('#statEnglishCharCount');
  const statEnglishChunks = $('#statEnglishChunkCount');

  const voiceSelect = $('#podcastVoice');
  const speedSlider = $('#podcastSpeed');
  const speedValue = $('#podcastSpeedValue');
  const styleInput = $('#podcastStyle');
  const englishStyleInput = $('#englishPodcastStyle');
  const btnResetStyle = $('#btnResetPodcastStyle');
  const btnResetEnglishStyle = $('#btnResetEnglishPodcastStyle');
  const btnSavePodcastDefaults = $('#btnSavePodcastDefaults');
  const btnRestorePodcastDefaults = $('#btnRestorePodcastDefaults');
  const btnPreviewAudio = $('#btnPreviewAudio');
  const btnPreviewEnglishAudio = $('#btnPreviewEnglishAudio');
  const audioSample = $('#audioSample');
  const audioSampleStatus = $('#audioSampleStatus');

  const enableSubtitles = $('#enableSubtitles');

  const bgmRadios = document.querySelectorAll('input[name="bgmMode"]');
  const customBgmWrap = $('#customBgmWrapper');
  const customBgmFile = $('#customBgmFile');
  const customBgmInfo = $('#customBgmInfo');
  const bgmVolumeSlider = $('#bgmVolume');
  const bgmVolumeValue = $('#bgmVolumeValue');
  const btnPreviewBgm = $('#btnPreviewBgm');
  const audioBgm = $('#audioBgm');
  const bgmStatus = $('#bgmStatus');

  const submitBtn = $('#btnSubmitPodcast');
  const submitError = $('#podcastSubmitError');

  const PODCAST_PREFERENCES_KEY = 'autoclip.podcast.tts-defaults.v1';

  function readSavedPodcastDefaults() {
    try {
      const value = JSON.parse(localStorage.getItem(PODCAST_PREFERENCES_KEY) || 'null');
      return value && typeof value === 'object' ? value : null;
    } catch (_) {
      return null;
    }
  }

  function applyPodcastDefaults(preferences) {
    const availableVoices = [...voiceSelect.options].map(option => option.value);
    voiceSelect.value = availableVoices.includes(preferences?.voice) ? preferences.voice : 'Iapetus';
    const savedSpeed = Number(preferences?.speed);
    speedSlider.value = Number.isFinite(savedSpeed) && savedSpeed >= 0.5 && savedSpeed <= 2 ? String(savedSpeed) : '0.9';
    styleInput.value = typeof preferences?.thaiStyle === 'string' && preferences.thaiStyle.trim()
      ? preferences.thaiStyle
      : getDefaultStyleForVoice(voiceSelect.value);
    englishStyleInput.value = typeof preferences?.englishStyle === 'string' && preferences.englishStyle.trim()
      ? preferences.englishStyle
      : PODCAST_ENGLISH_STYLE_MALE;
    speedValue.textContent = Number(speedSlider.value).toFixed(2);
  }

  // Initialize system defaults or the user's saved defaults.
  applyPodcastDefaults(readSavedPodcastDefaults());
  bgmVolumeValue.textContent = `${Number(bgmVolumeSlider.value).toFixed(2)} (${Math.round(bgmVolumeSlider.value * 100)}%)`;

  function selectScriptTab(language) {
    const english = language === 'english';
    const json = language === 'json';
    tabThaiScript.classList.toggle('active', !english && !json);
    tabEnglishScript.classList.toggle('active', english);
    tabImportJson.classList.toggle('active', json);
    tabThaiScript.setAttribute('aria-selected', String(!english && !json));
    tabEnglishScript.setAttribute('aria-selected', String(english));
    tabImportJson.setAttribute('aria-selected', String(json));
    panelThaiScript.hidden = english || json;
    panelEnglishScript.hidden = !english;
    panelImportJson.hidden = !json;
  }

  tabThaiScript.addEventListener('click', () => selectScriptTab('thai'));
  tabEnglishScript.addEventListener('click', () => selectScriptTab('english'));
  tabImportJson.addEventListener('click', () => selectScriptTab('json'));

  function normalizedJsonText(raw) {
    return raw.trim().replace(/^```(?:json)?\s*/i, '').replace(/\s*```$/, '');
  }

  function importedText(value) {
    return typeof value === 'string'
      ? value.replace(/\\r\\n/g, '\n').replace(/\\n/g, '\n').trim()
      : '';
  }

  function applyPodcastJson({ quiet = false } = {}) {
    const raw = normalizedJsonText(podcastJsonInput.value || '');
    if (!raw) {
      if (!quiet) podcastJsonStatus.textContent = 'กรุณาวาง Podcast JSON ก่อน';
      return false;
    }
    let data;
    try {
      data = JSON.parse(raw);
    } catch (error) {
      if (!quiet) podcastJsonStatus.textContent = `JSON ไม่ถูกต้อง: ${error.message}`;
      return false;
    }
    if (!data || Array.isArray(data) || typeof data !== 'object') {
      podcastJsonStatus.textContent = 'JSON root ต้องเป็น object';
      return false;
    }

    const filled = [];
    const title = importedText(typeof data.title === 'string' ? data.title : data.title?.youtube);
    if (title) {
      titleInput.value = title;
      filled.push('Title');
    }

    const caption = data.caption || {};
    const descriptionParts = [caption.bilingual_intro, caption.thai, caption.english]
      .map(importedText)
      .filter(Boolean);
    if (descriptionParts.length) {
      $('#podcastDescription').value = descriptionParts.join('\n\n');
      filled.push('Description');
    }
    if (Array.isArray(data.hashtags)) {
      $('#podcastHashtags').value = data.hashtags.filter(value => typeof value === 'string').join(' ');
      filled.push('Hashtags');
    } else if (typeof data.hashtags === 'string') {
      $('#podcastHashtags').value = data.hashtags.trim();
      filled.push('Hashtags');
    }

    const thaiTts = data.tts?.thai || {};
    const englishTts = data.tts?.english || {};
    const thaiScript = importedText(thaiTts.script);
    const englishScript = importedText(englishTts.script);
    const thaiStyle = importedText(thaiTts.style);
    const englishStyle = importedText(englishTts.style);
    if (thaiScript) {
      scriptInput.value = thaiScript;
      scriptInput.dispatchEvent(new Event('input'));
      filled.push('Thai script');
    }
    if (englishScript) {
      englishScriptInput.value = englishScript;
      englishScriptInput.dispatchEvent(new Event('input'));
      filled.push('English script');
    }
    if (thaiStyle) {
      styleInput.value = thaiStyle;
      filled.push('Thai style');
    }
    if (englishStyle) {
      englishStyleInput.value = englishStyle;
      filled.push('English style');
    }

    const requestedVoice = thaiTts.voice || englishTts.voice || data.tts?.voice;
    if (typeof requestedVoice === 'string' && [...voiceSelect.options].some(option => option.value === requestedVoice)) {
      voiceSelect.value = requestedVoice;
      filled.push('Voice');
    }
    const requestedSpeed = Number(thaiTts.speed ?? englishTts.speed ?? data.tts?.speed);
    if (Number.isFinite(requestedSpeed) && requestedSpeed >= 0.5 && requestedSpeed <= 2.0) {
      speedSlider.value = String(requestedSpeed);
      speedSlider.dispatchEvent(new Event('input'));
      filled.push('Speed');
    }

    const wantsEnglish = typeof data.audio?.generate_english_audio === 'boolean'
      ? data.audio.generate_english_audio
      : Boolean(englishScriptInput.value.trim());
    enableEnglishAudio.checked = wantsEnglish;
    filled.push(wantsEnglish ? 'English WAV enabled' : 'English WAV disabled');

    podcastJsonStatus.textContent = filled.length
      ? `Auto Fill สำเร็จ: ${filled.join(', ')}`
      : 'อ่าน JSON ได้ แต่ไม่พบ field ที่ AutoClip รองรับ';
    return true;
  }

  btnApplyPodcastJson.addEventListener('click', () => applyPodcastJson());
  btnClearPodcastJson.addEventListener('click', () => {
    podcastJsonInput.value = '';
    podcastJsonStatus.textContent = 'ล้าง JSON แล้ว (ข้อมูลที่ Auto Fill ลงฟอร์มยังคงอยู่)';
  });
  podcastJsonInput.addEventListener('paste', () => {
    setTimeout(() => applyPodcastJson({ quiet: true }), 0);
  });

  function buildPodcastJsonFromForm() {
    const title = titleInput?.value?.trim() || '';
    const desc = $('#podcastDescription')?.value?.trim() || '';
    const rawHashtags = $('#podcastHashtags')?.value?.trim() || '';
    const hashtags = rawHashtags ? rawHashtags.split(/\s+/).filter(Boolean) : [];
    const voiceVal = voiceSelect?.value || 'Enceladus';
    const speedVal = Number(speedSlider?.value || 0.95);
    const thaiScript = scriptInput?.value?.trim() || '';
    const thaiStyle = styleInput?.value?.trim() || '';
    const hasEnglish = Boolean(enableEnglishAudio?.checked);
    const englishScript = englishScriptInput?.value?.trim() || '';
    const englishStyle = englishStyleInput?.value?.trim() || '';
    const bgmTrack = bgmSelect?.value || 'none';
    const bgmVol = Number(bgmVolume?.value || 0.12);

    const data = {
      title: title,
      caption: {
        thai: desc,
        english: ''
      },
      hashtags: hashtags,
      tts: {
        thai: {
          voice: voiceVal,
          speed: speedVal,
          style: thaiStyle,
          script: thaiScript
        }
      },
      audio: {
        generate_english_audio: hasEnglish,
        bgm_track: bgmTrack,
        bgm_volume: bgmVol
      }
    };
    if (hasEnglish || englishScript) {
      data.tts.english = {
        voice: voiceVal,
        speed: speedVal,
        style: englishStyle,
        script: englishScript
      };
    }
    return data;
  }

  function downloadPodcastJson(data, filename) {
    const jsonStr = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  const btnViewPodcastJson = $('#btnViewPodcastJson');
  const btnExportPodcastJson = $('#btnExportPodcastJson');
  const jsonViewDialog = $('#jsonViewDialog');
  const jsonDialogCode = $('#jsonDialogCode');
  const btnCopyJsonDialog = $('#btnCopyJsonDialog');
  const btnDownloadJsonDialog = $('#btnDownloadJsonDialog');
  const btnCloseJsonDialog = $('#btnCloseJsonDialog');
  const btnCloseJsonDialogFooter = $('#btnCloseJsonDialogFooter');

  let currentPodcastJson = null;

  if (btnViewPodcastJson && jsonViewDialog) {
    const closePodcastModal = () => {
      if (typeof jsonViewDialog.close === 'function') {
        try { jsonViewDialog.close(); } catch (_) {}
      }
      jsonViewDialog.removeAttribute('open');
      jsonViewDialog.style.display = 'none';
    };

    btnViewPodcastJson.addEventListener('click', (e) => {
      e.preventDefault();
      currentPodcastJson = buildPodcastJsonFromForm();
      if (jsonDialogCode) jsonDialogCode.textContent = JSON.stringify(currentPodcastJson, null, 2);
      jsonViewDialog.setAttribute('open', '');
      if (typeof jsonViewDialog.showModal === 'function') {
        try { jsonViewDialog.showModal(); } catch (_) {}
      }
      jsonViewDialog.style.display = 'block';
    });

    btnCloseJsonDialog?.addEventListener('click', closePodcastModal);
    btnCloseJsonDialogFooter?.addEventListener('click', closePodcastModal);
    jsonViewDialog.addEventListener('click', (e) => {
      if (e.target === jsonViewDialog) closePodcastModal();
    });

    btnCopyJsonDialog?.addEventListener('click', async () => {
      if (!currentPodcastJson) return;
      try {
        await navigator.clipboard.writeText(JSON.stringify(currentPodcastJson, null, 2));
        const orig = btnCopyJsonDialog.textContent;
        btnCopyJsonDialog.textContent = '✓ คัดลอกแล้ว!';
        setTimeout(() => { btnCopyJsonDialog.textContent = orig; }, 2000);
      } catch (_) {
        alert('คัดลอกไม่สำเร็จ');
      }
    });

    btnDownloadJsonDialog?.addEventListener('click', () => {
      if (!currentPodcastJson) currentPodcastJson = buildPodcastJsonFromForm();
      const titleName = currentPodcastJson.title ? currentPodcastJson.title.replace(/[\\/*?:"<>|]/g, '').trim().replace(/\s+/g, '-') : 'podcast';
      downloadPodcastJson(currentPodcastJson, `${titleName || 'podcast'}.json`);
    });
  }

  if (btnExportPodcastJson) {
    btnExportPodcastJson.addEventListener('click', (e) => {
      e.preventDefault();
      const data = buildPodcastJsonFromForm();
      const titleName = data.title ? data.title.replace(/[\\/*?:"<>|]/g, '').trim().replace(/\s+/g, '-') : 'podcast';
      downloadPodcastJson(data, `${titleName || 'podcast'}.json`);
    });
  }


  const tabThaiStyle = $('#tabThaiStyle');
  const tabEnglishStyle = $('#tabEnglishStyle');
  const panelThaiStyle = $('#panelThaiStyle');
  const panelEnglishStyle = $('#panelEnglishStyle');
  function selectStyleTab(language) {
    const english = language === 'english';
    tabThaiStyle.classList.toggle('active', !english);
    tabEnglishStyle.classList.toggle('active', english);
    tabThaiStyle.setAttribute('aria-selected', String(!english));
    tabEnglishStyle.setAttribute('aria-selected', String(english));
    panelThaiStyle.hidden = english;
    panelEnglishStyle.hidden = !english;
  }
  tabThaiStyle.addEventListener('click', () => selectStyleTab('thai'));
  tabEnglishStyle.addEventListener('click', () => selectStyleTab('english'));

  // Focus select helper: suggestion placeholders
  const focusPlaceholders = {
    astronomy_science: 'เช่น ท่องอวกาศก่อนนอน: มหาสมุทรลับใต้ผืนน้ำแข็งเอนเซลาดัส',
    bedtime_meditation: 'เช่น นิทานดวงดาว: ปล่อยวางความเหนื่อยล้าใต้ฟากฟ้าอันสงบ',
    documentary_history: 'เช่น ย้อนรอยประวัติศาสตร์: การเดินทางของยานวอยเอเจอร์สู่ขอบระบบสุริยะ',
    philosophy_mind: 'เช่น ข้อคิดยามค่ำคืน: ความหมายของความโดดเดี่ยวในจักรวาลอันกว้างใหญ่',
    general: 'เช่น เจาะลึกเรื่องราวน่าทึ่งที่คุณอาจไม่เคยรู้มาก่อน'
  };

  focusSelect.addEventListener('change', () => {
    const hint = focusPlaceholders[focusSelect.value];
    if (hint && !titleInput.value.trim()) {
      titleInput.placeholder = hint;
    }
  });

  // Script Live Stats Calculation
  function updateScriptStats() {
    const text = scriptInput.value || '';
    const charCount = text.length;
    const utf8Bytes = new TextEncoder().encode(text).length;
    const chunkCount = utf8Bytes > 0 ? Math.max(1, Math.ceil(utf8Bytes / 2800)) : 0;

    const speed = parseFloat(speedSlider.value) || 1.1;
    // Pacing: approx ~13 chars per second at speed 1.0 (bedtime speech is slower)
    const seconds = charCount > 0 ? Math.round((charCount * 0.078) / speed) : 0;
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;

    statChars.textContent = charCount.toLocaleString();
    statBytes.textContent = utf8Bytes.toLocaleString();
    statChunks.textContent = chunkCount.toLocaleString();
    statDuration.textContent = charCount > 0 ? `${mins} นาที ${secs} วินาที` : '0 นาที 0 วินาที';
  }

  scriptInput.addEventListener('input', updateScriptStats);
  englishScriptInput.addEventListener('input', () => {
    const text = englishScriptInput.value || '';
    const bytes = new TextEncoder().encode(text).length;
    statEnglishChars.textContent = text.length.toLocaleString();
    statEnglishChunks.textContent = (bytes ? Math.max(1, Math.ceil(bytes / 2800)) : 0).toLocaleString();
    if (text.trim()) enableEnglishAudio.checked = true;
  });
  speedSlider.addEventListener('input', () => {
    speedValue.textContent = Number(speedSlider.value).toFixed(2);
    updateScriptStats();
  });

  // Cover Image Preview & Aspect Ratio Check
  let coverObjectUrl = null;
  coverInput.addEventListener('change', () => {
    const file = coverInput.files[0];
    if (!file) {
      coverInfo.textContent = 'ยังไม่ได้เลือกรูปภาพ';
      coverWrap.hidden = true;
      return;
    }

    coverInfo.textContent = `${file.name} · ${(file.size / 1024 / 1024).toFixed(2)} MB`;
    if (coverObjectUrl) URL.revokeObjectURL(coverObjectUrl);
    coverObjectUrl = URL.createObjectURL(file);

    coverImg.onload = () => {
      const w = coverImg.naturalWidth;
      const h = coverImg.naturalHeight;
      const ratio = w / h;
      const isSixteenNine = Math.abs(ratio - (16 / 9)) < 0.08;

      if (isSixteenNine) {
        aspectBadge.className = 'aspect-good';
        aspectBadge.textContent = `✓ สัดส่วน 16:9 เหมาะสม (${w}×${h})`;
      } else {
        aspectBadge.className = 'aspect-warning';
        aspectBadge.textContent = `⚠️ สัดส่วน ${ratio > 1 ? 'แนวนอน' : 'แนวตั้ง'} (${w}×${h}) — ไม่ใช่ 16:9 พอดี ระบบจะจัดตำแหน่งตรงกลางและครอบตัดเป็น 1920×1080 ให้อัตโนมัติ`;
      }
      coverWrap.hidden = false;
    };
    coverImg.src = coverObjectUrl;
  });

  // Voice & Style Reset
  voiceSelect.addEventListener('change', () => {
    const cur = styleInput.value.trim();
    if (!cur || cur === PODCAST_BEDTIME_STYLE_MALE || cur === PODCAST_BEDTIME_STYLE_FEMALE || cur.startsWith('Read aloud in a calm, warm, and gently formal Thai') || cur.startsWith('Read aloud in a calm, warm, gently formal male')) {
      styleInput.value = getDefaultStyleForVoice(voiceSelect.value);
    }
  });

  btnResetStyle.addEventListener('click', () => {
    styleInput.value = PODCAST_BEDTIME_STYLE_MALE;
    updateScriptStats();
  });

  btnResetEnglishStyle.addEventListener('click', () => {
    englishStyleInput.value = PODCAST_ENGLISH_STYLE_MALE;
    selectStyleTab('english');
  });

  btnSavePodcastDefaults.addEventListener('click', () => {
    localStorage.setItem(PODCAST_PREFERENCES_KEY, JSON.stringify({
      voice: voiceSelect.value,
      speed: Number(speedSlider.value),
      thaiStyle: styleInput.value,
      englishStyle: englishStyleInput.value,
    }));
    audioSampleStatus.textContent = 'บันทึกเสียง ความเร็ว และ Style เป็นค่าเริ่มต้นแล้ว';
  });

  btnRestorePodcastDefaults.addEventListener('click', () => {
    localStorage.removeItem(PODCAST_PREFERENCES_KEY);
    applyPodcastDefaults(null);
    audioSampleStatus.textContent = 'คืนค่าระบบ Iapetus · 0.90 และ Style เริ่มต้นแล้ว';
  });

  // Audio Sample Preview
  let audioSampleUrl = null;
  btnPreviewAudio.addEventListener('click', async () => {
    btnPreviewAudio.disabled = true;
    audioSampleStatus.textContent = 'กำลังสังเคราะห์เสียงตัวอย่าง…';
    try {
      // Pick first sentence of script or default bedtime sample
      let previewText = (scriptInput.value.trim().split(/[。\n.!?]/)[0] || '').trim();
      if (previewText.length < 15) {
        previewText = SAMPLE_TEXT;
      } else if (previewText.length > 200) {
        previewText = previewText.slice(0, 200);
      }

      const body = new FormData();
      body.append('text', previewText);
      body.append('voice', voiceSelect.value);
      body.append('speed', speedSlider.value);
      body.append('style_prompt', styleInput.value.trim());
      body.append('language', 'th-TH');

      const res = await fetch('/api/podcast/preview-audio', {
        method: 'POST',
        body
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw data.detail || data;
      }
      const blob = await res.blob();
      if (audioSampleUrl) URL.revokeObjectURL(audioSampleUrl);
      audioSampleUrl = URL.createObjectURL(blob);
      audioSample.src = audioSampleUrl;
      audioSample.hidden = false;
      await audioSample.play();
      audioSampleStatus.textContent = 'กำลังเล่นเสียงตัวอย่าง';
    } catch (err) {
      audioSampleStatus.textContent = `${err.code || 'TTS_PREVIEW_FAILED'}: ${err.message || 'สร้างเสียงตัวอย่างไม่สำเร็จ'}`;
    } finally {
      btnPreviewAudio.disabled = false;
    }
  });

  btnPreviewEnglishAudio.addEventListener('click', async () => {
    btnPreviewEnglishAudio.disabled = true;
    audioSampleStatus.textContent = 'Generating English voice sample…';
    try {
      let previewText = (englishScriptInput.value.trim().split(/[\n.!?]/)[0] || '').trim();
      if (previewText.length < 15) {
        previewText = 'Welcome. Tonight, we will travel quietly through space and time, and discover a remarkable story together.';
      } else if (previewText.length > 200) {
        previewText = previewText.slice(0, 200);
      }
      const body = new FormData();
      body.append('text', previewText);
      body.append('voice', voiceSelect.value);
      body.append('speed', speedSlider.value);
      body.append('style_prompt', englishStyleInput.value.trim());
      body.append('language', 'en-US');
      const res = await fetch('/api/podcast/preview-audio', { method: 'POST', body });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw data.detail || data;
      }
      const blob = await res.blob();
      if (audioSampleUrl) URL.revokeObjectURL(audioSampleUrl);
      audioSampleUrl = URL.createObjectURL(blob);
      audioSample.src = audioSampleUrl;
      audioSample.hidden = false;
      await audioSample.play();
      audioSampleStatus.textContent = 'Playing English sample';
    } catch (err) {
      audioSampleStatus.textContent = `${err.code || 'TTS_PREVIEW_FAILED'}: ${err.message || 'Could not create English sample'}`;
    } finally {
      btnPreviewEnglishAudio.disabled = false;
    }
  });

  // BGM Controls
  const bgmTrackSelect = document.getElementById('bgmTrack');
  const bgmTrackDesc = document.getElementById('bgmTrackDesc');
  const systemBgmWrap = document.getElementById('systemBgmWrapper');

  const TRACK_DESCRIPTIONS = {
    'mamase-podcast-bg.mp3': 'เพลงประกอบ Podcast หลักของ Mamase จากไฟล์ที่พี่พีเลือก',
    'space.mp3': 'เพลงอวกาศผ่อนคลายเดิมจาก /assets/sounds/space.mp3',
    cosmic_drift: 'โทนอวกาศเวิ้งว้าง นุ่มลึก เบสอุ่นละมุน ไม่รบกวนเสียงพูด เหมาะสำหรับการพักผ่อน',
    starlight_lullaby: 'แสงดาวกล่อมนอน แอมเบียนต์นุ่มละมุนผสมประกายดาวแผ่วเบา ช่วยคลายความเหนื่อยล้า',
    deep_nebula: 'เนบิวลาลึกภวังค์ บรรยากาศอบอุ่นโอบอุ้มจิตใจ ผสมผสานคลื่น Theta Wave',
    interstellar_voyage: 'การเดินทางข้ามกาแล็กซี คอร์ดเมเจอร์อบอุ่น ช้าๆ ให้ความรู้สึกสงบ ปลอดภัย',
    enceladus_ocean: 'มหาสมุทรใต้ผืนน้ำแข็ง คลื่นเสียงกังวานลุ่มลึก ชวนหลับสนิทตลอดคืน'
  };

  async function loadBgmCatalog() {
    if (!bgmTrackSelect) return;
    try {
      const res = await fetch('/api/podcast/bgm-tracks');
      if (!res.ok) return;
      const data = await res.json();
      if (!data.tracks || !data.tracks.length) return;

      bgmTrackSelect.innerHTML = '';

      const assetsGroup = document.createElement('optgroup');
      assetsGroup.label = 'ไฟล์จาก /assets/sounds';

      const builtinGroup = document.createElement('optgroup');
      builtinGroup.label = 'เพลงบรรยากาศ Space Ambient (ระบบ)';

      data.tracks.forEach(track => {
        const opt = document.createElement('option');
        opt.value = track.id;
        opt.textContent = track.name;
        if (track.description) {
          TRACK_DESCRIPTIONS[track.id] = track.description;
        }
        if (track.is_default || track.id === 'mamase-podcast-bg.mp3') {
          opt.selected = true;
        }
        if (track.source === 'builtin') {
          builtinGroup.appendChild(opt);
        } else {
          assetsGroup.appendChild(opt);
        }
      });

      if (assetsGroup.children.length > 0) bgmTrackSelect.appendChild(assetsGroup);
      if (builtinGroup.children.length > 0) bgmTrackSelect.appendChild(builtinGroup);

      const initialDesc = TRACK_DESCRIPTIONS[bgmTrackSelect.value] || '';
      if (bgmTrackDesc) bgmTrackDesc.textContent = initialDesc;
    } catch (e) {
      console.warn('Could not load BGM catalog', e);
    }
  }

  loadBgmCatalog();

  if (bgmTrackSelect) {
    bgmTrackSelect.addEventListener('change', () => {
      const desc = TRACK_DESCRIPTIONS[bgmTrackSelect.value] || `ไฟล์เสียง ${bgmTrackSelect.value}`;
      if (bgmTrackDesc) bgmTrackDesc.textContent = desc;
      if (audioBgm && !audioBgm.paused) {
        audioBgm.src = `/api/podcast/bgm-preview/${encodeURIComponent(bgmTrackSelect.value)}`;
        audioBgm.play().catch(() => {});
      }
    });
  }

  bgmRadios.forEach(radio => {
    radio.addEventListener('change', () => {
      const isCustom = radio.value === 'custom' && radio.checked;
      customBgmWrap.hidden = !isCustom;
      if (systemBgmWrap) systemBgmWrap.hidden = isCustom;
    });
  });

  let customBgmUrl = null;
  customBgmFile.addEventListener('change', () => {
    const file = customBgmFile.files[0];
    if (file) {
      customBgmInfo.textContent = `${file.name} · ${(file.size / 1024 / 1024).toFixed(2)} MB`;
      if (customBgmUrl) URL.revokeObjectURL(customBgmUrl);
      customBgmUrl = URL.createObjectURL(file);
    } else {
      customBgmInfo.textContent = 'ยังไม่ได้เลือกไฟล์เพลง';
      customBgmUrl = null;
    }
  });

  bgmVolumeSlider.addEventListener('input', () => {
    const val = Number(bgmVolumeSlider.value);
    bgmVolumeValue.textContent = `${val.toFixed(2)} (${Math.round(val * 100)}%)`;
    if (audioBgm && !audioBgm.paused) {
      audioBgm.volume = Math.min(1.0, Math.max(0.0, val * 2.5)); // slight boost for auditioning
    }
  });

  btnPreviewBgm.addEventListener('click', async () => {
    btnPreviewBgm.disabled = true;
    bgmStatus.textContent = 'กำลังโหลดเพลง…';
    try {
      const isCustom = document.querySelector('input[name="bgmMode"]:checked')?.value === 'custom';
      if (isCustom && customBgmUrl) {
        audioBgm.src = customBgmUrl;
      } else {
        const track = bgmTrackSelect ? bgmTrackSelect.value : 'mamase-podcast-bg.mp3';
        audioBgm.src = `/api/podcast/bgm-preview/${encodeURIComponent(track)}`;
      }
      audioBgm.volume = Math.min(1.0, Math.max(0.0, Number(bgmVolumeSlider.value) * 2.5));
      audioBgm.hidden = false;
      await audioBgm.play();
      bgmStatus.textContent = 'กำลังเล่นเพลงประกอบ';
    } catch (e) {
      bgmStatus.textContent = 'ไม่สามารถเล่น BGM ได้';
    } finally {
      btnPreviewBgm.disabled = false;
    }
  });

  // Form Submission
  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const title = titleInput.value.trim();
    if (!title) {
      alert('กรุณากรอกชื่อตอน Podcast');
      titleInput.focus();
      return;
    }

    const coverFile = coverInput.files[0];
    if (!coverFile) {
      alert('กรุณาเลือกภาพปก (Cover Image)');
      coverInput.focus();
      return;
    }

    const scriptText = scriptInput.value.trim();
    if (!scriptText) {
      alert('กรุณาวางบทพูดยาวสำหรับสร้าง Podcast');
      scriptInput.focus();
      return;
    }

    const englishScript = englishScriptInput.value.trim();
    if (enableEnglishAudio.checked && !englishScript) {
      selectScriptTab('english');
      alert('กรุณาใส่ English Podcast Script หรือปิดการสร้าง English WAV');
      englishScriptInput.focus();
      return;
    }

    submitBtn.disabled = true;
    submitError.hidden = true;
    submitBtn.textContent = '⏳ กำลังส่งคำสั่งสร้างวิดีโอ…';

    const formData = new FormData();
    formData.append('title', title);
    formData.append('cover_image', coverFile);
    formData.append('script', scriptText);
    formData.append('english_script', enableEnglishAudio.checked ? englishScript : '');
    formData.append('voice', voiceSelect.value);
    formData.append('speed', speedSlider.value);
    formData.append('style_prompt', styleInput.value.trim());
    formData.append('english_style_prompt', englishStyleInput.value.trim());
    formData.append('enable_subtitles', enableSubtitles.checked ? 'true' : 'false');
    formData.append('bgm_volume', bgmVolumeSlider.value);
    formData.append('description', document.getElementById('podcastDescription').value.trim());
    formData.append('hashtags', document.getElementById('podcastHashtags').value.trim());

    const isCustom = document.querySelector('input[name="bgmMode"]:checked')?.value === 'custom';
    if (isCustom && customBgmFile.files[0]) {
      formData.append('bgm_file', customBgmFile.files[0]);
    } else {
      const track = bgmTrackSelect ? bgmTrackSelect.value : 'mamase-podcast-bg.mp3';
      formData.append('bgm_track', track);
    }

    try {
      const response = await fetch('/api/podcast/jobs', {
        method: 'POST',
        body: formData
      });

      const data = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw data.detail || data;
      }

      // Redirect immediately to /jobs/${jobId} for real-time progress & preview
      window.location.href = `/jobs/${data.jobId}`;
    } catch (err) {
      submitError.hidden = false;
      submitError.textContent = `${err.code || 'PODCAST_FAILED'}: ${err.message || 'ส่งคำขอสร้าง Podcast ไม่สำเร็จ'}`;
      submitBtn.disabled = false;
      submitBtn.textContent = '🎙️ สร้าง YouTube Podcast (Generate Video)';
    }
  });

  // Initialize stats on load
  updateScriptStats();
})();
