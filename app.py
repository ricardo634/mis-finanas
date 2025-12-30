import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha PRO", layout="wide", page_icon="💳")

# --- ENLACES ---
EXCEL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQGHyOERYRdBB_KqWJjBvBG43Ujuf9y8xYFseHbX_ElKNLOAT_sStrolGifSVOGSsWJpanYtCq9fJz/pub?output=csv"
FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSd5nLZX5Uihw--o_JuKYqxMwnsc4M-g6HupBCuO2xBqTvgC0w/viewform"

st.title("💰 Mi Control Financiero")

tab_resumen, tab_tarjeta, tab_carga = st.tabs(["📊 Resumen y Comparativa", "💳 Solo Tarjetas", "📝 Cargar Datos"])

with tab_resumen:
    try:
        df = pd.read_csv(EXCEL_CSV)
        if not df.empty:
            df.columns = [c.strip() for c in df.columns]
            
            # --- BUSCADOR DE COLUMNAS ---
            col_tipo = next((c for c in df.columns if 'TIPO' in c.upper()), None)
            cols_montos = [c for c in df.columns if 'MONTO' in c.upper()]
            col_medio = next((c for c in df.columns if 'MÉTODO' in c.upper() or 'MEDIO' in c.upper()), None)
            col_estado = next((c for c in df.columns if 'ESTADO' in c.upper()), None)
            # Detectamos las categorías (Gasto o Ingreso)
            col_cat_gasto = next((c for c in df.columns if 'CATEGORÍA DE GASTO' in c.upper()), None)
            col_cat_ingreso = next((c for c in df.columns if 'CATEGORÍA DE INGRESO' in c.upper()), None)
            col_concepto = next((c for c in df.columns if 'CONCEPTO' in c.upper()), df.columns[4])

            for col in cols_montos:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # --- CREAR COLUMNA UNIFICADA DE CATEGORÍA ---
            # Esto junta "Categoría de Gasto" y "Categoría de Ingreso" en una sola para el gráfico
            df['Categoria_Unificada'] = df[col_cat_gasto].fillna(df[col_cat_ingreso]).fillna("Sin Categoría")
            # Sumamos todos los montos posibles en uno solo
            df['Monto_Total'] = df[cols_montos].sum(axis=1)

            # --- CÁLCULOS ---
            df_ingresos = df[df[col_tipo].astype(str).str.contains('INGRESO', case=False, na=False)]
            total_ingresos = df_ingresos['Monto_Total'].sum()
            
            df_egresos = df[df[col_tipo].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)]
            total_egresos = df_egresos['Monto_Total'].sum()
            
            # Deuda
            monto_deuda = 0
            if col_estado and col_medio:
                mask_pend = df_egresos[col_estado].astype(str).str.contains('PENDIENTE', case=False, na=False)
                mask_tarjeta = df_egresos[col_medio].astype(str).str.contains('CREDITO', case=False, na=False)
                mask_no_pagado = ~df_egresos[col_estado].astype(str).str.contains('REALIZADO|PAGADO', case=False, na=False)
                df_deuda = df_egresos[mask_pend | (mask_tarjeta & mask_no_pagado)]
                monto_deuda = df_deuda['Monto_Total'].sum()
            else:
                df_deuda = pd.DataFrame()

            disponible_caja = total_ingresos - (total_egresos - monto_deuda)
            
            # --- MÉTRICAS ---
            c1, c2, c3 = st.columns(3)
            c1.metric("Disponible (Caja)", f"${disponible_caja:,.2f}")
            c2.metric("Deuda Pendiente", f"${monto_deuda:,.2f}", delta="A pagar", delta_color="inverse")
            c3.metric("Saldo Neto Final", f"${disponible_caja - monto_deuda:,.2f}")
            
            st.divider()

            # --- NUEVO GRÁFICO: INGRESOS VS GASTOS ---
            st.write("### ⚖️ Comparativa: Ingresos vs Gastos por Categoría")
            # Agrupamos por categoría y tipo para el gráfico
            df_grafico = df.groupby(['Categoria_Unificada', col_tipo])['Monto_Total'].sum().reset_index()
            fig_comp = px.bar(df_grafico, 
                             x='Categoria_Unificada', 
                             y='Monto_Total', 
                             color=col_tipo, 
                             barmode='group',
                             labels={'Categoria_Unificada': 'Categoría', 'Monto_Total': 'Monto ($)'},
                             color_discrete_map={'INGRESO': '#2ecc71', 'EGRESO': '#e74c3c', 'GASTO': '#e74c3c'})
            st.plotly_chart(fig_comp, use_container_width=True)

            st.divider()

            # --- GRÁFICO CIRCULAR DE GASTOS ---
            if not df_egresos.empty:
                st.write("### 🍕 Distribución de Egresos")
                fig_pie = px.pie(df_egresos, values='Monto_Total', names='Categoria_Unificada', hole=0.4)
                st.plotly_chart(fig_pie, use_container_width=True)

    except Exception as e:
        st.error(f"Error al procesar los datos: {e}")

# ... (Las pestañas de Tarjeta y Carga se mantienen igual)
with tab_tarjeta:
    st.subheader("🔎 Detalle de Tarjeta de Crédito")
    try:
        df_solo_tarjeta = df[df[col_medio].astype(str).str.contains('CREDITO', case=False, na=False)]
        if not df_solo_tarjeta.empty:
            st.info(f"Consumos totales: ${df_solo_tarjeta['Monto_Total'].sum():,.2f}")
            st.dataframe(df_solo_tarjeta, use_container_width=True)
    except:
        st.write("Sin datos.")

with tab_carga:
    st.subheader("Registrar Movimiento")
    st.link_button("📝 IR AL FORMULARIO", FORM_LINK, use_container_width=True)
