import streamlit as st
from PIL import Image
import math
import random
import io
import os

# --- Configuración de página ---
st.set_page_config(page_title="Nube de Emojis 3D", layout="wide")
st.title("Generador de Nube Gravitacional (Alta Definición)")

# Asegúrate de que las imágenes estén en la misma carpeta que app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

EMOJIS_CONFIG = {
    "Like": {"file": os.path.join(BASE_DIR, "like.png"), "angle": -10},
    "Haha": {"file": os.path.join(BASE_DIR, "haha.png"), "angle": 5},
    "Corazón": {"file": os.path.join(BASE_DIR, "corazon.png"), "angle": 15},
    "Angry": {"file": os.path.join(BASE_DIR, "angry.png"), "angle": -5},
    "Sorpresa": {"file": os.path.join(BASE_DIR, "sorpresa.png"), "angle": -15},
    "Me entristece": {"file": os.path.join(BASE_DIR, "triste.png"), "angle": 10}
}

st.sidebar.header("Configurar Pesos")
pesos = {emoji: st.sidebar.slider(f"{emoji}", 0, 99, 50) for emoji in EMOJIS_CONFIG}

def hay_choque(nueva_caja, cajas_ocupadas):
    n_izq, n_arr, n_der, n_aba = nueva_caja
    for caja in cajas_ocupadas:
        c_izq, c_arr, c_der, c_aba = caja
        if not (n_der < c_izq or n_izq > c_der or n_aba < c_arr or n_arr > c_aba):
            return True
    return False

def generar_nube(pesos):
    activos = {k: v for k, v in pesos.items() if v > 0}
    if not activos: return Image.new("RGBA", (512, 512), (0,0,0,0))
    
    dim = 2400 
    lienzo = Image.new("RGBA", (dim, dim), (255, 255, 255, 0))
    centro_x, centro_y = dim // 2, dim // 2
    
    emojis_ordenados = sorted(activos.items(), key=lambda item: item, reverse=True)
    cajas_ocupadas = []

    for nombre, peso in emojis_ordenados:
        config = EMOJIS_CONFIG[nombre]
        img = Image.open(config["file"]).convert("RGBA")
        
        # Tamaño basado en 512px
        escala = 0.4 + (peso / 99.0) * 0.6
        nuevo_size = int(512 * escala)
        img = img.resize((nuevo_size, nuevo_size), Image.Resampling.LANCZOS)
        img = img.rotate(config["angle"], expand=True)
        new_w, new_h = img.size
        
        max_dist = 500 * (1.0 - (peso / 99.0))
        
        for _ in range(1000):
            theta = random.uniform(0, 2 * math.pi)
            r = random.uniform(0, max_dist)
            x = int(centro_x + r * math.cos(theta) - new_w // 2)
            y = int(centro_y + r * math.sin(theta) - new_h // 2)
            
            caja = (x, y, x + new_w, y + new_h)
            if not hay_choque(caja, cajas_ocupadas):
                lienzo.paste(img, (x, y), img)
                cajas_ocupadas.append(caja)
                break
                
    # Corrección lógica del BBOX
    bbox = lienzo.getbbox()
    if bbox:
        padding = 50
        # Ahora ajustamos cada valor de la tupla (left, top, right, bottom)
        left, top, right, bottom = bbox
        bbox = (max(0, left - padding), max(0, top - padding), 
                min(dim, right + padding), min(dim, bottom + padding))
        return lienzo.crop(bbox)
    return lienzo

# --- Renderizado ---
if st.button("Generar Nube HD"):
    with st.spinner("Renderizando..."):
        imagen_final = generar_nube(pesos)
        st.image(imagen_final, use_container_width=True) 
        
        buf = io.BytesIO()
        imagen_final.save(buf, format="PNG", optimize=True)
        st.download_button("⬇️ Descargar Nube HD", buf.getvalue(), "nube_hd.png", "image/png")
