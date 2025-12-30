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
            # Limpiamos nombres de columnas
            df.columns = [c.strip() for c in df.columns]
            
            # --- RASTREADOR DE COLUMNAS ---
            def encontrar(palabra):
                return next((c for c in df.columns if palabra.upper() in c.upper()), None)

            col_tipo = encontrar('TIPO')
            cols_montos = [c for c in df.columns if 'MONTO' in c.upper()]
            col_medio = encontrar('MÉTODO') or encontrar('MEDIO')
            col_estado = encontrar('ESTADO')
            col_cat_gasto = encontrar('CATEGORÍA DE GASTO') or encontrar('CATEGORÍA')
            col_cat_ingreso = encontrar('CATEGORÍA DE INGRESO')
            col_concepto = encontrar('CONCEPTO') or encontrar('DESCRIPCIÓN')

            # Limpiamos montos y creamos una columna total
            for col in cols_montos:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            df['Monto_Final'] = df[cols_montos].sum(axis=1)
            
            # Unificamos categorías para el gráfico
            df['Cat_Unificada'] = df[col_cat_gasto].fillna(df[col_cat_ingreso]).fillna("General")

            # --- CÁLCULOS ---
            df_ing = df[df[col_tipo].astype(str).str.contains('INGRESO', case=False, na=False)]
            total_ing = df_ing['Monto_Final'].sum()
            
            df_egr = df[df[col_tipo].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)]
            total_egr = df_egr['Monto_Final'].sum()
            
            # Deuda (Pendientes o Tarjeta)
            df_deuda = pd.DataFrame()
            if col_estado and col_medio:
                es_pend = df_egr[col_estado].astype(str).str.contains('PENDIENTE', case=False, na=False)
                es_tarj = df_egr[col_medio].astype(str).str.contains('CREDITO', case=False, na=False)
                no_pago = ~df_egr[col_estado].astype(str).str.contains('REALIZADO|PAGADO', case=False, na=False)
                df_deuda = df_egr[es_pend | (es_tarj & no_pago)]
            
            monto_deuda = df_deuda['Monto_Final'].sum() if not df_deuda.empty else 0
            disponible = total_ing - (total_egr - monto_deuda)
            
            # --- 🚩 PANEL DE ALERTAS ---
            if not df_deuda.empty:
                st.error(f"### 🚩 ¡Tenés {len(df_deuda)} pagos pendientes!")
                with st.expander("VER DETALLE DE DEUDAS", expanded=True):
                    st.table(df_deuda[[df.columns[1], 'Cat_Unificada', 'Monto_Final']])
                st.divider()

            # --- MÉTRICAS ---
            c1, c2, c3 = st.columns(3)
            c1.metric("Disponible (Caja)", f"${disponible:,.2f}")
            c2.metric("Deuda Pendiente", f"${monto_deuda:,.2f}", delta_color="inverse")
            c3.metric("Saldo Neto Final", f"${disponible - monto_deuda:,.2f}")
            
            st.divider()

            # --- NUEVO GRÁFICO COMPARATIVO ---
            st.write("### ⚖️ Comparativa: Ingresos vs Gastos por Categoría")
            df_graf = df.groupby(['Cat_Unificada', col_tipo])['Monto_Final'].sum().reset_index()
            fig = px.bar(df_graf, x='Cat_Unificada', y='Monto_Final', color=col_tipo, barmode='group',
                         color_discrete_map={'INGRESO': '#2ecc71', 'EGRESO': '#e74c3c', 'GASTO': '#e74c3c'})
            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Hubo un problema con los datos: {e}")

with tab_tarjeta:
    st.subheader("🔎 Detalle de Tarjeta de Crédito")
    try:
        df_tarj = df[df[col_medio].astype(str).str.contains('CREDITO', case=False, na=False)]
        if not df_tarj.empty:
            st.info(f"Consumos totales: ${df_tarj['Monto_Final'].sum():,.2f}")
            st.dataframe(df_tarj, use_container_width=True)
    except:
        st.write("Sin datos.")

with tab_carga:
    st.subheader("Registrar Movimiento")
    st.link_button("📝 IR AL FORMULARIO", FORM_LINK, use_container_width=True)
