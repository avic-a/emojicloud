import streamlit as st
from PIL import Image
import math
import random
import io

# --- Configuración de página ---
st.set_page_config(page_title="Nube de Emojis 3D", layout="wide")
st.title("Generador de Nube Gravitacional (Alta Definición)")

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
    
    # 1. Lienzo amplio (2000x2000) para evitar que los elementos se amontonen y pixelen.
    # Esto permite que los emojis mantengan su resolución de 512x512.
    dim = 2000 
    lienzo = Image.new("RGBA", (dim, dim), (255, 255, 255, 0))
    centro_x, centro_y = dim // 2, dim // 2
    
    emojis_ordenados = sorted(activos.items(), key=lambda item: item, reverse=True)
    cajas_ocupadas = []

    for nombre, peso in emojis_ordenados:
        config = EMOJIS_CONFIG[nombre]
        img = Image.open(config["file"]).convert("RGBA")
        
        # 2. Ajuste de tamaño proporcional sin perder calidad
        # Usamos 512 como base. Si el peso es bajo, el emoji es pequeño pero mantiene nitidez.
        escala = 0.4 + (peso / 99.0) * 0.6 
        nuevo_size = int(512 * escala)
        
        # Usamos Resampling.LANCZOS para mantener bordes suaves en alta definición
        img = img.resize((nuevo_size, nuevo_size), Image.Resampling.LANCZOS)
        img = img.rotate(config["angle"], expand=True)
        new_w, new_h = img.size
        
        # 3. Gravedad controlada
        # Los más pesados buscan el centro, pero con un radio que les permite no superponerse
        max_dist = 400 * (1.0 - (peso / 100.0))
        
        for _ in range(1000): # Más intentos para asegurar una posición sin choques
            theta = random.uniform(0, 2 * math.pi)
            r = random.uniform(0, max_dist)
            x = int(centro_x + r * math.cos(theta) - new_w // 2)
            y = int(centro_y + r * math.sin(theta) - new_h // 2)
            
            caja = (x, y, x + new_w, y + new_h)
            if not hay_choque(caja, cajas_ocupadas):
                lienzo.paste(img, (x, y), img)
                cajas_ocupadas.append(caja)
                break
                
    # 4. Recorte ajustado al contenido para no desperdiciar espacio
    bbox = lienzo.getbbox()
    # Añadimos un pequeño margen (padding) de 50px para que no queden pegados al borde
    if bbox:
        padding = 50
        bbox = (max(0, bbox-padding), max(0, bbox-padding), 
                min(dim, bbox+padding), min(dim, bbox+padding))
        return lienzo.crop(bbox)
    return lienzo

# --- Renderizado ---
if st.button("Generar Nube HD"):
    with st.spinner("Renderizando en alta definición..."):
        imagen_final = generar_nube(pesos)
        # Visualización ajustada en pantalla
        st.image(imagen_final, use_container_width=True) 
        
        buf = io.BytesIO()
        # Guardado en máxima calidad
        imagen_final.save(buf, format="PNG", optimize=True, compress_level=0)
        st.download_button("⬇️ Descargar Nube HD", buf.getvalue(), "nube_hd.png", "image/png")
