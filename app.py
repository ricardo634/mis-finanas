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
        # Limpieza profunda de nombres de columnas
        df.columns = [str(c).strip() for c in df.columns]
        
        # Mapeo de columnas basado en tu estructura estable
        cols_base = ['Timestamp', 'Fecha', 'Tipo', 'Categoría', 'Monto', 'Método', 'Concepto']
        nombres_finales = cols_base + list(df.columns[len(cols_base):])
        df.columns = nombres_finales
        
        # Limpieza de datos
        df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
        df['Tipo'] = df['Tipo'].astype(str).str.upper().str.strip()
        col_banco = df.columns[7] if len(df.columns) > 7 else 'Método'
        
        # --- FILTROS DE SEGURIDAD PARA INGRESOS Y GASTOS ---
        # Buscamos cualquier cosa que contenga "ING" para Ingresos y "EGR" o "GAS" para Gastos
        df_ingresos = df[df['Tipo'].str.contains('ING', na=False)].copy()
        df_gastos = df[df['Tipo'].str.contains('EGR|GAS', na=False)].copy()
        
        # Separación por flujo de pago (Tarjetas vs Contado)
        df_tarjeta = df_gastos[df_gastos['Método'].astype(str).str.contains('CRED', case=False, na=False)].copy()
        df_contado = df_gastos[~df_gastos['Método'].astype(str).str.contains('CRED', case=False, na=False)].copy()

        # 1. PESTAÑA BALANCES
        with tab_resumen:
            total_ing = df_ingresos["Monto"].sum()
            total_cont = df_contado["Monto"].sum()
            disponible_hoy = total_ing - total_cont
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Ingresos Totales", f"${total_ing:,.2f}")
            c2.metric("Gastos Cash/Débito", f"${total_cont:,.2f}")
            c3.metric("Efectivo Disponible (Caja)", f"${disponible_hoy:,.2f}")
            
            st.divider()
            col_a, col_b = st.columns(2)
            with col_a:
                if not df_gastos.empty:
                    fig_cat = px.pie(df_gastos, values='Monto', names='Categoría', title="Distribución de Gastos")
                    st.plotly_chart(fig_cat, use_container_width=True)
            with col_b:
                # Historial de TODO incluyendo ingresos
                st.write("### 📝 Últimos Movimientos")
                st.dataframe(df[['Fecha', 'Tipo', 'Categoría', 'Monto', 'Método']].sort_index(ascending=False).head(10), use_container_width=True)

        # 2. PESTAÑA PROYECCIÓN
        with tab_proyeccion:
            st.subheader("🔮 Impacto de Tarjetas en tu Sueldo")
            
            total_deuda_tc = df_tarjeta["Monto"].sum()
            balance_proyectado = disponible_hoy - total_deuda_tc
            porcentaje_comprometido = (total_deuda_tc / total_ing * 100) if total_ing > 0 else 0

            m1, m2, m3 = st.columns(3)
            m1.metric("Deuda Acumulada TC", f"${total_deuda_tc:,.2f}", delta="Pendiente", delta_color="inverse")
            m2.metric("Bolsillo Real (Proyectado)", f"${balance_proyectado:,.2f}", help="Saldo tras pagar tarjetas")
            m3.metric("% Ingresos Comprometidos", f"{porcentaje_comprometido:.1f}%")

            st.divider()
            
            if not df_tarjeta.empty:
                st.write("### 🏦 Deuda por Tarjeta/Banco")
                df_agrupado_tc = df_tarjeta.groupby(col_banco)['Monto'].sum().reset_index()
                fig_tc = px.bar(df_agrupado_tc, x=col_banco, y='Monto', color=col_banco, text_auto='.2s')
                st.plotly_chart(fig_tc, use_container_width=True)
                
                st.write("### 📜 Detalle de consumos de Tarjeta")
                st.dataframe(df_tarjeta[['Fecha', col_banco, 'Categoría', 'Concepto', 'Monto']].sort_values(by='Fecha', ascending=False), use_container_width=True)
            else:
                st.info("No hay deudas de tarjeta para proyectar.")

except Exception as e:
    st.error(f"Error: {e}")

with tab_carga:
    st.link_button("📝 REGISTRAR NUEVO MOVIMIENTO", FORM_LINK, use_container_width=True)
