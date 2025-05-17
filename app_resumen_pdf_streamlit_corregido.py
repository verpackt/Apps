
import streamlit as st
import fitz  # PyMuPDF
from io import BytesIO
import openai
import re

st.set_page_config(page_title="Resumen de Libros en PDF", layout="wide")
st.title("IA: Resumen y Audio de Libros en PDF")

# Paso 1: Subir PDF
uploaded_file = st.file_uploader("Carga tu archivo PDF", type=["pdf"])

# Paso 2: Configurar OpenAI API Key
openai_api_key = st.text_input("Tu clave API de OpenAI (requerida para resumir)", type="password")

# Función para dividir texto por capítulos
def dividir_por_capitulos(texto):
    capitulos = re.split(r'(Cap[ií]tulo\s+\d+|Chapter\s+\d+)', texto, flags=re.IGNORECASE)
    estructura = []
    for i in range(1, len(capitulos), 2):
        titulo = capitulos[i].strip()
        contenido = capitulos[i+1].strip() if (i+1) < len(capitulos) else ""
        estructura.append((titulo, contenido))
    return estructura

# Paso 3: Procesar PDF
if uploaded_file and openai_api_key:
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
            openai.api_key = openai_api_key
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
            )
            resumen = response["choices"][0]["message"]["content"]
            st.success("Resumen generado")
            st.write(resumen)

    st.subheader("Resúmenes por capítulo")
    capitulos = dividir_por_capitulos(full_text)
    for i, (titulo, contenido) in enumerate(capitulos):
        if st.button(f"Resumen para {titulo}"):
            with st.spinner(f"Resumiendo {titulo}..."):
                prompt = f"Resume el siguiente capitulo del libro titulado '{titulo}':\n\n{contenido[:4000]}"
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                )
                resumen = response["choices"][0]["message"]["content"]
                st.markdown(f"### {titulo}")
                st.write(resumen)
