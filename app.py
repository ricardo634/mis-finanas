import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

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
            col_fecha = df.columns[0]
            col_tipo = next((c for c in df.columns if 'TIPO' in c.upper()), None)
            cols_montos = [c for c in df.columns if 'MONTO' in c.upper()]
            col_medio = next((c for c in df.columns if 'MÉTODO' in c.upper() or 'MEDIO' in c.upper()), None)
            col_estado = next((c for c in df.columns if 'ESTADO' in c.upper()), None)
            col_cat_gasto = next((c for c in df.columns if 'CATEGORÍA DE GASTO' in c.upper() or 'CATEGORÍA' in c.upper()), df.columns[3])
            col_concepto = next((c for c in df.columns if 'CONCEPTO' in c.upper()), df.columns[4])

            for col in cols_montos:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # --- LÓGICA DE SALDOS ---
            df_ingresos = df[df[col_tipo].astype(str).str.contains('INGRESO', case=False, na=False)]
            total_ingresos = df_ingresos[cols_montos].sum(axis=1).sum()
            
            df_egresos = df[df[col_tipo].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)]
            total_egresos = df_egresos[cols_montos].sum(axis=1).sum()
            
            # Identificar Deudas (Pendientes o Tarjeta no pagada)
            mask_pend = df_egresos[col_estado].astype(str).str.contains('PENDIENTE', case=False, na=False) if col_estado else False
            mask_tarjeta = df_egresos[col_medio].astype(str).str.contains('CREDITO', case=False, na=False) if col_medio else False
            mask_no_pagado = ~df_egresos[col_estado].astype(str).str.contains('REALIZ
