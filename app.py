import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha PRO", layout="wide", page_icon="💰")

# --- ENLACES ---
EXCEL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQGHyOERYRdBB_KqWJjBvBG43Ujuf9y8xYFseHbX_ElKNLOAT_sStrolGifSVOGSsWJpanYtCq9fJz/pub?output=csv"
FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSd5nLZX5Uihw--o_JuKYqxMwnsc4M-g6HupBCuO2xBqTvgC0w/viewform"

st.title("💰 Mi Control Financiero")

tab_resumen, tab_historial, tab_carga = st.tabs(["📊 Resumen y Gráficos", "💳 Detalle por Banco", "📝 Cargar Datos"])

try:
    df = pd.read_csv(EXCEL_CSV)
    if not df.empty:
        # Limpieza de nombres de columnas
        df.columns = [str(c).strip() for c in df.columns]
        
        # --- BUSCADOR DE COLUMNAS ---
        def encontrar_col(palabras):
            for p in palabras:
                for c in df.columns:
                    if p.upper() in c.upper(): return c
            return None

        col_tipo = encontrar_col(['TIPO', 'CARGAR', 'MOVIMIENTO'])
        cols_montos = [c for c in df.columns if 'MONTO' in c.upper() or '$' in c]
        col_medio = encontrar_col(['MÉTODO', 'MEDIO', 'PAGO'])
        col_banco = encontrar_col(['CUAL TARJETA', 'BANCO', 'NOMBRE', 'TARJETA'])
        col_cat_gasto = encontrar_col(['CATEGORÍA DE GASTO', 'GASTO', 'CATEGORIA'])
        col_cat_ingreso = encontrar_col(['CATEGORÍA DE INGRESO', 'INGRESO'])
        col_fecha = encontrar_col(['FECHA']) or df.columns[1]
        col_concepto = encontrar_col(['CONCEPTO', 'DETALLE', 'DESCRIPCION']) or df.columns[4]

        # Limpiar y sumar montos
        for col in cols_montos:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df['Monto_Total'] = df[cols_montos].sum(axis=1)
        df['Cat_Final'] = df[col_cat_gasto].fillna(df[col_cat_ingreso]).fillna("Otros")

        # 1. PESTAÑA RESUMEN
        with tab_resumen:
            df_ing = df[df[col_tipo].astype(str).str.contains('INGRESO', case=False, na=False)]
            df_egr = df[df[col_tipo].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)]
            
            t_ing = df_ing['Monto_Total'].sum()
            t_egr = df_egr['Monto_Total'].sum()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Ingresos", f"${t_ing:,.2f}")
            c2.metric("Gastos", f"${t_egr:,.2f}")
            c3.metric("Saldo", f"${t_ing - t_egr:,.2f}")
            
            st.divider()
            g1, g2 = st.columns(2)
            with g1:
                st.write("### ⚖️ Gastos por Categoría")
                fig_bar = px.bar(df_egr.groupby('Cat_Final')['Monto_Total'].sum().reset_index(), x='Cat_Final', y='Monto_Total', color='Cat_Final')
                st.plotly_chart(fig_bar, use_container_width=True)
            with g2:
                st.write("### 🍕 Torta de Gastos")
                st.plotly_chart(px.pie(df_egr, values='Monto_Total', names='Cat_Final', hole=0.4), use_container_width=True)

        # 2. PESTAÑA HISTORIAL POR BANCO (Lo que pediste)
        with tab_historial:
            st.subheader("💳 Detalle por Tarjeta Bancaria")
            
            # Filtramos solo los gastos hechos con tarjeta
            df_tarjetas = df_egr[df_egr[col_medio].astype(str).str.contains('CRED', case=False, na=False)].copy()
            
            if not df_tarjetas.empty:
                # Selector de Banco
                opciones = ["TODAS"] + sorted(df_tarjetas[col_banco].dropna().unique().tolist())
                banco_sel = st.selectbox("Seleccioná el Banco o Tarjeta:", opciones)
                
                df_final = df_tarjetas if banco_sel == "TODAS" else df_tarjetas[df_tarjetas[col_banco] == banco_sel]
                
                st.info(f"Total gastado en {banco_sel}: ${df_final['Monto_Total'].sum():,.2f}")
                
                # Tabla limpia
                vista = df_final[[col_fecha, col_banco, 'Cat_Final', col_concepto, 'Monto_Total']]
                vista.columns = ['Fecha', 'Banco/Tarjeta', 'Categoría', 'Detalle', 'Monto $']
                st.dataframe(vista.sort_values(by='Fecha', ascending=False), use_container_width=True)
            else:
                st.info("No hay gastos con tarjeta registrados.")

except Exception as e:
    st.error(f"Error: {e}")

with tab_carga:
    st.link_button("📝 IR AL FORMULARIO", FORM_LINK, use_container_width=True)
