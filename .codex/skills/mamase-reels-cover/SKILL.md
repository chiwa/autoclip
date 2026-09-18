---
name: mamase-reels-cover
description: Create Mamase vertical Reels Master Covers (Scene 01 / Key Art) following the permanent ISS and Voyager 1 benchmark standards.
---

# Mamase Reels Master Cover Skill

This skill governs the production of **Scene 01 (Reel Master Cover / Key Art)** for Mamase (จักรวาลของใจ) vertical video packages (`1080x1920` 9:16 vertical, and optional separate `1080x1080` 1:1 square master).

---

## 0. Topic-Only Autonomous Contract

The user may provide only a topic, working title, or one-sentence idea. That is sufficient input.

- Do not ask the user to write an image prompt, choose a composition, place subjects, or define typography.
- Infer the strongest truthful hook, visual mystery, hero subject, contextual action, camera angle, lighting, wardrobe, protected zones, and mobile-safe layout.
- Verify current or uncertain facts from primary or authoritative sources before fixing the visual premise.
- Produce one Scene 01 candidate, inspect it, composite it, and present it for approval. Scene 01 approval is the only normal user decision gate.
- Read only the named permanent references and the most recent approved cover needed to avoid repetition. When inspecting past covers for style reference, consult the Reusable Asset Catalog following `/Users/zengcode/projects/autoclip/docs/asset-catalog.md`. Past Scene 01 covers are strictly `reuse_as_reference`; never reuse an old Scene 01 directly for a new topic.
- Do not create comparison thumbnails, contact sheets, multiple seeds, cutouts, use `rembg`, clone elements, or inpaint unless the user explicitly requests alternatives or repair.
- If native image generation fails, report it. Never silently substitute a pasted collage or lower-quality fallback.

---

## 1. Permanent Scene 01 Standard

Scene 01 is a **Premium Cinematic Science Documentary Key Art** that simultaneously fulfills 3 non-negotiable functions:

1. **Stops scrolling immediately (Thumb-stopping within 1–2 sec)**
2. **Visually communicates the core mystery, contradiction, or stakes of the video in a single frame**
3. **Presents readable Topic title and Thai Hook clearly on a phone screen**

**CRITICAL PROHIBITION**:
Never generate Scene 01 as an infographic, presentation slide, generic space wallpaper, or an isolated large object pasted flatly on a background.

---

## 2. Mandatory Visual Hierarchy

A viewer on mobile must perceive elements in this exact natural order:

$$\text{Hook Mystery} \longrightarrow \text{Hero Subject} \longrightarrow \text{Topic + Thai Hook} \longrightarrow \text{Mamase Brand}$$

Every compositional element must lead the viewer's eye into the same core story. Never scatter text, badges, or callouts erratically across the canvas.

---

## 3. Hero Subject Rules

- **Recognizable Form & Context**: The hero subject (spacecraft, planet, star, telescope, anomaly) must be prominent and convey immense physical scale, but **must retain its complete shape, silhouette, and spatial context**.
- **No Over-Zooming**: Never zoom in so close that the subject becomes just an ambiguous texture, unidentifiable surface, or cropped curve filling the screen.
- **No Pasted Cutouts**: Never shrink the hero subject into a tiny sticker or circle floating on a generic background.
- **Hook Direct Correlation**: The subject must directly embody the hook premise (e.g. ISS in continuous free fall above Earth's horizon, Voyager 1 transmitting across the cosmos).
- **Depth & Dimension**: Compose with clear **foreground, midground, and background** to create tangible physical depth.
- **Lighting Coherence**: Use strong directional light, crisp rim lighting, atmospheric glow, and scale cues. The human, dog, environment, and hero subject **must share the exact same light direction, shadow angle, and color temperature**, looking indisputably part of the same physical world.
- **Organic Sizing**: Do not enforce arbitrary pixel diameters or fixed percentages (e.g. "must be 65%"). Size the hero subject organically according to composition balance, storytelling clarity, and mobile readability.

---

## 4. Human + Dog Story Anchor (Recurring Identity, Not a Fixed Pose)

- Include the same recognizable Mamase male explorer and dog unless the user explicitly requests a cover without them.
- **Never default to the pair sitting on a rock and looking upward.** Do not reuse the same pose, camera angle, wardrobe, or location in two consecutive covers.
- Their placement is contextual: they may stand, walk, work, react, observe through glass, inspect equipment, or appear in a close/medium/wide shot according to the hook.
- Front, profile, 3/4, and rear views are all allowed. Choose the angle that tells this story best; rear view is not the default.
- Their expression and body language must react to the specific mystery. They are story participants, not a pasted brand stamp.
- Clothing must be youthful and professional, adapted to the environment, and free of NASA or third-party trademarks unless factually required and licensed.
- Show anatomically coherent bodies and grounded contact shadows. Match the hero's light direction, color temperature, focus depth, and perspective.
- Before generation, compare against the most recent approved Scene 01. If the composition reads as the same template, redesign it.

---

## 5. Typography & Branding Standard

Typography and branding are composited **deterministically onto clean, textless raw artwork** after image generation:

The permanent master visual reference is `assets/branding/mamase/reference/mamase-reels-editorial-poster-master.png`. Open and inspect it before designing every Scene 01. It is the default standard, not an optional mode.

1. **Mamase Reel Branding (Top)**:
   - Use exactly one authentic brand header `assets/branding/mamase/mamase_podcast_header.png`.
   - Use "Mamase" or "Mamase REELS" branding only. **Strictly NO "MAMASE PODCAST" text**, no audio-track callouts, and no duplicate wordmarks.
   - **Strictly NO bilingual badges** (`"AVAILABLE IN THAI & ENGLISH"`), language flags, or bilingual labels on Reel assets.
   - Do not also add the round logo, a duplicate wordmark, a fake patch, or generated branding.
   - **Never let an AI image model generate, draw, or invent logos.**
2. **Topic Title**:
   - Elegant editorial display typography sized to the composition. It must be prominent without becoming an opaque block or covering the scientific tableau.
   - Use restrained warm white, icy cyan, and warm gold accents like the permanent master reference.
3. **Thai Hook (2 Lines)**:
   - Clean, high-impact headline (`Kanit-Bold.ttf`, 80–83pt).
   - First line in warm white (`#F6F7F4`), second key question/phrase highlighted in cyan (`#78D7FF` or `#73DCFF`).
4. **Editorial Information Layer**:
   - Default Scene 01 uses the rich but ordered magazine-poster hierarchy of the permanent master reference.
   - A short contextual line, one restrained micro-tagline, and up to three small scientific labels are allowed when they help the single-frame story.
   - Every label must identify a visible subject and be factually correct. All text is composited deterministically; the image model never renders it.
   - Never add decorative filler, invented claims, random badges, dense fact boxes, or leader lines without a real labelled subject.
   - A restrained footer is allowed only for truthful deliverable information. Strictly never show language flags or bilingual badges ("AVAILABLE IN THAI & ENGLISH") on Reel assets.
5. **Protected-Zone Contract**:
   - Before compositing, record pixel rectangles for every hero subject, face/body, dog, spacecraft, planet/star silhouette, and critical story detail.
   - Pass labelled rectangles using `--protect-hero`, `--protect-celestial`, and two or more `--protect-character` arguments (one each for explorer and dog). Unlabelled `--protected-zone` input is forbidden.
   - A telescope or spacecraft is a hero subject; visible suns, planets, moons, or scientifically important star systems are celestial subjects. Never protect only the characters.
   - Text and branding must not overlap any protected rectangle or the lower subtitle-safe band.
   - If the compositor reports no safe region, recompose the raw artwork. Never shrink text into illegibility or cover the hero.

### Permanent Premium Editorial Poster Mode

Every Mamase Reel Scene 01 uses this visual language by default:

- Build a clear magazine-cover hierarchy: one authentic Mamase header, scientifically meaningful celestial tableau, elegant Topic title, concise Thai Hook, and a cinematic human-and-dog story layer.
- Secondary scientific labels are allowed only when they identify visible subjects and are factually correct. Composite them deterministically; never ask the image model to spell them.
- Small editorial copy may be used when it strengthens the story and the primary hierarchy remains readable on mobile.
- Never claim Thai/English audio availability, add flags, or promise a feature unless that deliverable actually contains those tracks.
- Match the permanent master reference for hierarchy, typography restraint, layered storytelling, premium finish, depth, and color—not as a literal fixed template. Change the human/dog action, location, props, and setting for every topic.
- Protected-zone rules remain blocking. Rich editorial design never permits text to cover a star, planet, spacecraft, telescope, face, or dog.

---

## 6. Color & Cinematic Lighting Palette

- **Base Colors**: Deep navy / cosmic black, icy cyan/white.
- **Accents**: Warm gold, solar amber, atmospheric orange.
- **Contrast**: Deep documentary contrast without crushed blacks or blown-out highlights.
- **Anti-Pattern**: Never apply a muddy brown or orange wash over the entire image unless physically dictated by the environment.

---

## 7. Multi-Ratio Composition (9:16 vs 1:1)

Vertical 9:16 and Square 1:1 must have distinct compositions:

- **Never create 1:1 by blind center-cropping a 9:16 master** if doing so clips logos, cuts off topic/hook typography, decapitates the explorer/dog, or reduces the hero subject to an unreadable texture.
- When a 1:1 square asset is requested, design a dedicated square crop or standalone 1:1 composition and visually verify it independently.

---

## 8. Mandatory 12-Point QA Gate (Blocking)

Before approving Scene 01, visually inspect the actual image on a mobile-sized screen against all 12 checks:

1. [ ] **Hook comprehension**: The mystery is understood from the image within 1–2 seconds.
2. [ ] **Typography legibility**: Topic and Thai hook are crisp and instantly readable on a phone.
3. [ ] **Hero subject integrity**: Subject has complete shape, clear context, and is not over-zoomed or a tiny speck.
4. [ ] **Story anchor**: Explorer and dog are intact, properly proportioned, and actively engaged.
5. [ ] **Authentic branding**: Exactly one authentic Mamase header is sharp; no duplicate logo or fake patch exists.
6. [ ] **No fake AI text**: Absolutely zero generated Thai lettering, gibberish labels, or halluncinated logos.
7. [ ] **Safe margins**: Text stays within safe zones and out of the subtitle band.
8. [ ] **Zero unmotivated dead space**: Composition feels rich, balanced, and intentional.
9. [ ] **Cinematic documentary feel**: Looks like premium key art, not an infographic card or slide.
10. [ ] **Scientific accuracy**: Astrophysical and engineering details are defensible.
11. [ ] **9:16 approved first**: Vertical master must pass before generating any subsequent scenes.
12. [ ] **Independent 1:1 review**: If 1:1 square is requested, verify its composition separately.

Also reject immediately if typography covers a planet, star, spacecraft, face, dog, or other focal silhouette; if the cover repeats the previous human-and-dog pose; or if any English filler, callout, badge, footer, or duplicate branding appears.

**If any item fails, redesign Scene 01. Do not proceed to subsequent scenes or ZIP packaging.**

---

## 9. Permanent Generation Workflow

For every Mamase Reel:

1. **Step 1: Concept & Hook**: Define the thumb-stopping hook and visual story premise.
2. **Step 2: Composition Plan**: Choose a story-specific camera, action, location, and text region. Compare it with the previous approved cover and reject template repetition.
3. **Step 3: Generate Clean Raw Artwork**: Create textless, logoless base artwork in 9:16 (`1080x1920`) with intentional negative space for text. Never ask the image model to render typography or logos.
4. **Step 4: Inspect + Map Protected Zones**: Verify anatomy, scientific form, scale, lighting, and depth. Record protected rectangles for every story subject.
5. **Step 5: Deterministic Composition**: Run `.agents/skills/mamase-reels-cover/scripts/generate_mamase_reels_cover.py` with the protected zones. Its JSON report must show `brand_asset_count: 1`, only `topic_title` and `thai_hook` text layers, and no forbidden layers.
6. **Step 6: Visual QA Inspection**: Open the rendered `scene-01-hook.png` at full size and mobile size and audit against the 12-Point QA Gate.
7. **Step 7: User Approval**: Present Scene 01 to the user for explicit approval.
8. **Step 8: Await Approval**: Stop and wait; do not generate scene 02+ or ZIP until approved.
9. **Step 9: Subsequent Scenes**: Generate remaining scenes only after Scene 01 approval.
10. **Step 10: Square Cover (If Requested)**: Generate a dedicated 1:1 layout only when requested; never center-crop the vertical cover.
