import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha PRO", layout="wide", page_icon="💰")

# --- ENLACES ---
EXCEL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQGHyOERYRdBB_KqWJjBvBG43Ujuf9y8xYFseHbX_ElKNLOAT_sStrolGifSVOGSsWJpanYtCq9fJz/pub?output=csv"

FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSd5nLZX5Uihw--o_JuKYqxMwnsc4M-g6HupBCuO2xBqTvgC0w/viewform"

st.title("🚀 Inteligencia de Gastos & Proyección")

tab_resumen, tab_proyeccion, tab_carga = st.tabs(["📊 Balances Actuales", "🔮 Proyección de Tarjetas", "📝 Cargar Datos"])

try:
    df = pd.read_csv(EXCEL_CSV)
    if not df.empty:
        # Estandarización de columnas
        cols_base = ['Timestamp', 'Fecha', 'Tipo', 'Categoría', 'Monto', 'Método', 'Concepto']
        # Identificamos si existe la columna de Banco (generalmente la 8va)
        df.columns = cols_base + list(df.columns[len(cols_base):])
        col_banco = df.columns[7] if len(df.columns) > 7 else 'Método'
        
        # Limpieza y conversión
        df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
        
        # Segmentación de datos
        df_gastos = df[df['Tipo'].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)].copy()
        df_ingresos = df[df['Tipo'].astype(str).str.contains('INGRESO', case=False, na=False)].copy()
        
        # Separación por flujo de pago
        df_tarjeta = df_gastos[df_gastos['Método'].astype(str).str.contains('CRED', case=False, na=False)].copy()
        df_contado = df_gastos[~df_gastos['Método'].astype(str).str.contains('CRED', case=False, na=False)].copy()

        # 1. PESTAÑA BALANCES (LO ACTUAL)
        with tab_resumen:
            total_ing = df_ingresos["Monto"].sum()
            total_cont = df_contado["Monto"].sum()
            disponible_hoy = total_ing - total_cont
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Ingresos Totales", f"${total_ing:,.2f}")
            c2.metric("Gastos Cash/Débito", f"${total_cont:,.2f}")
            c3.metric("Efectivo Disponible", f"${disponible_hoy:,.2f}", delta="Caja real")
            
            st.divider()
            col_a, col_b = st.columns(2)
            with col_a:
                st.plotly_chart(px.pie(df_gastos, values='Monto', names='Categoría', title="Distribución de Gastos"), use_container_width=True)
            with col_b:
                st.plotly_chart(px.bar(df_gastos.groupby('Método')['Monto'].sum().reset_index(), x='Método', y='Monto', color='Método', title="Uso de Medios de Pago"), use_container_width=True)

        # 2. PESTAÑA PROYECCIÓN (EL FUTURO)
        with tab_proyeccion:
            st.subheader("🔮 Impacto en el futuro de tu bolsillo")
            
            total_deuda_tc = df_tarjeta["Monto"].sum()
            balance_proyectado = disponible_hoy - total_deuda_tc
            porcentaje_comprometido = (total_deuda_tc / total_ing * 100) if total_ing > 0 else 0

            m1, m2, m3 = st.columns(3)
            m1.metric("Deuda Acumulada TC", f"${total_deuda_tc:,.2f}", delta="A liquidar", delta_color="inverse")
            m2.metric("Bolsillo Real (Proyectado)", f"${balance_proyectado:,.2f}", help="Es lo que te queda después de pagar las tarjetas")
            m3.metric("% de Sueldo Comprometido", f"{porcentaje_comprometido:.1f}%")

            st.divider()
            
            # Agrupación por Banco/Tarjeta
            st.write("### 🏦 Deuda discriminada por Tarjeta/Banco")
            df_agrupado_tc = df_tarjeta.groupby(col_banco)['Monto'].sum().reset_index().sort_values(by='Monto', ascending=False)
            
            p_col1, p_col2 = st.columns([1, 2])
            with p_col1:
                st.table(df_agrupado_tc.rename(columns={col_banco: 'Entidad', 'Monto': 'Deuda $'}))
            with p_col2:
                fig_tc = px.bar(df_agrupado_tc, x=col_banco, y='Monto', text_auto='.2s', color=col_banco, title="Carga de deuda por tarjeta")
                st.plotly_chart(fig_tc, use_container_width=True)
            
            st.write("### 📜 Detalle de consumos que vendrán en el resumen")
            st.dataframe(df_tarjeta[['Fecha', col_banco, 'Categoría', 'Concepto', 'Monto']].sort_values(by='Fecha', ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Error al procesar la proyección: {e}")

with tab_carga:
    st.link_button("📝 REGISTRAR NUEVO GASTO", FORM_LINK, use_container_width=True)
