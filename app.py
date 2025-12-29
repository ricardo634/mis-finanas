import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha PRO", layout="wide", page_icon="💰")

# --- CONFIGURACIÓN DE ENLACES ---
# 1. PEGÁ ACÁ EL LINK DE TU EXCEL (El que publicaste como .csv en 'Archivo > Compartir > Publicar en la web')
EXCEL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRNOMeVh6rLo1CKWzxYMAaBhByk4F5HuVwfCDUAQVUnABG4m30Tw2p8sr8LRs_ZuEpIskZqZsdr0y7-/pub?output=csv"

# 2. PEGÁ ACÁ EL LINK DE TU FORMULARIO (El de 'Enviar' formulario)
FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSd5nLZX5Uihw--o_JuKYqxMwnsc4M-g6HupBCuO2xBqTvgC0w/viewform?usp=header"

st.title("💰 Mi Control Financiero Permanente")

# --- TABS ---
tab_graficos, tab_carga = st.tabs(["📊 Resumen y Balances", "📝 Cargar Datos"])

with tab_graficos:
    try:
        # Leemos los datos desde Google Sheets
        df = pd.read_csv(EXCEL_CSV)
        
        if not df.empty:
            # Renombramos columnas por si Google Forms les puso nombres largos
            # Asumimos orden: [Marca Temporal, Fecha, Tipo, Categoría, Monto, Método]
            df.columns = ['Timestamp', 'Fecha', 'Tipo', 'Categoría', 'Monto', 'Método']
            
            # --- SECCIÓN DE BALANCE ---
            total_ingresos = df[df["Tipo"] == "Ingreso"]["Monto"].sum()
            total_gastos = df[df["Tipo"] == "Gasto"]["Monto"].sum()
            balance = total_ingresos - total_gastos
            
            st.subheader("💵 Balance General")
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Ingresos", f"${total_ingresos:,.2f}")
            c2.metric("Total Gastos", f"${total_gastos:,.2f}")
            c3.metric("Saldo Disponible", f"${balance:,.2f}", delta=f"${balance}")
            
            st.divider()
            
            # --- SECCIÓN DE GRÁFICOS ---
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.write("### 📂 Gastos por Categoría")
                fig_cat = px.pie(df[df["Tipo"]=="Gasto"], values='Monto', names='Categoría', hole=0.4)
                st.plotly_chart(fig_cat, use_container_width=True)
                
            with col_b:
                st.write("### 💳 Gastos por Tarjeta / Medio")
                # Filtramos solo los gastos para ver en qué tarjeta se fue la plata
                df_gastos = df[df["Tipo"]=="Gasto"]
                fig_tarj = px.bar(df_gastos, x='Método', y='Monto', color='Método', title="Uso de Tarjetas y Efectivo")
                st.plotly_chart(fig_tarj, use_container_width=True)
            
            st.divider()
            
            # --- HISTORIAL ---
            st.subheader("📝 Historial Detallado")
            st.dataframe(df.sort_values(by="Fecha", ascending=False), use_container_width=True)
            
        else:
            st.info("Aún no hay datos. Cargá tu primer movimiento en la pestaña 'Cargar Datos'.")
            
    except Exception as e:
        st.warning("Conectando con la base de datos de Google...")
        st.write("Asegurate de haber pegado los links correctamente y que el Excel esté 'Publicado en la web'.")

with tab_carga:
    st.subheader("Registrar Nuevo Movimiento")
    st.info("Completá el formulario abajo. Al terminar, dale a 'Enviar' y los datos aparecerán en la pestaña de Resumen.")
    # Formulario de Google embebido
    st.components.v1.iframe(FORM_LINK, height=800, scrolling=True)


