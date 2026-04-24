"""Genera uploads/og-preview.jpg (1200x630) para previews de WhatsApp/FB/IG."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "uploads", "Brownie 2 pisos manjar y chocolate .png")
OUT = os.path.join(ROOT, "uploads", "og-preview.jpg")

TARGET = (1200, 630)

# 1. Cargar foto base y recortar/escalar a 1200x630 (cover)
img = Image.open(SRC).convert("RGB")
sw, sh = img.size
tw, th = TARGET
src_ratio = sw / sh
tgt_ratio = tw / th
if src_ratio > tgt_ratio:
    # source too wide, crop sides
    new_w = int(sh * tgt_ratio)
    x0 = (sw - new_w) // 2
    img = img.crop((x0, 0, x0 + new_w, sh))
else:
    # source too tall, crop top/bottom
    new_h = int(sw / tgt_ratio)
    y0 = (sh - new_h) // 2
    img = img.crop((0, y0, sw, y0 + new_h))
img = img.resize(TARGET, Image.LANCZOS)

# 2. Dos capas: oscurecido general + gradiente columna para la zona del texto
img = img.convert("RGBA")

# capa 1: oscurecido general muy leve
darken = Image.new("RGBA", TARGET, (0, 0, 0, 60))
img = Image.alpha_composite(img, darken)

# capa 2: gradiente columna (izquierda sólida oscura, difumina a la derecha)
gradient = Image.new("RGBA", TARGET, (0, 0, 0, 0))
draw_ov = ImageDraw.Draw(gradient)
SOLID_END = int(tw * 0.40)
FADE_END  = int(tw * 0.72)
for x in range(tw):
    if x < SOLID_END:
        alpha = 220
    elif x < FADE_END:
        t = (x - SOLID_END) / (FADE_END - SOLID_END)
        alpha = int(220 * (1 - t))
    else:
        alpha = 0
    draw_ov.line([(x, 0), (x, th)], fill=(12, 5, 2, alpha))
img = Image.alpha_composite(img, gradient).convert("RGB")

# 3. Texto
draw = ImageDraw.Draw(img)

FONT_DIR = "C:/Windows/Fonts"
def font(name, size):
    path = os.path.join(FONT_DIR, name)
    return ImageFont.truetype(path, size) if os.path.exists(path) else ImageFont.load_default()

f_eyebrow = font("arial.ttf", 22)
f_title_a = font("georgiai.ttf", 92)  # italic
f_title_b = font("georgia.ttf", 92)
f_sub = font("arial.ttf", 28)
f_url = font("arialbd.ttf", 24)

PAD = 72
CREAM = (245, 237, 230)
CARAMEL = (217, 160, 99)
MUTED = (200, 185, 170)

# Eyebrow
eyebrow = "GUAYAQUIL  ·  ECUADOR"
draw.text((PAD, 80), eyebrow, font=f_eyebrow, fill=CARAMEL, spacing=4)

# Títulos en 2 líneas
y = 130
draw.text((PAD, y), "Brownies", font=f_title_b, fill=CREAM)
y += 100
draw.text((PAD, y), "que no se olvidan.", font=f_title_a, fill=CARAMEL)

# Subtítulo
y += 130
draw.text((PAD, y), "Artesanales, hechos a mano por Gigi.", font=f_sub, fill=MUTED)

# URL / CTA abajo
draw.rectangle([(PAD, th - 85), (PAD + 4, th - 45)], fill=CARAMEL)
draw.text((PAD + 18, th - 82), "luz-da-lua.vercel.app", font=f_url, fill=CREAM)

# 4. Guardar optimizado
img.save(OUT, "JPEG", quality=86, optimize=True, progressive=True)
sz = os.path.getsize(OUT) // 1024
print(f"OK {OUT} | {img.size} | {sz} KB")
