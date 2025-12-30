import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha PRO", layout="wide", page_icon="💰")

# --- ENLACES ---
# Asegurate de que este sea el link que termina en pub?output=csv
EXCEL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQGHyOERYRdBB_KqWJjBvBG43Ujuf9y8xYFseHbX_ElKNLOAT_sStrolGifSVOGSsWJpanYtCq9fJz/pub?output=csv"
FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSd5nLZX5Uihw--o_JuKYqxMwnsc4M-g6HupBCuO2xBqTvgC0w/viewform"

st.title("💰 Mi Control Financiero")

tab_resumen, tab_carga = st.tabs(["📊 Resumen y Balances", "📝 Cargar Datos"])

with tab_resumen:
    try:
        # Forzamos la descarga de datos nuevos
        df = pd.read_csv(EXCEL_CSV)
        
        if not df.empty:
            # TRUCO: Renombramos las columnas por su posición para evitar errores de nombres
            # 0:Marca temporal, 1:Fecha, 2:Tipo, 3:Categoría, 4:Monto, 5:Método
            nuevos_nombres = ['Timestamp', 'Fecha', 'Tipo', 'Categoría', 'Monto', 'Método']
            df.columns = nuevos_nombres[:len(df.columns)]
            
            # Limpiamos los números (quita el signo $ si lo hay)
            df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
            
            # --- CÁLCULOS ---
            ingresos = df[df["Tipo"].str.contains("Ingreso", case=False, na=False)]["Monto"].sum()
            gastos = df[df["Tipo"].str.contains("Gasto", case=False, na=False)]["Monto"].sum()
            balance = ingresos - gastos
            
            # --- MÉTRICAS ---
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Ingresos", f"${ingresos:,.2f}")
            c2.metric("Total Gastos", f"${gastos:,.2f}")
            c3.metric("Saldo Real", f"${balance:,.2f}")
            
            st.divider()
            
            # --- GRÁFICOS ---
            col_a, col_b = st.columns(2)
            df_gastos = df[df["Tipo"].str.contains("Gasto", case=False, na=False)]
            
            if not df_gastos.empty:
                with col_a:
                    fig_cat = px.pie(df_gastos, values='Monto', names='Categoría', title="Gastos por Categoría")
                    st.plotly_chart(fig_cat, use_container_width=True)
                with col_b:
                    fig_met = px.bar(df_gastos, x='Método', y='Monto', title="Gastos por Tarjeta/Medio", color='Método')
                    st.plotly_chart(fig_met, use_container_width=True)
            
            st.subheader("📝 Historial")
            st.dataframe(df.sort_values(by=df.columns[0], ascending=False), use_container_width=True)
            
        else:
            st.warning("El Excel está conectado pero no tiene datos cargados.")
            
    except Exception as e:
        st.error("Error al leer los datos. Verificá que el link de Publicar en la Web sea CSV.")
        st.info("Si acabás de cargar un dato, esperá 30 segundos y actualizá la página.")

with tab_carga:
    st.subheader("Registrar Nuevo Movimiento")
    st.link_button("📝 ABRIR FORMULARIO DE CARGA", FORM_LINK, use_container_width=True)


