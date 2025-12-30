import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha PRO", layout="wide", page_icon="💳")

# --- ENLACES ---
EXCEL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQGHyOERYRdBB_KqWJjBvBG43Ujuf9y8xYFseHbX_ElKNLOAT_sStrolGifSVOGSsWJpanYtCq9fJz/pub?output=csv"
FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSd5nLZX5Uihw--o_JuKYqxMwnsc4M-g6HupBCuO2xBqTvgC0w/viewform"

st.title("💰 Mi Control Financiero")

tab_resumen, tab_tarjeta, tab_carga = st.tabs(["📊 Resumen y Gráficos", "💳 Solo Tarjetas", "📝 Cargar Datos"])

try:
    df = pd.read_csv(EXCEL_CSV)
    if not df.empty:
        # LIMPIEZA CRÍTICA: Quitamos espacios vacíos al principio y final de los nombres de columnas
        df.columns = [str(c).strip() for c in df.columns]
        
        # --- BUSCADOR DE COLUMNAS ---
        def encontrar(palabras):
            for p in palabras:
                for c in df.columns:
                    if p.upper() in c.upper(): return c
            return None

        col_tipo = encontrar(['TIPO', 'CARGAR', 'MOVIMIENTO'])
        # Buscamos todas las columnas que tengan montos
        cols_montos = [c for c in df.columns if 'MONTO' in c.upper() or '$' in c or 'Total_Limpio' in c]
        col_medio = encontrar(['MÉTODO', 'MEDIO', 'PAGO'])
        col_estado = encontrar(['ESTADO'])
        col_cat_gasto = encontrar(['CATEGORÍA DE GASTO', 'GASTO'])
        col_cat_ingreso = encontrar(['CATEGORÍA DE INGRESO', 'INGRESO'])
        col_fecha = df.columns[1] 

        # Limpiar montos y crear una sola columna de valor
        for col in cols_montos:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df['Valor_Final'] = df[cols_montos].sum(axis=1)
        
        # Unificar categorías
        df['Cat_Grafico'] = df[col_cat_gasto].fillna(df[col_cat_ingreso]).fillna("General")

        with tab_resumen:
            # --- CÁLCULOS ---
            df_ing = df[df[col_tipo].astype(str).str.contains('INGRESO', case=False, na=False)]
            total_ing = df_ing['Valor_Final'].sum()
            
            df_egr = df[df[col_tipo].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)]
            total_egr = df_egr['Valor_Final'].sum()
            
            # Deuda (Pendientes o Tarjeta)
            monto_deuda = 0
            df_deuda = pd.DataFrame()
            if col_estado and col_medio:
                es_pend = df_egr[col_estado].astype(str).str.contains('PENDIENTE', case=False, na=False)
                es_tarj = df_egr[col_medio].astype(str).str.contains('CRED', case=False, na=False)
                no_pago = ~df_egr[col_estado].astype(str).str.contains('REALIZADO|PAGADO', case=False, na=False)
                df_deuda = df_egr[es_pend | (es_tarj & no_pago)]
                monto_deuda = df_deuda['Valor_Final'].sum()

            disponible = total_ing - (total_egr - monto_deuda)
            
            # --- MÉTRICAS ---
            c1, c2, c3 = st.columns(3)
            c1.metric("Disponible (Caja)", f"${disponible:,.2f}")
            c2.metric("Deuda Pendiente", f"${monto_deuda:,.2f}", delta_color="inverse")
            c3.metric("Saldo Neto Final", f"${disponible - monto_deuda:,.2f}")
            
            st.divider()

            # --- GRÁFICOS ---
            g1, g2 = st.columns(2)
            with g1:
                st.write("### ⚖️ Ingresos vs Gastos")
                df_graf = df.groupby(['Cat_Grafico', col_tipo])['Valor_Final'].sum().reset_index()
                fig_bar = px.bar(df_graf, x='Cat_Grafico', y='Valor_Final', color=col_tipo, barmode='group',
                                 color_discrete_map={'INGRESO': '#2ecc71', 'EGRESO': '#e74c3c', 'GASTO': '#e74c3c'})
                st.plotly_chart(fig_bar, use_container_width=True)

            with g2:
                st.write("### 🍕 Torta de Gastos")
                if not df_egr.empty:
                    fig_pie = px.pie(df_egr, values='Valor_Final', names='Cat_Grafico', hole=0.4)
                    st.plotly_chart(fig_pie, use_container_width=True)

        with tab_tarjeta:
            st.subheader("💳 Detalle de Gastos con Tarjeta")
            # Filtramos por cualquier cosa que diga CRED (Credito, Crédito Corporativa, etc)
            df_t = df[df[col_medio].astype(str).str.contains('CRED', case=False, na=False)].copy()
            if not df_t.empty:
                st.info(f"Monto total acumulado: ${df_t['Valor_Final'].sum():,.2f}")
                # Mostramos tabla limpia
                vista = df_t[[col_fecha, 'Cat_Grafico', 'Valor_Final']]
                vista.columns = ['Fecha', 'Categoría', 'Monto $']
                st.table(vista)
            else:
                st.warning("No hay gastos registrados con Tarjeta de Crédito.")

except Exception as e:
    st.error(f"Error detectado: {e}")

with tab_carga:
    st.link_button("📝 IR AL FORMULARIO", FORM_LINK, use_container_width=True)
