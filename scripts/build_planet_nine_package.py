import json
import math
import random
import shutil
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1080, 1920
FONT_PATH = "/System/Library/Fonts/Supplemental/SukhumvitSet.ttc"

def get_font():
    return ImageFont.truetype(FONT_PATH, 24, index=4)

def add_nebula(canvas, colors, count=45, seed=42):
    random.seed(seed)
    neb = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ndraw = ImageDraw.Draw(neb)
    for _ in range(count):
        nx = random.randint(100, W - 100)
        ny = random.randint(200, H - 200)
        nr = random.randint(180, 500)
        col = random.choice(colors)
        alpha = random.randint(12, 28)
        ndraw.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=(*col, alpha))

    neb = neb.filter(ImageFilter.GaussianBlur(70))
    return Image.alpha_composite(canvas.convert("RGBA"), neb).convert("RGB")

def add_stars(canvas, count=350, seed=42):
    random.seed(seed)
    sdraw = ImageDraw.Draw(canvas)
    for _ in range(count):
        x = random.randint(0, W)
        y = random.randint(0, H)
        r = random.choice([1, 1, 1, 1, 2, 2, 3])
        bright = random.randint(140, 255)
        tint = random.choice([(255, 255, 255), (200, 230, 255), (255, 240, 210), (180, 220, 255)])
        sdraw.ellipse([x - r, y - r, x + r, y + r], fill=tint)

        # Add diffraction spikes to occasional bright stars
        if r >= 3 and random.random() < 0.25:
            spike_len = random.randint(12, 28)
            sdraw.line([(x - spike_len, y), (x + spike_len, y)], fill=(*tint[:3], 160), width=1)
            sdraw.line([(x, y - spike_len), (x, y + spike_len)], fill=(*tint[:3], 160), width=1)

def draw_minimal_tag(draw, text, font, y=140):
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    bx0, by0, bx1, by1 = (W - tw) // 2 - 24, y, (W + tw) // 2 + 24, y + 44
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=20, fill=(15, 23, 42, 140), outline=(255, 255, 255, 80), width=1)
    draw.text((W // 2, y + 22), text, font=font, fill=(241, 245, 249), anchor="mm")

# ==================== 1. SCENE 01: THE GIANT IN THE DARK ====================
def render_scene_01(out):
    img = Image.new("RGB", (W, H), (3, 5, 14))
    img = add_nebula(img, [(14, 165, 233), (99, 102, 241), (6, 182, 212)], count=40, seed=11)
    add_stars(img, count=400, seed=11)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # Planet Nine: Colossal dark silhouette looming from right center
    cx, cy = int(W * 0.55), int(H * 0.48)
    pr = 380

    # Faint outer atmospheric glow
    for r in range(pr + 40, pr, -2):
        alpha = int(40 * (1 - (r - pr) / 40))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(6, 182, 212, alpha))

    # Shaded dark gas giant sphere
    d.ellipse([cx - pr, cy - pr, cx + pr, cy + pr], fill=(5, 8, 18))

    # Sharp atmospheric rim crescent (backlit from top-left)
    for width_offset in range(12, 0, -2):
        alpha = int(255 * (1 - width_offset / 14))
        d.arc([cx - pr - 2, cy - pr - 2, cx + pr + 2, cy + pr + 2], start=170, end=290, fill=(165, 243, 252, alpha), width=width_offset)

    # Massive planetary ice rings cutting across
    rx, ry = cx, cy
    rw, rh = 720, 160
    # Back ring behind planet
    d.arc([rx - rw, ry - rh, rx + rw, ry + rh], start=180, end=360, fill=(103, 232, 249, 90), width=6)
    d.arc([rx - rw + 30, ry - rh + 10, rx + rw - 30, ry + rh - 10], start=180, end=360, fill=(147, 197, 253, 50), width=14)
    # Front ring cutting over planet
    d.arc([rx - rw, ry - rh, rx + rw, ry + rh], start=0, end=180, fill=(103, 232, 249, 140), width=6)
    d.arc([rx - rw + 30, ry - rh + 10, rx + rw - 30, ry + rh - 10], start=0, end=180, fill=(147, 197, 253, 90), width=14)

    # Distant pinpoint Sun casting dramatic starlight in top-left
    sx, sy = 180, 380
    for sr in (30, 20, 12, 6):
        d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(254, 240, 138, 40 if sr>10 else 255))
    d.line([(sx - 80, sy), (sx + 80, sy)], fill=(254, 240, 138, 180), width=2)
    d.line([(sx, sy - 80), (sx, sy + 80)], fill=(254, 240, 138, 180), width=2)

    # Minimal subtle title badge
    font = get_font()
    draw_minimal_tag(d, "PLANET NINE  •  THE UNSEEN GIANT", font, y=120)

    res = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    res.save(out, quality=95)

# ==================== 2. SCENE 02: ORBITAL HARMONY IN DEEP SPACE ====================
def render_scene_02(out):
    img = Image.new("RGB", (W, H), (4, 4, 15))
    img = add_nebula(img, [(168, 85, 247), (139, 92, 246), (59, 130, 246)], count=45, seed=22)
    add_stars(img, count=450, seed=22)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # Dramatic perspective view of cosmic orbital trails
    cx, cy = W // 2, int(H * 0.52)

    # Multiple glowing orbital ellipses sweeping through space
    orbits = [
        (460, 260, (56, 189, 248), 120),
        (520, 310, (147, 197, 253), 100),
        (580, 360, (192, 132, 252), 90),
        (650, 420, (167, 139, 250), 70),
    ]
    for ew, eh, col, alpha in orbits:
        d.ellipse([cx - ew, cy - eh, cx + ew, cy + eh], outline=(*col, alpha), width=3)

    # Icy trans-Neptunian objects glowing along the trails
    asteroids = [
        (cx + 340, cy - 140, 14, "Sedna"),
        (cx + 420, cy + 90, 10, "2012 VP113"),
        (cx - 280, cy + 180, 12, "Leleakuhonua"),
        (cx - 390, cy - 80, 9, "eTNO 2013 RF98"),
    ]
    for ax, ay, ar, name in asteroids:
        # Comet / orbital trail glow
        d.ellipse([ax - ar * 3, ay - ar * 3, ax + ar * 3, ay + ar * 3], fill=(147, 197, 253, 30))
        d.ellipse([ax - ar, ay - ar, ax + ar, ay + ar], fill=(241, 245, 249, 240))
        d.line([(ax - 40, ay + 20), (ax, ay)], fill=(147, 197, 253, 140), width=2)

    # Center Sun with lens halo
    for r in (50, 30, 15, 6):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(250, 204, 21, 30 if r>10 else 255))
    d.line([(cx - 100, cy), (cx + 100, cy)], fill=(250, 204, 21, 160), width=2)
    d.line([(cx, cy - 100), (cx, cy + 100)], fill=(250, 204, 21, 160), width=2)

    font = get_font()
    draw_minimal_tag(d, "CLUSTERING OF EXTREME ORBITS", font, y=120)

    res = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    res.save(out, quality=95)

# ==================== 3. SCENE 03: THE ICE GIANT (ATMOSPHERIC CLOSE-UP) ====================
def render_scene_03(out):
    img = Image.new("RGB", (W, H), (3, 7, 20))
    img = add_nebula(img, [(37, 99, 235), (14, 165, 233), (99, 102, 241)], count=40, seed=33)
    add_stars(img, count=400, seed=33)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # Massive planet curvature dominating lower half of the screen
    cx, cy = W // 2, int(H * 1.12)
    pr = 880

    # Atmospheric outer glow
    for r in range(pr + 60, pr, -3):
        alpha = int(55 * (1 - (r - pr) / 60))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(14, 165, 233, alpha))

    # Planet body
    d.ellipse([cx - pr, cy - pr, cx + pr, cy + pr], fill=(8, 18, 45))

    # Swirling atmospheric storm bands on the ice giant
    for band_y, col, thickness in [
        (cy - pr + 40, (14, 165, 233, 90), 25),
        (cy - pr + 90, (56, 189, 248, 120), 40),
        (cy - pr + 160, (30, 58, 138, 140), 60),
        (cy - pr + 240, (96, 165, 250, 80), 35),
    ]:
        d.arc([cx - pr - 50, band_y - 20, cx + pr + 50, band_y + 120], start=190, end=350, fill=col, width=thickness)

    # Glowing edge crescent
    for w in range(16, 0, -2):
        alpha = int(240 * (1 - w / 18))
        d.arc([cx - pr - 2, cy - pr - 2, cx + pr + 2, cy + pr + 2], start=200, end=340, fill=(186, 230, 253, alpha), width=w)

    # Beautiful moon orbiting nearby
    mx, my, mr = 320, 560, 24
    d.ellipse([mx - mr*2, my - mr*2, mx + mr*2, my + mr*2], fill=(147, 197, 253, 25))
    d.ellipse([mx - mr, my - mr, mx + mr, my + mr], fill=(15, 23, 42))
    d.arc([mx - mr, my - mr, mx + mr, my + mr], start=190, end=330, fill=(224, 242, 254, 220), width=4)

    font = get_font()
    draw_minimal_tag(d, "ICE GIANT  •  5-10 EARTH MASSES", font, y=120)

    res = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    res.save(out, quality=95)

# ==================== 4. SCENE 04: THE CELESTIAL SEARCH ====================
def render_scene_04(out):
    img = Image.new("RGB", (W, H), (4, 6, 18))
    # Spectacular deep cosmos web
    img = add_nebula(img, [(234, 179, 8), (249, 115, 22), (168, 85, 247), (14, 165, 233)], count=50, seed=44)
    add_stars(img, count=550, seed=44)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    # Telescope target crosshair & celestial coordinates grid (subtle, high-tech, cinematic)
    cx, cy = W // 2, int(H * 0.48)

    # Crosshairs & rings
    for r in (320, 220, 120):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255, 30), width=1)

    # Crosshair ticks
    d.line([(cx - 360, cy), (cx - 140, cy)], fill=(255, 255, 255, 60), width=1)
    d.line([(cx + 140, cy), (cx + 360, cy)], fill=(255, 255, 255, 60), width=1)
    d.line([(cx, cy - 360), (cx, cy - 140)], fill=(255, 255, 255, 60), width=1)
    d.line([(cx, cy + 140), (cx, cy + 360)], fill=(255, 255, 255, 60), width=1)

    # Target lock on distant mysterious pinpoint of light
    tx, ty = cx + 80, cy - 60
    d.rounded_rectangle([tx - 28, ty - 28, tx + 28, ty + 28], radius=6, outline=(250, 204, 21, 200), width=2)
    d.ellipse([tx - 6, ty - 6, tx + 6, ty + 6], fill=(254, 240, 138))

    # Fine coordinates HUD text (minimalist, sci-fi documentary style)
    font = get_font()
    draw_minimal_tag(d, "VERA C. RUBIN OBSERVATORY  •  SKY SURVEY", font, y=120)

    res = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    res.save(out, quality=95)

def main():
    root = Path(__file__).resolve().parents[1]
    dist_dir = root / "dist"
    package_dir = dist_dir / "planet-nine-5scenes"
    images_dir = package_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    # 1. Render Cinematic Space Visuals (Scenes 1-4)
    render_scene_01(images_dir / "scene-01.jpg")
    render_scene_02(images_dir / "scene-02.jpg")
    render_scene_03(images_dir / "scene-03.jpg")
    render_scene_04(images_dir / "scene-04.jpg")
    print("Rendered 4 cinematic space visuals without heavy text cards")

    # 2. Copy Scene 5 from official Mamase brand outro
    src_scene_05 = root / "sample-package" / "lake-natron-mamase-v3" / "images" / "scene-08-brand-outro.png"
    shutil.copy2(src_scene_05, images_dir / "scene-05.png")
    print("Copied scene 5 brand outro")

    # 3. Write script.json
    script = {
        "project": {
            "id": "planet-nine-5scenes",
            "title": "Planet Nine มีจริงไหม? ดาวเคราะห์ยักษ์ดวงที่ 9 ที่ซ่อนอยู่ในความมืด (39 วินาที)",
            "language": "th-TH",
            "resolution": "1080x1920",
            "fps": 30
        },
        "voice": {
            "provider": "local",
            "voice": "thai-male-01",
            "speed": 0.95
        },
        "scenes": [
            {
                "id": "scene-01",
                "image": "images/scene-01.jpg",
                "narration": "คุณรู้ไหมครับว่า... ที่ขอบนอกสุดของระบบสุริยะ อาจมีดาวเคราะห์ขนาดยักษ์ดวงที่เก้า ซ่อนตัวอยู่ในความมืดมิด",
                "subtitle": "ดาวเคราะห์ดวงที่ 9\\nซ่อนตัวอยู่นอกระบบสุริยะ?",
                "motion": "cinematic_push_in",
                "motion_speed": "slow",
                "motion_intensity": 0.15,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Cinematic deep space documentary shot, giant dark planet silhouette at edge of solar system, faint cyan atmospheric rim glow, starry background.",
                    "negative_prompt": "watermark, blur, jitter, text",
                    "seed": 91,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-02",
                "image": "images/scene-02.jpg",
                "narration": "ในปีสองพันสิบหก นักดาราศาสตร์พบว่า วัตถุขอบน้ำแข็งหลายชิ้น มีวงโคจรเอียงไปในทิศทางเดียวกัน เหมือนถูกแรงโน้มถ่วงมหาศาลดึงไว้",
                "tts_text": "ในปี สอง-พัน-สิบ-หก นักดาราศาสตร์พบว่า วัตถุขอบน้ำแข็งหลายชิ้น มีวงโคจรเอียงไปในทิศทางเดียวกัน เหมือนถูกแรงโน้มถ่วงมหาศาลดึงไว้",
                "subtitle": "แรงโน้มถ่วงลึกลับ\\nดึงวงโคจรให้เอียงทิศเดียวกัน",
                "motion": "zoom_out",
                "motion_speed": "slow",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Solar system orbital paths in deep space, glowing cosmic dust trails, frozen icy planetoids orbiting in synchronized elliptical paths.",
                    "negative_prompt": "watermark, blur, jitter, text",
                    "seed": 92,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-03",
                "image": "images/scene-03.jpg",
                "narration": "การคำนวณชี้ว่า มันน่าจะมีมวลใหญ่กว่าโลกถึงห้าถึงสิบเท่า และอยู่ไกลกว่าดาวพลูโตกว่ายี่สิบเท่า ใช้เวลานับหมื่นปีโคจรรอบดวงอาทิตย์",
                "subtitle": "มวลใหญ่กว่าโลก 5-10 เท่า\\nไกลกว่าพลูโต 20 เท่า",
                "motion": "pan_left_to_right",
                "motion_speed": "normal",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Colossal Ice Giant planet close-up, vibrant deep sapphire blue and turquoise atmospheric bands, glowing faint rings, deep space darkness.",
                    "negative_prompt": "watermark, blur, jitter, text",
                    "seed": 93,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-04",
                "image": "images/scene-04.jpg",
                "narration": "ที่ยังมองไม่เห็น เพราะมันสะท้อนแสงอาทิตย์น้อยมากในความมืด แต่นักดาราศาสตร์กำลังใช้กล้องโทรทรรศน์รุ่นใหม่ตามล่าตัวมันอยู่",
                "subtitle": "สะท้อนแสงน้อยมาก\\nกล้องรุ่นใหม่กำลังตามล่า",
                "motion": "drift_top_right",
                "motion_speed": "slow",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Starlight piercing through cosmic void, telescope optical lens flare over deep cosmic web and dense star cluster, searching infinite dark.",
                    "negative_prompt": "watermark, blur, jitter, text",
                    "seed": 94,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-05",
                "image": "images/scene-05.png",
                "narration": "บ้านของเราอาจกว้างใหญ่กว่าที่คิด... ค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ",
                "tts_text": "บ้านของเราอาจกว้างใหญ่กว่าที่คิด... ค้นพบโลก ค้นพบใจ กับ มามาเซ่ จักรวาลของใจ",
                "subtitle": "จักรวาลยังมีเรื่องน่าค้นหา\\nMamase จักรวาลของใจ",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.10,
                "focus": "center",
                "transition": "fade_black",
                "wan": {
                    "prompt": "Mamase brand outro, glowing cyan orbiting planet in dark navy space, peaceful and contemplative.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 95,
                    "frames": 81,
                    "lip_sync": False
                }
            }
        ]
    }

    script_path = package_dir / "script.json"
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    print(f"Created {script_path}")

    # 4. Write video-metadata.json
    metadata = {
        "title": "Planet Nine มีจริงไหม? ดาวเคราะห์ยักษ์ดวงที่ 9 ที่ซ่อนอยู่ในความมืด 🪐🔭",
        "description": "คุณรู้ไหมว่า... ที่ขอบนอกสุดของระบบสุริยะ อาจมีดาวเคราะห์ยักษ์ดวงที่เก้าซ่อนตัวอยู่?\n\nในปี 2016 นักดาราศาสตร์จาก Caltech พบความผิดปกติครั้งใหญ่ เมื่อวัตถุขอบน้ำแข็งหลายชิ้น (eTNOs) มีวงโคจรเอียงไปในทิศทางเดียวกันอย่างน่าประหลาด ซึ่งโอกาสที่จะเกิดเรื่องนี้โดยบังเอิญมีไม่ถึง 0.001%\n\nแบบจำลองชี้ว่า มันคือ 'Planet Nine' ดาวเคราะห์ยักษ์น้ำแข็งที่มีมวลมากกว่าโลก 5-10 เท่า และอยู่ไกลกว่าดาวพลูโตถึง 20 เท่า ใช้เวลานับหมื่นปีโคจรรอบดวงอาทิตย์ 1 รอบ\n\nทำไมเราถึงยังมองไม่เห็น? และกล้องโทรทรรศน์รุ่นใหม่อย่าง Vera C. Rubin กำลังตามหามันอย่างไร?\n\nเพราะบ้านของเราอาจกว้างใหญ่กว่าที่เราเคยคิด\n\nค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ\n\n#PlanetNine #ดาวเคราะห์ดวงที่เก้า #ดาราศาสตร์ #อวกาศ #ระบบสุริยะ #วิทยาศาสตร์ #สารคดี #พลูโต #Astronomy #Space #SolarSystem #Caltech #Science #Mamase #จักรวาลของใจ #Shorts #YouTubeShorts #Reels #TikTok"
    }
    meta_path = package_dir / "video-metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Created {meta_path}")

    # 5. Build clean ZIP
    zip_path = dist_dir / "planet-nine-5scenes.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(package_dir.rglob("*")):
            if file_path.is_file() and not file_path.name.startswith("."):
                archive.write(file_path, file_path.relative_to(package_dir).as_posix())
    print(f"Created ZIP archive: {zip_path}")

if __name__ == "__main__":
    main()
