"""
SCRIPT 4 - GENERADOR DE QR PARA RESEÑAS
Genera un QR personalizado por negocio que lleva directo
a su página de Google Reviews. Listo para imprimir.
"""

import qrcode
import os
from PIL import Image, ImageDraw, ImageFont

def generar_qr(nombre_negocio: str, google_link: str) -> str:
    nombre_limpio = nombre_negocio.replace(" ", "_").replace("/", "-")
    archivo = f"QR_{nombre_limpio}.png"
    ruta = os.path.join(os.path.dirname(__file__), archivo)

    # Generar QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(google_link)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    qr_w, qr_h = qr_img.size

    # Crear imagen final con texto
    padding = 40
    texto_header = f"⭐ Déjanos tu reseña en Google"
    texto_negocio = nombre_negocio
    texto_footer = "Escanea el código con tu cámara"

    canvas_w = qr_w + padding * 2
    canvas_h = qr_h + padding * 4 + 120

    canvas = Image.new("RGB", (canvas_w, canvas_h), "white")
    draw = ImageDraw.Draw(canvas)

    # Intentar usar fuente del sistema, si no usa default
    try:
        font_grande = ImageFont.truetype("arial.ttf", 28)
        font_negocio = ImageFont.truetype("arialbd.ttf", 32)
        font_pequena = ImageFont.truetype("arial.ttf", 22)
    except:
        font_grande = ImageFont.load_default()
        font_negocio = font_grande
        font_pequena = font_grande

    # Texto arriba
    draw.text((canvas_w // 2, padding), texto_header, fill="black", font=font_grande, anchor="mt")
    draw.text((canvas_w // 2, padding + 40), texto_negocio, fill="#1F7A4A", font=font_negocio, anchor="mt")

    # QR centrado
    qr_x = (canvas_w - qr_w) // 2
    qr_y = padding + 90
    canvas.paste(qr_img, (qr_x, qr_y))

    # Texto abajo
    draw.text((canvas_w // 2, qr_y + qr_h + 20), texto_footer, fill="#666666", font=font_pequena, anchor="mt")

    # Línea decorativa arriba y abajo
    draw.rectangle([padding, padding - 5, canvas_w - padding, padding - 3], fill="#1F7A4A")
    draw.rectangle([padding, canvas_h - padding + 5, canvas_w - padding, canvas_h - padding + 7], fill="#1F7A4A")

    canvas.save(ruta, "PNG", dpi=(300, 300))
    return archivo


def main():
    print("\n=== GENERADOR DE QR PARA RESEÑAS ===\n")

    nombre_negocio = input("Nombre del negocio: ").strip()
    google_link = input("Link de Google Reviews del negocio: ").strip()

    print("\nGenerando QR...")
    archivo = generar_qr(nombre_negocio, google_link)

    print(f"\nQR guardado en: {archivo}")
    print(f"Listo para imprimir en recibos, mesas o puerta del negocio.")


if __name__ == "__main__":
    main()
