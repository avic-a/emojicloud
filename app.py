import streamlit as st
from PIL import Image
import random
import io

# --- Configuración de la página ---
st.set_page_config(page_title="Nube de Emojis 3D", layout="wide")

st.title("Generador de Nube de Emojis 3D")
st.markdown("Ajusta los pesos (0-99) en la barra lateral para escalar dinámicamente cada emoji. La posición se calculará automáticamente para evitar choques.")

# --- Configuración de Emojis ---
# Nombre, archivo local y ángulo de rotación (ya no necesitamos 'pos' fija)
EMOJIS_CONFIG = {
    "Like": {"file": "like.png", "angle": -10},
    "Haha": {"file": "haha.png", "angle": 5},
    "Corazón": {"file": "corazon.png", "angle": 15},
    "Angry": {"file": "angry.png", "angle": -5},
    "Sorpresa": {"file": "sorpresa.png", "angle": -15},
    "Me entristece": {"file": "triste.png", "angle": 10}
}

# --- Barra lateral de controles ---
st.sidebar.header("Configurar Pesos")
st.sidebar.markdown("Define la relevancia de cada reacción:")

pesos = {}
for emoji in EMOJIS_CONFIG.keys():
    pesos[emoji] = st.sidebar.slider(f"{emoji}", min_value=0, max_value=99, value=50)

# --- Constantes del Lienzo ---
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
MAX_EMOJI_SIZE = 350 # Tamaño en píxeles al alcanzar el peso de 99

# --- Funciones Core ---
def hay_choque(nueva_caja, cajas_ocupadas):
    """Verifica si la nueva caja delimitadora choca con alguna ya existente."""
    n_izq, n_arr, n_der, n_aba = nueva_caja
    
    for caja in cajas_ocupadas:
        c_izq, c_arr, c_der, c_aba = caja
        if not (n_der < c_izq or n_izq > c_der or n_aba < c_arr or n_arr > c_aba):
            return True # Hay choque
    return False # Espacio libre

def generar_nube(pesos):
    """Genera la imagen final acomodando los emojis según su peso."""
    lienzo = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), (255, 255, 255, 0))
    
    # Ordenar emojis de MAYOR a MENOR peso para acomodar primero los grandes
    emojis_ordenados = sorted(pesos.items(), key=lambda item: item, reverse=True)
    cajas_ocupadas = []

    for nombre, peso in emojis_ordenados:
        if peso == 0:
            continue
            
        config = EMOJIS_CONFIG[nombre]
        
        try:
            img_emoji = Image.open(config["file"]).convert("RGBA")
        except FileNotFoundError:
            st.sidebar.warning(f"⚠️ Falta la imagen '{config['file']}' en tu carpeta.")
            continue
            
        # Calcular tamaño y redimensionar
        size = int(20 + (peso / 99.0) * (MAX_EMOJI_SIZE - 20))
        img_emoji = img_emoji.resize((size, size), Image.Resampling.LANCZOS)
        
        # Rotar
        img_emoji = img_emoji.rotate(config["angle"], expand=True)
        new_w, new_h = img_emoji.size
        
        # Lógica de posicionamiento aleatorio con detección de colisión
        lugar_encontrado = False
        for intento in range(200): # Intentar hasta 200 veces por emoji
            x = random.randint(0, CANVAS_WIDTH - new_w)
            y = random.randint(0, CANVAS_HEIGHT - new_h)
            
            # Reducir la caja de colisión un 15% para que puedan juntarse de forma más estética
            margen_x = int(new_w * 0.15)
            margen_y = int(new_h * 0.15)
            caja_actual = (x + margen_x, y + margen_y, x + new_w - margen_x, y + new_h - margen_y)
            
            if not hay_choque(caja_actual, cajas_ocupadas):
                # Si hay espacio, se pega en el lienzo
                lienzo.paste(img_emoji, (x, y), img_emoji)
                cajas_ocupadas.append(caja_actual)
                lugar_encontrado = True
                break
                
        if not lugar_encontrado:
            st.warning(f"⚠️ El lienzo está muy lleno. No hubo espacio para '{nombre}'.")
            
    return lienzo

# --- Renderizado Final en Pantalla ---
st.markdown("---") # Línea divisoria estética en lugar de columnas

with st.spinner("Buscando espacios y renderizando..."):
    imagen_final = generar_nube(pesos)
    
    # Mostrar la imagen centrada de forma estándar
    st.image(imagen_final)
    
    # Buffer para descarga
    buf = io.BytesIO()
    imagen_final.save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    st.download_button(
        label="⬇️ Descargar Nube Transparente",
        data=byte_im,
        file_name="nube_reacciones_3d.png",
        mime="image/png"
    )
