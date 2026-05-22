import streamlit as st
from PIL import Image

# Configuración de la página
st.set_page_config(page_title="Nube de Emojis 3D", layout="wide")

st.title("Generador de Nube de Emojis 3D")
st.markdown("Ajusta los pesos (0-99) en la barra lateral para escalar dinámicamente cada emoji.")

# --- Configuración de Emojis ---
# Nombre, archivo local correspondiente, posición central (x, y) en lienzo de 800x600, y ángulo de rotación.
EMOJIS_CONFIG = {
    "Like": {"file": "like.png", "pos": (450, 420), "angle": -10},
    "Haha": {"file": "haha.png", "pos": (250, 320), "angle": 5},
    "Corazón": {"file": "corazon.png", "pos": (580, 220), "angle": 15},
    "Angry": {"file": "angry.png", "pos": (400, 150), "angle": -5},
    "Sorpresa": {"file": "sorpresa.png", "pos": (620, 420), "angle": -15},
    "Me entristece": {"file": "triste.png", "pos": (250, 500), "angle": 10}
}

# --- Barra lateral ---
st.sidebar.header("Configurar Pesos")
st.sidebar.markdown("Define la relevancia de cada reacción:")

pesos = {}
for emoji in EMOJIS_CONFIG.keys():
    pesos[emoji] = st.sidebar.slider(f"{emoji}", min_value=0, max_value=99, value=50)

# Configuración del Lienzo
CANVAS_WIDTH = 800
CANVAS_HEIGHT = 600
MAX_EMOJI_SIZE = 350 # Tamaño máximo en píxeles

def generar_nube(pesos):
    # Crear un lienzo transparente (RGBA)
    lienzo = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), (255, 255, 255, 0))
    
    # Ordenar emojis por peso para que los más grandes se dibujen AL FINAL (queden encima)
    emojis_ordenados = sorted(pesos.items(), key=lambda item: item[1])

    for nombre, peso in emojis_ordenados:
        if peso == 0:
            continue # Omitir si el peso es 0
            
        config = EMOJIS_CONFIG[nombre]
        
        try:
            # Abrir imagen con canal alfa
            img_emoji = Image.open(config["file"]).convert("RGBA")
        except FileNotFoundError:
            # Si no encuentra la imagen, dibuja un placeholder gris o ignora
            st.sidebar.warning(f"⚠️ Falta '{config['file']}' en la carpeta.")
            continue
            
        # Calcular tamaño proporcional al peso
        size = int(20 + (peso / 99.0) * (MAX_EMOJI_SIZE - 20))
        
        # Redimensionar
        img_emoji = img_emoji.resize((size, size), Image.Resampling.LANCZOS)
        
        # Rotar
        img_emoji = img_emoji.rotate(config["angle"], expand=True)
        
        # Calcular nuevas coordenadas tras rotación (posicionar desde el centro)
        new_w, new_h = img_emoji.size
        x_paste = config["pos"][0] - (new_w // 2)
        y_paste = config["pos"][1] - (new_h // 2)
        
        # Pegar en el lienzo usando transparencia
        lienzo.paste(img_emoji, (x_paste, y_paste), img_emoji)
        
    return lienzo

# --- Área Principal ---
col1, col2 = st.columns([1, 6], gap="small")
with col2:
    with st.spinner("Renderizando emojis..."):
        imagen_final = generar_nube(pesos)
        
        # Mostrar resultado en pantalla
        st.image(imagen_final, use_container_width=True)
        
        # Opción para descargar la imagen
        import io
        buf = io.BytesIO()
        imagen_final.save(buf, format="PNG")
        byte_im = buf.getvalue()
        
        st.download_button(
            label="⬇️ Descargar composición transparente",
            data=byte_im,
            file_name="nube_reacciones_3d.png",
            mime="image/png"
        )
