
import streamlit as st
import fitz  # PyMuPDF
from io import BytesIO
import openai
import re

st.set_page_config(page_title="Resumen de Libros en PDF (División flexible)", layout="wide")
st.title("IA: Resumen y Audio de Libros en PDF")

# Paso 1: Subir PDF
uploaded_file = st.file_uploader("Carga tu archivo PDF", type=["pdf"])

# Paso 2: Configurar OpenAI API Key
openai_api_key = st.text_input("Tu API Key de OpenAI (formato sk-proj-...)", type="password")

# Inicializar cliente OpenAI
client = None
if openai_api_key:
    client = openai.OpenAI(api_key=openai_api_key)

# Función mejorada para dividir capítulos
def dividir_por_capitulos(texto):
    texto = texto.replace("\n", " ").replace("\r", " ").replace("\t", " ").replace("
", " ")
    texto_normalizado = texto.lower()

    # Buscar encabezados comunes
    matches = re.split(r'(cap[ií]tulo\s+\d+|chapter\s+\d+|secci[oó]n\s+\d+|parte\s+\w+)', texto_normalizado, flags=re.IGNORECASE)

    estructura = []
    if len(matches) > 1:
        for i in range(1, len(matches), 2):
            titulo = matches[i].strip().capitalize()
            contenido = matches[i+1].strip() if (i+1) < len(matches) else ""
            estructura.append((titulo, contenido))
    else:
        # Fallback: dividir por bloques grandes si no hay encabezados
        bloques = re.split(r'(\n\s*\n){2,}', texto)
        for i, bloque in enumerate(bloques):
            if len(bloque.strip()) > 300:
                estructura.append((f"Sección {i+1}", bloque.strip()))
    return estructura

# Paso 3: Procesar PDF
if uploaded_file and client:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    full_text = ""
    for page in doc:
        full_text += page.get_text()

    st.subheader("Resumen general")
    if st.button("Generar resumen general"):
        with st.spinner("Generando resumen..."):
            prompt = (
                "Resume el siguiente contenido de un libro como si fuera una sinopsis ejecutiva de 1 a 2 paginas:\n\n"
                + full_text[:6000]
            )
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
            )
            resumen = response.choices[0].message.content
            st.success("Resumen generado")
            st.write(resumen)

    st.subheader("Resúmenes por capítulo o sección")
    capitulos = dividir_por_capitulos(full_text)
    for i, (titulo, contenido) in enumerate(capitulos):
        if st.button(f"Resumen para {titulo}", key=f"boton_{i}"):
            with st.spinner(f"Resumiendo {titulo}..."):
                prompt = f"Resume el siguiente contenido titulado '{titulo}':\n\n{contenido[:4000]}"
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                )
                resumen = response.choices[0].message.content
                st.markdown(f"### {titulo}")
                st.write(resumen)
