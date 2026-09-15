import os
from PIL import Image, ImageDraw, ImageFont

def main():
    img_dir = "/Users/zengcode/projects/autoclip/assets/angkor_cinematic_documentary/images"
    os.makedirs(img_dir, exist_ok=True)
    width, height = 1920, 1080 # Horizontal 16:9

    for i in range(1, 17):
        img = Image.new("RGB", (width, height), (30, 45, i * 10 % 255))
        draw = ImageDraw.Draw(img)
        text = f"Scene {i:02d} Placeholder\nWaiting for AI API Quota"
        
        # Try to load a generic font, or fallback
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Thonburi.ttc", 80)
        except:
            font = ImageFont.load_default()
            
        # Draw centered text roughly
        draw.text((width//2 - 400, height//2 - 100), text, fill=(255, 255, 255), font=font)
        
        # Save
        out_path = os.path.join(img_dir, f"scene-{i:02d}.png")
        img.save(out_path)
        print(f"Generated {out_path}")

if __name__ == "__main__":
    main()
