import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha PRO", layout="wide", page_icon="💰")

# --- ENLACES ---
# Asegurate de que este link termine en pub?output=csv
EXCEL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRNOMeVh6rLo1CKWzxYMAaBhByk4F5HuVwfCDUAQVUnABG4m3OTw2p8sr8LRs_ZuEplskZqZsdrOy7-/pub?output=csv"
FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSd5nLZX5Uihw--o_JuKYqxMwnsc4M-g6HupBCuO2xBqTvgC0w/viewform"

st.title("💰 Mi Control Financiero")

tab_resumen, tab_carga = st.tabs(["📊 Resumen y Balances", "📝 Cargar Datos"])

with tab_resumen:
    try:
        # Cargamos los datos
        df = pd.read_csv(EXCEL_CSV)
        
        if not df.empty:
            # Renombramos según tu Excel: Marca, Fecha, TIPO, Categoría, Monto, Método, Descripción
            columnas_reales = ['Timestamp', 'Fecha', 'Tipo', 'Categoría', 'Monto', 'Método', 'Descripción']
            df.columns = columnas_reales[:len(df.columns)]
            
            # Limpieza de datos
            df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
            
            # Ajuste para tus palabras: EGRESO / INGRESO
            # Buscamos cualquier cosa que empiece con 'E' para gastos y con 'I' para ingresos
            df_gastos = df[df["Tipo"].str.startswith(("E", "G"), na=False)]
            df_ingresos = df[df["Tipo"].str.startswith(("I"), na=False)]
            
            total_ingresos = df_ingresos["Monto"].sum()
            total_gastos = df_gastos["Monto"].sum()
            balance = total_ingresos - total_gastos
            
            # --- MÉTRICAS ---
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Ingresos", f"${total_ingresos:,.2f}")
            c2.metric("Total Gastos", f"${total_gastos:,.2f}")
            c3.metric("Saldo Real", f"${balance:,.2f}")
            
            st.divider()
            
            # --- GRÁFICOS ---
            if not df_gastos.empty:
                col_a, col_b = st.columns(2)
                with col_a:
                    fig_cat = px.pie(df_gastos, values='Monto', names='Categoría', title="Gastos por Categoría")
                    st.plotly_chart(fig_cat, use_container_width=True)
                with col_b:
                    fig_met = px.bar(df_gastos, x='Método', y='Monto', title="Gastos por Medio de Pago", color='Método')
                    st.plotly_chart(fig_met, use_container_width=True)
            
            st.subheader("📝 Historial Detallado")
            st.dataframe(df.sort_values(by="Timestamp", ascending=False), use_container_width=True)
            
        else:
            st.warning("El Excel está conectado pero parece estar vacío.")
            
    except Exception as e:
        st.error(f"Error al leer los datos. Verificá el link CSV.")
        st.info("Tip: Asegurate que en Google Sheets el link sea 'Valores separados por comas (.csv)'")

with tab_carga:
    st.subheader("Registrar Nuevo Movimiento")
    st.link_button("📝 ABRIR FORMULARIO DE CARGA", FORM_LINK, use_container_width=True)
