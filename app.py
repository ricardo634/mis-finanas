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
            df.columns = [c.strip() for c in df.columns]
            
            # Identificación de columnas
            col_tipo = [c for c in df.columns if 'TIPO' in c.upper()][0]
            col_monto = [c for c in df.columns if 'MONTO' in c.upper()][0]
            cols_estado = [c for c in df.columns if 'ESTADO' in c.upper()]
            col_estado = cols_estado[0] if cols_estado else None
            
            df[col_monto] = pd.to_numeric(df[col_monto], errors='coerce').fillna(0)
            
            # --- CÁLCULOS ---
            total_ingresos = df[df[col_tipo].astype(str).str.contains('INGRESO', case=False, na=False)][col_monto].sum()
            df_egresos = df[df[col_tipo].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)]
            total_egresos = df_egresos[col_monto].sum()
            
            # Filtrar las deudas reales
            df_pendientes = pd.DataFrame()
            if col_estado:
                df_pendientes = df_egresos[df_egresos[col_estado].astype(str).str.contains('PENDIENTE', case=False, na=False)]
                monto_pendientes = df_pendientes[col_monto].sum()
            else:
                monto_pendientes = 0
            
            balance_caja = total_ingresos - (total_egresos - monto_pendientes)
            
            # --- MÉTRICAS ---
            st.subheader("📌 Resumen General")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Ingresos", f"${total_ingresos:,.2f}")
            c2.metric("Egresos Totales", f"${total_egresos:,.2f}")
            c3.metric("A Pagar (Pendientes)", f"${monto_pendientes:,.2f}", delta="Pendiente", delta_color="inverse")
            c4.metric("Saldo Real en Caja", f"${balance_caja:,.2f}")
            
            st.divider()

            # --- SECCIÓN DE DEUDAS (SOLO SI HAY) ---
            if not df_pendientes.empty:
                with st.expander("🚩 VER DETALLE DE PAGOS PENDIENTES", expanded=True):
                    st.warning(f"Tenés {len(df_pendientes)} pagos por realizar:")
                    # Mostramos Fecha, Categoría, Monto y Concepto de la deuda
                    st.table(df_pendientes[['Fecha', 'Categoría', 'Monto', 'Concepto']])
                st.divider()
            
            # --- GRÁFICOS ---
            col_izq, col_der = st.columns(2)
            with col_izq:
                if not df_egresos.empty:
                    st.write("### 🍕 Gastos por Categoría")
                    fig_cat = px.pie(df_egresos, values=col_monto, names=df_egresos.columns[3], hole=0.3)
                    st.plotly_chart(fig_cat, use_container_width=True)
            with col_der:
                if not df_egresos.empty:
                    st.write("### 💳 Gastos por Medio de Pago")
                    fig_met = px.bar(df_egresos, x=df_egresos.columns[5], y=col_monto, color=col_estado if col_estado else None)
                    st.plotly_chart(fig_met, use_container_width=True)
            
            st.subheader("📝 Historial Completo")
            st.dataframe(df.sort_values(by=df.columns[0], ascending=False), use_container_width=True)
            
        else:
            st.info("No hay datos cargados aún.")
            
    except Exception as e:
        st.error(f"Error: {e}")

with tab_carga:
    st.subheader("Registrar Nuevo Movimiento")
    st.link_button("📝 ABRIR FORMULARIO DE CARGA", FORM_LINK, use_container_width=True)
