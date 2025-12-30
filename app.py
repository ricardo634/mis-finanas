import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha PRO", layout="wide", page_icon="💳")

# --- ENLACES ---
EXCEL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTQGHyOERYRdBB_KqWJjBvBG43Ujuf9y8xYFseHbX_ElKNLOAT_sStrolGifSVOGSsWJpanYtCq9fJz/pub?output=csv"
FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSd5nLZX5Uihw--o_JuKYqxMwnsc4M-g6HupBCuO2xBqTvgC0w/viewform"

st.title("💰 Mi Control Financiero")

tab_resumen, tab_historial, tab_carga = st.tabs(["📊 Resumen y Gráficos", "💳 Detalle por Tarjeta", "📝 Cargar Datos"])

try:
    df = pd.read_csv(EXCEL_CSV)
    if not df.empty:
        df.columns = [str(c).strip() for c in df.columns]
        
        # --- BUSCADOR DE COLUMNAS ---
        def encontrar_col(palabras):
            for p in palabras:
                for c in df.columns:
                    if p.upper() in c.upper(): return c
            return None

        col_tipo = encontrar_col(['TIPO', 'CARGAR', 'MOVIMIENTO'])
        cols_montos = [c for c in df.columns if 'MONTO' in c.upper() or '$' in c]
        col_medio = encontrar_col(['MÉTODO', 'MEDIO', 'PAGO'])
        col_nombre_tarjeta = encontrar_col(['CUAL TARJETA', 'NOMBRE TARJETA', 'TARJETA']) # Buscamos la columna de la tarjeta específica
        col_estado = encontrar_col(['ESTADO'])
        col_cat_gasto = encontrar_col(['CATEGORÍA DE GASTO', 'GASTO', 'CATEGORIA'])
        col_cat_ingreso = encontrar_col(['CATEGORÍA DE INGRESO', 'INGRESO'])
        col_fecha = encontrar_col(['FECHA']) or df.columns[1]
        col_concepto = encontrar_col(['CONCEPTO', 'DETALLE', 'DESCRIPCION']) or df.columns[4]

        # Limpiar montos
        for col in cols_montos:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df['Monto_Total'] = df[cols_montos].sum(axis=1)
        df['Cat_Final'] = df[col_cat_gasto].fillna(df[col_cat_ingreso]).fillna("Otros")

        # Separar Egresos
        df_egr = df[df[col_tipo].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)].copy()

        with tab_resumen:
            # (Aquí mantenemos tus 3 métricas y gráficos de barras/pastel que ya funcionan)
            df_ing = df[df[col_tipo].astype(str).str.contains('INGRESO', case=False, na=False)]
            monto_deuda = 0
            if col_estado and col_medio:
                es_pend = df_egr[col_estado].astype(str).str.contains('PENDIENTE', case=False, na=False)
                es_tarj = df_egr[col_medio].astype(str).str.contains('CRED', case=False, na=False)
                no_pago = ~df_egr[col_estado].astype(str).str.contains('REALIZADO|PAGADO', case=False, na=False)
                monto_deuda = df_egr[es_pend | (es_tarj & no_pago)]['Monto_Total'].sum()

            disponible = df_ing['Monto_Total'].sum() - (df_egr['Monto_Total'].sum() - monto_deuda)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Caja (Disponible)", f"${disponible:,.2f}")
            c2.metric("Deuda Pendiente", f"${monto_deuda:,.2f}", delta_color="inverse")
            c3.metric("Saldo Neto", f"${disponible - monto_deuda:,.2f}")
            
            st.divider()
            g1, g2 = st.columns(2)
            with g1:
                df_bar = df.groupby(['Cat_Final', col_tipo])['Monto_Total'].sum().reset_index()
                st.plotly_chart(px.bar(df_bar, x='Cat_Final', y='Monto_Total', color=col_tipo, barmode='group',
                                       color_discrete_map={'INGRESO': '#2ecc71', 'EGRESO': '#e74c3c'}), use_container_width=True)
            with g2:
                st.plotly_chart(px.pie(df_egr, values='Monto_Total', names='Cat_Final', hole=0.4), use_container_width=True)

        with tab_historial:
            st.subheader("💳 Control de Tarjetas Bancarias")
            
            # Filtramos solo los gastos que fueron con tarjeta
            df_solo_tarjeta = df_egr[df_egr[col_medio].astype(str).str.contains('CRED', case=False, na=False)].copy()

            if not df_solo_tarjeta.empty:
                # Si existe la columna de "Qué tarjeta es", permitimos filtrar
                nombres_tarjetas = df_solo_tarjeta[col_nombre_tarjeta].unique().tolist()
                seleccion = st.multiselect("Filtrar por Banco/Tarjeta:", nombres_tarjetas, default=nombres_tarjetas)
                
                df_filtrado = df_solo_tarjeta[df_solo_tarjeta[col_nombre_tarjeta].isin(seleccion)]
                
                st.info(f"Consumo Total Seleccionado: ${df_filtrado['Monto_Total'].sum():,.2f}")
                
                # Tabla organizada
                tabla_tarjeta = df_filtrado[[col_fecha, col_nombre_tarjeta, 'Cat_Final', col_concepto, 'Monto_Total']]
                tabla_tarjeta.columns = ['Fecha', 'Tarjeta', 'Categoría', 'Concepto', 'Importe $']
                
                st.dataframe(tabla_tarjeta.sort_values(by='Fecha', ascending=False), use_container_width=True)
                
                # Gráfico extra para ver cuál tarjeta gastó más
                st.write("### 📊 Gastos por Tarjeta")
                fig_tarj = px.bar(df_filtrado.groupby(col_nombre_tarjeta)['Monto_Total'].sum().reset_index(), 
                                  x=col_nombre_tarjeta, y='Monto_Total', color=col_nombre_tarjeta)
                st.plotly_chart(fig_tarj, use_container_width=True)
            else:
                st.info("No hay consumos de tarjeta registrados todavía.")

except Exception as e:
    st.error(f"Error: {e}")

with tab_carga:
    st.link_button("📝 IR AL FORMULARIO", FORM_LINK, use_container_width=True)
