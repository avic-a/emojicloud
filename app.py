import streamlit as st
from PIL import Image
import math
import random
import io
import os

# =====================================================
# CONFIGURACIÓN GENERAL
# =====================================================

st.set_page_config(
    page_title="Nube Emojis HD",
    layout="wide"
)

st.title("🎨 Nube de Emojis HD")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =====================================================
# CONFIG EMOJIS
# =====================================================

EMOJIS_CONFIG = {
    "Like": {
        "file": os.path.join(BASE_DIR, "like.png"),
        "angle": -6
    },

    "Haha": {
        "file": os.path.join(BASE_DIR, "haha.png"),
        "angle": 5
    },

    "Corazón": {
        "file": os.path.join(BASE_DIR, "corazon.png"),
        "angle": 8
    },

    "Angry": {
        "file": os.path.join(BASE_DIR, "angry.png"),
        "angle": -4
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

    pesos[emoji] = st.sidebar.slider(
        emoji,
        0,
        100,
        50
    )

# =====================================================
# COLISIONES
# =====================================================

def hay_choque(
    x,
    y,
    radio,
    elementos
):

    for ex, ey, er in elementos:

        distancia = math.sqrt(
            (x - ex) ** 2 +
            (y - ey) ** 2
        )

        # padding MUY pequeño para compactar
        padding = min(radio, er) * 0.04

        distancia_minima = (
            radio + er + padding
        )

        if distancia < distancia_minima:
            return True

    return False

# =====================================================
# GENERADOR
# =====================================================

def generar_nube(pesos):

    activos = {
        k: v for k, v in pesos.items()
        if v > 0
    }

    if not activos:

        return Image.new(
            "RGBA",
            (500, 500),
            (0,0,0,0)
        )

    # =================================================
    # CANVAS
    # =================================================

    dim = 1200

    lienzo = Image.new(
        "RGBA",
        (dim, dim),
        (255,255,255,0)
    )

    centro_x = dim // 2
    centro_y = dim // 2

    # =================================================
    # ORDENAR
    # =================================================

    emojis_ordenados = sorted(
        activos.items(),
        key=lambda x: x[1],
        reverse=True
    )

    elementos = []

    primer = True

    total_emojis = len(emojis_ordenados)

    # =================================================
    # LOOP PRINCIPAL
    # =================================================

    for i, (nombre, peso) in enumerate(emojis_ordenados):

        config = EMOJIS_CONFIG[nombre]

        # =============================================
        # CARGAR ORIGINAL
        # =============================================

        img_original = Image.open(
            config["file"]
        ).convert("RGBA")

        # =============================================
        # ROTAR PRIMERO
        # =============================================

        img_original = img_original.rotate(
            config["angle"],
            expand=True,
            resample=Image.Resampling.BICUBIC
        )

        # =============================================
        # ESCALA MUY AGRESIVA
        # =============================================

        peso_normalizado = peso / 100

        escala = (
            0.04 +
            (peso_normalizado ** 3.2) * 0.62
        )

        escala = max(0.05, escala)
        escala = min(0.68, escala)

        # =============================================
        # TAMAÑO
        # =============================================

        nuevo_w = int(512 * escala)
        nuevo_h = int(512 * escala)

        nuevo_w = min(nuevo_w, 512)
        nuevo_h = min(nuevo_h, 512)

        # mínimo visual
        nuevo_w = max(nuevo_w, 26)
        nuevo_h = max(nuevo_h, 26)

        img = img_original.resize(
            (nuevo_w, nuevo_h),
            Image.Resampling.LANCZOS
        )

        w, h = img.size

        # =============================================
        # RADIO MÁS REAL
        # =============================================

        radio = int(max(w, h) * 0.28)

        # =============================================
        # EMOJI PRINCIPAL
        # =============================================

        if primer:

            x = centro_x
            y = centro_y

            lienzo.paste(
                img,
                (
                    x - w // 2,
                    y - h // 2
                ),
                img
            )

            elementos.append(
                (x, y, radio)
            )

            primer = False

            continue

        # =============================================
        # DISTRIBUCIÓN RADIAL COMPACTA
        # =============================================

        colocado = False

        for intento in range(300):

            # =========================================
            # ÁNGULO ESTABLE
            # =========================================

            angulo_base = (
                (2 * math.pi / total_emojis)
                * i
            )

            angulo = (
                angulo_base +
                random.uniform(-0.12, 0.12)
            )

            # =========================================
            # DISTANCIA MUCHO MÁS COMPACTA
            # =========================================

            radio_principal = elementos[0][2]

            # emojis pequeños MUY pegados
            factor_peso = 1.0 - peso_normalizado

            distancia_base = (
                radio_principal * 0.82 +
                radio * 0.65
            )

            distancia = (
                distancia_base +
                (factor_peso * 28)
            )

            # expansión gradual mínima
            distancia += intento * 1.2

            x = int(
                centro_x +
                math.cos(angulo) * distancia
            )

            y = int(
                centro_y +
                math.sin(angulo) * distancia
            )

            if not hay_choque(
                x,
                y,
                radio,
                elementos
            ):

                lienzo.paste(
                    img,
                    (
                        x - w // 2,
                        y - h // 2
                    ),
                    img
                )

                elementos.append(
                    (x, y, radio)
                )

                colocado = True

                break

        # =============================================
        # FALLBACK
        # =============================================

        if not colocado:

            x = centro_x + random.randint(-15, 15)
            y = centro_y + random.randint(-15, 15)

            lienzo.paste(
                img,
                (
                    x - w // 2,
                    y - h // 2
                ),
                img
            )

    # =================================================
    # RECORTE AUTOMÁTICO
    # =================================================

    bbox = lienzo.getbbox()

    if bbox:

        padding = 25

        left, top, right, bottom = bbox

        bbox = (
            max(0, left - padding),
            max(0, top - padding),
            min(dim, right + padding),
            min(dim, bottom + padding)
        )

        lienzo = lienzo.crop(bbox)

    return lienzo

# =====================================================
# BOTÓN
# =====================================================

if st.button("✨ Generar Nube"):

    with st.spinner("Renderizando..."):

        imagen_final = generar_nube(pesos)

        st.image(
            imagen_final,
            use_container_width=True
        )

        # =============================================
        # DESCARGA
        # =============================================

        buf = io.BytesIO()

        imagen_final.save(
            buf,
            format="PNG"
        )

        st.download_button(
            "⬇️ Descargar PNG",
            data=buf.getvalue(),
            file_name="nube_emojis_hd.png",
            mime="image/png"
        )
