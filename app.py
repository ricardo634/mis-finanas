import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Finanzas Bocha PRO", layout="wide", page_icon="💳")

# --- ENLACES ---
EXCEL_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRNOMeVh6rLo1CKWzxYMAaBhByk4F5HuVwfCDUAQVUnABG4m3OTw2p8sr8LRs_ZuEplskZqZsdrOy7-/pub?output=csv"
FORM_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSd5nLZX5Uihw--o_JuKYqxMwnsc4M-g6HupBCuO2xBqTvgC0w/viewform"

st.title("💰 Mi Control Financiero")

tab_resumen, tab_tarjeta, tab_carga = st.tabs(["📊 Resumen y Comparativa", "💳 Solo Tarjetas", "📝 Cargar Datos"])

with tab_resumen:
    try:
        df = pd.read_csv(EXCEL_CSV)
        if not df.empty:
            df.columns = [c.strip() for c in df.columns]
            
            # --- BUSCADOR ULTRA AGRESIVO ---
            def encontrar_columna(lista_palabras):
                for palabra in lista_palabras:
                    for col in df.columns:
                        if palabra.upper() in col.upper():
                            return col
                return None

            col_tipo = encontrar_columna(['TIPO', 'CARGAR', 'MOVIMIENTO'])
            cols_montos = [c for c in df.columns if 'MONTO' in c.upper() or '$' in c]
            col_medio = encontrar_columna(['MÉTODO', 'MEDIO', 'PAGO'])
            col_estado = encontrar_columna(['ESTADO'])
            col_cat_gasto = encontrar_columna(['CATEGORÍA DE GASTO', 'GASTO'])
            col_cat_ingreso = encontrar_columna(['CATEGORÍA DE INGRESO', 'INGRESO'])

            # Si falta algo crítico, avisamos qué nombres vemos
            if not col_tipo or not cols_montos:
                st.warning("No encuentro las columnas principales. Nombres detectados:")
                st.write(list(df.columns))
            else:
                # Limpiar montos
                for col in cols_montos:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
                df['Suma_Final'] = df[cols_montos].sum(axis=1)
                # Unificar categorías
                df['Cat_Grafico'] = df[col_cat_gasto].fillna(df[col_cat_ingreso]).fillna("Otros")

                # --- CÁLCULOS ---
                df_ing = df[df[col_tipo].astype(str).str.contains('INGRESO', case=False, na=False)]
                total_ing = df_ing['Suma_Final'].sum()
                
                df_egr = df[df[col_tipo].astype(str).str.contains('EGRESO|GASTO', case=False, na=False)]
                total_egr = df_egr['Suma_Final'].sum()
                
                # Deuda
                monto_deuda = 0
                df_deuda = pd.DataFrame()
                if col_estado and col_medio:
                    es_pend = df_egr[col_estado].astype(str).str.contains('PENDIENTE', case=False, na=False)
                    es_tarj = df_egr[col_medio].astype(str).str.contains('CREDITO', case=False, na=False)
                    no_pago = ~df_egr[col_estado].astype(str).str.contains('REALIZADO|PAGADO', case=False, na=False)
                    df_deuda = df_egr[es_pend | (es_tarj & no_pago)]
                    monto_deuda = df_deuda['Suma_Final'].sum()

                disponible = total_ing - (total_egr - monto_deuda)
                
                # --- MÉTRICAS ---
                c1, c2, c3 = st.columns(3)
                c1.metric("Disponible (Caja)", f"${disponible:,.2f}")
                c2.metric("Deuda Pendiente", f"${monto_deuda:,.2f}", delta_color="inverse")
                c3.metric("Saldo Neto Final", f"${disponible - monto_deuda:,.2f}")
                
                st.divider()

                # --- GRÁFICO COMPARATIVO ---
                st.write("### ⚖️ Comparativa: Ingresos vs Gastos")
                df_graf = df.groupby(['Cat_Grafico', col_tipo])['Suma_Final'].sum().reset_index()
                fig = px.bar(df_graf, x='Cat_Grafico', y='Suma_Final', color=col_tipo, barmode='group',
                             color_discrete_map={'INGRESO': '#2ecc71', 'EGRESO': '#e74c3c', 'GASTO': '#e74c3c'})
                st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error detallado: {e}")

with tab_tarjeta:
    st.subheader("🔎 Detalle de Tarjeta de Crédito")
    try:
        col_m = encontrar_columna(['MÉTODO', 'MEDIO', 'PAGO'])
        df_t = df[df[col_m].astype(str).str.contains('CREDITO', case=False, na=False)]
        st.dataframe(df_t, use_container_width=True)
    except:
        st.write("Sin datos de tarjeta.")

with tab_carga:
    st.subheader("Registrar Movimiento")
    st.link_button("📝 IR AL FORMULARIO", FORM_LINK, use_container_width=True)
