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
        df = pd.read_csv(EXCEL_CSV)
        
        if not df.empty:
            # Orden de columnas: Timestamp, Fecha, Tipo, Categoría, Monto, Método, Concepto, Estado
            cols_base = ['Timestamp', 'Fecha', 'Tipo', 'Categoría', 'Monto', 'Método', 'Concepto', 'Estado']
            df.columns = list(cols_base) + list(df.columns[len(cols_base):])
            
            df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
            
            # --- CÁLCULOS ---
            ingresos = df[df['Tipo'].str.contains('INGRESO', case=False, na=False)]['Monto'].sum()
            
            # Gastos ya pagados
            gastos_pagados = df[(df['Tipo'].str.contains('EGRESO|GASTO', case=False, na=False)) & 
                                (df['Estado'].str.contains('Realizado|Pagado', case=False, na=False))]['Monto'].sum()
            
            # Gastos PENDIENTES
            pendientes = df[(df['Tipo'].str.contains('EGRESO|GASTO', case=False, na=False)) & 
                            (df['Estado'].str.contains('Pendiente', case=False, na=False))]['Monto'].sum()
            
            balance_actual = ingresos - gastos_pagados
            balance_final = balance_actual - pendientes

            # --- MÉTRICAS ---
            c1, c2, c3 = st.columns(3)
            c1.metric("Balance Actual (Caja)", f"${balance_actual:,.2f}")
            c2.metric("Pagos Pendientes", f"${pendientes:,.2f}", delta="- Deuda", delta_color="inverse")
            c3.metric("Saldo Final Neto", f"${balance_final:,.2f}", help="Es lo que te queda después de pagar los pendientes")
            
            st.divider()
            
            # --- GRÁFICOS ---
            df_gastos = df[df['Tipo'].str.contains('EGRESO|GASTO', case=False, na=False)]
            if not df_gastos.empty:
                col_a, col_b = st.columns(2)
                with col_a:
                    fig_cat = px.pie(df_gastos, values='Monto', names='Categoría', title="Gastos por Categoría")
                    st.plotly_chart(fig_cat, use_container_width=True)
                with col_b:
                    # Gráfico de barras que muestra qué está pagado y qué no
                    fig_met = px.bar(df_gastos, x='Método', y='Monto', color='Estado', title="Estado de Pagos por Medio")
                    st.plotly_chart(fig_met, use_container_width=True)
            
            st.subheader("📝 Historial")
            st.dataframe(df[['Fecha', 'Tipo', 'Categoría', 'Monto', 'Método', 'Estado']], use_container_width=True)
            
        else:
            st.warning("No hay datos en el Excel.")
            
    except Exception as e:
        st.error("Error. Revisá que el Formulario tenga la columna 'Estado'.")

with tab_carga:
    st.subheader("Registrar Nuevo Movimiento")
    st.link_button("📝 ABRIR FORMULARIO DE CARGA", FORM_LINK, use_container_width=True)
