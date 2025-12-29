import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

st.set_page_config(page_title="Finanzas Bocha Eterno", layout="wide")
st.title("💰 Mi Control Permanente")

# Crear la conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Leer los datos actuales
df = conn.read()

# --- FORMULARIO DE CARGA ---
st.sidebar.header("Nuevo Movimiento")
with st.sidebar.form("formulario"):
    tipo = st.selectbox("Tipo", ["Gasto", "Ingreso"])
    f = st.date_input("Fecha", date.today())
    if tipo == "Ingreso":
        cat = st.selectbox("Categoría", ["Sueldo", "Aguinaldo", "Varios"])
        met = st.selectbox("Medio", ["Cuenta Bancaria", "Efectivo"])
    else:
        cat = st.selectbox("Categoría", ["Colegio", "Comida", "Transporte", "Hogar", "Otros"])
        met = st.selectbox("Método", ["Efectivo", "Tarjeta Débito", "Visa Ctes", "Visa Nación", "MasterCard"])
    monto = st.number_input("Monto ($)", min_value=0.0)
    
    if st.form_submit_button("Guardar en Google"):
        # Crear el nuevo registro
        nuevo_dato = pd.DataFrame([{
            "Fecha": str(f),
            "Tipo": tipo,
            "Estado": "Realizado",
            "Categoría": cat,
            "Monto": monto,
            "Metodo": met,
            "Descripción": ""
        }])
        
        # Combinar con los datos viejos y subir
        df_actualizado = pd.concat([df, nuevo_dato], ignore_index=True)
        conn.update(data=df_actualizado)
        st.success("¡Guardado en el Excel!")
        st.rerun()

# --- MOSTRAR DATOS ---
st.subheader("Historial de la Nube")
st.dataframe(df, use_container_width=True)
