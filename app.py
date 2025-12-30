import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha PRO", layout="wide", page_icon="💳")

# --- ENLACES ---
EXCEL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQGHyOERYRdBB_KqWJjBvBG43Ujuf9y8xYFseHbX_ElKNLOAT_sStrolGifSVOGSsWJpanYtCq9fJz/pub?output=csv"
FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSd5nLZX5Uihw--o_JuKYqxMwnsc4M-g6HupBCuO2xBqTvgC0w/viewform"

st.title("💰 Mi Control Financiero")

tab_resumen, tab_historial, tab_carga = st.tabs(["📊 Resumen y Gráficos", "📋 Gastos por Banco/Tarjeta", "📝 Cargar Datos"])

try:
    df = pd.read_csv(EXCEL_CSV)
    if not df.empty:
        # Limpieza de nombres de columnas
        df.columns = [str(c).strip() for c in df.columns]
        
        # --- BUSCADOR DE COLUMNAS INTELIGENTE ---
        def encontrar_col(palabras):
            for p in palabras:
                for c in df.columns:
                    if p.upper() in c.upper(): return c
            return None

        col_tipo = encontrar_col(['TIPO', 'CARGAR', 'MOVIMIENTO'])
        cols_montos = [c for c in df.columns if 'MONTO' in c.upper() or '$' in c]
        col_medio = encontrar_col(['MÉTODO', 'MEDIO', 'PAGO'])
        # ESTA ES LA COLUMNA CLAVE PARA DISCRIMINAR EL BANCO:
        col_banco = encontrar_col(['CUAL TARJETA', 'NOMBRE TARJETA', 'BANCO', 'ESPECIFIQUE'])
        
        col_estado = encontrar_col(['ESTADO'])
        col_cat_gasto = encontrar_col(['CATEGORÍA DE GASTO', 'GASTO', 'CATEGORIA'])
        col_cat_ingreso = encontrar_col(['CATEGORÍA DE INGRESO', 'INGRESO'])
        col_fecha = encontrar_col(['FECHA']) or df.columns[1]
        col_concepto = encontrar_col(['CONCEPTO', 'DETALLE', 'DESCRIPCION']) or df.columns[4]

        # Limpiar montos
        for col in cols_montos:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df['Monto_Calculado'] = df[cols_montos].sum(axis=1)
        df['Cat_Final'] = df[col_cat_gasto].fillna(df[col_cat_ingreso]).fillna("Otros")

        # Separar Egresos (Gastos)
        df_egr = df[df[col_tipo].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)].copy()

        with tab_resumen:
            # --- CÁLCULOS PRINCIPALES ---
            df_ing = df[df[col_tipo].astype(str).str.contains('INGRESO', case=False, na=False)]
            total_ing = df_ing['Monto_Calculado'].sum()
            total_egr = df_egr['Monto_Calculado'].sum()
            
            monto_deuda = 0
            if col_estado and col_medio:
                es_pend = df_egr[col_estado].astype(str).str.contains('PENDIENTE', case=False, na=False)
                es_tarj = df_egr[col_medio].astype(str).str.contains('CRED', case=False, na=False)
                no_pago = ~df_egr[col_estado].astype(str).str.contains('REALIZADO|PAGADO', case=False, na=False)
                monto_deuda = df_egr[es_pend | (es_tarj & no_pago)]['Monto_Calculado'].sum()

            disponible = total_ing - (total_egr - monto_deuda)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Disponible (Caja)", f"${disponible:,.2f}")
            c2.metric("Deuda Pendiente", f"${monto_deuda:,.2f}", delta_color="inverse")
            c3.metric("Saldo Neto Final", f"${disponible - monto_deuda:,.2f}")
            
            st.divider()
            g1, g2 = st.columns(2)
            with g1:
                st.write("### ⚖️ Comparativa")
                df_bar = df.groupby(['Cat_Final', col_tipo])['Monto_Calculado'].sum().reset_index()
                st.plotly_chart(px.bar(df_bar, x='Cat_Final', y='Monto_Calculado', color=col_tipo, barmode='group',
                                       color_discrete_map={'INGRESO': '#2ecc71', 'EGRESO': '#e74c3c'}), use_container_width=True)
            with g2:
                st.write("### 🍕 Torta de Gastos")
                st.plotly_chart(px.pie(df_egr, values='Monto_Calculado', names='Cat_Final', hole=0.4), use_container_width=True)

        with tab_historial:
            st.subheader("📋 Historial por Tarjeta y Banco")
            
            # Filtramos solo lo que es tarjeta
            df_tarjetas = df_egr[df_egr[col_medio].astype(str).str.contains('CRED', case=False, na=False)].copy()
            
            if not df_tarjetas.empty:
                # Si encontramos la columna del nombre del banco, mostramos los detalles
                if col_banco:
                    bancos_disponibles = ["TODOS"] + df_tarjetas[col_banco].unique().tolist()
                    banco_sel = st.selectbox("Seleccioná un Banco/Tarjeta para ver el detalle:", bancos_disponibles)
                    
                    df_final = df_tarjetas.copy()
                    if banco_sel != "TODOS":
                        df_final = df_tarjetas[df_tarjetas[col_banco] == banco_sel]
                    
                    st.write(f"### Detalle de {banco_sel}")
                    st.warning(f"Total gastado: ${df_final['Monto_Calculado'].sum():,.2f}")
                    
                    # Tabla limpia con el nombre del banco
                    vista = df_final[[col_fecha, col_banco, 'Cat_Final', col_concepto, 'Monto_Calculado']]
