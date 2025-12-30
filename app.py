import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha PRO", layout="wide", page_icon="💳")

# --- ENLACES ---
EXCEL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQGHyOERYRdBB_KqWJjBvBG43Ujuf9y8xYFseHbX_ElKNLOAT_sStrolGifSVOGSsWJpanYtCq9fJz/pub?output=csv"
FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSd5nLZX5Uihw--o_JuKYqxMwnsc4M-g6HupBCuO2xBqTvgC0w/viewform"

st.title("💰 Mi Control Financiero")

tab_resumen, tab_tarjeta, tab_carga = st.tabs(["📊 Resumen y Gráficos", "💳 Solo Tarjetas", "📝 Cargar Datos"])

with tab_resumen:
    try:
        df = pd.read_csv(EXCEL_CSV)
        if not df.empty:
            df.columns = [c.strip() for c in df.columns]
            
            # --- BUSCADOR DE COLUMNAS ---
            def encontrar_columna(lista_palabras):
                for palabra in lista_palabras:
                    for col in df.columns:
                        if palabra.upper() in col.upper():
                            return col
                return None

            col_tipo = encontrar_columna(['TIPO', 'CARGAR', 'MOVIMIENTO'])
            cols_montos = [c for c in df.columns if 'MONTO' in c.upper() or '$' in c]
            col_medio = encontrar_columna(['MÉTODO', 'MEDIO', 'PAGO'])
            col_estado = encontrar_columna(['ESTADO'])
            col_cat_gasto = encontrar_columna(['CATEGORÍA DE GASTO', 'GASTO'])
            col_cat_ingreso = encontrar_columna(['CATEGORÍA DE INGRESO', 'INGRESO'])

            # Limpiar montos
            for col in cols_montos:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            df['Suma_Final'] = df[cols_montos].sum(axis=1)
            df['Cat_Grafico'] = df[col_cat_gasto].fillna(df[col_cat_ingreso]).fillna("Otros")

            # --- CÁLCULOS ---
            df_ing = df[df[col_tipo].astype(str).str.contains('INGRESO', case=False, na=False)]
            total_ing = df_ing['Suma_Final'].sum()
            
            df_egr = df[df[col_tipo].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)]
            total_egr = df_egr['Suma_Final'].sum()
            
            # Deuda
            monto_deuda = 0
            df_deuda = pd.DataFrame()
            if col_estado and col_medio:
                es_pend = df_egr[col_estado].astype(str).str.contains('PENDIENTE', case=False, na=False)
                es_tarj = df_egr[col_medio].astype(str).str.contains('CREDITO', case=False, na=False)
                no_pago = ~df_egr[col_estado].astype(str).str.contains('REALIZADO|PAGADO', case=False, na=False)
                df_deuda = df_egr[es_pend | (es_tarj & no_pago)]
                monto_deuda = df_deuda['Suma_Final'].sum()

            disponible = total_ing - (total_egr - monto_deuda)
            
            # --- MÉTRICAS ---
            c1, c2, c3 = st.columns(3)
            c1.
