# AutoClip — Start Here

ไฟล์นี้คือ **จุดเริ่มต้นเพียงไฟล์เดียว** สำหรับ Antigravity, Codex และ agent
อื่นทุกตัว เมื่อเริ่ม session ใหม่ให้ผู้ใช้สั่งอ่าน `start.md`; ไม่ต้องสั่งชื่อ
ไฟล์คำสั่งอื่นแยกกัน เพราะไฟล์นี้เป็น router ไปยังกฎที่เกี่ยวข้อง

## ขั้นตอนเริ่มต้นที่บังคับ

ก่อนวางแผน แก้โค้ด สร้างภาพ หรือสร้าง ZIP ให้อ่านตามลำดับและอ่านแต่ละไฟล์
เพียงครั้งเดียว ไม่ต้องวนกลับมาอ่านซ้ำ:

1. อ่านกฎระดับ repository ที่
   `/Users/zengcode/projects/autoclip/AGENTS.md`
2. อ่าน runbook กลางทั้งหมดที่
   `/Users/zengcode/projects/autoclip/agent.md`
3. ถ้าเป็นงานสร้างหรือแก้ content, ภาพ, `script.json` หรือ ZIP ของ AutoClip
   ให้อ่าน
   `/Users/zengcode/projects/autoclip/.codex/skills/autoclip-content/SKILL.md`
4. ถ้าเป็นช่อง **Mamase** ให้อ่านเพิ่ม
   `/Users/zengcode/projects/autoclip/.agents/skills/mamase-autoclip-package/SKILL.md`
   และถ้าเป็น Reel, Shorts หรือ TikTok ให้อ่านเพิ่ม
   `/Users/zengcode/projects/autoclip/.agents/skills/mamase-reels/SKILL.md`
   และสำหรับการสร้างภาพปก Scene 01 / Key Art ของ Reels อย่างรวดเร็ว ให้ใช้
   `/Users/zengcode/projects/autoclip/.agents/skills/mamase-reels-cover/SKILL.md`
   ไฟล์ใต้ `.agents/skills/` เป็น source of truth สำหรับ Antigravity; mirror ใต้
   `.codex/skills/` มีไว้ให้ Codex เรียกใช้และห้ามตีความกฎเก่ามาทับ source of truth
   และสำหรับงานภาพวิทยาศาสตร์/อวกาศให้อ่าน
   `/Users/zengcode/projects/autoclip/assets/parker_solar_probe_reel/visual-reference.md`
5. ถ้าเป็นช่อง **Thai Java Zone** ให้ใช้หัวข้อ
   `Thai Java Zone — shared visual style bible` ในไฟล์นี้และใน `agent.md`
   รวมถึงหัวข้อชื่อเดียวกันใน `autoclip-content/SKILL.md` ห้ามนำ visual
   direction, presenter หรือ branding ของ Mamase มาใช้
6. ถ้าเป็นงาน **คนเหนือดวง / ดวง 12 ราศี** ให้ใช้ flow แยกที่
   `/zodiac-weekly`: รับ weekly batch JSON หนึ่งไฟล์ แล้วสร้าง 12 MP4, 12
   metadata JSON และ `youtube-upload.csv` จากภาพต้นแบบคงที่ใน `assets/12ราศี`
   โดยเปลี่ยนเฉพาะวันที่ ห้ามนำ branding หรือ History ของ Mamase มาปน และ
   ห้าม rerender/TTS เมื่อแก้เฉพาะ publishing metadata
   และอ่าน skill ถาวรที่
   `/Users/zengcode/projects/autoclip/.codex/skills/khon-nuea-duang-zodiac/SKILL.md`

เฉพาะงานภาพ Mamase ให้ดูชุด
`/Users/zengcode/projects/autoclip/assets/tianwen-2-quasi-satellite-reel/images/`
เป็นตัวอย่าง workflow และระดับคุณภาพที่ผ่านการอนุมัติแล้ว ใช้วิธีคิดและ
มาตรฐานเดียวกัน แต่ห้ามคัดลอกเนื้อหา ฉาก หรือวัตถุของ Tianwen-2 ไปใส่ใน
หัวข้ออื่น สำหรับ Thai Java Zone ห้ามใช้ชุดนี้เป็น style reference

สำหรับงานภาพอวกาศและวิทยาศาสตร์ของ Mamase ให้ใช้สองชุดต่อไปนี้เป็น
**Visual Quality Baseline หลัก** เพิ่มเติม โดยต้องเทียบคุณภาพจากไฟล์ภาพจริง
ไม่ใช่เพียงอ่านชื่อไฟล์หรือคำบรรยาย:

- `/Users/zengcode/projects/autoclip/assets/artemis_ii_far_side_reel/images/`
- `/Users/zengcode/projects/autoclip/assets/parker_solar_probe_reel/`

ชุดใหม่ต้องมีรายละเอียด แสง สี ความลึก สเกล และพลังในการเล่าเรื่องอย่างน้อย
ใกล้เคียง baseline เหล่านี้ ห้ามลดเหลือ generic AI illustration, stock-like
space wallpaper, ภาพแบน ฉากโล่ง หรือวัตถุเล็กที่ไม่สื่อใจความของซีน

ภาพ **Eris Master Reference** ที่
`/Users/zengcode/projects/autoclip/assets/branding/mamase/reference/eris-master-reels-visual-reference.jpg`
ใช้เป็นเพียง baseline ด้านความคม แสง depth และ cinematic finish ไม่ใช่ template
สำหรับ pose, เสื้อผ้า, ตำแหน่งคน–หมา หรือตำแหน่งข้อความ กฎที่เป็น source of truth คือ
`.agents/skills/mamase-reels-cover/SKILL.md`: ต้องเปลี่ยน composition ตามเรื่อง ใช้โลโก้จริง
เพียงหนึ่งชุด มีข้อความเพียง Topic + Thai Hook และใช้ protected zones กันข้อความทับวัตถุสำคัญ

## Mamase Visual Production Contract

กฎส่วนนี้เป็น workflow บังคับเมื่อ Agent สร้างภาพ Mamase เอง ไม่ว่าผู้ใช้จะ
ส่ง prompt ยาวหรือให้เพียงชื่อเรื่อง:

### Topic-Only Autonomous Contract

พี่พีส่งเพียงชื่อเรื่อง หัวข้อ หรือแนวคิดหนึ่งประโยคถือว่า input ครบแล้ว Agent
ต้องคิด Hook, ตรวจข้อเท็จจริง, เขียนบท, วาง Scene, เลือก hero subject, action
ของคน–หมา, มุมกล้อง, แสง, wardrobe, layout, protected zones และ prompt เอง
ห้ามผลักภาระให้ผู้ใช้เขียน prompt รายภาพ จุดรอผู้ใช้ตามปกติมีเพียงการอนุมัติ
Scene 01 จากนั้นจึงทำซีนที่เหลือและ ZIP ให้จบ

Scene 01 ให้สร้าง native candidate ครั้งละหนึ่งภาพ ห้ามไล่ค้น assets ที่ไม่เกี่ยวข้อง,
ทำ thumbnail/contact sheet, สุ่มหลาย seed, ใช้ `rembg`, ตัดแปะ cutout หรือ inpainting
เอง เว้นแต่ผู้ใช้สั่งโดยตรง หาก native generation ล้มเหลวให้รายงานตรง ๆ ห้ามใช้
fallback คุณภาพต่ำเพื่อให้ดูเหมือนว่างานเสร็จ

### Permanent Mamase Scene 01 Master Reference

ทุก Mamase Reel ต้องเปิดตรวจภาพ
`/Users/zengcode/projects/autoclip/assets/branding/mamase/reference/mamase-reels-editorial-poster-master.png`
ก่อนออกแบบ Scene 01 และใช้เป็นมาตรฐานถาวรด้าน Premium Editorial Science Poster:
ภาพเดียวต้องมี scientific tableau ที่เล่าเรื่องครบ, Topic และ Thai Hook ที่มี hierarchy
สง่างาม, รายละเอียดเชิงบรรณาธิการที่เป็นระเบียบ, depth/แสงระดับภาพยนตร์ และคนกับหมา
ที่เชื่อมอารมณ์กับเรื่อง ห้ามลดเหลือข้อความก้อนใหญ่ทับภาพหรือปกมินิมอลโล่ง ๆ

ให้ยึดภาษาและคุณภาพของงาน ไม่ใช่คัดลอก layout หรือท่านั่งเดิมทุกครั้ง วัตถุ
สถานที่ action มุมกล้อง และ props ต้องเปลี่ยนตามหัวข้อ ข้อความทั้งหมดต้อง composite
ภายหลังและ protected zones ยังเป็น Blocking Gate เสมอ

### Mamase Reel canonical standard

Read `docs/mamase-reels-standard.md` before producing a Reel. It is the source
of truth for duration, scene count, hook, subtitles, motion, outro, optional
fields, warnings, and backward compatibility.

### Mamase Reel Hook Gate (Blocking QA Gate)

ก่อนอนุมัติบท Reel/Short/TikTok และก่อนสร้าง TTS หรือภาพ **ต้องตรวจครบทุก 10 ข้อ (Blocking Gate)**:
หากข้อสำคัญข้อใดไม่ผ่าน ให้เขียนช่วงเปิดใหม่ก่อนเดินหน้าต่อเด็ดขาด ห้ามฝ่าฝืนไปสร้าง TTS หรือภาพ

#### กฎเปิดคลิป 1–3 วินาทีแรก (Mandatory Reels Hook Rules)
1. **1–3 วินาทีแรกต้องหยุดนิ้วโป้งผู้ชมทันที (Stop the viewer's thumb)**: ผู้ชมปัดทิ้งได้ในเสี้ยววินาที
2. **ห้ามเด็ดขาด (Never begin with)**:
   - คำทักทาย (สวัสดีครับ, ยินดีต้อนรับสู่...)
   - แนะนำช่องหรือตัวเอง (สู่ Mamase จักรวาลของใจ, ผมพี จาก Mamase)
   - “วันนี้เราจะมาพูดถึง...”, “วันนี้ Mamase จะพาไป...”, “ในคลิปนี้...”
   - “ก่อนอื่น...”, “มาเริ่มกันที่...”
   - “รู้หรือไม่...”, “คุณเคยสงสัยไหม...” (ยกเว้นต่อด้วยประเด็นความขัดแย้งที่น่าทึ่งทันที)
   - เกริ่นประวัติความเป็นมา (History/Background)
   - การเปิดด้วยนิยามเชิงวิชาการ (Definitions)
   - บทนำหรือเกริ่นเรื่องแบบช้า (Slow setup)
3. **เปิดทันทีด้วยหนึ่งใน 5 หมวดนี้**:
   - ข้อเท็จจริงที่น่าตกใจ (Surprising fact)
   - ความขัดแย้งที่ชวนสงสัย (Contradiction)
   - คำถามกระตุ้นความอยากรู้อย่างแรง (Strong curiosity question)
   - ผลลัพธ์คาดไม่ถึง (Unexpected consequence)
   - จังหวะวิทยาศาสตร์แท้จริงที่ทำให้รู้สึก “เฮ้ย เป็นแบบนี้ได้ยังไง?”
4. **ถูกต้องทางวิทยาศาสตร์และปกป้องได้ (Truthful & Scientifically Defensible)**: ห้ามใช้ clickbait หลอกหรือสร้างข้อเท็จจริงเท็จ
5. **เข้าใจง่ายสำหรับคนทั่วไป (General Audience Clarity)**: ใช้คำถาม/ข้อความง่ายๆ ที่คนไม่ใช่นักวิทยาศาสตร์เข้าใจได้ทันที
6. **สร้าง Open Loop & สานต่อทันที**: เปิดปมที่ทำให้ผู้ชมอยากฟังประโยคถัดไปทันที และประโยคที่สองต้องสานต่อคำสัญญาของ Hook ทันที ห้ามวกกลับไปปูพื้นหลังทั่วไป
7. **Hook Matching**: ข้อความในฟิลด์ `hook` ต้องตรงกับประโยคพูดประโยคแรกใน `tts` แบบคำต่อคำ 100%

#### โครงสร้างเวลาและการเดินเรื่อง (Pacing & Duration Standard)
- **0–3 วินาที**: **HOOK** — ประโยคแรกเปิดด้วยจุดที่น่าทึ่งที่สุด หยุดการเลื่อนฟีดทันที
- **3–10 วินาที**: **MINIMAL CONTEXT** — ให้ข้อมูลเฉพาะที่จำเป็นต่อการเข้าใจปริศนาเท่านั้น
- **10–30 วินาที**: **PAYOFF + WOW** — ส่งมอบคำตอบหรือข้อมูลจริงอย่างรวดเร็ว พร้อมเปิดเผย Mini-wow หรือจุดหักมุมทุก 10–15 วินาที
- **30–45 วินาที**: **TWIST / BIGGER QUESTION / FINAL PAYOFF** — จบด้วยนัยสำคัญที่ใหญ่ขึ้นหรือการหักมุมทางวิทยาศาสตร์
- **ช่วงท้าย**: จบด้วย scientific payoff, twist หรือคำถามเฉพาะเรื่องสั้น ๆ เมื่อช่วยให้ตอนจบแข็งแรงขึ้น
- **เป้าหมายความยาว**: เป้าหมายหลัก **45–55 วินาที** และปกติไม่เกิน **60 วินาที** ใช้ประมาณ 6–9 ซีนเนื้อหาที่มีเสียง แล้วต่อ silent branding post-roll 2 วินาทีแยกต่างหาก โดยไม่เติมเนื้อหาฟุ่มเฟือย

#### กฎ TTS, ภาพ, CTA และ Branding
- **TTS Rule**: ใช้ Google Gemini TTS เสียง `Fenrir`, ภาษา `th-TH`; ซีนแรกใช้ Hook Style ที่ความเร็ว `1.10` อัตโนมัติ และซีนที่ 2 เป็นต้นไปใช้ Normal Style ที่ `1.05` ตาม `docs/mamase-reels-standard.md` เสียงพากย์ต้องเริ่มต้นด้วย Hook ทันที ห้ามใส่ชื่อช่อง คำทักทาย เลขตอน หรือเพลงเปิดนำหน้า Hook
- **Visual Rule**: ภาพแรกต้องเสริมพลังและสื่อสารปริศนาของ Hook โดยตรงทันที **Hero Subject ทางดาราศาสตร์/วิทยาศาสตร์ต้องใหญ่ ยิ่งใหญ่ ครองเฟรม (Dominate the frame)** ห้ามเปิดด้วยดาวเคราะห์ดวงเล็กแปะบนพื้นหลังโล่ง ห้ามเป็นวิวพื้นดิน/หลุมอุกกาบาตโล่งที่เด่นกว่าวัตถุหลัก
- **Topic-Specific CTA Rule**: ประโยคจบต้องเป็นคำถามสั้นๆ ที่ชวนคุยเฉพาะประเด็นของเรื่องนั้น (เช่น "ถ้ามีโอกาส คุณกล้าเป็นมนุษย์รุ่นแรกที่ไปอยู่ดาวอังคารไหม?" หรือ "คุณคิดว่ามนุษย์จะไปถึงอารยธรรมระดับหนึ่งก่อน หรือเราจะหยุดตัวเองเสียก่อน?") **ห้ามเด็ดขาด**: คำลงท้ายทั่วไป ("อย่าลืมกดไลก์ กดติดตาม", "คอมเมนต์คุยกันหน่อยนะครับ", "ขอบคุณที่รับชม", หรือ outro สำเร็จรูปเดิม) และห้ามมีเสียงพูดใดๆ ต่อท้าย CTA อีก
- **Branding Rule**: ใช้คำว่า "Mamase" หรือ "Mamase REELS" เท่านั้น **ห้ามใส่คำว่า "MAMASE PODCAST"** บน Reel assets เด็ดขาด และ **ห้ามใส่ badge สองภาษา ("AVAILABLE IN THAI & ENGLISH")** หรือรูปธงภาษาใดๆ บน Reel assets

#### เช็กลิสต์บังคับ: Mamase Reel Hook Gate (10 ข้อ)
1. Hook อยู่ภายใน 1–3 วินาทีแรก
2. ไม่มีคำทักทาย แนะนำช่อง หรือ setup ก่อน Hook
3. คนทั่วไปที่ไม่รู้เรื่องนี้เข้าใจได้ทันที
4. สร้าง Curiosity Gap / Open Loop ชัดเจน
5. ถูกต้องทางวิทยาศาสตร์และปกป้องได้ด้วยหลักฐาน
6. ภาพแรกเสริมพลัง Hook ทันที และวัตถุหลักครองเฟรม
7. ไม่มี filler หรือประโยคยืดเยื้อ
8. มีข้อมูล payoff หรือมุมมองใหม่ทุกไม่กี่วินาที
9. ตอนจบทิ้งแนวคิดใหญ่ twist หรือคำถามที่น่าจดจำ
10. TTS เริ่มด้วย Hook โดยตรง 100%

1. ตรวจข้อเท็จจริงและวางลำดับเรื่องก่อนสร้างภาพ
2. เขียน narration, `tts_text`, subtitle และ shot plan ให้แต่ละซีนมีแนวคิด
   ภาพที่แตกต่างกันและตรงกับบท
3. ค้นหาภาพในคลัง Reusable Asset Library (`scripts/search_assets.py` หรือ
   `assets/reusable-library/assets-index.jsonl`) ตามกฎใน `docs/asset-catalog.md` เสมอ
   หากพบภาพเนื้อหาที่ตรงบท สเกล แบรนด์ และไม่มีข้อความเฉพาะเรื่องเดิม ให้คัดลอก
   จาก `library_path` มาใช้ หากไม่มีภาพที่เหมาะสมจึงวางแผนสร้างใหม่
4. สร้าง Scene 01 ก่อน และใช้ภาพที่ผ่านเป็น **visual anchor** สำหรับ palette,
   lighting, contrast, texture และระดับรายละเอียดของทั้งชุด
5. หากผู้ใช้ไม่ได้อนุมัติให้ทำเองทั้งหมด ให้หยุดรอรีวิว Scene 01; หากผู้ใช้
   อนุมัติ autonomous execution แล้ว ให้ Agent ตรวจและตัดสินตามมาตรฐานนี้เอง
6. สร้างภาพที่เหลือเป็น batch ละไม่เกิน 3 ภาพ เพื่อให้ตรวจพบ style drift,
   ตัวละครผิด หรือคุณภาพตกได้เร็ว
7. เปิดตรวจภาพจริงทุกภาพ ทั้งเต็มเฟรมและขนาดย่อบนจอมือถือ ห้ามรับรองจาก
   prompt, metadata, resolution หรือรายงานของ generator
8. ภาพที่ไม่ตรงบท, generic, โล่ง, แบน, แสงไม่ต่อเนื่อง, มีโลโก้/ลายน้ำ,
   ข้อความผิด, anatomy/hardware ผิด หรือคุณภาพต่ำกว่า baseline ต้องสร้างใหม่
   เฉพาะซีนทันที ห้ามเก็บไว้เพียงเพื่อให้จำนวนครบ
9. Scene 02 เป็นต้นไปต้องไม่มี presenter, generated text, subtitle, watermark,
   ธงหรือตราหน่วยงาน สำหรับ Mamase Reel ให้ composite โลโก้จริงจาก
   `assets/branding/mamase/logo.png` หลังสร้างภาพตาม skill `mamase-reels`
10. เมื่อทุกภาพผ่านแล้วจึงสร้าง `script.json`, `video-metadata.json` และ ZIP;
    ห้ามประกาศว่างานเสร็จก่อนตรวจ package ด้วย AutoClip `PackageService`
11. รายงานชื่อและตำแหน่ง ZIP, จำนวนซีน, จำนวน Wan scenes, resolution,
    package validation และข้อจำกัดของภาพตามจริง

### คำสั่ง “โหมดประหยัดเครดิต”

เมื่อผู้ใช้ระบุ **โหมดประหยัดเครดิต** ให้รักษามาตรฐานภาพเดิม แต่ลดจำนวนการ
generate ด้วยวิธีต่อไปนี้:

- สร้าง Scene 01 ใหม่เป็น Hero Key Art คุณภาพสูงเสมอ
- วาง master images ใหม่ประมาณ 5–6 ภาพสำหรับคลิปสั้นทั่วไป และเพิ่มเฉพาะเมื่อ
  เนื้อหาไม่สามารถเล่าชัดด้วยจำนวนนี้
- แตก shot เพิ่มจาก master ที่เหมาะสมด้วย crop focus, close/medium/wide,
  pan, zoom และ motion โดยห้ามใช้ภาพซ้ำติดกันจนผู้ชมจับได้
- ใช้ `assets/branding/mamase/reels-end-scene.png` เป็น silent branding post-roll หลัง narration และ subtitle จบทั้งหมดเท่านั้น ห้ามสร้างเป็น scene บรรยายหรือส่งเข้า TTS
  ห้ามสร้างใหม่ ครอป รีทัช เปลี่ยนสีหรือข้อความ อนุญาตให้ย่อสำเนาแบบรักษา
  aspect ratio เป็น `1080×1920` สำหรับ ZIP โดยห้ามแก้ artwork ต้นฉบับ
- ใส่ Wan plan เฉพาะ 1–2 ซีนที่ motion เพิ่มคุณค่าชัดเจน ที่เหลือใช้ FFmpeg
- ห้ามลดความละเอียด องค์ประกอบ ความถูกต้อง หรือ Visual QA เพื่อประหยัดเครดิต
- หากภาพหนึ่งสามารถรองรับหลายซีน ต้องเลือก crop/focus ที่เล่าใจความของแต่ละ
  ซีนต่างกันจริง ไม่ใช่ทำสำเนาไฟล์เดิมแล้วเปลี่ยนชื่อ

คำว่า “ประหยัดเครดิต” หมายถึงลดจำนวน generation และ reuse อย่างมีศิลปะ
ไม่ใช่ลดคุณภาพของภาพที่ส่งมอบ

## Thai Java Zone — shared visual style bible

เมื่อหัวข้อ แพ็กเกจ หรือ asset เป็นของ **Thai Java Zone** ให้ใช้ base style
เดียวกันตลอดทั้งชุด: clean modern software-engineering explainer, หนึ่งแนวคิด
ชัดเจนต่อหนึ่งซีน, ภาพ developer หรือ software architecture ที่สมจริงและเป็น
มืออาชีพ, minimal clutter, balanced composition, soft natural lighting,
dark neutral tech background, subtle depth และเฟรมแนวตั้ง 9:16

ห้ามใส่ text, subtitle, watermark, logo, fake UI label หรือข้อความที่สร้างขึ้น
ในภาพ เว้นแต่ผู้ใช้สั่งเฉพาะเจาะจง และห้ามใช้ cyberpunk, futuristic hologram,
fantasy technology, excessive neon, glowing monolith หรือภาพแบบ sci-fi
movie poster ทุก scene prompt ต้องเริ่มจากและ inherit base style นี้ แล้วเพิ่ม
เฉพาะ subject/action ของซีน ห้ามสร้าง visual direction ใหม่แยกต่อซีน ต้องรักษา
palette, lighting, realism, composition language และระดับรายละเอียดให้ต่อเนื่อง
ทั้งคลิป

กฎนี้ใช้แทน visual direction ของ Mamase เฉพาะเมื่อสร้าง Thai Java Zone เท่านั้น;
workflow ด้านการตรวจภาพ ความปลอดภัย และ package validation ที่ใช้ร่วมกันยังคง
มีผลตามเดิม

## โหมดสร้างรูปจากชื่อเรื่องอย่างเดียว

เมื่อผู้ใช้สั่ง `อ่าน start.md แล้วสร้างรูปเรื่อง "<ชื่อเรื่อง>"` หรือให้เพียง
ชื่อเรื่องพร้อมขอชุดภาพ ให้ถือว่าอนุมัติ **Autonomous Master Image
Production** แล้ว ผู้ใช้ไม่ต้องเขียน image prompt หรือรายละเอียดรายซีน

Agent ต้องทำเองจนเสร็จ: ทำความเข้าใจเรื่อง → วาง visual story/shot list →
เขียน prompt รายซีน → สร้าง master images → เปิดตรวจภาพจริงทุกไฟล์ → สร้าง
ใหม่เฉพาะภาพที่ตกเกณฑ์ → เก็บชุดที่ผ่านใน `assets/<topic_name>/` → รายงาน
รายชื่อไฟล์และผลตรวจ หากผู้ใช้ขอเฉพาะรูป ห้ามขยายงานไปสร้าง JSON หรือ ZIP
เอง

ห้ามถือว่ารูปผ่านเพียงเพราะ prompt หรือรายงานบอกว่าผ่าน ต้องเปิดดูทุกภาพจริง
งาน Mamase ให้เทียบกับ Parker/Tianwen-2 benchmark ส่วน Thai Java Zone ให้
เทียบกับ shared visual style bible ด้านบน ภาพไม่ตรงบท, ตัวละครดูแปะทับ,
มี watermark/logo, ข้อความผิด, คุณภาพหรือสไตล์ไม่ต่อเนื่อง, องค์ประกอบโล่ง
หรือไม่เล่าเรื่องของซีน ต้องสร้างใหม่ก่อนส่งงาน

## กฎสำคัญสำหรับการสร้างภาพ

### ภาษาภาพประจำช่อง — สิ่งที่คำว่า “เหมือนงานที่เราทำกัน” หมายถึง

ภาพประจำช่อง Mamase คือ **Premium Cinematic Documentary Key Art** หรือ
**Cinematic Editorial Concept Art**: ภาพสารคดีที่จัดองค์ประกอบเหมือนโปสเตอร์
ภาพยนตร์หรือปกหนังสือวิทยาศาสตร์ระดับพรีเมียม แต่ยังรักษาความน่าเชื่อถือของ
วัตถุ สถานที่ เหตุการณ์ และหลักวิทยาศาสตร์ ภาพไม่จำเป็นต้องดูเหมือนภาพถ่าย
ดิบจากกล้อง และไม่ใช่การนำภาพถ่ายหลายรูปมาต่อกันแบบ collage ราคาถูก

ทุกภาพต้องมี “เรื่องที่กำลังเกิดขึ้น” ไม่ใช่เพียง “สถานที่สวย ๆ” ให้แปลง
narration ของซีนเป็นความสัมพันธ์ที่มองเห็นได้ เช่น ใคร/อะไรเป็นตัวเอก,
กำลังทำอะไร, เจอกับแรงหรืออุปสรรคอะไร, ผลหรือความหมายคืออะไร ผู้ชมควรเดา
ใจความของซีนได้ก่อนอ่าน subtitle

องค์ประกอบที่ต้องเห็นในงาน Mamase:

- **Hero subject ใหญ่และชัด**: วัตถุหลักครองภาพและอ่านออกทันทีบนจอมือถือ
  ไม่ใช่ยาน ดวงดาว คน หรือสิ่งสำคัญขนาดเล็กจมหายอยู่ในฉากกว้าง
- **ความสัมพันธ์เชิงเรื่องราว**: แสดงเหตุและผล, การเผชิญหน้า, ระยะทาง,
  อันตราย, การปกป้อง, การค้นพบ หรือ before/after ในเฟรมเดียวเมื่อเหมาะสม
- **ความลึกสามชั้น**: foreground, midground และ background ต้องช่วยพาสายตา
  เข้าหาตัวเอก ไม่ใช่พื้นหลังแบน ๆ หรือท้องฟ้าดำโล่ง
- **แสงแบบภาพยนตร์**: มีทิศทางของแสงชัดเจน, rim light, reflected light,
  atmospheric glow, volumetric dust/ice/gas/particles และ contrast ที่ควบคุม
  ให้ทุกวัตถุรู้สึกอยู่ในโลกเดียวกัน
- **รายละเอียดพื้นผิว**: ผิวดาว, โลหะ, กระจก, น้ำแข็ง, เมฆ, ฝุ่น และเสื้อผ้า
  ต้องมี texture และ material response ไม่ใช่ผิวเรียบหรือรูปทรงลอย ๆ
- **สเกลและพลัง**: ใช้ขนาดเปรียบเทียบ มุมกล้อง เส้นนำสายตา และชั้นบรรยากาศ
  ทำให้ผู้ชมรู้สึกถึงความใหญ่ ความเร็ว ความร้อน ความลึก หรือระยะทาง
- **สีต่อเนื่องทั้งชุด**: เลือก color script ของเรื่อง เช่น deep navy/cyan
  ตัดกับ fiery orange/gold แล้วรักษา palette, contrast และ mood ให้รู้สึกว่า
  ทุกภาพมาจากสารคดีเรื่องเดียวกันตลอดทุกซีน
- **Active composition 70–80%**: พื้นที่ภาพส่วนใหญ่ต้องมีข้อมูลและพลังทาง
  สายตา เว้น lower-center สำหรับ subtitle อย่างตั้งใจ แต่ห้ามปล่อยพื้นที่ดำ
  หรือพื้นที่ว่างครึ่งภาพโดยอ้างว่าเป็น subtitle safe area

สิ่งที่ **ไม่ใช่** ภาษาภาพ Mamase และต้อง reject:

- ภาพถ่ายดาว ทางช้างเผือก ภูเขา หรือทะเลทรายทั่วไปที่สวยแต่ไม่เล่า
  narration ของซีน
- ภาพ stock, wallpaper หรือ b-roll ทั่วไปที่เปลี่ยนใช้กับเรื่องอื่นได้
  โดยแทบไม่ต้องแก้
- วัตถุเดี่ยวเล็ก ๆ วางกลาง starfield หรือพื้นหลังดำ
- collage ที่แสง มุมมอง ความคม และสไตล์ของแต่ละวัตถุไม่สัมพันธ์กัน
- ภาพ presenter ถูกตัดแปะบนฉากหลังโดยไม่มีแสง เงา สี และ depth ร่วมกัน
- infographic, presentation slide, textbook diagram, HUD, เส้นลูกศร, label,
  ตัวเลขอธิบาย หรือกราฟิกเรขาคณิตแบน ๆ เว้นแต่ผู้ใช้ขอโดยเฉพาะ
- ภาพความละเอียดต่ำ เบลอ แตก มี compression, banding, noise หรือรายละเอียด
  หลอมผิดธรรมชาติ รวมถึงมือ ใบหน้า ยาน และสถาปัตยกรรมผิดรูป
- รูปจากเว็บที่มีลายน้ำ เครดิตช่างภาพ โลโก้ หรือสิทธิ์ใช้งานไม่ชัดเจน

### Scene 01 — Permanent Standard (Premium Science Documentary Key Art)

Scene 01 ของ Mamase Reel ต้องทำหน้าที่พร้อมกัน 3 อย่าง:
1. หยุดการเลื่อนฟีดทันที (1–2 วินาทีแรก)
2. สื่อปริศนาหรือเรื่องราวหลักของคลิปภายในภาพเดียว
3. อ่านชื่อเรื่องและ Hook ได้ชัดเจนบนหน้าจอมือถือ

ห้ามสร้างเป็น infographic, presentation slide, generic space wallpaper หรือภาพวัตถุขนาดใหญ่แปะอยู่บนฉากหลังเด็ดขาด

- **Mandatory Visual Hierarchy**: Hook Mystery → Hero Subject → Topic + Thai Hook → Mamase Brand ทุกองค์ประกอบต้องช่วยเล่าเรื่องเดียวกัน ห้ามกระจายข้อความและ callout ไปทั่วภาพ
- **Hero Subject Rules**: เด่น มีสเกล แต่ต้องเห็นรูปทรงและบริบทครบ ห้ามขยายจนเหลือเพียงพื้นผิว/texture เต็มจอ และห้ามปล่อยให้ subject เล็กจนดูเหมือนวัตถุแปะบนพื้นหลัง ต้องสัมพันธ์โดยตรงกับ Hook สร้างความลึกด้วย foreground, midground, background มี directional light, rim light, atmosphere และ scale cues ร่วมกันอย่างกลมกลืน อย่าบังคับขนาดเป็นจำนวนพิกเซลหรือเปอร์เซ็นต์ตายตัว ให้เลือกขนาดตาม composition และ readability
- **Human + Dog Story Anchor**: รักษาตัวตนคู่หูเดิม แต่ห้ามใช้ท่านั่งบนก้อนหินหันหลังมองฟ้าเป็น template ถาวร ห้ามใช้ pose, camera angle, เสื้อผ้า หรือ location เดิมติดกันสองปก ต้องเลือก action, expression และ framing ตามเรื่องจริง โดยตรวจเทียบปกที่อนุมัติล่าสุดก่อนสร้าง
- **Typography & Branding (Deterministic Post-Composite)**: สร้าง raw artwork ที่ไม่มีข้อความ/โลโก้ก่อน ใช้โลโก้ header จริงเพียงหนึ่งชุด และมีข้อความเพียง Topic + Thai Hook ห้าม English filler, kicker, footer, badge, slogan, leader line, fact box, callout และโลโก้ซ้ำ ต้องส่ง protected zones แบบมีหมวดครบ `hero`, `celestial`, `characters` โดยแยกคนและหมาคนละกรอบ; ห้ามกันเฉพาะตัวละครแล้วปล่อยข้อความทับกล้อง ยาน ดาว หรือดาวเคราะห์ หากไม่มีพื้นที่ปลอดภัยให้จัด raw artwork ใหม่
- **Multi-Ratio (9:16 vs 1:1)**: ห้ามสร้าง Square 1:1 ด้วยการ crop กึ่งกลางจาก 9:16 หากทำให้องค์ประกอบเสียรูป ให้สร้าง 1:1 เฉพาะเมื่อร้องขอและออกแบบ layout แยก
- **Mandatory Workflow**: วาง Hook + layout ที่ไม่ซ้ำปกก่อน → สร้าง raw artwork ไร้ข้อความ → ตรวจ raw artworkและทำ protected-zone map → composite ด้วย `.agents/skills/mamase-reels-cover/scripts/generate_mamase_reels_cover.py` → ตรวจเต็มภาพและขนาดมือถือ → **ส่ง Scene 01 ให้ผู้ใช้อนุมัติและหยุดรอ** → หลังอนุมัติจึงเริ่มสร้างภาพซีนอื่น

### Scene 02 เป็นต้นไป — Visual storytelling

แต่ละซีนต้องเปลี่ยนแนวคิด narration ให้เป็นภาพเฉพาะซีน หากบทพูดถึงตำนาน
“เส้นทางของนก” ภาพต้องเห็นฝูงนกใช้แนวดาวเป็นเส้นทาง หากพูดถึง “ทางของคน
ขนฟาง” ต้องเห็นการเดินทางและร่องรอยฟางเชื่อมกับแถบดาวอย่างมีศิลปะ ไม่ใช่
เพียงทะเลทรายใต้ทางช้างเผือก หากพูดถึงเกราะกันความร้อน ต้องให้เกราะเป็น
hero subject พร้อมความต่างของความร้อนสองด้าน ไม่ใช่ภาพยานลอยอยู่ไกล ๆ

ใช้ภาพถ่ายดาราศาสตร์หรือภาพจริงได้เมื่อมันเป็นหลักฐานหรือวัตถุของเรื่องนั้น
โดยตรง แต่ต้อง crop/compose ให้มี hero subject ชัดและเหมาะกับเฟรม ห้ามใช้
ภาพถ่ายท้องฟ้าทั่วไปเป็น filler สำหรับ narration เชิงตำนาน กลไก หรือเหตุผล

### ความละเอียดและไฟล์ Master

- Reel/Shorts/TikTok ใช้สัดส่วน 9:16 ไฟล์พร้อม AutoClip ขั้นต่ำ
  `1080×1920` PNG
- Mamase Reel/Shorts/TikTok ใช้ความยาวรวมมาตรฐาน **45–55 วินาที** และปกติไม่เกิน 60 วินาที เว้นแต่
  ผู้ใช้ระบุความยาวอื่นเป็นรายคลิป
- ใช้อย่างน้อย **8 ซีนรวม Mamase outro บังคับ** เพิ่มเกิน 8 ได้เมื่อแต่ละซีน
  มีข้อเท็จจริง reveal คำอธิบาย หรืออารมณ์ใหม่ ห้ามเติมซีนเพื่อยืดเวลา
- Master แนะนำ `2160×3840` (vertical 4K) เมื่อระบบสร้างภาพรองรับโดยตรงและ
  ต้องการเผื่อ zoom/crop; AutoClip ยังสามารถย่อเป็น `1080×1920` ตอน render
- YouTube แนวนอนใช้ขั้นต่ำ `1920×1080`; Master แนะนำ `3840×2160` เมื่อสร้าง
  ได้โดยตรง
- 4K ไม่ใช่เงื่อนไขว่าภาพจะผ่าน งาน `1080×1920` ที่องค์ประกอบ แสง texture
  และความคมดี ย่อมดีกว่าภาพ 4K ที่โล่ง ทั่วไป หรือไม่ตรงบท
- ห้าม upscale ภาพเล็กแล้วเรียกว่า 4K หากต้นฉบับไม่มีรายละเอียดเพิ่ม ให้รายงาน
  native generation size และ delivery size ตามจริง
- ภาพในชุดเดียวกันต้องมีสัดส่วนและ delivery dimensions เท่ากันทั้งหมด

### Visual QA ที่ต้องทำจริง

หลังสร้างแต่ละภาพ Agent ต้องเปิดดูไฟล์จริงแบบเต็มภาพและแบบย่อเท่าจอมือถือ
แล้วตรวจ: ความตรงกับ narration, hero subject, story/action, depth, lighting,
texture, scale, subtitle safe area, continuity, anatomy/hardware, text accuracy,
watermark/logo และความคม ห้ามใช้เพียงชื่อไฟล์ prompt metadata หรือคำรายงาน
ของ generator เป็นหลักฐาน

ภาพที่ไม่ผ่านข้อใดข้อหนึ่งต้อง regenerate เฉพาะซีนและตรวจซ้ำก่อนรายงานว่า
เสร็จ หากยังไม่สามารถสร้างให้ถึงมาตรฐาน ให้รายงานตรง ๆ ว่าซีนใดยังไม่ผ่าน
ห้ามประกาศว่าภาพครบสมบูรณ์หรือส่งต่อให้ package โดยซ่อนข้อบกพร่อง

- สร้าง master images เองจากบทและ scene plan ที่อนุมัติแล้ว ไม่โยนให้ผู้ใช้
  เขียน image prompt ทีละซีน
- ภาพต้องตรงกับ narration ของซีน ไม่ใช้ภาพอวกาศทั่วไปเพื่อเติมจำนวน
- ใช้มาตรฐาน premium cinematic science documentary: subject เด่น,
  foreground/midground/background ชัด, มี scale, depth, atmosphere และแสง
  ที่มีทิศทาง
- ให้ active composition ครอบคลุมราว 70–80% ของภาพ และเว้นพื้นที่ซับด้านล่าง
  เพียงพอดี ห้ามปล่อยพื้นที่ดำโล่งเกินประมาณหนึ่งในสามโดยไม่มีเหตุผล
- Scene 1 เป็น Narrative Key Art: มี Mamase presenter คนเดิม, ชื่อหัวข้อ,
  short hook และภาพรวมที่เล่าเรื่องทั้งคลิปได้ตั้งแต่แรกเห็น
- เสื้อผ้าและสีหน้าพิธีกรปรับตามเนื้อหาได้ แต่ต้องรักษาใบหน้า แว่น ทรงผม และ
  identity ของ `mamase-presenter-v1`
- Scene 2 เป็นต้นไปไม่มี generated text, label, HUD, subtitle ฝังภาพ,
  agency logo หรือ watermark แต่ต้อง composite โลโก้ Mamase ของจริงตาม skill
  `mamase-reels` หลังสร้าง artwork ห้ามให้ image model วาดโลโก้เอง
- ตรวจภาพทุกซีนบนขนาดจอมือถือก่อนประกอบ ZIP แล้ว regenerate เฉพาะภาพที่
  ไม่ผ่าน โดยรักษาภาพที่ดีไว้
- เก็บ master assets ไว้ใต้ `assets/`; ห้ามใช้ `dist/` เป็น reference ถาวร
  เพราะ output อาจถูก cleanup

## กฎสำคัญสำหรับบทและ ZIP

- เสนอบทและ scene plan ทั้งหมดให้ผู้ใช้รีวิวก่อนสร้างภาพและ ZIP เว้นแต่ผู้ใช้
  อนุมัติให้ทำเองทั้งหมด หรือระบุว่าเป็น technical test package
- เขียนบทภาษาไทยให้เหมือนนักเล่าเรื่องวิทยาศาสตร์ที่เป็นกันเอง กระฉับกระเฉง
  ขี้เล่น และฟังชัด ไม่ใช่น้ำเสียงผู้ประกาศข่าว
- แยก `narration` สำหรับข้อความจริงออกจาก `tts_text` สำหรับแก้การออกเสียง
  ชื่อภาษาอังกฤษ ตัวเลข และศัพท์เฉพาะ
- ZIP root ต้องมี `script.json` และ `images/`; `audio/` เป็น optional
- ทุก asset path ใน JSON ต้องเป็น relative POSIX path ที่ปลอดภัย
- รักษาลำดับซีนจาก `script.json`
- ใส่ motion, transition และ Wan plan ให้พร้อมใช้ทั้ง FFmpeg Motion และ
  Wan 2.2 ตามกติกาใน Mamase skill
- ZIP เดียวต้องใช้ได้ทั้งสองโหมด: ทุกซีนมีภาพและ FFmpeg `motion`; ใส่ `wan`
  เฉพาะซีนที่ต้องการ AI motion เมื่อเลือก Wan ในหน้า Generate ระบบใช้ Wan
  เฉพาะซีนเหล่านั้นและใช้ FFmpeg กับซีนที่ไม่มี `wan`; หากเลือก FFmpeg ให้
  ทุกซีนใช้ FFmpeg และไม่สนใจ `wan` โดยไม่ต้องแก้ `script.json`
- ทุก Reel จบด้วยคำถามชวนคุยเฉพาะเรื่อง (Topic-Specific Discussion CTA)
  1 ประโยคสั้นๆ เพื่อชวนแลกเปลี่ยนความเห็น/คาดการณ์ตามประเด็นของเรื่องนั้น โดย
  ไม่มีเสียงพูดใดๆ ต่อท้าย CTA อีก
- ห้ามใช้ CTA ทั่วไป เช่น "อย่าลืมกดไลก์ กดติดตาม", "คอมเมนต์คุยกันหน่อยนะครับ",
  "ขอบคุณที่รับชม" หรือประโยคยาวแบบเดิม (ประโยค "ถ้าชอบเรื่องราวอวกาศ... กดไลก์ กดแชร์..." ยกเลิกการใช้งานแล้ว)
- ตรวจ JSON, image paths, dimensions และความสมบูรณ์ของ ZIP ก่อนส่งมอบ
- รายงานชื่อ ZIP, ตำแหน่งไฟล์, จำนวนซีน, รูปแบบภาพ และผลการตรวจสอบให้ผู้ใช้

## YouTube Podcast Generator

AutoClip รองรับการสร้าง YouTube Visual Podcast แนวนอน 16:9 จากภาพปก 1 ภาพและบทพูดยาวผ่านหน้า `/podcast`:

- **ความละเอียด**: 1920×1080 Full HD (16:9), 30 FPS, H.264 / AAC 48 kHz stereo
- **ระบบตัดแบ่งบท (Thai-Aware Chunking)**: ตัดแบ่งตามย่อหน้า ประโยค และขอบเขตคำภาษาไทย (PyThaiNLP) ไม่เกิน ~2,800 UTF-8 bytes ต่อท่อน
- **เสียงและสไตล์เริ่มต้น**: Google Gemini TTS เสียง `Iapetus` ความเร็ว `0.90` พร้อม prompt ที่เน้น connected phrasing, จังหวะสนทนาธรรมชาติ, การเชื่อมประโยคลื่นไหล และหยุดสั้นเฉพาะเครื่องหมายวรรคตอนหรือช่วงเปลี่ยนหัวข้อ หน้า Podcast บันทึก Voice, Speed และ Thai/English Style ปัจจุบันเป็นค่าเริ่มต้นของ browser ได้โดยไม่ต้องแก้โค้ด และคืนค่าระบบได้เสมอ
- **การประมวลผลเสียงขนาน**: สร้างภาษาไทยก่อน แล้วจึงเริ่มภาษาอังกฤษ โดยยิง Google TTS พร้อมกันสูงสุด 3 รายการ (`AUTOCLIP_PODCAST_CONCURRENCY=3`) เพื่อไม่ให้สองภาษาแย่ง quota กัน มี retry สูงสุด 5 รอบโดยเว้นอย่างน้อย 5 วินาที, รองรับ `Retry-After` และ manifest-based cache (`podcast_chunks/`) ปุ่ม Retry งาน Podcast ต้องใช้เฉพาะ chunk ที่ขาดจาก cache เดิม ไม่สร้างเสียงส่วนที่สำเร็จแล้วใหม่
- **การเคลื่อนไหวและดนตรีประกอบ**: เคลื่อนไหวภาพปกด้วย 6-stage gentle breathing motion cycle ต่อเนื่อง พร้อมระบบ Sidechain Audio Ducking ลดเสียง BGM อัตโนมัติขณะมีเสียงบรรยาย
- **English alternate WAV**: เมื่อมีบทอังกฤษ ไฟล์ `podcast-en.wav` ต้องผสม BGM เพลงเดียวกัน ระดับเสียงเดียวกัน และ Sidechain Ducking ชุดเดียวกับวิดีโอไทย เพื่ออัปโหลดเป็นภาษาเพิ่มเติมบน YouTube ได้ทันที โดยเก็บ narration ดิบไว้สำหรับ retry
- **BGM เริ่มต้น**: ใช้ `assets/sounds/mamase-podcast-bg.mp3` เป็นเพลง Podcast ค่าเริ่มต้น ส่วน `space.mp3` เดิมยังเก็บไว้ให้เลือก งานเก่ารักษาเพลงที่บันทึกไว้ใน job settings เดิม
- **การแสดงผล**: เชื่อมต่อเข้ากับระบบ Persistence, History (`/history`) และ Preview (`/jobs/{id}/preview`) โดยตรง
- **ความเข้ากันได้**: แยกการทำงานเป็นอิสระ ไม่กระทบค่าเริ่มต้นหรือพฤติกรรมของหน้าสร้างวิดีโอเดิม (Reel / Shorts) และ ZIP contract

## Quick Reel ("หลายภาพ • เสียงเดียว • พร้อมโพสต์")

AutoClip รองรับวิดีโอแนวตั้ง 9:16 จากภาพเรียงลำดับ 1–20 รูป และบทพูดหนึ่งชุดผ่านหน้า `/quick-reel` โดยงานภาพเดียวเดิมยังใช้ได้เหมือนเดิม:

- **ความละเอียด**: 1080×1920 Vertical Full HD (9:16), 30 FPS, H.264 / AAC
- **Image Fit Modes**:
  - `Cover` (ค่าเริ่มต้น): Center crop พอดีจอ 9:16 โดยไม่บิดเบี้ยว
  - `Contain`: เก็บภาพครบทั้งสัดส่วน พร้อมพื้นหลังสีมืด (#12141a)
- **เสียงและสไตล์**: Google Gemini TTS เสียง `Iapetus` ความเร็ว `1.10` เป็นค่าเริ่มต้น พร้อมสไตล์เสียงธรรมชาติ คมชัด มีพลัง ไหลลื่น
- **Voice Preview & Saved Style**: หน้า Quick Reel ต้องแสดง Style Prompt ให้แก้ไขได้ มีปุ่มฟังตัวอย่างด้วย Voice/Speed/Style ปัจจุบัน และบันทึกหรือคืนค่าเริ่มต้นเฉพาะ Quick Reel ได้ทันที
- **การเคลื่อนไหว**: `Static` (ภาพนิ่ง คมชัดเต็มจอ เป็นค่าเริ่มต้น) หรือ `Slow Zoom` (ซูมเข้าช้าๆ นุ่มนวล)
- **ลำดับและเวลา**: รักษาลำดับ Browse/Drop และรองรับลากการ์ดจัดใหม่ กระจายเวลาภาพเท่ากันตาม duration เสียงจริง พร้อม Crossfade ภาพ 0.4 วินาทีโดยชดเชยเวลา overlap ให้คลิปจบตรงเสียง
- **Audio Integrity**: สร้าง narration เพียงครั้งเดียวและห้าม split, crossfade หรือตัดเสียงตามรอยต่อภาพ
- **TTS JSON Input**: รองรับทั้ง `"tts": "บทพูด"` และ `"tts": ["ช่วงแรก", "ช่วงถัดไป"]` โดย `tts[0]` เป็นเสียงของภาพที่ 1, `tts[1]` เป็นเสียงของภาพที่ 2 ตามลำดับ จำนวนข้อความต้องเท่าจำนวนภาพ และแต่ละภาพยึด duration ของเสียงคู่กัน
- **Hook Text Overlay (ตัวเลือก)**: พาดหัวตัวหนังสือใหญ่ชัดเจนบนภาพ (Top, Center, Bottom) ด้วยฟอนต์ Kanit-Bold สีขาวขอบดำหนา ไม่ถูกเสียงพูดอ่าน
- **Subtitles**: เปิดใช้งานเป็นค่าเริ่มต้น วางกึ่งกลางล่างอ่านสบายตา
- **BGM**: ปิดเป็นค่าเริ่มต้น (เสียงบรรยายเพียวๆ) หากเปิดจะใช้เพลงบรรยากาศคลอเบาๆ ระดับเสียง 0.10 พร้อมรองรับการอัปโหลดเพลงเอง
- **History & Routing**: มีหน้าประวัติแยก `/quick-reel-history` และแท็บตัวกรองใน `/history` (project_type=`quick-reel`)
- **ความเข้ากันได้**: แยกเป็นอิสระ ไม่กระทบ Generate Reels, Podcast, หรือดวง 12 ราศี

## ความปลอดภัยและ repository

- ห้ามแสดง คัดลอก commit หรือใส่ API key, `.env`, cloud credential,
  service-account key หรือ SSH private key ลงใน ZIP
- รักษาการแก้ไขเดิมของผู้ใช้และ agent อื่น ห้ามลบ reset หรือเขียนทับงานที่
  ไม่เกี่ยวข้อง
- ก่อน commit ให้ตรวจว่าไม่มี secret หรือไฟล์ขนาดใหญ่ที่ไม่ควรอยู่ใน Git
- หลังแก้โค้ด ให้รันการทดสอบที่เกี่ยวข้อง และ restart native AutoClip service
  เมื่อจำเป็น

## คำสั่งสั้นสำหรับเริ่ม session

ใช้ข้อความนี้ได้ทุกครั้ง:

> อ่าน `/Users/zengcode/projects/autoclip/start.md` ทั้งหมดก่อนเริ่มงาน
> แล้วปฏิบัติตามไฟล์ที่อ้างอิงอยู่ภายใน ถือเป็นข้อกำหนดของ session นี้

สำหรับสร้างภาพ พิมพ์สั้น ๆ ได้ว่า:

> อ่าน start.md แล้วสร้างรูปเรื่อง "<ชื่อเรื่อง>"

สำหรับให้ทำคลิปครบจนได้ ZIP โดยลดจำนวนการสร้างภาพ พิมพ์ว่า:

> อ่าน start.md แล้วทำ AutoClip Reel เรื่อง "<ชื่อเรื่อง>" โหมดประหยัดเครดิต

คำสั่งสั้นนี้ถือว่า Agent ต้องใช้ Visual Production Contract, Visual Quality
Baseline, Mamase branding และกติกา ZIP ทั้งหมดจากไฟล์นี้โดยอัตโนมัติ ผู้ใช้
ไม่จำเป็นต้องส่ง image prompt รายซีนซ้ำอีก
