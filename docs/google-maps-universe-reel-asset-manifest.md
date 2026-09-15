# Google Maps ของจักรวาล (แผนที่ 4 พันล้านวัตถุ) — Asset & Production Manifest

- **Project ID**: `mamase-google-maps-universe-reel-v1`
- **Topic**: มนุษย์เพิ่งสร้างแผนที่จักรวาลที่ใหญ่ที่สุดเท่าที่เคยมีมา (4 พันล้านวัตถุ / Dark Energy / Cosmic Web)
- **Format**: Vertical 9:16 (1080×1920 PNG 30 FPS)
- **Package Path**: `dist/mamase-google-maps-universe-reel-v1.zip`
- **Durable Assets**: `assets/google-maps-universe-reel/`
- **TTS Provider**: Google Gemini (`Fenrir`, speed 1.0, phonetic `tts_text` included for all 9 scenes)

---

## 🎬 Shot List & Master Visual QA

| Scene | ID | Visual Description | Dimensions | Motion Mode |
|---|---|---|---|---|
| **01** | `scene-01-hook` | **Narrative Key Art**: Mamase presenter (grounded bottom-right), Cosmic Web map, Chonburi Gold Foil typography with motion safe headroom (`y >= 220px`). | 1080×1920 PNG | `cinematic_push_in` + Wan 2.2 |
| **02** | `scene-02-scale-4-billion` | **3D Cosmic Survey**: Point cloud mapping 4 billion galaxies, stars, and quasars across the observable universe. | 1080×1920 PNG | `slow_zoom_in` |
| **03** | `scene-03-cosmic-web` | **Cosmic Web Filaments**: Intricate filaments of dark matter and gas connecting galaxy clusters like a giant neural web. | 1080×1920 PNG | `documentary_pan` |
| **04** | `scene-04-empty-voids` | **Cosmic Voids & Laser Guide**: VLT telescope firing laser into deep space void framed by the glowing Milky Way. | 1080×1920 PNG | `cinematic_pull_out` |
| **05** | `scene-05-dark-energy` | **Dark Energy Geometry**: Space observatory mapping expansion cones and geometric acceleration of the universe. | 1080×1920 PNG | `cinematic_push_in` |
| **06** | `scene-06-cosmic-time-machine` | **Ancient Early Galaxies**: JWST deep field showing ancient infant spiral galaxies and redshifted cosmic dawn. | 1080×1920 PNG | `slow_zoom_in` |
| **07** | `scene-07-future-physics` | **High-Tech Survey Detector**: 300-megapixel mosaic detector array capturing incoming light rays from distant spiral galaxies. | 1080×1920 PNG | `documentary_pan` |
| **08** | `scene-08-human-perspective` | **Human & Cosmos**: Solitary human silhouette standing in a desert canyon gazing at the towering Milky Way horizon. | 1080×1920 PNG | `cinematic_pull_out` |
| **09** | `scene-09-mamase-outro` | **Canonical Mamase Outro**: Glowing cyan planet orbiting in dark navy space, peaceful and contemplative. | 1080×1920 PNG | `slow_zoom_in` + Wan 2.2 |

---

## 📦 Package Archive Verification
```text
mamase-google-maps-universe-reel-v1.zip
├── script.json (All 9 scenes with Thai TTS & Phonetic guidance)
├── video-metadata.json (Optimized title, SEO description, hashtags)
└── images/
    ├── scene-01-hook.png
    ├── scene-02-scale-4-billion.png
    ├── scene-03-cosmic-web.png
    ├── scene-04-empty-voids.png
    ├── scene-05-dark-energy.png
    ├── scene-06-cosmic-time-machine.png
    ├── scene-07-future-physics.png
    ├── scene-08-human-perspective.png
    └── scene-09-mamase-outro.png
```
All files passed integrity verification (`unzip -t` and Python Schema Validator).
