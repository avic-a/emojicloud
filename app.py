import streamlit as st
from PIL import Image
import math
import random
import io
import os

# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="Nube de Emojis HD",
    layout="wide"
)

st.title("Generador de Nube de Emojis")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================================================
# CONFIG EMOJIS
# =========================================================

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
        "angle": -12
    },

    "Me entristece": {
        "file": os.path.join(BASE_DIR, "triste.png"),
        "angle": 8
    }
}

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("⚙️ Configurar pesos")

pesos = {}

for emoji in EMOJIS_CONFIG:
    pesos[emoji] = st.sidebar.slider(
        emoji,
        min_value=0,
        max_value=100,
        value=50
    )

# =========================================================
# COLISIONES
# =========================================================

def hay_choque(nueva_caja, cajas_ocupadas, padding=18):

    n_izq, n_arr, n_der, n_aba = nueva_caja

    # separación visual mínima
    n_izq -= padding
    n_arr -= padding
    n_der += padding
    n_aba += padding

    for caja in cajas_ocupadas:

        c_izq, c_arr, c_der, c_aba = caja

        if not (
            n_der < c_izq or
            n_izq > c_der or
            n_aba < c_arr or
            n_arr > c_aba
        ):
            return True

    return False

# =========================================================
# GENERADOR
# =========================================================

def generar_nube(pesos):

    activos = {
        k: v for k, v in pesos.items()
        if v > 0
    }

    if not activos:
        return Image.new(
            "RGBA",
            (512, 512),
            (0, 0, 0, 0)
        )

    # =====================================================
    # CANVAS
    # =====================================================

    dim = 1400

    lienzo = Image.new(
        "RGBA",
        (dim, dim),
        (255, 255, 255, 0)
    )

    centro_x = dim // 2
    centro_y = dim // 2

    # =====================================================
    # ORDENAR POR PESO
    # =====================================================

    emojis_ordenados = sorted(
        activos.items(),
        key=lambda item: item[1],
        reverse=True
    )

    cajas_ocupadas = []

    # =====================================================
    # ESCALA
    # =====================================================

    MIN_SIZE = 70
    MAX_SIZE = 250

    primer_emoji = True

    # =====================================================
    # GENERAR EMOJIS
    # =====================================================

    for nombre, peso in emojis_ordenados:

        config = EMOJIS_CONFIG[nombre]

        # =================================================
        # CARGAR IMAGEN
        # =================================================

        img = Image.open(
            config["file"]
        ).convert("RGBA")

        # =================================================
        # ROTAR PRIMERO
        # =================================================

        img = img.rotate(
            config["angle"],
            expand=True,
            resample=Image.Resampling.BICUBIC
        )

        # =================================================
        # TAMAÑO CONTROLADO
        # =================================================

        nuevo_size = int(
            MIN_SIZE +
            (
                (peso / 100.0) *
                (MAX_SIZE - MIN_SIZE)
            )
        )

        img = img.resize(
            (nuevo_size, nuevo_size),
            Image.Resampling.LANCZOS
        )

        new_w, new_h = img.size

        # =================================================
        # PRIMER EMOJI CENTRADO
        # =================================================

        if primer_emoji:

            x = centro_x - new_w // 2
            y = centro_y - new_h // 2

            caja = (
                x,
                y,
                x + new_w,
                y + new_h
            )

            lienzo.paste(
                img,
                (x, y),
                img
            )

            cajas_ocupadas.append(caja)

            primer_emoji = False

            continue

        # =================================================
        # DISTRIBUCIÓN COMPACTA
        # =================================================

        max_dist = 130 - (peso * 0.8)
        max_dist = max(30, max_dist)

        colocado = False

        for _ in range(3000):

            theta = random.uniform(
                0,
                2 * math.pi
            )

            r = abs(
                random.gauss(
                    0,
                    max_dist / 2
                )
            )

            x = int(
                centro_x +
                r * math.cos(theta) -
                new_w // 2
            )

            y = int(
                centro_y +
                r * math.sin(theta) -
                new_h // 2
            )

            caja = (
                x,
                y,
                x + new_w,
                y + new_h
            )

            if not hay_choque(
                caja,
                cajas_ocupadas
            ):

                lienzo.paste(
                    img,
                    (x, y),
                    img
                )

                cajas_ocupadas.append(caja)

                colocado = True

                break

        # fallback
        if not colocado:

            lienzo.paste(
                img,
                (centro_x, centro_y),
                img
            )

    # =====================================================
    # RECORTE AUTOMÁTICO
    # =====================================================

    bbox = lienzo.getbbox()

    if bbox:

        padding = 40

        left, top, right, bottom = bbox

        bbox = (
            max(0, left - padding),
            max(0, top - padding),
            min(dim, right + padding),
            min(dim, bottom + padding)
        )

        lienzo = lienzo.crop(bbox)

    return lienzo

# =========================================================
# BOTÓN GENERAR
# =========================================================

if st.button("✨ Generar Nube"):

    with st.spinner("Renderizando..."):

        imagen_final = generar_nube(pesos)

        st.image(
            imagen_final,
            use_container_width=True
        )

        # =================================================
        # DESCARGA
        # =================================================

        buf = io.BytesIO()

        imagen_final.save(
            buf,
            format="PNG",
            optimize=True
        )

        st.download_button(
            "⬇️ Descargar PNG",
            data=buf.getvalue(),
            file_name="nube_emojis.png",
            mime="image/png"
        )
