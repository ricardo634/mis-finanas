import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha PRO", layout="wide", page_icon="💳")

# --- ENLACES ---
EXCEL_CSV ="https://docs.google.com/spreadsheets/d/e/2PACX-1vTQGHyOERYRdBB_KqWJjBvBG43Ujuf9y8xYFseHbX_ElKNLOAT_sStrolGifSVOGSsWJpanYtCq9fJz/pub?output=csv"
FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSd5nLZX5Uihw--o_JuKYqx)mwnsc4M-g6HupBCuO2xBqTvgC0w/viewform"

st.title("💰 Mi Control Financiero")

tab_resumen, tab_tarjeta, tab_carga = st.tabs(["📊 Resumen y Gráficos", "💳 Solo Tarjetas", "📝 Cargar Datos"])

try:
    df = pd.read_csv(EXCEL_CSV)
    if not df.empty:
        # Limpiamos nombres de columnas de espacios extra
        df.columns = [c.strip() for c in df.columns]
        
        # --- BUSCADOR FLEXIBLE DE COLUMNAS ---
        def buscar(palabras):
            for p in palabras:
                for c in df.columns:
                    if p.upper() in c.upper(): return c
            return None

        # Asignamos las columnas detectadas
        c_tipo = buscar(['TIPO', 'CARGAR', 'MOVIMIENTO'])
        c_monto = [c for c in df.columns if 'MONTO' in c.upper() or '$' in c]
        c_medio = buscar(['MÉTODO', 'MEDIO', 'PAGO'])
        c_estado = buscar(['ESTADO'])
        c_cat = buscar(['CATEGORÍA DE GASTO', 'CATEGORIA', 'GASTO'])
        c_fecha = buscar(['FECHA']) or df.columns[1]

        # Limpiamos los montos (sumamos todas las columnas que tengan "$" o "Monto")
        for col in c_monto:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df['Total_Limpio'] = df[c_monto].sum(axis=1)

        # 1. PESTAÑA RESUMEN
        with tab_resumen:
            df_ing = df[df[c_tipo].astype(str).str.contains('INGRESO', case=False, na=False)]
            df_egr = df[df[c_tipo].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)]
            
            # Cálculo de deuda (Tarjeta o Pendiente)
            m_deuda = 0
            df_deuda = pd.DataFrame()
            if c_estado and c_medio:
                es_pend = df_egr[c_estado].astype(str).str.contains('PENDIENTE', case=False, na=False)
                es_tarj = df_egr[c_medio].astype(str).str.contains('CRED', case=False, na=False)
                no_pago = ~df_egr[c_estado].astype(str).str.contains('REALIZADO|PAGADO', case=False, na=False)
                df_deuda = df_egr[es_pend | (es_tarj & no_pago)]
                m_deuda = df_deuda['Total_Limpio'].sum()

            disponible = df_ing['Total_Limpio'].sum() - (df_egr['Total_Limpio'].sum() - m_deuda)

            # Métricas
            col1, col2, col3 = st.columns(3)
            col1.metric("Disponible (Caja)", f"${disponible:,.2f}")
            col2.metric("Deuda (Tarjeta/Pend)", f"${m_deuda:,.2f}", delta_color="inverse")
            col3.metric("Saldo Real Final", f"${disponible - m_deuda:,.2f}")

            st.divider()
            
            # Gráficos
            g1, g2 = st.columns(2)
            with g1:
                st.write("### ⚖️ Ingresos vs Gastos")
                df_bar = df.groupby([c_cat, c_tipo])['Total_Limpio'].sum().reset_index()
                st.plotly_chart(px.bar(df_bar, x=c_cat, y='Total_Limpio', color=c_tipo, barmode='group'), use_container_width=True)
            with g2:
                st.write("### 🍕 Torta de Gastos")
                st.plotly_chart(px.pie(df_egr, values='Total_Limpio', names=c_cat, hole=0.4), use_container_width=True)

        # 2. PESTAÑA TARJETA (Aquí arreglamos lo que no salía)
        with tab_tarjeta:
            st.subheader("💳 Detalle de Gastos con Tarjeta")
            # Buscamos cualquier fila donde el medio de pago diga "CRED" (Crédito, Credito, etc)
            df_t = df[df[c_medio].astype(str).str.contains('CRED', case=False, na=False)].copy()
            
            if not df_t.empty:
                st.success(f"Monto total en tarjeta: ${df_t['Total_Limpio'].sum():,.2f}")
                # Mostramos solo las columnas que importan para que sea legible
                st.table(df_t[[c_fecha, c_cat, 'Total_Limpio']].rename(columns={c_fecha:'Fecha', c_cat:'Categoría', 'Total_Limpio':'Monto $'}))
            else:
                st.info("No detecté gastos con 'Tarjeta'. Revisá que en el formulario hayas elegido esa opción.")
                st.write("Nombres de columnas detectados para depurar:", list(df.columns))

except Exception as e:
    st.error(f"Error de sistema: {e}")

with tab_carga:
    st.link_button("📝 ABRIR FORMULARIO", FORM_LINK, use_container_width=True)
