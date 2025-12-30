import streamlit as st
import pandas as pd
import plotly.express as px

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
            
            # Identificamos columnas
            col_tipo = [c for c in df.columns if 'TIPO' in c.upper()][0]
            col_monto = [c for c in df.columns if 'MONTO' in c.upper()][0]
            col_medio = [c for c in df.columns if 'MEDIO' in c.upper() or 'PAGO' in c.upper()][0]
            col_estado = [c for c in df.columns if 'ESTADO' in c.upper()][0]
            
            df[col_monto] = pd.to_numeric(df[col_monto], errors='coerce').fillna(0)
            
            # --- CÁLCULOS GENERALES ---
            ingresos = df[df[col_tipo].str.contains('INGRESO', case=False, na=False)][col_monto].sum()
            
            # Gastos REALIZADOS (No son tarjeta o ya fueron pagados)
            gastos_reales = df[(df[col_tipo].str.contains('EGRESO|GASTO', case=False, na=False)) & 
                               (~df[col_medio].str.contains('CREDITO', case=False, na=False))][col_monto].sum()
            
            # Deuda de Tarjeta (Todo lo que diga Crédito y no esté pagado)
            deuda_tarjeta = df[(df[col_medio].str.contains('CREDITO', case=False, na=False)) & 
                               (~df[col_estado].str.contains('REALIZADO|PAGADO', case=False, na=False))][col_monto].sum()

            balance_disponible = ingresos - gastos_reales
            
            # --- MÉTRICAS ---
            c1, c2, c3 = st.columns(3)
            c1.metric("Efectivo/Débito Disponible", f"${balance_disponible:,.2f}")
            c2.metric("Deuda Total Tarjeta", f"${deuda_tarjeta:,.2f}", delta="A pagar", delta_color="inverse")
            c3.metric("Saldo Final (Post-Tarjeta)", f"${balance_disponible - deuda_tarjeta:,.2f}")
            
            st.divider()
            st.write("### 📈 Gastos Totales (Mix)")
            fig_mix = px.bar(df[df[col_tipo].str.contains('EGRESO|GASTO', case=False, na=False)], 
                             x='Categoría', y=col_monto, color=col_medio, barmode='group')
            st.plotly_chart(fig_mix, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")

with tab_tarjeta:
    st.subheader("🔎 Detalle de Tarjeta de Crédito")
    try:
        df_solo_tarjeta = df[df[col_medio].str.contains('CREDITO', case=False, na=False)]
        if not df_solo_tarjeta.empty:
            # Gráfico de torta solo de la tarjeta
            fig_torta_tarjeta = px.pie(df_solo_tarjeta, values=col_monto, names='Categoría', title="¿En qué usé la tarjeta?")
            st.plotly_chart(fig_torta_tarjeta)
            
            st.write("#### Movimientos de la Tarjeta")
            st.dataframe(df_solo_tarjeta[['Fecha', 'Categoría', col_monto, col_estado]], use_container_width=True)
        else:
            st.info("No hay consumos con tarjeta registrados.")
    except:
        st.write("Cargá datos para ver el detalle.")

with tab_carga:
    st.subheader("Registrar Movimiento")
    st.link_button("📝 IR AL FORMULARIO ÚNICO", FORM_LINK, use_container_width=True)
    st.info("💡 Consejo: En el mismo formulario, seleccioná 'Tarjeta de Crédito' para que se sume automáticamente a tu deuda.")
