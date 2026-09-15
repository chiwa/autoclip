# Asset Manifest: Mamase "LZ Dark Matter Hint" Reel
**Package ID**: `mamase-lz-dark-matter-hint-reel-v1`  
**Topic**: เราอาจเพิ่งเห็นสสารมืดเป็นครั้งแรกหรือไม่? (LUX-ZEPLIN High-Energy Anomalous Recoil Hint)  
**Target Platform**: TikTok / Reels / YouTube Shorts (9:16 Vertical, 1080x1920)  
**Estimated Duration**: ~48–52 seconds (10 scenes)  
**Distribution ZIP**: `dist/mamase-lz-dark-matter-hint-reel-v1.zip`  
**Durable Assets**: `assets/lz_dark_matter_hint_reel/`  

---

## 1. Package Verification Status
- **PackageService Validation**: Passed (10/10 scenes validated, script structure, transitions, motions, image paths, metadata valid).
- **Archive Integrity (`unzip -t`)**: Passed with zero errors.
- **Presenter Anchor**: Canonical Mamase presenter cutout on Scene 01 (`mamase-presenter-v1.png`).
- **Outro Anchor**: Canonical Mamase outro slate on Scene 10 (`seed: 98`, `frames: 81`, `lip_sync: false`).
- **Typography & Formatting**: Clean Thai typography on Scene 01 using system Sukhumvit Set Bold; Scenes 02–09 have **zero in-image text, zero flat 2D vector diagrams, zero UI chrome**, preserving pure cinematic immersion for burned subtitles.

---

## 2. Complete Scene Breakdown & Asset Details

| Scene # | ID | Image Filename | Resolution | File Size | Motion | Transition | Audio / Narration Summary |
|---|---|---|---|---|---|---|---|
| **01** | `scene-01-hook` | `scene-01-hook.png` | 1080x1920 | 1.92 MB | `slow_zoom_in` | `fade` | **Hook**: เราอาจเพิ่งเห็นสิ่งที่มองไม่เห็น แต่คิดเป็น 85% ของสสารในจักรวาลหรือเปล่า? (Presenter + 3D COSMOS Dark Matter map) |
| **02** | `scene-02-invisible-matter` | `scene-02-invisible-matter.png` | 1080x1920 | 2.50 MB | `slow_zoom_out` | `fade` | **Scientific Context**: สสารมืดไม่ปล่อย/ดูดกลืนแสง แต่ครองมวล 85% ของสสารทั้งหมด (NASA Chandra/Hubble Bullet Cluster) |
| **03** | `scene-03-underground-shield` | `scene-03-underground-shield.png` | 1080x1920 | 3.39 MB | `documentary_pan` | `fade` | **Underground Shielding**: ลึกเกือบ 1 ไมล์ใต้ดิน เพื่อให้ชั้นหินหนากั้นรังสีคอสมิก (Towering mountain rock massif) |
| **04** | `scene-04-lz-detector` | `scene-04-lz-detector.png` | 1080x1920 | 2.53 MB | `cinematic_push_in` | `fade` | **Instrument**: แนะนำ LUX-ZEPLIN (LZ) เครื่องตรวจจับที่เงียบที่สุดในโลก (DOE/LBNL LZ outer detector PMT interior) |
| **05** | `scene-05-xenon-collision-mechanism` | `scene-05-xenon-collision-mechanism.png` | 1080x1920 | 1.54 MB | `slow_zoom_in` | `fade` | **Mechanism**: ซีนอนเหลวบริสุทธิ์สูง ปลดปล่อยแสงกะพริบและอิเล็กตรอนเมื่อถูกชน (Subatomic scintillation flash & electron drift) |
| **06** | `scene-06-unexplained-signal` | `scene-06-unexplained-signal.png` | 1080x1920 | 1.19 MB | `cinematic_push_in` | `fade` | **The Anomaly**: ตรวจพบเหตุการณ์พลังงานสูงผิดปกติ 1 ครั้ง ที่กระบวนการพื้นหลังอธิบายไม่ได้ (3D Particle Detector collision event display) |
| **07** | `scene-07-wimp-candidate` | `scene-07-wimp-candidate.png` | 1080x1920 | 3.23 MB | `gentle_float` | `fade` | **Candidate**: เข้ากันได้กับอนุภาค WIMP ที่มีมวลมากกว่าโปรตอนถึง 200 เท่า (Cosmic web filaments & mass node contrast) |
| **08** | `scene-08-not-a-discovery-yet` | `scene-08-not-a-discovery-yet.png` | 1080x1920 | 2.76 MB | `documentary_pan` | `fade` | **Scientific Caution**: สถิติ 2.6 ซิกมา ยังไม่ถึงเกณฑ์ 5 ซิกมา ยังไม่เรียกว่าค้นพบ (Underground physics control center) |
| **09** | `scene-09-the-ongoing-quest` | `scene-09-the-ongoing-quest.png` | 1080x1920 | 3.05 MB | `slow_zoom_in` | `none` | **Forward Look**: เบาะแสแรกอันน่าตื่นเต้นที่พาเราเข้าใกล้การไขปริศนาสสารมืด (Actual LZ cryostat & water shield tank at SURF) |
| **10** | `scene-10-mamase-outro` | `scene-10-mamase-outro.png` | 1080x1920 | 2.01 MB | `slow_zoom_in` | `none` | **Channel Call-to-Action**: กดติดตาม Mamase เพื่อร่วมสำรวจความลับของจักรวาลไปด้วยกัน (Canonical outro card) |

---

## 3. Scientific Fact-Checking & Phonetic Rigor
- **Matter vs Energy**: Accurately clarifies that dark matter constitutes ~85% of *matter* in the universe (not 85% of total cosmic energy).
- **Discovery Caution**: Strictly uses "เบาะแสแรก" (first hint) and emphasizes 2.6 sigma (~0.5% fluctuation probability) vs the required 5-sigma discovery gold standard.
- **Xenon Interaction**: Accurately explains liquid xenon scintillation (S1 light flash) and ionization electron drift (S2).
- **WIMP Hypothesis**: Specifies WIMP mass threshold $\ge 200\text{ GeV}/c^2$ (>200x proton mass).
- **Phonetic TTS Overrides**:
  - `LUX-ZEPLIN` -> `ลักซ์ เซพพลิน`
  - `LZ` -> `แอลแซด`
  - `WIMP` -> `วิมป์`

---

## 4. Render Engine Compatibility
- **FFmpeg 2D Fallback Engine**: Fully configured with camera motions (`slow_zoom_in`, `slow_zoom_out`, `cinematic_push_in`, `documentary_pan`, `gentle_float`) and smooth cross-fades.
- **Wan 2.2 Generative I2V Engine**: All 10 scenes include high-precision generative camera & physical motion prompts (`wan22_prompt` with negative prompts) and scene-level rendering settings:
  - Scene 01: Host speaking with subtle head movement, cosmic projection shimmering.
  - Scenes 02–09: Slow camera floats, particle drifts, glowing detector optics, authentic scientific documentary pacing.
  - Scene 10: Canonical static freeze (`seed: 98`, `frames: 81`, `lip_sync: false`).
