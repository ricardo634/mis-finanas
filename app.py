import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha PRO", layout="wide", page_icon="💰")

# --- ENLACES ---
EXCEL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQGHyOERYRdBB_KqWJjBvBG43Ujuf9y8xYFseHbX_ElKNLOAT_sStrolGifSVOGSsWJpanYtCq9fJz/pub?output=csv"
FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSd5nLZX5Uihw--o_JuKYqxMwnsc4M-g6HupBCuO2xBqTvgC0w/viewform"

st.title("💰 Mi Control Financiero")

tab_resumen, tab_carga = st.tabs(["📊 Resumen y Balances", "📝 Cargar Datos"])

with tab_resumen:
    try:
        # Cargamos los datos ignorando errores de columnas extra
        df = pd.read_csv(EXCEL_CSV)
        
        if not df.empty:
            # Forzamos los nombres de las primeras 7 columnas que vemos en tu foto
            # [Marca, Fecha, TIPO, Categoría, Monto, Método, Descripción]
            cols_necesarias = ['Timestamp', 'Fecha', 'Tipo', 'Categoría', 'Monto', 'Método', 'Concepto']
            df.columns = list(cols_necesarias) + list(df.columns[len(cols_necesarias):])
            
            # Limpieza de montos
            df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
            
            # Filtramos Gastos (EGRESO) e Ingresos
            # Usamos .str.contains para que detecte "EGRESO" o "INGRESO" sin importar mayúsculas
            mask_gastos = df['Tipo'].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)
            mask_ingresos = df['Tipo'].astype(str).str.contains('INGRESO', case=False, na=False)
            
            df_gastos = df[mask_gastos]
            df_ingresos = df[mask_ingresos]
            
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
            
            st.subheader("📝 Historial de Movimientos")
            # Mostramos solo las columnas principales para que no quede gigante
            st.dataframe(df[['Fecha', 'Tipo', 'Categoría', 'Monto', 'Método', 'Concepto']], use_container_width=True)
            
        else:
            st.warning("El Excel está conectado pero parece estar vacío.")
            
    except Exception as e:
        st.error("Error al leer los datos. Verificá el link CSV.")
        st.info("Asegurate de que el Excel esté publicado como CSV.")

with tab_carga:
    st.subheader("Registrar Nuevo Movimiento")
    st.link_button("📝 ABRIR FORMULARIO DE CARGA", FORM_LINK, use_container_width=True)

