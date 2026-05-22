import streamlit as st
from PIL import Image, ImageFilter
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

st.title("🎨 Generador de Nube de Emojis HD")

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
        "angle": 12
    },

    "Angry": {
        "file": os.path.join(BASE_DIR, "angry.png"),
        "angle": -5
    },

    "Sorpresa": {
        "file": os.path.join(BASE_DIR, "sorpresa.png"),
        "angle": -14
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
# FUNCIÓN DE COLISIÓN SUAVE
# =========================================================

def hay_choque(nueva_caja, cajas_ocupadas, tolerancia=0.20):

    n_izq, n_arr, n_der, n_aba = nueva_caja

    for caja in cajas_ocupadas:

        c_izq, c_arr, c_der, c_aba = caja

        overlap_x = min(n_der, c_der) - max(n_izq, c_izq)
        overlap_y = min(n_aba, c_aba) - max(n_arr, c_arr)

        if overlap_x > 0 and overlap_y > 0:

            area_overlap = overlap_x * overlap_y

            area_nueva = (
                (n_der - n_izq) *
                (n_aba - n_arr)
            )

            if area_overlap > area_nueva * tolerancia:
                return True

    return False

# =========================================================
# GENERADOR PRINCIPAL
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
    # CONTROL DE ESCALA
    # =====================================================

    MIN_SIZE = 90
    MAX_SIZE = 340

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
        # ROTAR PRIMERO (MEJOR CALIDAD)
        # =================================================

        img = img.rotate(
            config["angle"],
            expand=True,
            resample=Image.Resampling.BICUBIC
        )

        # =================================================
        # ESCALA LIMITADA
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
        # DISTRIBUCIÓN GRAVITACIONAL
        # =================================================

        max_dist = 180 - (peso * 1.2)
        max_dist = max(40, max_dist)

        colocado = False

        for _ in range(2500):

            theta = random.uniform(
                0,
                2 * math.pi
            )

            # distribución compacta
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

                # =========================================
                # SOMBRA SUAVE
                # =========================================

                shadow = Image.new(
                    "RGBA",
                    img.size,
                    (0, 0, 0, 70)
                )

                shadow = shadow.filter(
                    ImageFilter.GaussianBlur(14)
                )

                lienzo.paste(
                    shadow,
                    (x + 10, y + 14),
                    shadow
                )

                # =========================================
                # PEGAR EMOJI
                # =========================================

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

        padding = 50

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

if st.button("✨ Generar Nube HD"):

    with st.spinner("Renderizando nube..."):

        imagen_final = generar_nube(pesos)

        st.image(
            imagen_final,
            use_container_width=True
        )

        # =================================================
        # DESCARGA PNG
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
            file_name="nube_emojis_hd.png",
            mime="image/png"
        )
