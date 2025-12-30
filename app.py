import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha PRO", layout="wide", page_icon="💰")

# --- ENLACES ---
EXCEL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQGHyOERYRdBB_KqWJjBvBG43Ujuf9y8xYFseHbX_ElKNLOAT_sStrolGifSVOGSsWJpanYtCq9fJz/pub?output=csv"
FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSd5nLZX5Uihw--o_JuKYqxMwnsc4M-g6HupBCuO2xBqTvgC0w/viewform"

st.title("💰 Mi Control Financiero")

tab_resumen, tab_carga = st.tabs(["📊 Resumen y Balances", "📝 Cargar Datos"])

with tab_resumen:
    try:
        df = pd.read_csv(EXCEL_CSV)
        
        if not df.empty:
            # Limpiamos los nombres de columnas para que no tengan espacios raros
            df.columns = [c.strip() for c in df.columns]
            
            # Buscamos las columnas por palabras clave por si cambiaron de lugar
            col_tipo = [c for c in df.columns if 'TIPO' in c.upper()][0]
            col_monto = [c for c in df.columns if 'MONTO' in c.upper()][0]
            # Si no encuentra 'Estado', usa una columna vacía para no dar error
            cols_estado = [c for c in df.columns if 'ESTADO' in c.upper()]
            col_estado = cols_estado[0] if cols_estado else None
            
            # Convertimos monto a número
            df[col_monto] = pd.to_numeric(df[col_monto], errors='coerce').fillna(0)
            
            # --- CALCULOS ---
            ingresos = df[df[col_tipo].astype(str).str.contains('INGRESO', case=False, na=False)][col_monto].sum()
            
            # Filtro de Pendientes (Solo si existe la columna Estado)
            if col_estado:
                pendientes = df[(df[col_tipo].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)) & 
                                (df[col_estado].astype(str).str.contains('PENDIENTE', case=False, na=False))][col_monto].sum()
                
                realizados = df[(df[col_tipo].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)) & 
                                (~df[col_estado].astype(str).str.contains('PENDIENTE', case=False, na=False))][col_monto].sum()
            else:
                pendientes = 0
                realizados = df[df[col_tipo].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)][col_monto].sum()

            balance_actual = ingresos - realizados
            
            # --- MÉTRICAS ---
            c1, c2 = st.columns(2)
            c1.metric("Balance Actual (Caja)", f"${balance_actual:,.2f}")
            c2.metric("Pagos Pendientes", f"${pendientes:,.2f}", delta_color="inverse")
            
            if pendientes > 0:
                st.warning(f"⚠️ Tenés ${pendientes:,.2f} en pagos pendientes.")
            
            st.divider()
            
            # --- GRÁFICO ---
            df_gastos = df[df[col_tipo].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)]
            if not df_gastos.empty:
                fig_cat = px.pie(df_gastos, values=col_monto, names=df_gastos.columns[3], title="Distribución de Gastos")
                st.plotly_chart(fig_cat, use_container_width=True)
            
            st.subheader("📝 Historial Reciente")
            st.dataframe(df.tail(10), use_container_width=True)
            
        else:
            st.info("El Excel está vacío. Cargá un dato para empezar.")
            
    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Asegurate de que las columnas TIPO y MONTO existan en tu Excel.")

with tab_carga:
    st.subheader("Registrar Nuevo Movimiento")
    st.link_button("📝 ABRIR FORMULARIO DE CARGA", FORM_LINK, use_container_width=True)
