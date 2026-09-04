import json
import math
import shutil
import zipfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FONT_PATH = "/System/Library/Fonts/Supplemental/SukhumvitSet.ttc"

def get_fonts():
    return {
        "title_large": ImageFont.truetype(FONT_PATH, 56, index=5),
        "title_med": ImageFont.truetype(FONT_PATH, 38, index=4),
        "sub": ImageFont.truetype(FONT_PATH, 28, index=2),
        "body": ImageFont.truetype(FONT_PATH, 24, index=2),
        "body_bold": ImageFont.truetype(FONT_PATH, 25, index=4),
        "hero_num": ImageFont.truetype(FONT_PATH, 72, index=5),
        "badge": ImageFont.truetype(FONT_PATH, 22, index=4),
    }

def wrap_thai(text, font, max_w):
    words = text.split(" ")
    lines = []
    curr = ""
    for w in words:
        test = (curr + " " + w).strip()
        if font.getbbox(test)[2] <= max_w:
            curr = test
        else:
            if curr:
                lines.append(curr)
                curr = ""
            if font.getbbox(w)[2] > max_w:
                sub = ""
                for ch in w:
                    if font.getbbox(sub + ch)[2] <= max_w:
                        sub += ch
                    else:
                        lines.append(sub)
                        sub = ch
                curr = sub
            else:
                curr = w
    if curr:
        lines.append(curr)
    return lines

def create_base_canvas(glow_color=(37, 99, 235), glow_y=600):
    canvas = Image.new("RGB", (W, H), (8, 12, 24))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    cx, cy = W // 2, glow_y
    for r in range(480, 0, -15):
        alpha = int(45 * (1 - r / 480))
        gdraw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(*glow_color, alpha))

    # Subtle dark grid lines
    for y in range(0, H, 120):
        gdraw.line([(0, y), (W, y)], fill=(255, 255, 255, 5), width=1)
    for x in range(0, W, 120):
        gdraw.line([(x, 0), (x, H)], fill=(255, 255, 255, 5), width=1)

    return Image.alpha_composite(Image.new("RGBA", (W, H), (8, 12, 24, 255)), glow).convert("RGB")

def draw_badge(draw, text, font, color=(234, 179, 8), y=290):
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    bx0, by0, bx1, by1 = (W - tw) // 2 - 28, y, (W + tw) // 2 + 28, y + 48
    draw.rounded_rectangle([bx0, by0, bx1, by1], radius=24, fill=(*color, 25), outline=(*color, 180), width=2)
    draw.text((W // 2, y + 24), text, font=font, fill=(*color, 255), anchor="mm")

def draw_header(draw, badge_text, title_text, sub_text, fonts, color=(234, 179, 8)):
    draw_badge(draw, badge_text, fonts["badge"], color=color, y=280)
    draw.text((W // 2, 395), title_text, font=fonts["title_large"], fill=(255, 255, 255), anchor="mm")
    draw.text((W // 2, 465), sub_text, font=fonts["sub"], fill=(148, 163, 184), anchor="mm")

def draw_checkmark(draw, x, y, size=18, color=(74, 222, 128)):
    draw.line([(x, y + size * 0.5), (x + size * 0.4, y + size), (x + size, y)], fill=color, width=3)

def draw_down_arrow(draw, x, y, length=30, color=(148, 163, 184)):
    draw.line([(x, y), (x, y + length)], fill=color, width=3)
    draw.polygon([(x - 7, y + length - 5), (x + 7, y + length - 5), (x, y + length + 4)], fill=color)

# ==================== SCENE RENDERING ====================

def render_scene_01(fonts, out):
    img = create_base_canvas(glow_color=(234, 179, 8), glow_y=680)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    draw_header(d, "CLINICAL GOLD STANDARD", "VITAMIN A & RETINOIDS", "สารตัวเดียวที่งานวิจัยยืนยันว่ากู้คอลลาเจนได้จริง", fonts, color=(234, 179, 8))

    # Main Card
    d.rounded_rectangle([90, 530, 990, 1260], radius=24, fill=(15, 23, 42, 230), outline=(234, 179, 8, 120), width=2)

    # Center Icon
    cx, cy = W // 2, 690
    for r in (110, 75, 45):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(234, 179, 8, 80 if r!=45 else 220), width=2)
    d.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=(234, 179, 8, 230))
    d.text((cx, cy), "A", font=fonts["title_large"], fill=(15, 23, 42), anchor="mm")

    points = [
        ("กระตุ้นเซลล์ Fibroblast", "ส่งสัญญาณสั่งงานระดับยีนให้สร้างโปรตีนคอลลาเจนใหม่"),
        ("ยับยั้งเอนไซม์ MMP", "หยุดการสลายตัวของคอลลาเจนเดิมที่ถูกทำลายจากแสงแดด"),
        ("รับรองผลทางการแพทย์", "มีงานวิจัยระดับ Double-Blind ยืนยันยาวนานกว่า 40 ปี")
    ]
    y = 850
    for title, desc in points:
        d.rounded_rectangle([130, y, 950, y + 115], radius=16, fill=(30, 41, 59, 180), outline=(234, 179, 8, 70), width=1)
        draw_checkmark(d, 160, y + 32, size=20, color=(250, 204, 21))
        d.text((200, y + 42), title, font=fonts["title_med"], fill=(255, 255, 255), anchor="lm")
        d.text((200, y + 82), desc, font=fonts["body"], fill=(203, 213, 225), anchor="lm")
        y += 130

    res = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    res.save(out, quality=95)

def render_scene_02(fonts, out):
    img = create_base_canvas(glow_color=(239, 68, 68), glow_y=680)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    draw_header(d, "COLLAGEN LOSS OVER TIME", "วิกฤตคอลลาเจนใต้ผิว", "โครงสร้างผิวที่สูญเสียไปตามกาลเวลาและแสงแดด", fonts, color=(248, 113, 113))

    d.rounded_rectangle([90, 530, 990, 1260], radius=24, fill=(15, 23, 42, 230), outline=(239, 68, 68, 100), width=2)

    # 2 Stat Blocks
    d.rounded_rectangle([130, 580, 520, 770], radius=18, fill=(239, 68, 68, 25), outline=(239, 68, 68, 150), width=2)
    d.text((325, 650), "-1% / ปี", font=fonts["hero_num"], fill=(248, 113, 113), anchor="mm")
    d.text((325, 725), "คอลลาเจนลดลงหลังอายุ 20", font=fonts["body_bold"], fill=(255, 255, 255), anchor="mm")

    d.rounded_rectangle([560, 580, 950, 770], radius=18, fill=(249, 115, 22, 25), outline=(249, 115, 22, 150), width=2)
    d.text((755, 650), "PHOTO", font=fonts["hero_num"], fill=(251, 146, 60), anchor="mm")
    d.text((755, 725), "แดดเร่งทำลายคอลลาเจน x4", font=fonts["body_bold"], fill=(255, 255, 255), anchor="mm")

    # Comparison sections
    y = 820
    cards = [
        ("ผิววัยหนุ่มสาว (Youthful Skin)", "โครงข่ายเส้นใยคอลลาเจน Type I และ III ถักทอหนาแน่น ผิวเด้งกระชับ", (34, 197, 94)),
        ("ผิวที่ขาดการฟื้นฟู (Degraded Skin)", "เอนไซม์ MMP ย่อยสลายเส้นใยคอลลาเจน เกิดเป็นรอยเหี่ยวย่นและร่องลึก", (239, 68, 68))
    ]
    for h_txt, b_txt, col in cards:
        d.rounded_rectangle([130, y, 950, y + 175], radius=18, fill=(30, 41, 59, 200), outline=(*col, 120), width=2)
        d.ellipse([160, y + 38, 185, y + 63], fill=col)
        d.text((210, y + 50), h_txt, font=fonts["title_med"], fill=(255, 255, 255), anchor="lm")
        wrapped = wrap_thai(b_txt, fonts["body"], 700)
        for idx, line in enumerate(wrapped):
            d.text((210, y + 100 + idx * 36), line, font=fonts["body"], fill=(203, 213, 225), anchor="lm")
        y += 205

    res = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    res.save(out, quality=95)

def render_scene_03(fonts, out):
    img = create_base_canvas(glow_color=(14, 165, 233), glow_y=680)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    draw_header(d, "CELLULAR MESSENGER", "ผู้ส่งสารระดับเซลล์", "เรตินอยด์ไม่ได้เคลือบผิว แต่สั่งการตรงสู่นิวเคลียส", fonts, color=(56, 189, 248))

    d.rounded_rectangle([90, 530, 990, 1260], radius=24, fill=(15, 23, 42, 230), outline=(14, 165, 233, 120), width=2)

    # Cellular diagram
    cx, cy = W // 2, 730
    d.ellipse([cx - 150, cy - 140, cx + 150, cy + 140], outline=(14, 165, 233, 140), width=3)
    d.ellipse([cx - 85, cy - 80, cx + 85, cy + 80], fill=(14, 165, 233, 35), outline=(56, 189, 248, 200), width=2)
    d.text((cx, cy - 12), "NUCLEUS", font=fonts["title_med"], fill=(255, 255, 255), anchor="mm")
    d.text((cx, cy + 28), "(ดีเอ็นเอของเซลล์ผิว)", font=fonts["badge"], fill=(148, 163, 184), anchor="mm")

    # Receptor Box
    d.rounded_rectangle([130, cy - 45, 300, cy + 45], radius=14, fill=(234, 179, 8, 35), outline=(234, 179, 8, 220), width=2)
    d.text((215, cy - 10), "RAR Receptor", font=fonts["body_bold"], fill=(250, 204, 21), anchor="mm")
    d.text((215, cy + 20), "ตัวรับสัญญาณ", font=fonts["badge"], fill=(203, 213, 225), anchor="mm")
    d.line([(300, cy), (cx - 150, cy)], fill=(234, 179, 8), width=3)

    # Output box
    d.rounded_rectangle([W - 300, cy - 45, W - 130, cy + 45], radius=14, fill=(34, 197, 94, 35), outline=(34, 197, 94, 220), width=2)
    d.text((W - 215, cy - 10), "Pro-Collagen", font=fonts["body_bold"], fill=(74, 222, 128), anchor="mm")
    d.text((W - 215, cy + 20), "สร้างคอลลาเจนใหม่", font=fonts["badge"], fill=(203, 213, 225), anchor="mm")
    d.line([(cx + 150, cy), (W - 300, cy)], fill=(34, 197, 94), width=3)

    # Bottom explanation
    d.rounded_rectangle([130, 930, 950, 1190], radius=18, fill=(30, 41, 59, 180), outline=(14, 165, 233, 70), width=1)
    d.text((W // 2, 980), "กลไกการส่งสัญญาณ (Signal Transduction)", font=fonts["title_med"], fill=(255, 255, 255), anchor="mm")
    p1 = "เรตินอยด์ทำหน้าที่เหมือนกุญแจที่ไขเข้าสู่ตัวรับ RAR เพื่อสั่งให้ยีนในไฟโบรบลาสต์เริ่มสังเคราะห์เส้นใยโปรตีนคอลลาเจนใหม่อย่างต่อเนื่อง"
    for idx, l in enumerate(wrap_thai(p1, fonts["body"], 760)):
        d.text((W // 2, 1045 + idx * 36), l, font=fonts["body"], fill=(203, 213, 225), anchor="mm")

    res = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    res.save(out, quality=95)

def render_scene_04(fonts, out):
    img = create_base_canvas(glow_color=(168, 85, 247), glow_y=680)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    draw_header(d, "THE RETINOID CASCADE", "บันไดการแปลงรูปในผิว", "เซลล์ผิวจะตอบสนองต่อ กรดเรติโนอิก เท่านั้น", fonts, color=(192, 132, 252))

    d.rounded_rectangle([90, 530, 990, 1310], radius=24, fill=(15, 23, 42, 230), outline=(168, 85, 247, 120), width=2)

    steps = [
        ("1. Retinyl Esters", "อนุพันธ์กลุ่มเอสเทอร์", "แปลง 3 ขั้นตอน • อ่อนโยนมาก ไม่ระคายเคือง", (100, 116, 139), False),
        ("2. Retinol (เรตินอล)", "มาตรฐานยอดนิยม", "แปลง 2 ขั้นตอน • ผ่านการวิจัยยาวนานที่สุด", (59, 130, 246), False),
        ("3. Retinal (เรตินัล)", "อนุพันธ์ขั้นกว่า", "แปลง 1 ขั้นตอน • ทำงานเร็วกว่า 11 เท่า + คุมสิว", (249, 115, 22), False),
        ("4. Retinoic Acid", "กรดเรติโนอิก (Active Form)", "จับตัวรับทันที • สั่งยีนสร้างคอลลาเจนได้โดยตรง", (234, 179, 8), True)
    ]

    y = 570
    for name, tag, desc, col, is_active in steps:
        bg_col = (*col, 40 if is_active else 20)
        border_col = (*col, 255 if is_active else 120)
        d.rounded_rectangle([130, y, 950, y + 120], radius=16, fill=bg_col, outline=border_col, width=3 if is_active else 1)

        d.text((165, y + 35), name, font=fonts["title_med"], fill=(250, 204, 21) if is_active else (255, 255, 255), anchor="lm")

        # Tag badge
        tb_box = fonts["badge"].getbbox(tag)
        tb_w = tb_box[2] - tb_box[0]
        d.rounded_rectangle([910 - tb_w - 20, y + 20, 910, y + 55], radius=10, fill=(*col, 40), outline=(*col, 180), width=1)
        d.text((910 - tb_w // 2 - 10, y + 38), tag, font=fonts["badge"], fill=(255, 255, 255), anchor="mm")

        d.text((165, y + 85), desc, font=fonts["body"], fill=(203, 213, 225), anchor="lm")

        if y < 1000:
            draw_down_arrow(d, W // 2, y + 120, length=28, color=(148, 163, 184))
        y += 152

    res = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    res.save(out, quality=95)

def render_scene_05(fonts, out):
    img = create_base_canvas(glow_color=(59, 130, 246), glow_y=680)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    draw_header(d, "OTC GOLD STANDARD", "RETINOL (เรตินอล)", "มาตรฐานสากลที่ผ่านการวิจัยยาวนานที่สุด", fonts, color=(96, 165, 250))

    d.rounded_rectangle([90, 530, 990, 1260], radius=24, fill=(15, 23, 42, 230), outline=(59, 130, 246, 120), width=2)

    # 2 Stat Cards
    d.rounded_rectangle([130, 580, 520, 770], radius=18, fill=(30, 41, 59, 220), outline=(59, 130, 246, 150), width=2)
    d.text((325, 650), "2 STEPS", font=fonts["hero_num"], fill=(96, 165, 250), anchor="mm")
    d.text((325, 725), "ขั้นตอนการแปลงรูปในผิว", font=fonts["body_bold"], fill=(255, 255, 255), anchor="mm")

    d.rounded_rectangle([560, 580, 950, 770], radius=18, fill=(30, 41, 59, 220), outline=(34, 197, 94, 150), width=2)
    d.text((755, 650), "8-12 WKS", font=fonts["hero_num"], fill=(74, 222, 128), anchor="mm")
    d.text((755, 725), "ระยะเวลาเห็นผลชัดเจน", font=fonts["body_bold"], fill=(255, 255, 255), anchor="mm")

    y = 820
    features = [
        ("ค่อยๆ ปลดปล่อยสารอย่างอ่อนโยน", "ให้ผิวมีเวลาปรับสภาพ ลดโอกาสแสบ แดง หรือลอกเป็นขุย"),
        ("ผลัดเซลล์ผิวเก่าที่เสื่อมสภาพ", "เร่งกระบวนการผลัดเซลล์ผิวชั้นบน เผยผิวใหม่ที่เรียบเนียน"),
        ("ฟื้นฟูคอลลาเจนในผิวชั้นลึก", "ลดเลือนริ้วรอยเส้นเล็ก (Fine Lines) ให้ผิวแน่นเฟิร์มกระชับ")
    ]
    for h_txt, b_txt in features:
        d.rounded_rectangle([130, y, 950, y + 120], radius=16, fill=(30, 41, 59, 180), outline=(59, 130, 246, 70), width=1)
        d.ellipse([160, y + 35, 185, y + 60], fill=(59, 130, 246))
        d.text((210, y + 45), h_txt, font=fonts["title_med"], fill=(255, 255, 255), anchor="lm")
        d.text((210, y + 85), b_txt, font=fonts["body"], fill=(203, 213, 225), anchor="lm")
        y += 135

    res = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    res.save(out, quality=95)

def render_scene_06(fonts, out):
    img = create_base_canvas(glow_color=(249, 115, 22), glow_y=680)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    draw_header(d, "NEXT-LEVEL POTENCY", "RETINAL (เรตินัล)", "อนุพันธ์ขั้นกว่า ออกฤทธิ์เร็วกว่าและคุมสิว", fonts, color=(251, 146, 60))

    d.rounded_rectangle([90, 530, 990, 1260], radius=24, fill=(15, 23, 42, 230), outline=(249, 115, 22, 120), width=2)

    # Comparison Cards
    d.rounded_rectangle([130, 580, 520, 840], radius=18, fill=(30, 41, 59, 220), outline=(100, 116, 139, 140), width=2)
    d.text((325, 630), "RETINOL", font=fonts["title_med"], fill=(148, 163, 184), anchor="mm")
    d.text((325, 710), "2 ขั้นตอน", font=fonts["hero_num"], fill=(255, 255, 255), anchor="mm")
    d.text((325, 790), "ความเร็วระดับมาตรฐาน", font=fonts["body"], fill=(203, 213, 225), anchor="mm")

    d.rounded_rectangle([560, 580, 950, 840], radius=18, fill=(249, 115, 22, 35), outline=(249, 115, 22, 200), width=2)
    d.text((755, 630), "RETINAL", font=fonts["title_med"], fill=(251, 146, 60), anchor="mm")
    d.text((755, 710), "1 ขั้นตอน", font=fonts["hero_num"], fill=(250, 204, 21), anchor="mm")
    d.text((755, 790), "ออกฤทธิ์เร็วกว่า 11 เท่า", font=fonts["body_bold"], fill=(250, 204, 21), anchor="mm")

    # Anti-acne box
    d.rounded_rectangle([130, 890, 950, 1200], radius=18, fill=(30, 41, 59, 200), outline=(249, 115, 22, 90), width=1)
    d.text((W // 2, 945), "คุณสมบัติพิเศษด้านการดูแลสิว (Anti-Acne)", font=fonts["title_med"], fill=(255, 255, 255), anchor="mm")
    p2 = "งานวิจัยระดับห้องปฏิบัติการพบว่า เรตินัล มีคุณสมบัติช่วยยับยั้งแบคทีเรีย C. acnes ซึ่งเป็นต้นเหตุของสิวอักเสบได้โดยตรง เหมาะอย่างยิ่งสำหรับผู้ที่ต้องการฟื้นฟูคอลลาเจนควบคู่กับการคุมสิว"
    for idx, l in enumerate(wrap_thai(p2, fonts["body"], 760)):
        d.text((W // 2, 1015 + idx * 36), l, font=fonts["body"], fill=(203, 213, 225), anchor="mm")

    res = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    res.save(out, quality=95)

def render_scene_07(fonts, out):
    img = create_base_canvas(glow_color=(139, 92, 246), glow_y=680)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    draw_header(d, "NEXT-GEN MOLECULE", "HPR (อนุพันธ์รุ่นใหม่)", "Hydroxypinacolone Retinoate อ่อนโยนและทรงพลัง", fonts, color=(167, 139, 250))

    d.rounded_rectangle([90, 530, 990, 1260], radius=24, fill=(15, 23, 42, 230), outline=(139, 92, 246, 120), width=2)

    points = [
        ("จับตัวรับได้โดยตรง (Direct Binding)", "ไม่ต้องผ่านกระบวนการแปลงสภาพ สามารถสื่อสารกับเซลล์ผิวได้ทันที"),
        ("อ่อนโยนเป็นพิเศษ (Low Irritation)", "ลดปัญหาการแสบ แดง ลอก หรือ Retinoid Dermatitis ได้อย่างมีนัยสำคัญ"),
        ("โครงสร้างโมเลกุลเสถียรสูง (High Stability)", "ไม่เสื่อมสลายจากแสงและความร้อนได้ง่ายเหมือนเรตินอยด์รุ่นเดิม")
    ]
    y = 610
    for idx_p, (title, desc) in enumerate(points):
        d.rounded_rectangle([130, y, 950, y + 180], radius=18, fill=(30, 41, 59, 200), outline=(139, 92, 246, 100), width=2)
        # Number badge
        d.rounded_rectangle([160, y + 25, 205, y + 70], radius=10, fill=(139, 92, 246, 40), outline=(139, 92, 246, 200), width=1)
        d.text((182, y + 47), str(idx_p + 1), font=fonts["title_med"], fill=(167, 139, 250), anchor="mm")

        d.text((225, y + 48), title, font=fonts["title_med"], fill=(255, 255, 255), anchor="lm")
        wrapped = wrap_thai(desc, fonts["body"], 700)
        for idx_l, l in enumerate(wrapped):
            d.text((160, y + 105 + idx_l * 36), l, font=fonts["body"], fill=(203, 213, 225), anchor="lm")
        y += 215

    res = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    res.save(out, quality=95)

def render_scene_08(fonts, out):
    img = create_base_canvas(glow_color=(34, 197, 94), glow_y=680)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    draw_header(d, "DUAL ANTI-AGING ACTION", "พลังสองด้าน: สร้าง + ปกป้อง", "กลไกคู่ขนานที่หยุดการเสื่อมสลายของผิว", fonts, color=(74, 222, 128))

    d.rounded_rectangle([90, 530, 990, 1260], radius=24, fill=(15, 23, 42, 230), outline=(34, 197, 94, 120), width=2)

    # Box 1: Build (Green)
    d.rounded_rectangle([130, 580, 950, 880], radius=18, fill=(34, 197, 94, 25), outline=(34, 197, 94, 160), width=2)
    d.text((170, 630), "1. สั่งสร้างคอลลาเจนใหม่ (Pro-Collagen I & III)", font=fonts["title_med"], fill=(74, 222, 128), anchor="lm")
    t1 = "กระตุ้นเซลล์ไฟโบรบลาสต์ให้สังเคราะห์เส้นใยโปรตีนคอลลาเจนใหม่ในชั้นผิวแท้ ช่วยคืนความยืดหยุ่นและลดเลือนริ้วรอยร่องลึก"
    for idx, l in enumerate(wrap_thai(t1, fonts["body"], 720)):
        d.text((170, 700 + idx * 36), l, font=fonts["body"], fill=(203, 213, 225), anchor="lm")

    # Box 2: Protect (Red/Amber)
    d.rounded_rectangle([130, 920, 950, 1220], radius=18, fill=(239, 68, 68, 25), outline=(239, 68, 68, 160), width=2)
    d.text((170, 970), "2. ยับยั้งเอนไซม์ทำลายผิว (Inhibit MMPs)", font=fonts["title_med"], fill=(248, 113, 113), anchor="lm")
    t2 = "สั่งปิดกั้นเอนไซม์คอลลาจิเนส (MMP-1) ที่ถูกกระตุ้นจากรังสี UV แสงแดด ปกป้องไม่ให้คอลลาเจนเดิมที่มีอยู่ถูกย่อยสลายไปก่อนเวลา"
    for idx, l in enumerate(wrap_thai(t2, fonts["body"], 720)):
        d.text((170, 1040 + idx * 36), l, font=fonts["body"], fill=(203, 213, 225), anchor="lm")

    res = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    res.save(out, quality=95)

def render_scene_09(fonts, out):
    img = create_base_canvas(glow_color=(234, 179, 8), glow_y=680)
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)

    draw_header(d, "DERMATOLOGY RULES", "กฎ 3 ข้อการใช้อย่างปลอดภัย", "ความงามที่ยั่งยืน ต้องมาพร้อมความเข้าใจที่ถูกต้อง", fonts, color=(250, 204, 21))

    d.rounded_rectangle([90, 530, 990, 1260], radius=24, fill=(15, 23, 42, 230), outline=(234, 179, 8, 120), width=2)

    rules = [
        ("1. เริ่มจากต่ำและช้า (Start Low & Slow)", "เริ่มต้นจากความเข้มข้นต่ำ (เช่น 0.1% - 0.2%) สัปดาห์ละ 2-3 ครั้ง เพื่อให้เซลล์ผิวปรับตัว"),
        ("2. เสริมเกราะชั้นผิว (Barrier Support)", "บำรุงด้วยมอยส์เจอไรเซอร์ที่มีเซราไมด์ (Ceramides) เพื่อกักเก็บความชุ่มชื้นและลดการระคายเคือง"),
        ("3. ทากันแดดทุกเช้า (Sunscreen Daily)", "เรตินอยด์ทำให้ผิวไวต่อแดด ต้องปกป้องผิวด้วยกันแดด SPF 50+ PA++++ เป็นประจำทุกเช้า")
    ]
    y = 610
    for title, desc in rules:
        d.rounded_rectangle([130, y, 950, y + 180], radius=18, fill=(30, 41, 59, 200), outline=(234, 179, 8, 80), width=2)
        draw_checkmark(d, 160, y + 36, size=20, color=(250, 204, 21))
        d.text((195, y + 46), title, font=fonts["title_med"], fill=(255, 255, 255), anchor="lm")
        wrapped = wrap_thai(desc, fonts["body"], 720)
        for idx_l, l in enumerate(wrapped):
            d.text((160, y + 105 + idx_l * 36), l, font=fonts["body"], fill=(203, 213, 225), anchor="lm")
        y += 215

    res = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    res.save(out, quality=95)

def main():
    root = Path(__file__).resolve().parents[1]
    dist_dir = root / "dist"
    package_dir = dist_dir / "vitamin-a-collagen-10scenes"
    images_dir = package_dir / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    fonts = get_fonts()

    # 1. Render clean typography scenes 1 to 9
    render_scene_01(fonts, images_dir / "scene-01.jpg")
    render_scene_02(fonts, images_dir / "scene-02.jpg")
    render_scene_03(fonts, images_dir / "scene-03.jpg")
    render_scene_04(fonts, images_dir / "scene-04.jpg")
    render_scene_05(fonts, images_dir / "scene-05.jpg")
    render_scene_06(fonts, images_dir / "scene-06.jpg")
    render_scene_07(fonts, images_dir / "scene-07.jpg")
    render_scene_08(fonts, images_dir / "scene-08.jpg")
    render_scene_09(fonts, images_dir / "scene-09.jpg")
    print("Rendered clean typography scenes 1-9 without square tofu or text overflows")

    # 2. Copy Scene 10 from official Mamase brand outro
    src_scene_10 = root / "sample-package" / "lake-natron-mamase-v3" / "images" / "scene-08-brand-outro.png"
    shutil.copy2(src_scene_10, images_dir / "scene-10.png")
    print("Copied scene 10 brand outro")

    # 3. Write script.json
    script = {
        "project": {
            "id": "vitamin-a-collagen-10scenes",
            "title": "วิตามินเอ กู้คอลลาเจนได้จริงไหม? วิทยาศาสตร์ผิวหนังมีคำตอบ (90 วินาที)",
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
                "narration": "ในโลกของสกินแคร์ มีสารเพียงกลุ่มเดียวเท่านั้น ที่งานวิจัยทั่วโลกยืนยันตรงกันว่า ช่วยกู้คอลลาเจนได้จริง",
                "subtitle": "สารเพียงกลุ่มเดียว...\\nที่กู้คอลลาเจนได้จริง",
                "motion": "cinematic_push_in",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Luxury clinical dermatology diagram card, Vitamin A Gold Standard, glowing golden badge, clean dark background, no flicker.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 111,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-02",
                "image": "images/scene-02.jpg",
                "narration": "หลังอายุยี่สิบปี ผิวเราจะสูญเสียคอลลาเจนปีละหนึ่งเปอร์เซ็นต์ และแสงแดดยังกระตุ้นเอนไซม์มาทำลายโครงสร้างผิว",
                "subtitle": "ผิวสูญเสียคอลลาเจน\\nปีละ 1% หลังอายุ 20",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Collagen degradation curve and skin layers diagram, epidermis and dermis support, clean science aesthetic.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 222,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-03",
                "image": "images/scene-03.jpg",
                "narration": "แต่สารกลุ่มเรตินอยด์ หรืออนุพันธ์ของวิตามินเอ ไม่ได้ทำหน้าที่แค่เคลือบผิว แต่มันทำหน้าที่เหมือนผู้ส่งสารระดับเซลล์",
                "tts_text": "แต่สารกลุ่ม เร-ติ-นอยด์ หรืออนุพันธ์ของวิตามินเอ ไม่ได้ทำหน้าที่แค่เคลือบผิว แต่มันทำหน้าที่เหมือนผู้ส่งสารระดับเซลล์",
                "subtitle": "ผู้ส่งสารระดับเซลล์\\nสื่อสารตรงกับนิวเคลียส",
                "motion": "drift_top_right",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Cellular messenger diagram, glowing blue cell receptor binding, RAR pathway stimulating collagen gene, no flicker.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 333,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-04",
                "image": "images/scene-04.jpg",
                "narration": "เซลล์ผิวเราจะตอบสนองต่อกรดเรติโนอิกเท่านั้น มันจะเข้าไปจับกับตัวรับในเซลล์ เพื่อสั่งให้ยีนเริ่มสร้างคอลลาเจนขึ้นมาใหม่",
                "tts_text": "เซลล์ผิวเราจะตอบสนองต่อ กรด-เร-ติ-โน-อิก เท่านั้น มันจะเข้าไปจับกับตัวรับในเซลล์ เพื่อสั่งให้ยีนเริ่มสร้างคอลลาเจนขึ้นมาใหม่",
                "subtitle": "กรดเรติโนอิกเท่านั้น\\nที่สั่งให้ยีนสร้างคอลลาเจน",
                "motion": "zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.15,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "The Retinoid Cascade flowchart, step by step conversion to Retinoic Acid active form, purple glowing cards, no flicker.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 444,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-05",
                "image": "images/scene-05.jpg",
                "narration": "เรตินอล ที่เราคุ้นเคย ต้องผ่านการแปลงสภาพสองขั้นตอนในผิว แม้จะใช้เวลา แต่ให้ผลลัพธ์ที่ชัดเจนและระคายเคืองน้อย",
                "tts_text": "เร-ติ-นอล ที่เราคุ้นเคย ต้องผ่านการแปลงสภาพสองขั้นตอนในผิว แม้จะใช้เวลา แต่ให้ผลลัพธ์ที่ชัดเจนและระคายเคืองน้อย",
                "subtitle": "เรตินอล แปลงสภาพ 2 ขั้น\\nเห็นผลชัดเจนและอ่อนโยน",
                "motion": "pan_left_to_right",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Retinol OTC standard card, 2 steps conversion metric, 8-12 weeks clinical timeline, clean blue aesthetic, no flicker.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 555,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-06",
                "image": "images/scene-06.jpg",
                "narration": "ส่วนเรตินัล แปลงสภาพเพียงขั้นตอนเดียว จึงออกฤทธิ์ได้เร็วกว่า และยังมีงานวิจัยพบว่าช่วยลดแบคทีเรียสิวได้อีกด้วย",
                "tts_text": "ส่วน เร-ติ-นัล แปลงสภาพเพียงขั้นตอนเดียว จึงออกฤทธิ์ได้เร็วกว่า และยังมีงานวิจัยพบว่าช่วยลดแบคทีเรียสิวได้อีกด้วย",
                "subtitle": "เรตินัล แปลงเพียง 1 ขั้น\\nออกฤทธิ์เร็ว + คุมสิว",
                "motion": "cinematic_push_in",
                "motion_speed": "normal",
                "motion_intensity": 0.15,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Retinal vs Retinol comparison card, orange glowing 1-step conversion card, anti-acne benefits, clean design, no flicker.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 666,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-07",
                "image": "images/scene-07.jpg",
                "narration": "และยังมีอนุพันธ์ยุคใหม่อย่าง เอชพีอาร์ ที่สามารถส่งสัญญาณกระตุ้นคอลลาเจนได้โดยตรง โดยแทบไม่ทำให้ผิวระคายเคือง",
                "tts_text": "และยังมีอนุพันธ์ยุคใหม่อย่าง เอช-พี-อาร์ ที่สามารถส่งสัญญาณกระตุ้นคอลลาเจนได้โดยตรง โดยแทบไม่ทำให้ผิวระคายเคือง",
                "subtitle": "HPR อนุพันธ์รุ่นใหม่\\nจับตัวรับตรง ไม่ระคายเคือง",
                "motion": "drift_top_right",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "HPR Next-Gen molecule diagram, direct binding to receptors, purple aesthetic card, high stability, no flicker.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 777,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-08",
                "image": "images/scene-08.jpg",
                "narration": "งานวิจัยยืนยันว่า เรตินอยด์ไม่เพียงสร้างคอลลาเจนใหม่ แต่ยังสั่งหยุดเอนไซม์ เอ็มเอ็มพี ที่คอยกัดกินคอลลาเจนเก่าของเรา",
                "tts_text": "งานวิจัยยืนยันว่า เร-ติ-นอยด์ ไม่เพียงสร้างคอลลาเจนใหม่ แต่ยังสั่งหยุดเอนไซม์ เอ็ม-เอ็ม-พี ที่คอยกัดกินคอลลาเจนเก่าของเรา",
                "subtitle": "พลังสองด้าน\\nสร้างคอลลาเจน + หยุด MMP",
                "motion": "pan_left_to_right_zoom_in",
                "motion_speed": "normal",
                "motion_intensity": 0.14,
                "focus": "center",
                "transition": "dissolve",
                "wan": {
                    "prompt": "Dual action mechanism diagram, green boost collagen arrow, red block MMP enzyme, balanced science infographic, no flicker.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 888,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-09",
                "image": "images/scene-09.jpg",
                "narration": "แต่หัวใจสำคัญคือความอดทน เริ่มจากเปอร์เซ็นต์ต่ำ ให้ความชุ่มชื้น และอย่าลืมทาครีมกันแดดเป็นประจำทุกเช้า",
                "subtitle": "กฎเหล็กการใช้\\nเริ่มจากต่ำ เติมชุ่มชื้น ทากันแดด",
                "motion": "zoom_out",
                "motion_speed": "slow",
                "motion_intensity": 0.12,
                "focus": "center",
                "transition": "fade",
                "wan": {
                    "prompt": "Dermatology safety rules, start low and slow, hydration barrier, broad spectrum sunscreen SPF 50+, golden aesthetic, no flicker.",
                    "negative_prompt": "watermark, blur, jitter",
                    "seed": 999,
                    "frames": 81,
                    "lip_sync": False
                }
            },
            {
                "id": "scene-10",
                "image": "images/scene-10.png",
                "narration": "เพราะความงามที่ยั่งยืน เริ่มต้นจากความเข้าใจธรรมชาติในระดับเซลล์... ค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ",
                "tts_text": "เพราะความงามที่ยั่งยืน เริ่มต้นจากความเข้าใจธรรมชาติในระดับเซลล์... ค้นพบโลก ค้นพบใจ กับ มามาเซ่ จักรวาลของใจ",
                "subtitle": "ความงามที่ยั่งยืน\\nเข้าใจธรรมชาติระดับเซลล์",
                "motion": "slow_zoom_in",
                "motion_speed": "slow",
                "motion_intensity": 0.10,
                "focus": "center",
                "transition": "fade_black",
                "wan": {
                    "prompt": "Mamase brand outro, glowing cyan orbiting planet in dark navy space, peaceful and contemplative, no text.",
                    "negative_prompt": "flicker, jitter, blurry",
                    "seed": 1000,
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
        "title": "วิตามินเอ กู้คอลลาเจนได้จริงไหม? วิทยาศาสตร์ผิวหนังมีคำตอบ 🧬✨",
        "description": "ในโลกของสกินแคร์ มีสารเพียงกลุ่มเดียวเท่านั้นที่งานวิจัยทางการแพทย์ทั่วโลกรับรองตรงกันว่าเป็น Gold Standard ในการกู้และสร้างคอลลาเจนใหม่ได้จริง นั่นคือ 'วิตามินเอและกลุ่มเรตินอยด์' (Retinoids)\n\nคลิปนี้จะพาคุณเจาะลึกกลไกชีววิทยาความงามในระดับเซลล์:\n• ทำไมผิวถึงสูญเสียคอลลาเจนปีละ 1% หลังอายุ 20?\n• บันไดการแปลงรูปของเรตินอยด์ (Retinol ➔ Retinal ➔ Retinoic Acid)\n• เรตินัล (Retinal) ทำงานเร็วกว่าเรตินอล 11 เท่าและช่วยคุมสิวได้อย่างไร?\n• นวัตกรรมโมเลกุลยุคใหม่อย่าง HPR ที่จับตัวรับตรงโดยไม่ระคายเคือง\n• พลังสองด้าน: สั่งสร้าง Pro-Collagen ใหม่ พร้อมสั่งบล็อกเอนไซม์ MMP ไม่ให้มาย่อยสลายคอลลาเจนเดิม\n• กฎเหล็ก 3 ข้อในการใช้ให้ปลอดภัยและเห็นผลยั่งยืน\n\nเพราะความงามที่ยั่งยืน เริ่มต้นจากความเข้าใจธรรมชาติในระดับเซลล์\n\nค้นพบโลก ค้นพบใจ กับ Mamase จักรวาลของใจ\n\n#วิทยาศาสตร์และความงาม #วิตามินเอ #เรตินอล #เรตินัล #คอลลาเจน #สกินแคร์ #Retinol #Retinal #Retinoids #SkincareScience #Dermatology #AntiAging #Collagen #Mamase #จักรวาลของใจ #Shorts #YouTubeShorts #Reels #TikTok"
    }
    meta_path = package_dir / "video-metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Created {meta_path}")

    # 5. Build clean ZIP
    zip_path = dist_dir / "vitamin-a-collagen-10scenes.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for file_path in sorted(package_dir.rglob("*")):
            if file_path.is_file() and not file_path.name.startswith("."):
                archive.write(file_path, file_path.relative_to(package_dir).as_posix())
    print(f"Created ZIP archive: {zip_path}")

if __name__ == "__main__":
    main()
