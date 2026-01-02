import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha PRO", layout="wide", page_icon="💰")

# --- ENLACES ---
EXCEL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQGHyOERYRdBB_KqWJjBvBG43Ujuf9y8xYFseHbX_ElKNLOAT_sStrolGifSVOGSsWJpanYtCq9fJz/pub?output=csv"
FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSd5nLZX5Uihw--o_JuKYqxMwnsc4M-g6HupBCuO2xBqTvgC0w/viewform"

st.title("💰 Inteligencia Financiera Bocha")

tab_resumen, tab_proyeccion, tab_carga = st.tabs(["📊 Balances Actuales", "🔮 Proyección de Tarjetas", "📝 Cargar Datos"])

try:
    # 1. Carga y Limpieza Automática
    df = pd.read_csv(EXCEL_CSV)
    df.columns = [str(c).strip() for c in df.columns] # Limpiar espacios en títulos
    df = df.dropna(how='all', axis=0) # Eliminar filas vacías que causan el loop

    if not df.empty:
        # 2. Motor de Rastreo de Columnas (Busca por palabras clave)
        def detectar(lista_palabras):
            for p in lista_palabras:
                for c in df.columns:
                    if p.upper() in c.upper(): return c
            return None

        col_monto = detectar(['MONTO', 'CANTIDAD', '$'])
        col_tipo = detectar(['TIPO', 'MOVIMIENTO', 'CARGAR'])
        col_medio = detectar(['MÉTODO', 'MEDIO', 'PAGO'])
        col_banco = detectar(['CUAL TARJETA', 'BANCO', 'NOMBRE', 'TARJETA'])
        col_cat = detectar(['CATEGORÍA', 'GASTO', 'CONCEPTO'])
        col_fecha = detectar(['FECHA', 'TIMESTAMP'])

        # 3. Procesamiento de Datos
        df[col_monto] = pd.to_numeric(df[col_monto], errors='coerce').fillna(0)
        
        # Filtros de seguridad
        df_ing = df[df[col_tipo].astype(str).str.upper().str.contains('ING', na=False)].copy()
        df_gas = df[df[col_tipo].astype(str).str.upper().str.contains('EGR|GAS', na=False)].copy()
        
        # Separación para Proyección (Tarjetas vs Otros)
        df_tc = df_gas[df_gas[col_medio].astype(str).str.upper().str.contains('CRED', na=False)].copy()
        df_contado = df_gas[~df_gas[col_medio].astype(str).str.upper().str.contains('CRED', na=False)].copy()

        with tab_resumen:
            total_ing = df_ing[col_monto].sum()
            total_contado = df_contado[col_monto].sum()
            total_tc = df_tc[col_monto].sum()
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Ingresos Totales", f"${total_ing:,.2f}")
            c2.metric("Gastos Realizados (Caja)", f"${total_contado:,.2f}")
            c3.metric("Saldo Real Hoy", f"${total_ing - total_contado:,.2f}", help="Dinero en mano/cuenta")
            
            st.divider()
            col_a, col_b = st.columns(2)
            with col_a:
                st.plotly_chart(px.pie(df_gas, values=col_monto, names=col_cat, title="Gastos por Categoría"), use_container_width=True)
            with col_b:
                # Historial rápido
                st.write("### 📝 Últimos Movimientos")
                st.dataframe(df[[col_fecha, col_tipo, col_cat, col_monto]].sort_index(ascending=False).head(10), use_container_width=True)

        with tab_proyeccion:
            st.subheader("🔮 Proyección de Deuda y Futuro")
            
            saldo_proyectado = (total_ing - total_contado) - total_tc
            impacto = (total_tc / total_ing * 100) if total_ing > 0 else 0
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Deuda Acumulada TC", f"${total_tc:,.2f}", delta_color="inverse")
            m2.metric("Saldo Post-Tarjetas", f"${saldo_proyectado:,.2f}", help="Lo que te quedará tras pagar las tarjetas")
            m3.metric("% Sueldo Comprometido", f"{impacto:.1f}%")

            st.divider()
            
            if not df_tc.empty:
                st.write("### 🏦 Deuda discriminada por Banco")
                # Agrupamos por la columna de Banco que detectamos
                df_bancos = df_tc.groupby(col_banco)[col_monto].sum().reset_index()
                st.plotly_chart(px.bar(df_bancos, x=col_banco, y=col_monto, color=col_banco, text_auto='.2s'), use_container_width=True)
                
                st.write("### 📜 Detalle de gastos con tarjeta")
                st.dataframe(df_tc[[col_fecha, col_banco, col_cat, col_monto]].sort_values(by=col_fecha, ascending=False), use_container_width=True)

except Exception as e:
    st.error(f"Error de sincronización. Probablemente el Excel tiene filas vacías al final. Detalle: {e}")

with tab_carga:
    st.link_button("📝 ABRIR FORMULARIO", FORM_LINK, use_container_width=True)
