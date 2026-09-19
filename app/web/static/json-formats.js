// AutoClip Unified JSON Formats Reference Component
(() => {
  const FORMATS = {
    'quick-reel': {
      id: 'quick-reel',
      title: '⚡ Quick Reel JSON Format',
      badge: '9:16 Vertical · Shorts / Reels / TikTok',
      note: '💡 <strong>จุดสำคัญ:</strong> หน้านี้ใช้สร้างวิดีโอแนวตั้ง 9:16 หัวข้อคลิปใช้คีย์ <code>"topic"</code> (ไม่ใช่ "title") และบทพูดใช้คีย์ <code>"tts"</code> ซึ่งใส่เป็นข้อความเดี่ยว หรือเป็น Array ข้อความตามลำดับภาพที่อัปโหลดได้',
      fields: [
        { key: 'topic', required: true, desc: 'ชื่อเรื่องหรือหัวข้อคลิป (จะถูกนำไปใช้เป็น Title ในวิดีโอ)' },
        { key: 'description', required: false, desc: 'คำอธิบายคลิป แคปชั่น และแฮชแท็กสำหรับโพสต์ลงโซเชียล' },
        { key: 'voice', required: false, desc: 'การตั้งค่าเสียง { provider: "google", voice: "Fenrir"|"Iapetus", speed: 1.05, style_prompt: "..." }' },
        { key: 'motion', required: false, desc: 'รูปแบบการเคลื่อนไหวภาพ เช่น "gentle_float", "cinematic_push_in", "cinematic_pull_out", "none"' },
        { key: 'tts', required: true, desc: 'บทพูดภาษาไทย (รับทั้งสตริงเดี่ยว เช่น "..." หรือ Array สตริง เช่น ["ท่อน 1", "ท่อน 2"] ตามลำดับภาพ)' }
      ],
      template: {
        topic: "Black Hole Star — ดาวที่มีหลุมดำอยู่ข้างใน?",
        description: "JWST พบหลักฐานสำคัญจากวัตถุประเภท Little Red Dot ในจักรวาลยุคแรก #ThaiJavaZone #Astronomy #Science #Space",
        voice: {
          provider: "google",
          voice: "Fenrir",
          speed: 1.05,
          style_prompt: "น้ำเสียงตื่นเต้น น่าค้นหา ดึงดูดผู้ฟัง กระชับและชัดเจน"
        },
        motion: "cinematic_pull_out",
        tts: "ถ้าคุณคิดว่าหลุมดำคือจุดจบของดาวทุกดวง... คุณอาจต้องคิดใหม่ เพราะในจักรวาลยุคแรกเริ่ม อาจเคยมีสิ่งที่เรียกว่า Black Hole Star อยู่จริง"
      },
      insertTargetId: '#jsonImport',
      insertCallback: (text) => {
        const el = document.querySelector('#jsonImport');
        if (el) {
          el.value = text;
          el.dispatchEvent(new Event('input'));
          el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }
    },
    'podcast': {
      id: 'podcast',
      title: '🎙️ YouTube Podcast JSON Format',
      badge: '16:9 Horizontal · YouTube Visual Podcast',
      note: '💡 <strong>จุดสำคัญ:</strong> หน้านี้ใช้สร้างคลิปพอดแคสต์แนวนอน 16:9 ความยาวปกติ 5–30 นาที หัวข้อใช้คีย์ <code>"title"</code> (ไม่ใช่ "topic") และบทพูดจะจัดเก็บแยกภาษาใน <code>"tts": { "thai": { "script": "..." } }</code> พร้อมรองรับแทร็กภาษาอังกฤษและ BGM คลอ',
      fields: [
        { key: 'title', required: true, desc: 'ชื่อตอนพอดแคสต์ (ใช้เป็นชื่อเรื่องบน YouTube)' },
        { key: 'caption', required: false, desc: 'ออบเจ็กต์แคปชั่น { thai: "คำอธิบายภาษาไทย...", english: "" }' },
        { key: 'hashtags', required: false, desc: 'รายการแฮชแท็กเป็น Array เช่น ["#Podcast", "#เรื่องลี้ลับ", "#สารคดี"]' },
        { key: 'tts.thai', required: true, desc: 'บทพูดภาษาไทย { voice: "Fenrir"|"Enceladus", speed: 0.95, style: "...", script: "(บทพากย์เต็ม)" }' },
        { key: 'tts.english', required: false, desc: 'บทพูดภาษาอังกฤษ (ไม่บังคับ) สำหรับเจนไฟล์เสียงอังกฤษเพิ่มเติม' },
        { key: 'audio', required: false, desc: 'การตั้งค่าเสียง { generate_english_audio: false, bgm_track: "none", bgm_volume: 0.12 }' }
      ],
      template: {
        title: "นางตานี — รักคนเป็นได้...แต่ไม่มีวันได้ครองคู่",
        caption: {
          thai: "ตำนานนางตานี ผีสาวแห่งดงกล้วย ผู้ถูกเล่าขานมานานในความเชื่อไทย ว่ากันว่าเธออาจปรากฏกายในคืนเงียบงัน #คนเหนือดวง #นางตานี #Podcast",
          english: ""
        },
        hashtags: [
          "#คนเหนือดวง",
          "#นางตานี",
          "#ตำนานไทย",
          "#ความรักต้องห้าม",
          "#Podcast"
        ],
        tts: {
          thai: {
            voice: "Fenrir",
            speed: 0.97,
            style: "Speak in Thai with a deep, haunting, romantic and sorrowful tone. Keep pacing cinematic and natural.",
            script: "ถ้าคุณรู้ตั้งแต่วันแรกว่า... คนที่คุณกำลังจะรัก ไม่มีวันใช้ชีวิตอยู่กับคุณได้เหมือนคนธรรมดา คุณยังจะยอมรักเขาไหม..."
          }
        },
        audio: {
          generate_english_audio: false,
          bgm_track: "none",
          bgm_volume: 0.12
        }
      },
      insertTargetId: '#podcastJsonInput',
      insertCallback: (text) => {
        const tabBtn = document.querySelector('#tabImportJson');
        if (tabBtn) tabBtn.click();
        const el = document.querySelector('#podcastJsonInput');
        if (el) {
          el.value = text;
          el.dispatchEvent(new Event('input'));
          el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }
    },
    'zodiac': {
      id: 'zodiac',
      title: '🔮 คนเหนือดวง 12 ราศี JSON Format',
      badge: '9:16 Vertical · Weekly Batch 12 ราศี',
      note: '💡 <strong>จุดสำคัญ:</strong> สคริปต์สัปดาห์เดียวสำหรับสร้างวิดีโอ 12 ราศีพร้อมกัน 12 คลิป โดยมีข้อมูลวันที่ <code>week</code> และรายการราศี <code>zodiacs</code> ครบ 12 ราศี (aries, taurus, gemini, cancer, leo, virgo, libra, scorpio, sagittarius, capricorn, aquarius, pisces)',
      fields: [
        { key: 'week', required: true, desc: 'ช่วงวันที่ของสัปดาห์ { start_date: "YYYY-MM-DD", end_date: "YYYY-MM-DD", display_th: "..." }' },
        { key: 'zodiacs', required: true, desc: 'Array 12 ราศี แต่ละราศีมี { id, name_th, title, hook, work, money, love, advice, encouragement, tts }' }
      ],
      template: {
        week: {
          start_date: "2026-09-22",
          end_date: "2026-09-28",
          display_th: "22 - 28 กันยายน 2569"
        },
        zodiacs: [
          {
            id: "aries",
            name_th: "เมษ",
            title: "ดวงรายสัปดาห์ ราศีเมษ",
            hook: "สัปดาห์นี้การเงินมีเกณฑ์สะพัด แต่ระวังเรื่องอารมณ์ร้อน",
            work: "งานมีความก้าวหน้า ผู้ใหญ่ให้ความเมตตาและไว้วางใจ",
            money: "มีรายรับเข้ามาจากหลายช่องทาง การลงทุนเริ่มเห็นผลกำไร",
            love: "คนโสดมีคนเข้ามาพูดคุย คนมีคู่ปรับความเข้าใจกันได้ดีขึ้น",
            advice: "หมั่นทำบุญตักบาตรหรือปล่อยปลา เสริมพลังบารมีให้ราบรื่น",
            encouragement: "ขอให้เป็นสัปดาห์ที่เต็มไปด้วยพลังใจและความสำเร็จครับ",
            tts: "ดวงรายสัปดาห์ ราศีเมษ ประจำวันที่ 22 ถึง 28 กันยายน 2569 สัปดาห์นี้การเงินมีเกณฑ์สะพัด..."
          }
        ]
      },
      insertTargetId: '#json',
      insertCallback: (text) => {
        const el = document.querySelector('#json');
        if (el) {
          el.value = text;
          el.dispatchEvent(new Event('input'));
          el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }
    },
    'studio': {
      id: 'studio',
      title: '📦 Studio Package script.json Format',
      badge: 'AutoClip Package · script.json + images/',
      note: '💡 <strong>จุดสำคัญ:</strong> โครงสร้างไฟล์ <code>script.json</code> ที่วางอยู่ที่ Root ของไฟล์ ZIP สำหรับ AutoClip Studio โดยแต่ละ scene จะต้องมีชื่อไฟล์ภาพตรงกับไฟล์ในโฟลเดอร์ <code>images/</code>',
      fields: [
        { key: 'project', required: true, desc: 'ข้อมูลโครงการ { title: "...", aspectRatio: "9:16"|"16:9", language: "th" }' },
        { key: 'voice', required: true, desc: 'เสียงพากย์หลัก { provider: "google", voice: "Fenrir"|"Iapetus", speed: 1.05 }' },
        { key: 'scenes', required: true, desc: 'Array ฉากต่างๆ แต่ละฉากมี { id, image, narration, tts_text, motion, transition, estimated_duration }' }
      ],
      template: {
        project: {
          title: "ความลับของหลุมดำ",
          aspectRatio: "9:16",
          language: "th"
        },
        voice: {
          provider: "google",
          voice: "Fenrir",
          speed: 1.05
        },
        scenes: [
          {
            id: "scene-01",
            image: "scene-01.png",
            narration: "ยินดีต้อนรับสู่การเดินทางสำรวจความลึกลับของจักรวาล",
            tts_text: "ยินดีต้อนรับสู่การเดินทางสำรวจความลึกลับของจักรวาล",
            motion: "cinematic_push_in",
            transition: "fade",
            estimated_duration: 6
          },
          {
            id: "scene-02",
            image: "scene-02.png",
            narration: "ใจกลางของกาแล็กซีมีสิ่งมโหฬารที่กลืนกินได้แม้กระทั่งแสง",
            tts_text: "ใจกลางของกาแล็กซีมีสิ่งมโหฬารที่กลืนกินได้แม้กระทั่งแสง",
            motion: "gentle_float",
            transition: "dissolve",
            estimated_duration: 7
          }
        ]
      },
      insertTargetId: null,
      insertCallback: null
    }
  };

  let dialogEl = null;
  let currentActiveTab = 'quick-reel';

  function detectDefaultTab() {
    const path = window.location.pathname;
    if (path.includes('quick-reel')) return 'quick-reel';
    if (path.includes('podcast')) return 'podcast';
    if (path.includes('zodiac')) return 'zodiac';
    return 'studio';
  }

  function ensureDialogMounted() {
    if (dialogEl) return dialogEl;
    let existing = document.querySelector('#jsonFormatDialog');
    if (existing) {
      dialogEl = existing;
      return dialogEl;
    }

    const html = `
    <dialog id="jsonFormatDialog" class="studio-dialog">
      <div class="studio-dialog-card">
        <div class="studio-dialog-head">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1.3rem;">📖</span>
            <div>
              <h3 class="studio-dialog-title" id="jsonFormatTitle">คู่มือโครงสร้าง JSON (JSON Format Reference)</h3>
              <span class="muted" style="font-size: 0.8rem;">เลือกดูและคัดลอก Template ให้ตรงกับประเภทงานที่ต้องการ</span>
            </div>
          </div>
          <button type="button" class="studio-dialog-close" id="btnCloseJsonFormatDialog" aria-label="Close">✕</button>
        </div>

        <!-- Format Switcher Tabs -->
        <div class="format-nav-tabs" role="tablist">
          <button type="button" class="format-tab-btn" data-format-tab="quick-reel">⚡ Quick Reel (9:16)</button>
          <button type="button" class="format-tab-btn" data-format-tab="podcast">🎙️ YouTube Podcast (16:9)</button>
          <button type="button" class="format-tab-btn" data-format-tab="zodiac">🔮 คนเหนือดวง 12 ราศี</button>
          <button type="button" class="format-tab-btn" data-format-tab="studio">📦 Studio ZIP (script.json)</button>
        </div>

        <div class="studio-dialog-body" style="padding-top: 10px;">
          <div class="format-meta-bar">
            <div id="formatBadgeWrap">
              <span id="formatBadgePill" class="pill"></span>
            </div>
            <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-left: auto;">
              <button type="button" id="btnCopyFormatTemplate" class="button secondary small">📋 คัดลอก Template</button>
              <button type="button" id="btnInsertFormatTemplate" class="button primary small" style="display: none;">✏️ นำไปวางในกล่อง JSON หน้านี้</button>
              <button type="button" id="btnDownloadFormatTemplate" class="button secondary small">⬇️ ดาวน์โหลด .json</button>
            </div>
          </div>

          <div id="formatNoteBox" class="format-note-box"></div>
          <div id="formatFieldsBox" class="format-fields-box"></div>

          <pre class="json-preview-pre" style="margin-top: 10px; max-height: 40vh;"><code id="formatCodeView"></code></pre>
        </div>

        <div class="studio-dialog-footer">
          <span class="muted" style="font-size: 0.82rem; margin-right: auto;">💡 คลิกเลือกแท็บด้านบนเพื่อดูเปรียบเทียบ Format ของหน้าอื่น ๆ ได้ทันที</span>
          <button type="button" class="button secondary" id="btnCloseJsonFormatDialogFooter">ปิด</button>
        </div>
      </div>
    </dialog>
    `;

    const wrap = document.createElement('div');
    wrap.innerHTML = html.trim();
    dialogEl = wrap.firstChild;
    document.body.appendChild(dialogEl);

    // Bind Close events
    const closeDialog = () => {
      if (typeof dialogEl.close === 'function') {
        try { dialogEl.close(); } catch (_) {}
      }
      dialogEl.removeAttribute('open');
      dialogEl.style.display = 'none';
    };

    dialogEl.querySelector('#btnCloseJsonFormatDialog')?.addEventListener('click', closeDialog);
    dialogEl.querySelector('#btnCloseJsonFormatDialogFooter')?.addEventListener('click', closeDialog);
    dialogEl.addEventListener('click', (e) => {
      if (e.target === dialogEl) closeDialog();
    });

    // Bind Tab Switching
    dialogEl.querySelectorAll('[data-format-tab]').forEach(btn => {
      btn.addEventListener('click', () => {
        renderFormatTab(btn.dataset.formatTab);
      });
    });

    // Bind Copy Button
    dialogEl.querySelector('#btnCopyFormatTemplate')?.addEventListener('click', async () => {
      const active = FORMATS[currentActiveTab];
      if (!active) return;
      const text = JSON.stringify(active.template, null, 2);
      try {
        await navigator.clipboard.writeText(text);
        const btn = dialogEl.querySelector('#btnCopyFormatTemplate');
        const orig = btn.textContent;
        btn.textContent = '✓ คัดลอกแล้ว!';
        setTimeout(() => { btn.textContent = orig; }, 2000);
      } catch (_) {
        alert('คัดลอกไม่สำเร็จ');
      }
    });

    // Bind Insert Button
    dialogEl.querySelector('#btnInsertFormatTemplate')?.addEventListener('click', () => {
      const active = FORMATS[currentActiveTab];
      if (!active || !active.insertCallback) return;
      const text = JSON.stringify(active.template, null, 2);
      active.insertCallback(text);
      closeDialog();
    });

    // Bind Download Button
    dialogEl.querySelector('#btnDownloadFormatTemplate')?.addEventListener('click', () => {
      const active = FORMATS[currentActiveTab];
      if (!active) return;
      const text = JSON.stringify(active.template, null, 2);
      const blob = new Blob([text], { type: 'application/json;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${active.id}-template.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });

    return dialogEl;
  }

  function renderFormatTab(tabKey) {
    if (!FORMATS[tabKey]) tabKey = 'quick-reel';
    currentActiveTab = tabKey;
    const dialog = ensureDialogMounted();
    const data = FORMATS[tabKey];

    // Update active tab buttons
    dialog.querySelectorAll('[data-format-tab]').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.formatTab === tabKey);
    });

    // Update Content
    const titleEl = dialog.querySelector('#jsonFormatTitle');
    if (titleEl) titleEl.textContent = data.title;

    const badgeEl = dialog.querySelector('#formatBadgePill');
    if (badgeEl) badgeEl.textContent = data.badge;

    const noteEl = dialog.querySelector('#formatNoteBox');
    if (noteEl) noteEl.innerHTML = data.note;

    const fieldsEl = dialog.querySelector('#formatFieldsBox');
    if (fieldsEl) {
      fieldsEl.innerHTML = `
        <div style="font-weight: 600; margin-bottom: 6px; color: #fff;">คำอธิบายคีย์สำคัญ (Key Fields):</div>
        <ul style="margin: 0; padding-left: 18px;">
          ${data.fields.map(f => `<li><strong>${f.key}</strong> ${f.required ? '<span style="color:#ff6b8b; font-size:10.5px;">(จำเป็น)</span>' : '<span style="color:#8ca0ba; font-size:10.5px;">(ไม่บังคับ)</span>'}: ${f.desc}</li>`).join('')}
        </ul>
      `;
    }

    const codeEl = dialog.querySelector('#formatCodeView');
    if (codeEl) {
      codeEl.textContent = JSON.stringify(data.template, null, 2);
    }

    // Toggle Insert Button
    const insertBtn = dialog.querySelector('#btnInsertFormatTemplate');
    if (insertBtn) {
      const canInsert = data.insertTargetId && document.querySelector(data.insertTargetId);
      insertBtn.style.display = canInsert ? 'inline-block' : 'none';
      if (canInsert) {
        insertBtn.textContent = '✏️ นำตัวอย่างไปใส่ในกล่อง JSON หน้านี้';
      }
    }
  }

  function open(tabKey) {
    const dialog = ensureDialogMounted();
    const targetTab = tabKey || detectDefaultTab();
    renderFormatTab(targetTab);

    dialog.setAttribute('open', '');
    if (typeof dialog.showModal === 'function') {
      try { dialog.showModal(); } catch (_) {}
    }
    dialog.style.display = 'block';
  }

  window.AutoClipJsonFormat = {
    open,
    FORMATS
  };

  // Auto-bind click handlers on DOM readiness
  function autoBindButtons() {
    document.querySelectorAll('[data-open-json-format]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        const tab = btn.dataset.openJsonFormat || detectDefaultTab();
        open(tab);
      });
    });

    const explicitIds = [
      { id: 'btnViewQuickReelJsonFormat', tab: 'quick-reel' },
      { id: 'btnViewPodcastJsonFormat', tab: 'podcast' },
      { id: 'btnViewZodiacJsonFormat', tab: 'zodiac' },
      { id: 'btnViewStudioJsonFormat', tab: 'studio' }
    ];

    explicitIds.forEach(({ id, tab }) => {
      const btn = document.querySelector(`#${id}`);
      if (btn) {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          open(tab);
        });
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoBindButtons);
  } else {
    autoBindButtons();
  }
})();
