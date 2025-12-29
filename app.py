import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha Eterno", layout="wide")
st.title("💰 Mi Control Permanente")

# Conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Leer los datos de la planilla
df = conn.read()

# --- PANEL DE CARGA ---
st.sidebar.header("🕹️ Nuevo Registro")
with st.sidebar.form("formulario"):
    tipo = st.selectbox("Tipo", ["Gasto", "Ingreso"])
    f = st.date_input("Fecha", date.today())
    
    if tipo == "Ingreso":
        cat = st.selectbox("Categoría", ["Sueldo", "Aguinaldo", "Varios"])
        met = st.selectbox("Donde ingresó", ["Cuenta Bancaria", "Efectivo"])
    else:
        cat = st.selectbox("Categoría", ["Colegio", "Comida", "Transporte", "Hogar", "Otros"])
        met = st.selectbox("Método", ["Efectivo", "Tarjeta Débito", "Visa Ctes", "Visa Nación", "MasterCard"])
    
    monto = st.number_input("Monto ($)", min_value=0.0)
    
    if st.form_submit_button("Guardar en Google Sheets"):
        nuevo_registro = pd.DataFrame([{
            "Fecha": str(f),
            "Tipo": tipo,
            "Estado": "Realizado",
            "Categoría": cat,
            "Monto": monto,
            "Metodo": met,
            "Descripción": ""
        }])
        
        # Unir datos nuevos con los viejos
        df_final = pd.concat([df, nuevo_registro], ignore_index=True)
        
        # Subir a Google Sheets
        conn.update(data=df_final)
        st.success("¡Guardado para siempre!")
        st.rerun()

# --- VISUALIZACIÓN ---
if not df.empty:
    st.subheader("📊 Resumen de Gastos")
    fig = px.pie(df[df["Tipo"]=="Gasto"], values='Monto', names='Categoría')
    st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("📝 Historial en la Nube")
    st.dataframe(df, use_container_width=True)
else:
    st.info("Todavía no hay datos en tu Google Sheet.")
