import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard Mantenimiento Pro", layout="wide")

st.title("📊 Dashboard de Gestión y Calidad de Mantenimiento")
st.markdown("---")

archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo:
    xls = pd.ExcelFile(archivo)
    hoja_seleccionada = st.selectbox("1. Selecciona la hoja de datos", xls.sheet_names)
    df = pd.read_excel(archivo, sheet_name=hoja_seleccionada)

    # --- NOMBRES ESPECÍFICOS ---
    COL_MANTO = "Tipo de mantención"
    COL_TECNICO = "Nombre Técnico"
    COL_OT = "N°OT"
    COL_HH = "Horas Hombres"
    COL_TIEMPO = "Tiempo mantención"
    COL_EQUIPO = "Equipo"

    # Verificación rápida
    requeridos = [COL_MANTO, COL_TECNICO, COL_OT, COL_TIEMPO]
    if all(col in df.columns for col in requeridos):
        
        # --- FILTROS ---
        st.sidebar.header("⚙️ Filtros")
        manto_sel = st.sidebar.multiselect("Tipo de Mantención", sorted(df[COL_MANTO].unique()), default=df[COL_MANTO].unique())
        tecnico_sel = st.sidebar.multiselect("Técnicos", sorted(df[COL_TECNICO].unique()), default=df[COL_TECNICO].unique())

        df_filtrado = df[(df[COL_MANTO].isin(manto_sel)) & (df[COL_TECNICO].isin(tecnico_sel))].copy()
        df_filtrado[COL_TIEMPO] = pd.to_numeric(df_filtrado[COL_TIEMPO], errors='coerce').fillna(0)
        df_filtrado[COL_HH] = pd.to_numeric(df_filtrado[COL_HH], errors='coerce').fillna(0)

        # --- 1. GRÁFICO DE TORTA (Distribución de OT) ---
        st.subheader(f"Distribución de OT por {COL_MANTO}")
        resumen_torta = df_filtrado.groupby(COL_MANTO)[COL_OT].count().reset_index()
        resumen_torta.columns = [COL_MANTO, 'Cantidad']
        resumen_torta['Porcentaje'] = (resumen_torta['Cantidad'] / resumen_torta['Cantidad'].sum() * 100).map("{:.1f}%".format)

        col1, col2 = st.columns([2, 1])
        with col1:
            fig_pie = px.pie(resumen_torta, values='Cantidad', names=COL_MANTO, hole=0.4)
            fig_pie.update_traces(textinfo='value') # Solo valores en el gráfico
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            st.write("**Hoja de Verificación**")
            st.dataframe(resumen_torta, hide_index=True, use_container_width=True)
        st.divider()

        # --- 2. HISTOGRAMA (Distribución de Tiempos) ---
        st.subheader("Análisis de Tiempos: Histograma de Frecuencias")
        fig_hist = px.histogram(df_filtrado, x=COL_TIEMPO, nbins=20, 
                               title="Frecuencia de Duración de Mantenimientos",
                               color_discrete_sequence=['#636EFA'], marginal="box")
        fig_hist.update_layout(xaxis_title="Tiempo de Mantención", yaxis_title="Frecuencia (Cantidad de OTs)")
        st.plotly_chart(fig_hist, use_container_width=True)
        st.info("💡 Este gráfico ayuda a identificar si existen 'outliers' o trabajos que toman mucho más tiempo del promedio.")
        st.divider()

        # --- 3. DIAGRAMA DE PARETO (Herramienta de Calidad sugerida) ---
        st.subheader("Herramienta de Calidad: Diagrama de Pareto (Técnicos vs HH)")
        pareto_data = df_filtrado.groupby(COL_TECNICO)[COL_HH].sum().sort_values(ascending=False).reset_index()
        pareto_data['CumSum'] = pareto_data[COL_HH].cumsum()
        pareto_data['CumPerc'] = 100 * pareto_data['CumSum'] / pareto_data[COL_HH].sum()

        fig_pareto = go.Figure()
        fig_pareto.add_trace(go.Bar(x=pareto_data[COL_TECNICO], y=pareto_data[COL_HH], name="HH Acumuladas"))
        fig_pareto.add_trace(go.Scatter(x=pareto_data[COL_TECNICO], y=pareto_data['CumPerc'], name="% Acumulado", yaxis="y2", line=dict(color="red", width=3)))
        
        fig_pareto.update_layout(
            yaxis=dict(title="Horas Hombres"),
            yaxis2=dict(title="Porcentaje Acumulado (%)", overlaying="y", side="right", range=[0, 105]),
            legend=dict(x=0.8, y=1.1)
        )
        st.plotly_chart(fig_pareto, use_container_width=True)

        # --- OTROS REPORTES ---
        def generar_seccion(titulo, g_col, a_col, func):
            st.subheader(titulo)
            resumen = df_filtrado.groupby(g_col)[a_col].agg(func).reset_index().sort_values(by=a_col, ascending=False)
            st.plotly_chart(px.bar(resumen.head(10), x=g_col, y=a_col, text_auto='.2f'), use_container_width=True)

        generar_seccion("Top 10: Promedio Tiempo Mantención por Técnico", COL_TECNICO, COL_TIEMPO, "mean")

    else:
        st.error("No se encontraron todas las columnas necesarias.")
else:
    st.info("Sube tu archivo Excel para comenzar el análisis de calidad.")
