import io
from pathlib import Path

import qrcode
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = Path(__file__).resolve().parents[2] / "assets" / "fonts"
GREEN = (46, 158, 67)
INK = (22, 32, 26)
DIM = (110, 125, 115)


def make_badge(full_name: str, grade: str | None, qr_token: str,
               school: str = "Trinityhouse Centurion") -> bytes:
    sg = str(FONT_DIR / "SpaceGrotesk.ttf")
    inter = str(FONT_DIR / "Inter.ttf")
    f_brand = ImageFont.truetype(sg, 46)
    f_name = ImageFont.truetype(sg, 50)
    f_sub = ImageFont.truetype(inter, 30)
    f_small = ImageFont.truetype(inter, 24)

    W, H = 620, 860
    card = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(card)
    d.rectangle([0, 0, W, 120], fill=GREEN)
    d.text((W / 2, 60), "GuardianGate", font=f_brand, fill="white", anchor="mm")

    qr = qrcode.QRCode(border=2, box_size=10,
                       error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(qr_token)
    qr.make(fit=True)
    qimg = qr.make_image(fill_color="black", back_color="white") \
              .convert("RGB").resize((380, 380), Image.NEAREST)
    card.paste(qimg, ((W - 380) // 2, 190))

    d.text((W / 2, 630), full_name, font=f_name, fill=INK, anchor="mm")
    d.text((W / 2, 685), grade or "", font=f_sub, fill=DIM, anchor="mm")
    d.text((W / 2, 730), school, font=f_sub, fill=GREEN, anchor="mm")
    d.line([60, 790, W - 60, 790], fill=(220, 230, 223), width=2)
    d.text((W / 2, 820), "Scan at the gate  ·  Learner pickup pass",
           font=f_small, fill=DIM, anchor="mm")

    buf = io.BytesIO()
    card.save(buf, format="PNG")
    return buf.getvalue()