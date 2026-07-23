import os, sys
from PIL import Image

sys.stdout.reconfigure(encoding="utf-8")
d = r"D:\_Means\MIMO_CODE\BL\mimocode-windows-x64-baseline\春节档院线电影\posters"
MAX_WIDTH = 300
QUALITY = 75

total_saved = 0
for f in os.listdir(d):
    fp = os.path.join(d, f)
    orig = os.path.getsize(fp)
    if orig < 30000:
        continue
    try:
        img = Image.open(fp)
        if img.width > MAX_WIDTH:
            ratio = MAX_WIDTH / img.width
            img = img.resize((MAX_WIDTH, int(img.height * ratio)), Image.LANCZOS)
        img.save(fp, "JPEG", quality=QUALITY, optimize=True)
        new_size = os.path.getsize(fp)
        saved = orig - new_size
        total_saved += saved
        print(f"  {f}: {orig//1024}KB -> {new_size//1024}KB (saved {saved//1024}KB)")
    except Exception as e:
        print(f"  ERROR {f}: {e}")

print(f"\nTotal saved: {total_saved//1024}KB ({total_saved//1024//1024}MB)")
