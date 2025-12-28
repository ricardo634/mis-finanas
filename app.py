import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha", page_icon="💰", layout="wide")

DATA_FILE = "mis_finanzas.csv"

# Cargar datos
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Fecha", "Tipo", "Estado", "Categoría", "Monto", "Metodo"])
    df.to_csv(DATA_FILE, index=False)

df = pd.read_csv(DATA_FILE)

# --- BARRA LATERAL (CARGA) ---
st.sidebar.header("🕹️ Registro")
with st.sidebar.form("form_carga"):
    tipo = st.selectbox("Tipo", ["Gasto", "Ingreso"])
    f = st.date_input("Fecha", date.today())
    if tipo == "Ingreso":
        cat = st.selectbox("Categoría", ["Sueldo", "Aguinaldo", "Varios"])
        met = st.selectbox("Medio", ["Cuenta Bancaria", "Efectivo"])
    else:
        cat = st.selectbox("Categoría", ["Colegio", "Comida", "Transporte", "Hogar", "Salud", "Ocio", "Servicios", "Impuestos", "Otros"])
        met = st.selectbox("Método", ["Efectivo", "Tarjeta Débito", "Visa Ctes", "Visa Nación", "MasterCard"])
    monto = st.number_input("Monto ($)", min_value=0.0)
    estado = st.radio("Estado", ["Realizado", "Proyectado"])
    if st.form_submit_button("Guardar"):
        nuevo = pd.DataFrame([[str(f), tipo, estado, cat, monto, met]], columns=df.columns)
        nuevo.to_csv(DATA_FILE, mode='a', header=False, index=False)
        st.rerun()

# --- CUERPO PRINCIPAL ---
tab1, tab2 = st.tabs(["📊 Resumen", "📝 Historial y Edición"])

with tab1:
    if not df.empty:
        c1, c2 = st.columns(2)
        fig1 = px.pie(df[df["Tipo"]=="Gasto"], values='Monto', names='Categoría', title="Gastos")
        c1.plotly_chart(fig1, use_container_width=True)
        fig2 = px.pie(df[df["Tipo"]=="Ingreso"], values='Monto', names='Categoría', title="Ingresos")
        c2.plotly_chart(fig2, use_container_width=True)

with tab2:
    if not df.empty:
        st.subheader("Historial de Movimientos")
        # Mostramos el DataFrame con el índice para saber qué fila borrar
        st.dataframe(df, use_container_width=True)
        
        st.divider()
        col_del, col_edit = st.columns(2)
        
        with col_del:
            st.subheader("🗑️ Borrar Registro")
            fila_a_borrar = st.number_input("Número de fila a eliminar:", min_value=0, max_value=len(df)-1, step=1)
            if st.button("Eliminar Fila Seleccionada", type="primary"):
                df = df.drop(df.index[fila_a_borrar])
                df.to_csv(DATA_FILE, index=False)
                st.success(f"Fila {fila_a_borrar} eliminada.")
                st.rerun()

        with col_edit:
            st.subheader("✏️ Editar Monto Rápido")
            fila_a_editar = st.number_input("Número de fila a editar:", min_value=0, max_value=len(df)-1, step=1)
            nuevo_monto = st.number_input("Nuevo Monto ($):", min_value=0.0)
            if st.button("Actualizar Monto"):
                df.at[fila_a_editar, "Monto"] = nuevo_monto
                df.to_csv(DATA_FILE, index=False)
                st.success("Monto actualizado.")
                st.rerun()
    else:
        st.info("No hay datos para mostrar.")
