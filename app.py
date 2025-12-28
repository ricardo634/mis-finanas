import streamlit as st
import pandas as pd
import os
from datetime import date
import plotly.express as px

# Configuración profesional de la página
st.set_page_config(page_title="Control Finanzas Bocha", page_icon="💰", layout="wide")
st.title("💰 Mi Panel de Control Financiero")
st.markdown("---")

DATA_FILE = "mis_finanzas.csv"

# Inicializar base de datos
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Fecha", "Tipo", "Estado", "Categoría", "Monto", "Metodo", "Descripción"])
    df.to_csv(DATA_FILE, index=False)

# --- BARRA LATERAL (SIDEBAR) CON REGISTROS SEPARADOS ---
st.sidebar.header("🕹️ Panel de Carga")

# 📥 FORMULARIO DE INGRESOS
with st.sidebar.expander("📥 REGISTRAR INGRESO", expanded=False):
    with st.form("form_ingresos"):
        f_ing = st.date_input("Fecha", date.today(), key="f_ing")
        cat_ing = st.selectbox("Categoría de Ingreso", ["Sueldo", "Aguinaldo", "Varios"])
        monto_ing = st.number_input("Monto ($)", min_value=0.0, format="%.2f", key="m_ing")
        met_ing = st.selectbox("¿Dónde ingresó?", ["Cuenta Bancaria", "Efectivo"], key="met_ing")
        est_ing = st.radio("Estado", ["Realizado", "Proyectado"], key="est_ing")
        desc_ing = st.text_input("Descripción", key="d_ing")
        
        if st.form_submit_button("Guardar Ingreso"):
            nuevo = pd.DataFrame([[str(f_ing), "Ingreso", est_ing, cat_ing, monto_ing, met_ing, desc_ing]], 
                                columns=["Fecha", "Tipo", "Estado", "Categoría", "Monto", "Metodo", "Descripción"])
            nuevo.to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.success("¡Ingreso guardado!")
            st.rerun()

# 📤 FORMULARIO DE GASTOS
with st.sidebar.expander("📤 REGISTRAR GASTO", expanded=True):
    with st.form("form_gastos"):
        f_gas = st.date_input("Fecha", date.today(), key="f_gas")
        cat_gas = st.selectbox("Categoría de Gasto", ["Colegio", "Comida", "Transporte", "Hogar", "Salud", "Ocio", "Servicios", "Impuestos", "Otros"])
        monto_gas = st.number_input("Monto ($)", min_value=0.0, format="%.2f", key="m_gas")
        met_gas = st.selectbox("Método de Pago", ["Efectivo", "Tarjeta Débito", "Visa Ctes", "Visa Nación", "MasterCard"])
        est_gas = st.radio("Estado", ["Realizado", "Proyectado"], key="est_gas")
        desc_gas = st.text_input("Descripción", key="d_gas")
        
        if st.form_submit_button("Guardar Gasto"):
            nuevo = pd.DataFrame([[str(f_gas), "Gasto", est_gas, cat_gas, monto_gas, met_gas, desc_gas]], 
                                columns=["Fecha", "Tipo", "Estado", "Categoría", "Monto", "Metodo", "Descripción"])
            nuevo.to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.success("¡Gasto guardado!")
            st.rerun()

# --- CARGAR DATOS ---
df = pd.read_csv(DATA_FILE)

# --- TABS PRINCIPALES ---
tab_resumen, tab_pendientes, tab_historial = st.tabs(["📊 Resumen", "✅ Confirmar Pendientes", "📝 Historial"])

with tab_resumen:
    if not df.empty:
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df_mes = df[df['Fecha'].dt.month == date.today().month]
        
        if not df_mes.empty:
            ing_tot = df_mes[df_mes["Tipo"] == "Ingreso"]["Monto"].sum()
            gas_real = df_mes[(df_mes["Tipo"] == "Gasto") & (df_mes["Estado"] == "Realizado")]["Monto"].sum()
            gas_proy = df_mes[(df_mes["Tipo"] == "Gasto") & (df_mes["Estado"] == "Proyectado")]["Monto"].sum()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Ingresos Totales", f"${ing_tot:,.2f}")
            c2.metric("Gastos Realizados", f"${gas_real:,.2f}")
            c3.metric("Saldo Real (en mano)", f"${ing_tot - gas_real:,.2f}")
            
            st.divider()
            col_a, col_b = st.columns(2)
            with col_a:
                df_ing = df_mes[df_mes["Tipo"] == "Ingreso"]
                if not df_ing.empty:
                    fig_i = px.pie(df_ing, values='Monto', names='Categoría', title="Origen de Ingresos", hole=0.4)
                    st.plotly_chart(fig_i, use_container_width=True)
            with col_b:
                df_gas = df_mes[df_mes["Tipo"] == "Gasto"]
                if not df_gas.empty:
                    fig_g = px.pie(df_gas, values='Monto', names='Categoría', title="Gastos por Categoría", hole=0.4)
                    st.plotly_chart(fig_g, use_container_width=True)
    else:
        st.info("La base de datos está vacía. Empezá cargando tus movimientos en la izquierda.")

with tab_pendientes:
    st.subheader("Movimientos Proyectados")
    pendientes = df[df["Estado"] == "Proyectado"]
    if not pendientes.empty:
        for i, r in pendientes.iterrows():
            with st.expander(f"📅 {r['Fecha']} - {r['Categoría']}: ${r['Monto']} ({r['Tipo']})"):
                cx, cy = st.columns(2)
                opciones = ["Efectivo", "Tarjeta Débito", "Visa Ctes", "Visa Nación", "MasterCard"] if r["Tipo"] == "Gasto" else ["Cuenta Bancaria", "Efectivo"]
                nuevo_m = cx.selectbox("Confirmar Medio:", opciones, key=f"conf_{i}")
                if cy.button("Confirmar Realizado", key=f"btn_{i}"):
                    df.at[i, "Estado"] = "Realizado"
                    df.at[i, "Metodo"] = nuevo_m
                    df.to_csv(DATA_FILE, index=False)
                    st.rerun()
    else:
        st.write("✅ Todo al día. No tenés pendientes.")

with tab_historial:
    st.dataframe(df.sort_values(by="Fecha", ascending=False), use_container_width=True)