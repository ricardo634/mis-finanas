import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha PRO", layout="wide", page_icon="💰")

# --- ENLACES ---
EXCEL_CSV = import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha PRO", layout="wide", page_icon="💰")

# --- ENLACES ---
EXCEL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQGHyOERYRdBB_KqWJjBvBG43Ujuf9y8xYFseHbX_ElKNLOAT_sStrolGifSVOGSsWJpanYtCq9fJz/pub?output=csv"
FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSd5nLZX5Uihw--o_JuKYqxMwnsc4M-g6HupBCuO2xBqTvgC0w/viewform"

st.title("💰 Inteligencia Financiera Bocha")

tab_resumen, tab_tarjetas, tab_carga = st.tabs(["📊 Balance y Proyección", "💳 Análisis de Tarjetas", "📝 Cargar Datos"])

try:
    df = pd.read_csv(EXCEL_CSV)
    if not df.empty:
        # Estandarizamos columnas (Marca, Fecha, Tipo, Categoría, Monto, Método, Concepto, [Banco/Tarjeta])
        # Asumimos que la columna 8 (índice 7) es donde guardas el nombre de la tarjeta/banco
        cols_base = ['Timestamp', 'Fecha', 'Tipo', 'Categoría', 'Monto', 'Método', 'Concepto']
        nombres_finales = cols_base + list(df.columns[len(cols_base):])
        df.columns = nombres_finales
        
        # Limpieza de montos y fechas
        df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
        col_banco = df.columns[7] if len(df.columns) > 7 else 'Método'

        # Separación de datos
        df_gastos = df[df['Tipo'].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)].copy()
        df_ingresos = df[df['Tipo'].astype(str).str.contains('INGRESO', case=False, na=False)].copy()
        
        # Identificación de Tarjetas de Crédito
        df_tc = df_gastos[df_gastos['Método'].astype(str).str.contains('CRED', case=False, na=False)].copy()
        df_contado = df_gastos[~df_gastos['Método'].astype(str).str.contains('CRED', case=False, na=False)].copy()

        with tab_resumen:
            # --- CÁLCULOS DE PROYECCIÓN ---
            total_ing = df_ingresos["Monto"].sum()
            total_contado = df_contado["Monto"].sum()
            total_tc = df_tc["Monto"].sum()
            
            saldo_caja = total_ing - total_contado
            saldo_final_proyectado = saldo_caja - total_tc
            impacto_tc = (total_tc / total_ing * 100) if total_ing > 0 else 0

            # --- MÉTRICAS ESTRATÉGICAS ---
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Efectivo/Débito (Caja)", f"${saldo_caja:,.2f}")
            c2.metric("Deuda Tarjetas (A pagar)", f"${total_tc:,.2f}", delta_color="inverse")
            c3.metric("Saldo Final Proyectado", f"${saldo_final_proyectado:,.2f}")
            c4.metric("Impacto en Ingresos", f"{impacto_tc:.1f}%")

            st.divider()
            
            col_izq, col_der = st.columns(2)
            with col_izq:
                # Gráfico de barras comparativo
                resumen_visual = pd.DataFrame({
                    'Estado': ['Disponible', 'Comprometido (TC)'],
                    'Monto': [saldo_final_proyectado if saldo_final_proyectado > 0 else 0, total_tc]
                })
                fig_impacto = px.pie(resumen_visual, values='Monto', names='Estado', 
                                    title="Disponibilidad Real vs Compromisos",
                                    color_discrete_sequence=['#2ecc71', '#e74c3c'])
                st.plotly_chart(fig_impacto, use_container_width=True)
            
            with col_der:
                fig_evol = px.line(df_gastos, x='Fecha', y='Monto', title="Flujo de Gastos en el Tiempo")
                st.plotly_chart(fig_evol, use_container_width=True)

        with tab_tarjetas:
            st.subheader("💳 Distribución de Deuda por Banco/Tarjeta")
            
            if not df_tc.empty:
                # Agrupación por banco
                df_bancos = df_tc.groupby(col_banco)['Monto'].sum().reset_index()
                
                col_t1, col_t2 = st.columns([1, 2])
                with col_t1:
                    st.write("### Deuda por Plástico")
                    st.dataframe(df_bancos.sort_values(by='Monto', ascending=False), hide_index=True)
                
                with col_t2:
                    fig_bancos = px.bar(df_bancos, x=col_banco, y='Monto', color=col_banco,
                                       text_auto='.2s', title="Carga por Entidad Bancaria")
                    st.plotly_chart(fig_bancos, use_container_width=True)
                
                st.divider()
                st.write("### 🔍 Detalle de consumos a liquidar")
                st.dataframe(df_tc[['Fecha', col_banco, 'Categoría', 'Concepto', 'Monto']].sort_values(by='Fecha', ascending=False), use_container_width=True)
            else:
                st.info("No hay deudas de tarjeta detectadas.")

except Exception as e:
    st.error(f"Error de sincronización: {e}")

with tab_carga:
    st.link_button("📝 REGISTRAR MOVIMIENTO", FORM_LINK, use_container_width=True)
FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSd5nLZX5Uihw--o_JuKYqxMwnsc4M-g6HupBCuO2xBqTvgC0w/viewform"

st.title("💰 Inteligencia Financiera Bocha")

tab_resumen, tab_tarjetas, tab_carga = st.tabs(["📊 Balance y Proyección", "💳 Análisis de Tarjetas", "📝 Cargar Datos"])

try:
    df = pd.read_csv(EXCEL_CSV)
    if not df.empty:
        # Estandarizamos columnas (Marca, Fecha, Tipo, Categoría, Monto, Método, Concepto, [Banco/Tarjeta])
        # Asumimos que la columna 8 (índice 7) es donde guardas el nombre de la tarjeta/banco
        cols_base = ['Timestamp', 'Fecha', 'Tipo', 'Categoría', 'Monto', 'Método', 'Concepto']
        nombres_finales = cols_base + list(df.columns[len(cols_base):])
        df.columns = nombres_finales
        
        # Limpieza de montos y fechas
        df['Monto'] = pd.to_numeric(df['Monto'], errors='coerce').fillna(0)
        col_banco = df.columns[7] if len(df.columns) > 7 else 'Método'

        # Separación de datos
        df_gastos = df[df['Tipo'].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)].copy()
        df_ingresos = df[df['Tipo'].astype(str).str.contains('INGRESO', case=False, na=False)].copy()
        
        # Identificación de Tarjetas de Crédito
        df_tc = df_gastos[df_gastos['Método'].astype(str).str.contains('CRED', case=False, na=False)].copy()
        df_contado = df_gastos[~df_gastos['Método'].astype(str).str.contains('CRED', case=False, na=False)].copy()

        with tab_resumen:
            # --- CÁLCULOS DE PROYECCIÓN ---
            total_ing = df_ingresos["Monto"].sum()
            total_contado = df_contado["Monto"].sum()
            total_tc = df_tc["Monto"].sum()
            
            saldo_caja = total_ing - total_contado
            saldo_final_proyectado = saldo_caja - total_tc
            impacto_tc = (total_tc / total_ing * 100) if total_ing > 0 else 0

            # --- MÉTRICAS ESTRATÉGICAS ---
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Efectivo/Débito (Caja)", f"${saldo_caja:,.2f}")
            c2.metric("Deuda Tarjetas (A pagar)", f"${total_tc:,.2f}", delta_color="inverse")
            c3.metric("Saldo Final Proyectado", f"${saldo_final_proyectado:,.2f}")
            c4.metric("Impacto en Ingresos", f"{impacto_tc:.1f}%")

            st.divider()
            
            col_izq, col_der = st.columns(2)
            with col_izq:
                # Gráfico de barras comparativo
                resumen_visual = pd.DataFrame({
                    'Estado': ['Disponible', 'Comprometido (TC)'],
                    'Monto': [saldo_final_proyectado if saldo_final_proyectado > 0 else 0, total_tc]
                })
                fig_impacto = px.pie(resumen_visual, values='Monto', names='Estado', 
                                    title="Disponibilidad Real vs Compromisos",
                                    color_discrete_sequence=['#2ecc71', '#e74c3c'])
                st.plotly_chart(fig_impacto, use_container_width=True)
            
            with col_der:
                fig_evol = px.line(df_gastos, x='Fecha', y='Monto', title="Flujo de Gastos en el Tiempo")
                st.plotly_chart(fig_evol, use_container_width=True)

        with tab_tarjetas:
            st.subheader("💳 Distribución de Deuda por Banco/Tarjeta")
            
            if not df_tc.empty:
                # Agrupación por banco
                df_bancos = df_tc.groupby(col_banco)['Monto'].sum().reset_index()
                
                col_t1, col_t2 = st.columns([1, 2])
                with col_t1:
                    st.write("### Deuda por Plástico")
                    st.dataframe(df_bancos.sort_values(by='Monto', ascending=False), hide_index=True)
                
                with col_t2:
                    fig_bancos = px.bar(df_bancos, x=col_banco, y='Monto', color=col_banco,
                                       text_auto='.2s', title="Carga por Entidad Bancaria")
                    st.plotly_chart(fig_bancos, use_container_width=True)
                
                st.divider()
                st.write("### 🔍 Detalle de consumos a liquidar")
                st.dataframe(df_tc[['Fecha', col_banco, 'Categoría', 'Concepto', 'Monto']].sort_values(by='Fecha', ascending=False), use_container_width=True)
            else:
                st.info("No hay deudas de tarjeta detectadas.")

except Exception as e:
    st.error(f"Error de sincronización: {e}")

with tab_carga:
    st.link_button("📝 REGISTRAR MOVIMIENTO", FORM_LINK, use_container_width=True)
