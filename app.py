import streamlit as st
from PIL import Image
import math
import random
import io
import os

# =====================================================
# CONFIG
# =====================================================

st.set_page_config(
    page_title="Emoji Cloud Spiral",
    layout="wide"
)

st.title("🌀 Emoji Cloud Spiral Packing")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EMOJIS_CONFIG = {
    "Like": {
        "file": os.path.join(BASE_DIR, "like.png"),
        "angle": -8
    },
    "Haha": {
        "file": os.path.join(BASE_DIR, "haha.png"),
        "angle": 6
    },
    "Corazón": {
        "file": os.path.join(BASE_DIR, "corazon.png"),
        "angle": 10
    },
    "Angry": {
        "file": os.path.join(BASE_DIR, "angry.png"),
        "angle": -5
    },
    "Sorpresa": {
        "file": os.path.join(BASE_DIR, "sorpresa.png"),
        "angle": -10
    },
    "Me entristece": {
        "file": os.path.join(BASE_DIR, "triste.png"),
        "angle": 7
    }
}

# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.header("⚙️ Pesos")

pesos = {}
for emoji in EMOJIS_CONFIG:
    pesos[emoji] = st.sidebar.slider(emoji, 0, 100, 50)

# =====================================================
# COLLISION (más ajustada)
# =====================================================

def hay_choque(x, y, radio, elementos):
    for ex, ey, er in elementos:
        distancia = math.sqrt((x - ex) ** 2 + (y - ey) ** 2)
        # === CAMBIO: padding reducido de 0.06 a 0.02 ===
        padding = min(radio, er) * 0.02
        if distancia < (radio + er + padding):
            return True
    return False

# =====================================================
# ESCALA (más pronunciada para pesos pequeños/medianos)
# =====================================================

def calcular_escala(peso):
    p = peso / 100.0
    # === CAMBIO: nueva curva con mayor contraste ===
    escala = 0.05 + (p ** 1.8) * 0.80
    escala = max(0.05, min(0.85, escala))
    return escala

# =====================================================
# SPIRAL PACKING (radio y espiral más compactos)
# =====================================================

def generar_nube(pesos):
    activos = {k: v for k, v in pesos.items() if v > 0}
    if not activos:
        return Image.new("RGBA", (400, 400), (0, 0, 0, 0))

    dim = 1600
    lienzo = Image.new("RGBA", (dim, dim), (255, 255, 255, 0))
    centro_x = dim // 2
    centro_y = dim // 2

    emojis_ordenados = sorted(activos.items(), key=lambda x: x[1], reverse=True)
    elementos = []

    for idx, (nombre, peso) in enumerate(emojis_ordenados):
        config = EMOJIS_CONFIG[nombre]

        img_original = Image.open(config["file"]).convert("RGBA")
        img_original = img_original.rotate(config["angle"], expand=True, resample=Image.Resampling.BICUBIC)

        escala = calcular_escala(peso)
        nuevo_w = int(512 * escala)
        nuevo_h = int(512 * escala)
        nuevo_w = max(40, nuevo_w)
        nuevo_h = max(40, nuevo_h)
        img = img_original.resize((nuevo_w, nuevo_h), Image.Resampling.LANCZOS)

        w, h = img.size
        # === CAMBIO: radio de colisión más pequeño (0.30 en lugar de 0.36) ===
        radio = int(max(w, h) * 0.30)

        # Primer elemento va al centro
        if idx == 0:
            x, y = centro_x, centro_y
            lienzo.paste(img, (x - w // 2, y - h // 2), img)
            elementos.append((x, y, radio))
            continue

        # Búsqueda en espiral (más densa)
        colocado = False
        for t in range(0, 12000):
            angle = t * 0.15
            # === CAMBIO: radio espiral reducido y menor aleatoriedad ===
            spiral_radius = 2.5 * math.sqrt(t) + random.uniform(-0.8, 0.8)
            x = int(centro_x + math.cos(angle) * spiral_radius)
            y = int(centro_y + math.sin(angle) * spiral_radius)

            if not hay_choque(x, y, radio, elementos):
                lienzo.paste(img, (x - w // 2, y - h // 2), img)
                elementos.append((x, y, radio))
                colocado = True
                break

        # Fallback (casi nunca ocurre con los nuevos parámetros)
        if not colocado:
            x = centro_x + random.randint(-20, 20)
            y = centro_y + random.randint(-20, 20)
            lienzo.paste(img, (x - w // 2, y - h // 2), img)

    # Recorte automático
    bbox = lienzo.getbbox()
    if bbox:
        padding = 35
        left, top, right, bottom = bbox
        bbox = (max(0, left - padding), max(0, top - padding),
                min(dim, right + padding), min(dim, bottom + padding))
        lienzo = lienzo.crop(bbox)

    return lienzo

# =====================================================
# RENDER
# =====================================================

if st.button("✨ Generar Nube"):
    with st.spinner("Renderizando nube..."):
        imagen_final = generar_nube(pesos)
        st.image(imagen_final, use_container_width=True)

        buf = io.BytesIO()
        imagen_final.save(buf, format="PNG")
        st.download_button("⬇️ Descargar PNG", data=buf.getvalue(),
                           file_name="emoji_cloud_spiral.png", mime="image/png")
