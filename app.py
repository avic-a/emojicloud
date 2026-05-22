import streamlit as st
from PIL import Image
import math
import random
import io

# --- Configuración de página ---
st.set_page_config(page_title="Nube de Emojis 3D", layout="wide")
st.title("Generador de Nube Gravitacional")

# --- Configuración ---
EMOJIS_CONFIG = {
    "Like": {"file": "like.png", "angle": -10},
    "Haha": {"file": "haha.png", "angle": 5},
    "Corazón": {"file": "corazon.png", "angle": 15},
    "Angry": {"file": "angry.png", "angle": -5},
    "Sorpresa": {"file": "sorpresa.png", "angle": -15},
    "Me entristece": {"file": "triste.png", "angle": 10}
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
    if not activos: return Image.new("RGBA", (256, 256), (0,0,0,0))
    
    # 1. Lienzo inicial grande para trabajar
    dim = 1200 
    lienzo = Image.new("RGBA", (dim, dim), (255, 255, 255, 0))
    centro_x, centro_y = dim // 2, dim // 2
    
    emojis_ordenados = sorted(activos.items(), key=lambda item: item, reverse=True)
    cajas_ocupadas = []

    for nombre, peso in emojis_ordenados:
        config = EMOJIS_CONFIG[nombre]
        img = Image.open(config["file"]).convert("RGBA")
        
        # Escala: peso 0 -> 30% del original (76px), peso 99 -> 100% (256px)
        escala = 0.3 + (peso / 99.0) * 0.7
        nuevo_size = int(256 * escala)
        img = img.resize((nuevo_size, nuevo_size), Image.Resampling.LANCZOS)
        img = img.rotate(config["angle"], expand=True)
        new_w, new_h = img.size
        
        # 2. Gravedad: los más pesados buscan radio más pequeño hacia el centro
        factor_gravedad = 1.0 - (peso / 99.0)
        max_dist = 250 * factor_gravedad
        
        for _ in range(500):
            theta = random.uniform(0, 2 * math.pi)
            r = random.uniform(0, max_dist)
            x = int(centro_x + r * math.cos(theta) - new_w / 2)
            y = int(centro_y + r * math.sin(theta) - new_h / 2)
            
            # Margen de colisión del 15%
            margen = int(new_w * 0.15)
            caja = (x + margen, y + margen, x + new_w - margen, y + new_h - margen)
            
            if not hay_choque(caja, cajas_ocupadas):
                lienzo.paste(img, (x, y), img)
                cajas_ocupadas.append(caja)
                break
                
    # 3. Recorte: ajustar al contenido real
    bbox = lienzo.getbbox()
    return lienzo.crop(bbox) if bbox else lienzo

# --- Renderizado ---
if st.button("Generar Nube Gravitacional"):
    with st.spinner("Calculando órbitas..."):
        imagen_final = generar_nube(pesos)
        st.image(imagen_final)
        
        buf = io.BytesIO()
        imagen_final.save(buf, format="PNG")
        st.download_button("Descargar Nube", buf.getvalue(), "nube_gravity.png", "image/png")
