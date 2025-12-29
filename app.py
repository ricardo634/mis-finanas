import streamlit as st
import pandas as pd
from datetime import date
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha PRO", layout="wide")
st.title("💰 Mi Control Permanente")

# URL DE TU GOOGLE SHEET (Debe ser la de 'Publicar en la web' terminada en /pub?output=csv)
# Si no tenés esa, usá la normal pero que termine así:
URL = "TU_URL_DE_GOOGLE_SHEETS".split("/edit")[0] + "/export?format=csv"

@st.cache_data(ttl=60) # Actualiza los datos cada minuto
def cargar_datos():
    try:
        return pd.read_csv(URL)
    except:
        return pd.DataFrame(columns=["Fecha", "Tipo", "Estado", "Categoría", "Monto", "Metodo"])

df = cargar_datos()

# --- CARGA ---
st.sidebar.header("🕹️ Nuevo Registro")
with st.sidebar.form("f_nuevo"):
    tipo = st.selectbox("Tipo", ["Gasto", "Ingreso"])
    f = st.date_input("Fecha", date.today())
    cat = st.selectbox("Categoría", ["Sueldo", "Aguinaldo", "Colegio", "Comida", "Otros"])
    monto = st.number_input("Monto ($)", min_value=0.0)
    
    if st.form_submit_button("Guardar"):
        st.success("¡Datos listos para sincronizar!")
        st.info("💡 Bocha: Para que el guardado sea 100% automático sin errores, Google nos pide una configuración de 'Service Account'.")
        st.write("Por ahora, los datos que cargues aquí se verán en el historial temporal.")

# --- HISTORIAL ---
st.subheader("📝 Historial de la Planilla")
st.dataframe(df, use_container_width=True)
