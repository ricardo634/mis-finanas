import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha PRO", layout="wide", page_icon="💰")

# --- ENLACES ---
EXCEL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQGHyOERYRdBB_KqWJjBvBG43Ujuf9y8xYFseHbX_ElKNLOAT_sStrolGifSVOGSsWJpanYtCq9fJz/pub?output=csv"
FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSd5nLZX5Uihw--o_JuKYqxMwnsc4M-g6HupBCuO2xBqTvgC0w/viewform"

st.title("💰 Mi Control Financiero")

tab_resumen, tab_historial, tab_carga = st.tabs(["📊 Resumen y Gráficos", "💳 Historial por Banco", "📝 Cargar Datos"])

try:
    df = pd.read_csv(EXCEL_CSV)
    if not df.empty:
        # Limpieza de nombres de columnas (borra espacios vacíos invisibles)
        df.columns = [str(c).strip() for c in df.columns]
        
        # --- BUSCADOR INTELIGENTE DE COLUMNAS ---
        def encontrar_col(palabras):
            for p in palabras:
                for c in df.columns:
                    if p.upper() in c.upper(): return c
            return None

        # Identificamos las columnas del formulario
        col_tipo = encontrar_col(['TIPO', 'CARGAR', 'MOVIMIENTO'])
        cols_montos = [c for c in df.columns if 'MONTO' in c.upper() or '$' in c]
        col_medio = encontrar_col(['MÉTODO', 'MEDIO', 'PAGO'])
        col_banco = encontrar_col(['CUAL TARJETA', 'BANCO', 'NOMBRE', 'TARJETA']) # <--- Identifica Visa/Master/BBVA
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
            
            total_ing = df_ing['Monto_Total'].sum()
            total_egr = df_egr['Monto_Total'].sum()
            balance = total_ing - total_egr

            c1, c2, c3 = st.columns(3)
            c1.metric("Ingresos Totales", f"${total_ing:,.2f}")
            c2.metric("Gastos Totales", f"${total_egr:,.2f}")
            c3.metric("Saldo Actual", f
