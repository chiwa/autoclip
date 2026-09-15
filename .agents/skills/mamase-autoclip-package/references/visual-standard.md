# Visual Standard: Real Science + Cinematic Documentary

This reference details the visual execution requirements for all **Mamase — จักรวาลของใจ** short-form videos, enforcing the standards established in `start.md`, `agent.md`, `assets/parker_solar_probe_reel/visual-reference.md`, and `assets/tianwen-2-quasi-satellite-reel/images/`.

---

## 1. Aesthetic Identity: Cinematic Science, Not Infographics

Mamase is an international-grade science documentary channel. Every frame must look like high-budget documentary cinematography.

### Preferred Sources
- Authentic astronomy and space science photography from:
  - **NASA / JPL-Caltech**
  - **European Space Agency (ESA)**
  - **James Webb Space Telescope (JWST)**
  - **Hubble Space Telescope (HST)**
  - **European Southern Observatory (ESO)**
  - **Caltech / IPAC**

### Prohibited Visual Styles
- ❌ **No 2D Flat Vector Art**: Programmatically drawn basic lines, ellipses, or simplistic geometric diagrams.
- ❌ **No Infographic UI Cards**: Semi-opaque text boxes, numbered cards, callout arrows, or telemetry overlays.
- ❌ **No Sparse Starfield Slides**: A tiny planet or isolated spacecraft floating in a sea of black space with sparse random dots.
- ❌ **No Cartoonish AI Art**: Oversaturated, plastic-looking fantasy space art with unphysical glowing halos or distorted geometries.

---

## 2. Master Composition Rules (70–80% Active Frame)

1. **Full Vertical Dynamic Energy**:
   - Visual interest must run vertically through the frame.
   - Establish depth through **Foreground, Midground, and Background layers**.
   - Example: Foreground high-tech probe details + Midground textured planetary surface/horizon + Background stellar nursery/solar corona.
2. **Directional & Physically Credible Light**:
   - Lighting must have a clear physical origin (e.g. bright directional solar glare casting sharp rim-light on one edge and deep, realistic shadows on the opposing side).
   - Use volumetric scattering, micro-dust particles, and solar wind glints to convey environmental scale.
3. **Subtitle Safe Area**:
   - Bottom area (**y: 1380–1920, x: 160–920**) must remain clean, calm, and dark for AutoClip Thai subtitles.
   - Blend the scene into this area using a natural cosmic dark gradient rather than an artificial black box.

---

## 3. Scene 01: Narrative Key Art

Scene 01 acts as the visual movie poster and thumbnail for the video:

- **Integrated Character**:
  - The canonical presenter (`mamase-presenter-v1`: Thai adult male, messy black hair, rectangular glasses, navy blazer over black shirt, explanatory pointing gesture) stands on the right side grounded at the bottom.
  - Apply directional rim-lighting matching the scene's primary light source (e.g., golden solar light or cyan planetary bounce) and soft ground shadows.
  - The character must feel physically present inside the scene's world, never cut-and-pasted.
- **Logo Placement (Top-Center Crown Rule)**:
  - Place `assets/branding/mamase/logo.png` **Top-Center Crown** above the title (`x = 475`, `y = 60–65`, diameter ~130–140px, with soft Gaussian drop shadow).
  - This establishes immediate channel identity at thumbnail/mobile view without colliding with side margins or video progress UI.
- **Thai Typography & Motion-Safe Execution (Chonburi Serif & Gold Foil)**:
  - **Font**: **Chonburi (ชลบุรี)** — High-contrast Thai serif display font for luxurious cosmic documentary aesthetics.
  - **Title (Centered Top)**: Rendered in **Chonburi (~120–130pt)** with multi-stage metallic gold foil gradient (`#FFF8D6` -> `#FFD700` -> `#8B4500`), sparkling micro-grain texture, 3D bevel top highlight, dark chocolate/amber separation stroke (8–10px), horizontal lens flare bar underneath, and warm radial orange glow.
  - **Hook (Centered Below Title)**: Rendered in **Chonburi (~60–65pt)** in warm creamy white (`#FFFAF0`) with black stroke and Gaussian drop shadow.
  - **Motion-Safe Margins (Critical for Push-in / Wan Motion)**:
    - **Top Safe Margin**: `y >= 215–220px` for title text to prevent cropping during 10–20% camera zoom-in/push-in.
    - **Side Safe Margin**: `x >= 150px` padding on left and right borders.
    - **Character Safe Placement**: Presenter grounded on bottom-right (~55–58% canvas height), color-graded/tinted to scene lighting.
    - **Subtitle Safe Area**: Bottom area (`y: 1380–1920`) preserved calm and dark.

---

## 4. Scenes 02 Onward: Zero In-Image Text

From Scene 02 to the scene immediately preceding the brand outro:
- **ZERO in-image text**: No English labels, Thai titles, numbers, callout pointers, HUD elements, NASA/ESA logos, or watermarks.
- All narration and factual context are delivered via voiceover and AutoClip subtitles.

---

## 5. Visual Quality Gate Checklist

Before compiling any package into a ZIP, inspect all master images:

- [ ] Is the resolution strictly **1080x1920 PNG** (RGB 8-bit)?
- [ ] Does active composition fill **70–80%** of the vertical canvas?
- [ ] Is the focal subject large, sharp, and instantly readable on a phone screen?
- [ ] Is there any unmotivated dead space (>1/3 of the frame)?
- [ ] Are Scenes 02+ completely free of text, numbers, logos, and watermarks?
- [ ] In Scene 01, is the presenter naturally integrated with realistic lighting and shadow?
- [ ] Does the visual directly illustrate the specific fact stated in that scene's narration?

If any scene fails, regenerate that specific scene while preserving all approved scenes.
