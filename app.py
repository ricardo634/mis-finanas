import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha PRO", layout="wide", page_icon="💳")

# --- ENLACES ---
EXCEL_CSV ="https://docs.google.com/spreadsheets/d/e/2PACX-1vTQGHyOERYRdBB_KqWJjBvBG43Ujuf9y8xYFseHbX_ElKNLOAT_sStrolGifSVOGSsWJpanYtCq9fJz/pub?output=csv"
FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSd5nLZX5Uihw--o_JuKYqxMwnsc4M-g6HupBCuO2xBqTvgC0w/viewform"

st.title("💰 Mi Control Financiero")

tab_resumen, tab_tarjeta, tab_carga = st.tabs(["📊 Resumen General", "💳 Solo Tarjetas", "📝 Cargar Datos"])

with tab_resumen:
    try:
        df = pd.read_csv(EXCEL_CSV)
        if not df.empty:
            # Limpiamos nombres de columnas
            df.columns = [c.strip() for c in df.columns]
            
            # Buscamos columnas por palabras clave para que no falle si cambian de nombre
            def buscar_col(keyword):
                lista = [c for c in df.columns if keyword.upper() in c.upper()]
                return lista[0] if lista else None

            col_tipo = buscar_col('TIPO')
            col_monto = buscar_col('MONTO')
            col_medio = buscar_col('MÉTODO') or buscar_col('MEDIO')
            col_estado = buscar_col('ESTADO')
            col_cat_gasto = buscar_col('CATEGORÍA DE GASTO') or buscar_col('CATEGORÍA')
            
            # Limpieza de montos (para que no de error con textos)
            df[col_monto] = pd.to_numeric(df[col_monto], errors='coerce').fillna(0)
            
            # --- CÁLCULOS ---
            total_ingresos = df[df[col_tipo].astype(str).str.contains('INGRESO', case=False, na=False)][col_monto].sum()
            
            df_egresos = df[df[col_tipo].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)]
            total_egresos = df_egresos[col_monto].sum()
            
            # Deuda (Tarjeta o cualquier cosa Pendiente)
            if col_estado:
                mask_pend = df_egresos[col_estado].astype(str).str.contains('PENDIENTE', case=False, na=False)
                mask_tarjeta = df_egresos[col_medio].astype(str).str.contains('CREDITO', case=False, na=False)
                # Es deuda si es Pendiente O si es Tarjeta (y no está explícitamente Pagado)
                df_deuda = df_egresos[mask_pend | (mask_tarjeta & ~df_egresos[col_estado].astype(str).str.contains('REALIZADO|PAGADO', case=False, na=False))]
                monto_deuda = df_deuda[col_monto].sum()
            else:
                monto_deuda = 0

            balance_disponible = total_ingresos - (total_egresos - monto_deuda)
            
            # --- MÉTRICAS ---
            c1, c2, c3 = st.columns(3)
            c1.metric("Disponible (Caja)", f"${balance_disponible:,.2f}")
            c2.metric("Deuda (Tarjeta/Pend.)", f"${monto_deuda:,.2f}", delta_color="inverse")
            c3.metric("Saldo Neto Final", f"${balance_disponible - monto_deuda:,.2f}")
            
            st.divider()

            # --- GRÁFICO (Corregido para que no falle por nombre de columna) ---
            if not df_egresos.empty:
                st.write("### 📈 Distribución de Gastos")
                fig_mix = px.bar(df_egresos, x=col_cat_gasto, y=col_monto, color=col_medio, barmode='group')
                st.plotly_chart(fig_mix, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {e}")

with tab_tarjeta:
    st.subheader("🔎 Detalle de Tarjeta de Crédito")
    try:
        df_solo_tarjeta = df[df[col_medio].astype(str).str.contains('CREDITO', case=False, na=False)]
        if not df_solo_tarjeta.empty:
            st.write(f"#### Total a pagar en resumen: ${df_solo_tarjeta[col_monto].sum():,.2f}")
            st.dataframe(df_solo_tarjeta, use_container_width=True)
        else:
            st.info("No hay consumos con tarjeta.")
    except:
        st.write("Cargá datos para ver el detalle.")

with tab_carga:
    st.subheader("Registrar Movimiento")
    st.link_button("📝 IR AL FORMULARIO", FORM_LINK, use_container_width=True)
