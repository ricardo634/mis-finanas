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
            
            # --- RASTREADOR DE COLUMNAS ---
            def encontrar(palabra):
                return next((c for c in df.columns if palabra.upper() in c.upper()), None)

            col_tipo = encontrar('TIPO')
            cols_montos = [c for c in df.columns if 'MONTO' in c.upper()]
            col_medio = encontrar('MÉTODO') or encontrar('MEDIO')
            col_estado = encontrar('ESTADO')
            # Buscamos categorías de ambos tipos
            col_cat_gasto = encontrar('CATEGORÍA DE GASTO') or encontrar('CATEGORÍA')
            col_cat_ingreso = encontrar('CATEGORÍA DE INGRESO')
            col_concepto = encontrar('CONCEPTO') or encontrar('DESCRIPCIÓN')

            # Limpiamos montos
            for col in cols_montos:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Unificamos para el gráfico
            df['Categoria_Final'] = df[col_cat_gasto].fillna(df[col_cat_ingreso]).fillna("Otros")
            df['Suma_Montos'] = df[cols_montos].sum(axis=1)

            # --- CÁLCULOS ---
            df_ing = df[df[col_tipo].astype(str).str.contains('INGRESO', case=False, na=False)]
            total_ing = df_ing['Suma_Montos'].sum()
            
            df_egr = df[df[col_tipo].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)]
            total_egr = df_egr['Suma_Montos'].sum()
            
            # Deuda
            monto_deuda = 0
            df_deuda = pd.DataFrame()
            if col_estado and col_medio:
                es_pend = df_egr[col_estado].astype(str).str.contains('PENDIENTE', case=False, na=False)
                es_tarj = df_egr[col_medio].astype(str).str.contains('CREDITO', case=False, na=False)
                no_pago = ~df_egr[col_estado].astype(str).str.contains('REALIZADO|PAGADO', case=False, na=False)
                df_deuda = df_egr[es_pend | (es_tarj & no_pago)]
                monto_deuda = df_deuda['Suma_Montos'].sum()

            disponible = total_ing - (total_egr - monto_deuda)
            
            # --- PANEL DE ALERTAS ---
            if not df_deuda.empty:
                st.error(f"### 🚩 ¡Tenés {len(df_deuda)} pagos pendientes!")
                with st.expander("DETALLE DE DEUDAS"):
                    st.table(df_deuda[['Fecha' if 'Fecha' in df.columns else df.columns[1], 'Categoria_Final', 'Suma_Montos']])

            # --- MÉTRICAS ---
            c1, c2, c3 = st.columns(3)
            c1.metric("Disponible (Caja)", f"${disponible:,.2f}")
            c2.metric("Deuda Pendiente", f"${monto_deuda:,.2f}", delta_color="inverse")
            c3.metric("Saldo Neto Final", f"${disponible - monto_deuda:,.2f}")
            
            st.divider()

            # --- GRÁFICO COMPARATIVO ---
            st.write("### ⚖️ Comparativa: Ingresos vs Gastos")
            df_graf = df.groupby(['Categoria_Final', col_tipo])['Suma_Montos'].sum().reset_index()
            fig = px.bar(df_graf, x='Categoria_Final', y='Suma_Montos', color=col_tipo, barmode='group',
                         color_discrete_map={'INGRESO': '#2ecc71', 'EGRESO': '#e74c3c', 'GASTO': '#e74c3c'})
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Hubo un problema al organizar las columnas: {e}")
        st.info("Tip: Asegurate que las preguntas del formulario tengan las palabras MONTO, TIPO y ESTADO.")
