import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha PRO", layout="wide", page_icon="💳")

# --- ENLACES ---
EXCEL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQGHyOERYRdBB_KqWJjBvBG43Ujuf9y8xYFseHbX_ElKNLOAT_sStrolGifSVOGSsWJpanYtCq9fJz/pub?output=csv"
FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSd5nLZX5Uihw--o_JuKYqxMwnsc4M-g6HupBCuO2xBqTvgC0w/viewform"

st.title("💰 Mi Control Financiero")

tab_resumen, tab_tarjeta, tab_carga = st.tabs(["📊 Resumen General", "💳 Solo Tarjetas", "📝 Cargar Datos"])

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
            col_cat_gasto = next((c for c in df.columns if 'CATEGORÍA DE GASTO' in c.upper() or 'CATEGORÍA' in c.upper()), df.columns[3])
            col_concepto = next((c for c in df.columns if 'CONCEPTO' in c.upper()), df.columns[4])

            for col in cols_montos:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # --- CÁLCULOS ---
            df_ingresos = df[df[col_tipo].astype(str).str.contains('INGRESO', case=False, na=False)]
            total_ingresos = df_ingresos[cols_montos].sum(axis=1).sum()
            
            df_egresos = df[df[col_tipo].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)]
            total_egresos = df_egresos[cols_montos].sum(axis=1).sum()
            
            # Lógica de Deuda: Pendientes o Tarjeta no marcada como Realizado
            if col_estado and col_medio:
                mask_pend = df_egresos[col_estado].astype(str).str.contains('PENDIENTE', case=False, na=False)
                mask_tarjeta = df_egresos[col_medio].astype(str).str.contains('CREDITO', case=False, na=False)
                mask_no_pagado = ~df_egresos[col_estado].astype(str).str.contains('REALIZADO|PAGADO', case=False, na=False)
                
                df_deuda = df_egresos[mask_pend | (mask_tarjeta & mask_no_pagado)]
                monto_deuda = df_deuda[cols_montos].sum(axis=1).sum()
            else:
                df_deuda = pd.DataFrame()
                monto_deuda = 0

            disponible_caja = total_ingresos - (total_egresos - monto_deuda)
            
            # --- 🚩 PANEL DE ALERTAS ---
            if not df_deuda.empty:
                st.error(f"### 🚩 ¡Tenés {len(df_deuda)} pagos pendientes!")
                with st.expander("VER DETALLE DE DEUDAS", expanded=True):
                    for i, row in df_deuda.iterrows():
                        st.write(f"⚠️ **${row[cols_montos].sum():,.2f}** - {row[col_cat_gasto]} ({row[col_concepto]})")
                st.divider()

            # --- MÉTRICAS ---
            c1, c2, c3 = st.columns(3)
            c1.metric("Disponible (Caja)", f"${disponible_caja:,.2f}")
            c2.metric("Deuda Acumulada", f"${monto_deuda:,.2f}", delta="A pagar", delta_color="inverse")
            c3.metric("Saldo Neto Final", f"${disponible_caja - monto_deuda:,.2f}")
            
            st.divider()

            # --- GRÁFICO ---
            if not df_egresos.empty:
                st.write("### 📈 Gastos por Categoría")
                fig_mix = px.bar(df_egresos, x=col_cat_gasto, y=cols_montos[0], color=col_medio if col_medio else None, barmode='group')
                st.plotly_chart(fig_mix, use_container_width=True)

    except Exception as e:
        st.error(f"Error en los números: {e}")

with tab_tarjeta:
    st.subheader("🔎 Detalle de Tarjeta de Crédito")
    try:
        df_solo_tarjeta = df[df[col_medio].astype(str).str.contains('CREDITO', case=False, na=False)]
        if not df_solo_tarjeta.empty:
            st.success(f"#### Consumos totales en tarjeta: ${df_solo_tarjeta[cols_montos].sum(axis=1).sum():,.2f}")
            st.dataframe(df_solo_tarjeta, use_container_width=True)
    except:
        st.write("No hay datos de tarjeta.")

with tab_carga:
    st.subheader("Registrar Movimiento")
    st.link_button("📝 IR AL FORMULARIO", FORM_LINK, use_container_width=True)
