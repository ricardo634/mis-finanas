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

# --- PANEL DE CARGA (IZQUIERDA) ---
st.sidebar.header("🕹️ Panel de Carga")

with st.sidebar.expander("📥 REGISTRAR INGRESO"):
    with st.form("form_ingresos"):
        f_ing = st.date_input("Fecha", date.today(), key="f_ing")
        cat_ing = st.selectbox("Categoría", ["Sueldo", "Aguinaldo", "Varios"])
        monto_ing = st.number_input("Monto ($)", min_value=0.0, format="%.2f", key="m_ing")
        met_ing = st.selectbox("¿Dónde ingresó?", ["Cuenta Bancaria", "Efectivo"])
        est_ing = st.radio("Estado", ["Realizado", "Proyectado"], key="est_ing")
        if st.form_submit_button("Guardar Ingreso"):
            nuevo = pd.DataFrame([[str(f_ing), "Ingreso", est_ing, cat_ing, monto_ing, met_ing, ""]], columns=["Fecha", "Tipo", "Estado", "Categoría", "Monto", "Metodo", "Descripción"])
            nuevo.to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.rerun()

with st.sidebar.expander("📤 REGISTRAR GASTO", expanded=True):
    with st.form("form_gastos"):
        f_gas = st.date_input("Fecha", date.today(), key="f_gas")
        cat_gas = st.selectbox("Categoría", ["Colegio", "Comida", "Transporte", "Hogar", "Salud", "Ocio", "Servicios", "Impuestos", "Otros"])
        monto_gas = st.number_input("Monto ($)", min_value=0.0, format="%.2f", key="m_gas")
        met_gas = st.selectbox("Método", ["Efectivo", "Tarjeta Débito", "Visa Ctes", "Visa Nación", "MasterCard"])
        est_gas = st.radio("Estado", ["Realizado", "Proyectado"], key="est_gas")
        if st.form_submit_button("Guardar Gasto"):
            nuevo = pd.DataFrame([[str(f_gas), "Gasto", est_gas, cat_gas, monto_gas, met_gas, ""]], columns=["Fecha", "Tipo", "Estado", "Categoría", "Monto", "Metodo", "Descripción"])
            nuevo.to_csv(DATA_FILE, mode='a', header=False, index=False)
            st.rerun()

# --- CARGAR DATOS ---
df = pd.read_csv(DATA_FILE)

# --- TABS ---
tab_resumen, tab_pendientes, tab_historial = st.tabs(["📊 Resumen", "✅ Confirmar Pendientes", "📝 Historial y Edición"])

with tab_resumen:
    if not df.empty:
        df['Fecha'] = pd.to_datetime(df['Fecha'])
        df_mes = df[df['Fecha'].dt.month == date.today().month]
        if not df_mes.empty:
            ing = df_mes[df_mes["Tipo"] == "Ingreso"]["Monto"].sum()
            gas = df_mes[(df_mes["Tipo"] == "Gasto") & (df_mes["Estado"] == "Realizado")]["Monto"].sum()
            c1, c2, c3 = st.columns(3)
            c1.metric("Ingresos", f"${ing:,.2f}")
            c2.metric("Gastos Realizados", f"${gas:,.2f}")
            c3.metric("Saldo Real", f"${ing - gas:,.2f}")
            col_a, col_b = st.columns(2)
            fig_i = px.pie(df_mes[df_mes["Tipo"]=="Ingreso"], values='Monto', names='Categoría', title="Ingresos")
            col_a.plotly_chart(fig_i, use_container_width=True)
            fig_g = px.pie(df_mes[df_mes["Tipo"]=="Gasto"], values='Monto', names='Categoría', title="Gastos")
            col_b.plotly_chart(fig_g, use_container_width=True)

with tab_pendientes:
    p = df[df["Estado"] == "Proyectado"]
    if not p.empty:
        for i, r in p.iterrows():
            with st.expander(f"{r['Fecha']} - {r['Categoría']}: ${r['Monto']}"):
                if st.button("Confirmar Pago", key=f"p_{i}"):
                    df.at[i, "Estado"] = "Realizado"
                    df.to_csv(DATA_FILE, index=False)
                    st.rerun()
    else:
        st.write("No hay pendientes.")

with tab_historial:
    if not df.empty:
        st.dataframe(df.sort_values(by="Fecha", ascending=False), use_container_width=True)
        st.divider()
        c_del, c_edit = st.columns(2)
        with c_del:
            idx_del = st.number_input("ID de fila a borrar:", min_value=0, max_value=len(df)-1, step=1)
            if st.button("Eliminar Registro", type="primary"):
                df = df.drop(df.index[idx_del])
                df.to_csv(DATA_FILE, index=False)
                st.rerun()
        with c_edit:
            idx_ed = st.number_input("ID de fila a editar:", min_value=0, max_value=len(df)-1, step=1)
            nuevo_m = st.number_input("Nuevo Monto:", min_value=0.0)
            if st.button("Actualizar"):
                df.at[idx_ed, "Monto"] = nuevo_m
                df.to_csv(DATA_FILE, index=False)
                st.rerun()
