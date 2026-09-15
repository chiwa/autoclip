import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

def make_star_glow(size, color, core_radius, corona_radius, spikes=True, num_spikes=4, spike_length=150):
    """Generates a high-dynamic range volumetric star with coronas, glow, and optional diffraction spikes."""
    w, h = size
    cx, cy = w // 2, h // 2
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    
    # 1. Broad soft outer halo / interstellar scattered glow
    outer_halo = Image.new("RGBA", size, (0, 0, 0, 0))
    d_halo = ImageDraw.Draw(outer_halo)
    for r in range(corona_radius * 2, corona_radius // 2, -4):
        alpha = int(25 * (1.0 - (r / (corona_radius * 2)) ** 0.5))
        if alpha > 0:
            d_halo.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(color[0], color[1], color[2], alpha))
    outer_halo = outer_halo.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, outer_halo)

    # 2. Main stellar corona
    corona = Image.new("RGBA", size, (0, 0, 0, 0))
    d_corona = ImageDraw.Draw(corona)
    for r in range(corona_radius, core_radius, -2):
        t = (r - core_radius) / (corona_radius - core_radius)
        alpha = int(140 * (1.0 - t ** 0.7))
        if alpha > 0:
            d_corona.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(color[0], color[1], color[2], alpha))
    corona = corona.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, corona)

    # 3. Diffraction spikes (cinematic astrophysical telescope look)
    if spikes:
        spike_layer = Image.new("RGBA", size, (0, 0, 0, 0))
        d_spike = ImageDraw.Draw(spike_layer)
        angles = [45 + i * (360 / num_spikes) for i in range(num_spikes)]
        for angle in angles:
            rad = math.radians(angle)
            dx = math.cos(rad)
            dy = math.sin(rad)
            # Tapered spike
            for dist in range(core_radius, spike_length, 2):
                t = dist / spike_length
                alpha = int(180 * (1.0 - t ** 0.5))
                thickness = max(1, int(3 * (1.0 - t)))
                px = cx + dx * dist
                py = cy + dy * dist
                d_spike.ellipse([px - thickness, py - thickness, px + thickness, py + thickness],
                                fill=(min(255, color[0] + 40), min(255, color[1] + 40), min(255, color[2] + 40), alpha))
                # opposite side
                opx = cx - dx * dist
                opy = cy - dy * dist
                d_spike.ellipse([opx - thickness, opy - thickness, opx + thickness, opy + thickness],
                                fill=(min(255, color[0] + 40), min(255, color[1] + 40), min(255, color[2] + 40), alpha))
        spike_layer = spike_layer.filter(ImageFilter.GaussianBlur(1.5))
        img = Image.alpha_composite(img, spike_layer)

    # 4. Brilliant super-dense stellar core (pure brilliant white with tinted inner glow)
    core = Image.new("RGBA", size, (0, 0, 0, 0))
    d_core = ImageDraw.Draw(core)
    for r in range(core_radius, 0, -1):
        t = r / core_radius
        # Blending color to pure white
        cr = int(color[0] * t + 255 * (1.0 - t))
        cg = int(color[1] * t + 255 * (1.0 - t))
        cb = int(color[2] * t + 255 * (1.0 - t))
        d_core.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(cr, cg, cb, 255))
    core = core.filter(ImageFilter.GaussianBlur(1.5))
    img = Image.alpha_composite(img, core)

    return img

def main():
    W, H = 1080, 1920
    canvas = Image.new("RGBA", (W, H), (4, 6, 14, 255))

    # --- 1. Base Observatory Plate (ESO Paranal VLT Telescope & Terrace) ---
    # We load scratch/telescope_lasers_milkyway_3000.jpg
    eso_plate_path = "scratch/telescope_lasers_milkyway_3000.jpg"
    eso_img = Image.open(eso_plate_path).convert("RGBA")
    
    # We crop and scale the ESO plate to anchor the bottom/middle:
    # ESO image is 3000 x 1608.
    # The telescope domes and observatory platform are around the bottom half.
    # Let's scale it so the platform and domes fit nicely in the lower 45% (y=1050..1920)
    # Target width = 1080, target height for bottom slice = 950
    # Let's inspect ESO proportions: 3000w x 1608h.
    # If we take a slice x=400..2600, y=600..1608:
    eso_crop = eso_img.crop((300, 500, 2700, 1608))
    eso_crop = eso_crop.resize((W, int(W * (1608 - 500) / (2700 - 300))), Image.Resampling.LANCZOS)
    # eso_crop height is approx 500px. Let's make it fill from y=1000 to y=1920 (920px height)
    eso_bg = eso_img.crop((200, 300, 2800, 1608)).resize((W, 1100), Image.Resampling.LANCZOS)
    
    # Create an atmospheric dark gradient for the top sky (y=0..1200)
    # Deep midnight indigo to cosmic black, with soft southern stars
    sky_plate = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d_sky = ImageDraw.Draw(sky_plate)
    
    # Soft background cosmic glow
    for y in range(H):
        if y < 800:
            # Clean dark typography space (y=0..800)
            # Gentle vertical gradient from deep cosmic blue-black (6, 9, 20) to (8, 12, 26)
            t = y / 800.0
            r = int(6 + 3 * t)
            g = int(8 + 5 * t)
            b = int(18 + 10 * t)
            d_sky.line([(0, y), (W, y)], fill=(r, g, b, 255))
        elif y < 1200:
            t = (y - 800) / 400.0
            r = int(9 + 8 * t)
            g = int(13 + 12 * t)
            b = int(28 + 20 * t)
            d_sky.line([(0, y), (W, y)], fill=(r, g, b, 255))
    
    canvas = Image.alpha_composite(canvas, sky_plate)
    
    # Blend the ESO observatory platform into the bottom (y=1000..1920)
    # Create smooth feather mask for ESO platform top edge
    eso_mask = Image.new("L", (W, eso_bg.height), 255)
    d_mask = ImageDraw.Draw(eso_mask)
    fade_h = 250
    for y in range(fade_h):
        alpha = int(255 * (y / fade_h) ** 1.5)
        d_mask.line([(0, y), (W, y)], fill=alpha)
        
    canvas.paste(eso_bg, (0, H - eso_bg.height), eso_mask)

    # Add realistic subtle starry background in upper sky (sparse, non-distracting, clean)
    np.random.seed(42)
    stars_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d_stars = ImageDraw.Draw(stars_layer)
    for _ in range(160):
        sx = np.random.randint(20, W - 20)
        sy = np.random.randint(20, 1100)
        # Avoid heavy clutter in title zone (y=190..500)
        if 180 < sy < 520 and np.random.rand() > 0.3:
            continue
        brightness = np.random.randint(40, 210)
        size = 1 if np.random.rand() > 0.15 else 2
        col = (brightness, brightness, min(255, brightness + 30), brightness)
        if size == 1:
            d_stars.point((sx, sy), fill=col)
        else:
            d_stars.ellipse([sx - 1, sy - 1, sx + 1, sy + 1], fill=col)
    stars_layer = stars_layer.filter(ImageFilter.GaussianBlur(0.4))
    canvas = Image.alpha_composite(canvas, stars_layer)

    # --- 2. Hero Subject: Alpha Centauri Binary System (A & B) + Proxima Centauri ---
    # Position: In the upper-mid sky (y=820..1100), right-of-center (x=500..950)
    # Alpha Centauri A: Brilliant G2V yellow-white sun (like our Sun, 1.1 M☉)
    # Alpha Centauri B: Warm K1V orange-amber sun (0.9 M☉), close companion
    # Proxima Centauri: Small M5.5 red dwarf with ruby glow, slightly separated
    
    # Alpha Centauri A
    star_a = make_star_glow((450, 450), color=(255, 230, 170), core_radius=22, corona_radius=95, spikes=True, num_spikes=4, spike_length=180)
    # Alpha Centauri B (slightly smaller, warmer amber)
    star_b = make_star_glow((380, 380), color=(255, 185, 110), core_radius=16, corona_radius=75, spikes=True, num_spikes=4, spike_length=140)
    # Proxima Centauri (red dwarf, distinct separation)
    star_p = make_star_glow((220, 220), color=(255, 80, 70), core_radius=8, corona_radius=35, spikes=False)

    # Composite Alpha Centauri A & B into a shared interacting gravitational glow
    system_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    
    # Mutual glowing gas bridge / stellar envelope
    bridge = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d_bridge = ImageDraw.Draw(bridge)
    # Center positions:
    # Star A at (680, 890)
    # Star B at (810, 930) (distance ~135px, authentic close binary visual perspective)
    # Proxima at (540, 830) (offset to upper left)
    pos_a = (680, 890)
    pos_b = (810, 930)
    pos_p = (540, 830)
    
    # Soft mutual glow between A and B
    d_bridge.ellipse([pos_a[0] - 140, pos_a[1] - 110, pos_b[0] + 140, pos_b[1] + 110], fill=(255, 200, 130, 35))
    bridge = bridge.filter(ImageFilter.GaussianBlur(30))
    system_layer = Image.alpha_composite(system_layer, bridge)

    # Paste stars (centering at pos)
    system_layer.paste(star_a, (pos_a[0] - 225, pos_a[1] - 225), star_a)
    system_layer.paste(star_b, (pos_b[0] - 190, pos_b[1] - 190), star_b)
    system_layer.paste(star_p, (pos_p[0] - 110, pos_p[1] - 110), star_p)

    canvas = Image.alpha_composite(canvas, system_layer)

    # --- 3. Story Anchors: Standing Mamase Explorer & Alert Golden Retriever ---
    # From where_space_begins_reel scene-01-hook.png, we extract the explorer
    # In where_space_begins_reel, 'พี' is standing looking up at the sky, wearing his glasses and expedition coat!
    ref_path = "assets/where_space_begins_reel/images/scene-01-hook.png"
    ref_img = Image.open(ref_path).convert("RGBA")
    
    # Let's inspect where_space_begins explorer:
    # He is in the lower-left standing on a hill/platform looking up.
    # We extract him with a clean feathered mask and composite him onto the observatory deck!
    
    # Explorer crop from where_space_begins (approx x=0..500, y=950..1920)
    explorer_crop = ref_img.crop((0, 950, 520, 1920))
    
    # Extract alpha mask for explorer:
    # In where_space_begins, the sky behind him is dark blue/black.
    # We can create a precision cutout using luminance thresholding + feathering:
    exp_np = np.array(explorer_crop)
    # The figure has coat (beige/brown/black), skin, hair. The background is dark space (R<30, G<35, B<50).
    # Let's inspect or make a smooth alpha:
    bg_dist = np.maximum.reduce([exp_np[:, :, 0], exp_np[:, :, 1], exp_np[:, :, 2]])
    
    # More robust: create a clean composite mask for the standing explorer
    mask = Image.new("L", explorer_crop.size, 0)
    # In where_space_begins, the explorer is roughly within polygon
    d_m = ImageDraw.Draw(mask)
    # Human silhouette polygon coordinates
    # Let's inspect the actual dimensions and subject in where_space_begins
    print(f"Explorer crop size: {explorer_crop.size}")
    
    # We also have the golden retriever. Let's make sure the dog is standing/sitting beside him cleanly,
    # completely free of square seams, grounded on the observatory terrace.

if __name__ == "__main__":
    main()
