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
            # Limpieza de nombres de columnas
            df.columns = [c.strip() for c in df.columns]
            
            # Buscamos columnas clave por nombre
            col_tipo = [c for c in df.columns if 'TIPO' in c.upper()][0]
            col_monto = [c for c in df.columns if 'MONTO' in c.upper()][0]
            cols_estado = [c for c in df.columns if 'ESTADO' in c.upper()]
            col_estado = cols_estado[0] if cols_estado else None
            
            df[col_monto] = pd.to_numeric(df[col_monto], errors='coerce').fillna(0)
            
            # --- CÁLCULOS ---
            total_ingresos = df[df[col_tipo].astype(str).str.contains('INGRESO', case=False, na=False)][col_monto].sum()
            
            # Gastos REALES (Todo lo que sea egreso/gasto, esté pagado o no para el total)
            df_egresos = df[df[col_tipo].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)]
            total_egresos = df_egresos[col_monto].sum()
            
            # Cálculo de Pendientes
            if col_estado:
                pendientes = df_egresos[df_egresos[col_estado].astype(str).str.contains('PENDIENTE', case=False, na=False)][col_monto].sum()
            else:
                pendientes = 0
            
            # El balance de caja es lo que entró menos lo que ya se pagó de verdad
            balance_caja = total_ingresos - (total_egresos - pendientes)
            
            # --- DISEÑO DE TARJETAS (Métricas) ---
            st.subheader("📌 Resumen de Movimientos")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Ingresos", f"${total_ingresos:,.2f}")
            c2.metric("Total Egresos", f"${total_egresos:,.2f}", delta_color="inverse")
            c3.metric("Pagos Pendientes", f"${pendientes:,.2f}", delta="A Pagar", delta_color="normal")
            c4.metric("Saldo en Caja", f"${balance_caja:,.2f}")
            
            st.divider()
            
            # --- GRÁFICOS ---
            col_izq, col_der = st.columns(2)
            with col_izq:
                if not df_egresos.empty:
                    st.write("### 🍕 Gastos por Categoría")
                    # Usamos la columna 3 que suele ser Categoría
                    fig_cat = px.pie(df_egresos, values=col_monto, names=df_egresos.columns[3], hole=0.3)
                    st.plotly_chart(fig_cat, use_container_width=True)
            with col_der:
                if not df_egresos.empty:
                    st.write("### 💳 Gastos por Medio de Pago")
                    fig_met = px.bar(df_egresos, x=df_egresos.columns[5], y=col_monto, color=col_estado if col_estado else None)
                    st.plotly_chart(fig_met, use_container_width=True)
            
            st.subheader("📝 Historial de Movimientos")
            st.dataframe(df.tail(15), use_container_width=True)
            
        else:
            st.info("No hay datos cargados aún.")
            
    except Exception as e:
        st.error(f"Error de visualización: {e}")
        st.info("Asegurate de que las columnas TIPO y MONTO estén bien escritas en el Excel.")

with tab_carga:
    st.subheader("Registrar Nuevo Movimiento")
    st.link_button("📝 ABRIR FORMULARIO DE CARGA", FORM_LINK, use_container_width=True)
