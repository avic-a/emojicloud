import streamlit as st
from PIL import Image
import math
import random
import io
import os

# =====================================================
# CONFIGURACIÓN
# =====================================================

st.set_page_config(
    page_title="Emoji Cloud Spiral - Círculo Invisible",
    layout="wide"
)

st.title("🌀 Emoji Cloud Spiral Packing (Alta Calidad)")

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
# SIDEBAR (pesos + radio del círculo)
# =====================================================

st.sidebar.header("⚙️ Pesos")
pesos = {}
for emoji in EMOJIS_CONFIG:
    pesos[emoji] = st.sidebar.slider(emoji, 0, 100, 50)

radio_circulo = st.sidebar.slider("📏 Radio del círculo (píxeles)", 300, 800, 600)

# =====================================================
# FUNCIONES AUXILIARES
# =====================================================

def hay_choque(x, y, radio, elementos, padding_factor=0.07):
    """Detecta colisión con una separación adicional (padding)"""
    for ex, ey, er in elementos:
        distancia = math.hypot(x - ex, y - ey)
        padding = min(radio, er) * padding_factor
        if distancia < (radio + er + padding):
            return True
    return False

def dentro_del_circulo(x, y, radio, centro_x, centro_y, radio_limite):
    """Verifica que el emoji completo esté dentro del círculo invisible"""
    dist_al_centro = math.hypot(x - centro_x, y - centro_y)
    return dist_al_centro + radio <= radio_limite

def calcular_escala(peso):
    """Curva que acentúa diferencias entre pesos pequeños y medianos"""
    p = peso / 100.0
    escala = 0.05 + (p ** 1.8) * 0.80
    escala = max(0.05, min(0.85, escala))
    return escala

# =====================================================
# GENERACIÓN DE LA NUBE (contenedor circular, alta calidad)
# =====================================================

def generar_nube(pesos, radio_circulo):
    activos = {k: v for k, v in pesos.items() if v > 0}
    if not activos:
        return Image.new("RGBA", (400, 400), (0, 0, 0, 0))

    # Lienzo grande (se puede aumentar a 2400 para más resolución)
    dim = 1600
    lienzo = Image.new("RGBA", (dim, dim), (255, 255, 255, 0))
    centro_x = dim // 2
    centro_y = dim // 2

    # Ordenar de mayor a menor peso
    emojis_ordenados = sorted(activos.items(), key=lambda x: x[1], reverse=True)
    elementos = []  # lista de (x, y, radio_colision)

    for idx, (nombre, peso) in enumerate(emojis_ordenados):
        config = EMOJIS_CONFIG[nombre]

        # Cargar, rotar y redimensionar con alta calidad
        img_original = Image.open(config["file"]).convert("RGBA")
        img_rotada = img_original.rotate(
            config["angle"],
            expand=True,
            resample=Image.Resampling.BICUBIC
        )

        escala = calcular_escala(peso)
        nuevo_w = int(512 * escala)
        nuevo_h = int(512 * escala)

        # MÍNIMO 60x60 para mantener calidad visible
        nuevo_w = max(25, nuevo_w)
        nuevo_h = max(25, nuevo_h)
        # NUNCA agrandar más de 512 (respetar original)
        nuevo_w = min(512, nuevo_w)
        nuevo_h = min(512, nuevo_h)

        img = img_rotada.resize((nuevo_w, nuevo_h), Image.Resampling.LANCZOS)
        w, h = img.size
        radio = int(max(w, h) * 0.38)  # radio de colisión (ligeramente mayor que el visual)

        # Primer emoji: centro
        if idx == 0:
            x, y = centro_x, centro_y
            if dentro_del_circulo(x, y, radio, centro_x, centro_y, radio_circulo):
                lienzo.paste(img, (x - w // 2, y - h // 2), img)
                elementos.append((x, y, radio))
            else:
                # Si no cabe (raro), reducimos más
                nueva_escala = (radio_circulo * 2) / max(w, h) * 0.8
                nuevo_w2 = int(512 * nueva_escala)
                nuevo_h2 = int(512 * nueva_escala)
                nuevo_w2 = max(60, min(512, nuevo_w2))
                nuevo_h2 = max(60, min(512, nuevo_h2))
                img = img_rotada.resize((nuevo_w2, nuevo_h2), Image.Resampling.LANCZOS)
                w, h = img.size
                radio = int(max(w, h) * 0.38)
                lienzo.paste(img, (centro_x - w//2, centro_y - h//2), img)
                elementos.append((centro_x, centro_y, radio))
            continue

        # Búsqueda espiral dentro del círculo
        colocado = False
        max_intentos = 18000
        for t in range(max_intentos):
            angle = t * 0.15
            # Espiral logarítmica con ligera aleatoriedad
            spiral_radius = 2.5 * math.sqrt(t) + random.uniform(-1.0, 1.0)
            x = int(centro_x + math.cos(angle) * spiral_radius)
            y = int(centro_y + math.sin(angle) * spiral_radius)

            if not dentro_del_circulo(x, y, radio, centro_x, centro_y, radio_circulo):
                continue
            if not hay_choque(x, y, radio, elementos, padding_factor=0.07):
                lienzo.paste(img, (x - w // 2, y - h // 2), img)
                elementos.append((x, y, radio))
                colocado = True
                break

        # Fallback en el borde del círculo
        if not colocado:
            for angulo in range(0, 360, 15):
                rad = math.radians(angulo)
                x = int(centro_x + (radio_circulo - radio) * math.cos(rad))
                y = int(centro_y + (radio_circulo - radio) * math.sin(rad))
                if not hay_choque(x, y, radio, elementos, padding_factor=0.05):
                    lienzo.paste(img, (x - w // 2, y - h // 2), img)
                    elementos.append((x, y, radio))
                    colocado = True
                    break
            if not colocado:  # último recurso (casi nunca ocurre)
                lienzo.paste(img, (centro_x - w//2, centro_y - h//2), img)
                elementos.append((centro_x, centro_y, radio))

    # Recorte automático para eliminar bordes vacíos
    bbox = lienzo.getbbox()
    if bbox:
        padding = 40
        left, top, right, bottom = bbox
        bbox = (max(0, left - padding), max(0, top - padding),
                min(dim, right + padding), min(dim, bottom + padding))
        lienzo = lienzo.crop(bbox)

    # (Opcional) Dibujar el círculo de guía (descomentar para ver el borde)
    # from PIL import ImageDraw
    # draw = ImageDraw.Draw(lienzo)
    # draw.ellipse((centro_x-radio_circulo, centro_y-radio_circulo, centro_x+radio_circulo, centro_y+radio_circulo), outline="red", width=2)

    return lienzo

# =====================================================
# RENDER Y DESCARGA (ALTA CALIDAD)
# =====================================================

if st.button("✨ Generar Nube de Alta Calidad"):
    with st.spinner("Colocando emojis dentro del círculo (máxima calidad)..."):
        imagen_final = generar_nube(pesos, radio_circulo)

        # Mostrar sin reescalado de Streamlit (ancho fijo)
        st.image(imagen_final, width=800)   # ← evita pixelado

        # Descargar PNG sin compresión
        buf = io.BytesIO()
        imagen_final.save(buf, format="PNG", compress_level=0)
        st.download_button(
            "⬇️ Descargar PNG (Máxima Calidad)",
            data=buf.getvalue(),
            file_name="emoji_cloud_circular_alta_calidad.png",
            mime="image/png"
        )
