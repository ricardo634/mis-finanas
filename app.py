import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha PRO", layout="wide", page_icon="💰")

# --- ENLACES ---
EXCEL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQGHyOERYRdBB_KqWJjBvBG43Ujuf9y8xYFseHbX_ElKNLOAT_sStrolGifSVOGSsWJpanYtCq9fJz/pub?output=csv"
FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSd5nLZX5Uihw--o_JuKYqxMwnsc4M-g6HupBCuO2xBqTvgC0w/viewform"

st.title("💰 Mi Control Financiero")

# Creamos 3 pestañas para que sea más ordenado
tab_resumen, tab_bancos, tab_carga = st.tabs(["📊 Resumen y Balances", "💳 Detalle por Tarjeta/Banco", "📝 Cargar Datos"])

try:
    df = pd.read_csv(EXCEL_CSV)
    
    if not df.empty:
        # Forzamos nombres para las columnas principales
        # [Marca, Fecha, TIPO, Categoría, Monto, Método, Descripción, BANCO...]
        cols_base = ['Timestamp', 'Fecha', 'Tipo', 'Categoría', 'Monto', 'Método', 'Concepto']
        # Mantenemos el resto de las columnas originales para capturar el Banco
        df.columns = cols_base + list(df.columns[len(cols_base):])
        
        # Limpieza de montos
        df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
        
        # Separamos Ingresos y Gastos
        df_gastos = df[df['Tipo'].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)].copy()
        df_ingresos = df[df['Tipo'].astype(str).str.contains('INGRESO', case=False, na=False)].copy()

        # --- PESTAÑA 1: RESUMEN ---
        with tab_resumen:
            total_ing = df_ingresos["Monto"].sum()
            total_gas = df_gastos["Monto"].sum()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Ingresos", f"${total_ing:,.2f}")
            c2.metric("Total Gastos", f"${total_gas:,.2f}")
            c3.metric("Saldo Real", f"${total_ing - total_gas:,.2f}")
            
            st.divider()
            
            col_a, col_b = st.columns(2)
            with col_a:
                fig_cat = px.pie(df_gastos, values='Monto', names='Categoría', title="¿En qué se va la plata? (Categorías)")
                st.plotly_chart(fig_cat, use_container_width=True)
            with col_b:
                fig_met = px.bar(df_gastos.groupby('Método')['Monto'].sum().reset_index(), 
                                 x='Método', y='Monto', title="Gastos por Medio de Pago", color='Método')
                st.plotly_chart(fig_met, use_container_width=True)

        # --- PESTAÑA 2: DETALLE POR BANCO (Lo que pediste) ---
        with tab_bancos:
            st.subheader("🔍 Análisis de Tarjetas y Bancos")
            
            # Buscamos la columna donde elegís el banco (suele ser la 8va o 9na columna)
            # Vamos a intentar detectarla automáticamente
            col_banco_nombre = df.columns[7] if len(df.columns) > 7 else 'Método'
            
            # Filtramos solo lo que se pagó con Tarjeta
            df_tarjetas = df_gastos[df_gastos['Método'].astype(str).str.contains('CRED', case=False, na=False)].copy()
            
            if not df_tarjetas.empty:
                # Selector de Banco/Tarjeta
                lista_bancos = ["TODOS"] + sorted(df_tarjetas[col_banco_nombre].dropna().unique().tolist())
                banco_sel = st.selectbox("Seleccioná la Tarjeta o Banco:", lista_bancos)
                
                df_filtro = df_tarjetas if banco_sel == "TODOS" else df_tarjetas[df_tarjetas[col_banco_nombre] == banco_sel]
                
                st.warning(f"Consumo Total en {banco_sel}: ${df_filtro['Monto'].sum():,.2f}")
                
                # Tabla de historial limpia
                st.write("### 📜 Movimientos de esta selección")
                st.dataframe(df_filtro[['Fecha', col_banco_nombre, 'Categoría', 'Concepto', 'Monto']], use_container_width=True)
            else:
                st.info("No hay gastos registrados con Tarjeta de Crédito todavía.")

        # --- PESTAÑA 3: CARGA ---
        with tab_carga:
            st.link_button("📝 ABRIR FORMULARIO DE CARGA", FORM_LINK, use_container_width=True)

    else:
        st.warning("El Excel está vacío.")

except Exception as e:
    st.error(f"Error técnico: {e}")
    st.info("Avisame si cambiaste alguna pregunta del formulario.")
