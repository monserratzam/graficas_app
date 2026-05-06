import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard Mantenimiento Integral", layout="wide")

st.title("📊 Dashboard de Gestión, Calidad y Rendimiento de Mantenimiento")
st.markdown("---")

archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo:
    xls = pd.ExcelFile(archivo)
    hoja_seleccionada = st.selectbox("1. Selecciona la hoja de datos", xls.sheet_names)
    df = pd.read_excel(archivo, sheet_name=hoja_seleccionada)

    # --- CONFIGURACIÓN DE NOMBRES EXACTOS ---
    COL_MANTO = "Tipo de mantención"
    COL_TECNICO = "Nombre Técnico"
    COL_OT = "N°OT"
    COL_HH = "Horas Hombres"
    COL_TIEMPO = "Tiempo mantención"
    COL_EQUIPO = "Equipo"

    requeridos = [COL_MANTO, COL_TECNICO, COL_OT, COL_TIEMPO, COL_HH, COL_EQUIPO]
    
    if all(col in df.columns for col in requeridos):
        
        # --- FILTROS GLOBALES ---
        st.sidebar.header("⚙️ Filtros Globales")
        manto_sel = st.sidebar.multiselect("Tipo de Mantención", sorted(df[COL_MANTO].unique()), default=df[COL_MANTO].unique())
        tecnico_sel = st.sidebar.multiselect("Técnicos", sorted(df[COL_TECNICO].unique()), default=df[COL_TECNICO].unique())

        # Limpieza y filtrado
        df_f = df[(df[COL_MANTO].isin(manto_sel)) & (df[COL_TECNICO].isin(tecnico_sel))].copy()
        for c in [COL_HH, COL_TIEMPO]:
            df_f[c] = pd.to_numeric(df_f[c], errors='coerce').fillna(0)

        # --- CREACIÓN DE PESTAÑAS ---
        t1, t2, t3, t4, t5, t6, t7, t8, t9 = st.tabs([
            "👥 Rendimiento Técnico", 
            "📊 Consolidado Calidad",
            "📍 Análisis de Dispersión",
            "⚙️ Análisis de Equipos",
            "⏱️ Análisis de Tiempos",
            "🍰 Distribución OT",
            "📉 Histogramas",
            "🎯 Paretos (Calidad)",
            "📋 Datos Crudos"
        ])

        # --- TAB 1: RENDIMIENTO TÉCNICO ---
        with t1:
            st.subheader("Productividad y Carga de Trabajo por Técnico")
            res_ot = df_f.groupby(COL_TECNICO)[COL_OT].count().reset_index().sort_values(COL_OT, ascending=False)
            st.plotly_chart(px.bar(res_ot.head(15), x=COL_TECNICO, y=COL_OT, title="Total de OT por Técnico", text_auto=True), use_container_width=True)
            st.write("**Hoja de Verificación: Cantidad OT**")
            st.dataframe(res_ot, hide_index=True, use_container_width=True)
            st.divider()
            
            res_hh_sum = df_f.groupby(COL_TECNICO)[COL_HH].sum().reset_index().sort_values(COL_HH, ascending=False)
            st.plotly_chart(px.bar(res_hh_sum.head(15), x=COL_TECNICO, y=COL_HH, title="Suma Total de Horas Hombre (HH)", text_auto='.2f', color_discrete_sequence=['#2ca02c']), use_container_width=True)
            st.divider()

            res_hh_avg = df_f.groupby(COL_TECNICO)[COL_HH].mean().reset_index().sort_values(COL_HH, ascending=False)
            st.plotly_chart(px.bar(res_hh_avg.head(15), x=COL_TECNICO, y=COL_HH, title="Promedio de HH por OT", text_auto='.2f', color_discrete_sequence=['#9467bd']), use_container_width=True)

        # --- TAB 2: CONSOLIDADO DE CALIDAD ---
        with t2:
            st.subheader("Consolidado: Tiempo Promedio por Orden de Trabajo")
            consolidado = df_f.groupby(COL_TECNICO).agg({COL_OT: 'count', COL_TIEMPO: 'sum'}).reset_index()
            consolidado['Promedio Tiempo por OT'] = consolidado[COL_TIEMPO] / consolidado[COL_OT]
            consolidado.columns = ["Nombre del Técnico", "Suma de OT", "Suma Tiempo de Mantenimiento", "Promedio de Tiempo Mto por OT"]
            st.dataframe(consolidado.sort_values("Promedio de Tiempo Mto por OT", ascending=False).style.format({
                "Suma Tiempo de Mantenimiento": "{:.2f}",
                "Promedio de Tiempo Mto por OT": "{:.2f}"
            }), use_container_width=True, hide_index=True)

        # --- TAB 3: ANÁLISIS DE DISPERSIÓN (NUEVO) ---
        with t3:
            st.subheader("Análisis de Linealidad: Cantidad de OT vs Tiempo Total")
            st.info("💡 Este gráfico ayuda a comparar si el aumento de órdenes de trabajo se traduce proporcionalmente en el tiempo empleado.")
            
            # Preparar datos para la dispersión
            dispersion_data = df_f.groupby(COL_TECNICO).agg({
                COL_OT: 'count',
                COL_TIEMPO: 'sum'
            }).reset_index()
            dispersion_data.columns = ["Técnico", "Cantidad de OT", "Tiempo Total Mantenimiento"]

            fig_disp = px.scatter(
                dispersion_data, 
                x="Cantidad de OT", 
                y="Tiempo Total Mantenimiento", 
                text="Técnico",
                trendline="ols", # Línea de tendencia lineal
                title="Relación entre Carga de Trabajo y Tiempo Invertido",
                labels={"Cantidad de OT": "Número de Órdenes de Trabajo", "Tiempo Total Mantenimiento": "Tiempo Total de Mantención"}
            )
            fig_disp.update_traces(textposition='top center', marker=dict(size=12, color='red', line=dict(width=2, color='DarkSlateGrey')))
            st.plotly_chart(fig_disp, use_container_width=True)
            
            st.write("**Hoja de Verificación: Datos de Dispersión**")
            st.dataframe(dispersion_data.sort_values("Cantidad de OT", ascending=False), use_container_width=True, hide_index=True)

        # --- TAB 4: ANÁLISIS DE EQUIPOS ---
        with t4:
            st.subheader("Frecuencia de Mantenimiento por Equipo")
            res_eq = df_f.groupby(COL_EQUIPO)[COL_OT].count().reset_index().sort_values(COL_OT, ascending=False)
            st.plotly_chart(px.bar(res_eq.head(20), x=COL_EQUIPO, y=COL_OT, title="Top 20 Equipos con más OT", text_auto=True), use_container_width=True)
            st.write("**Hoja de Verificación: Carga por Equipo**")
            st.dataframe(res_eq, use_container_width=True, hide_index=True)

        # --- TAB 5: ANÁLISIS DE TIEMPOS ---
        with t5:
            st.subheader("Tiempos Totales y Promedios")
            res_t_sum = df_f.groupby(COL_TECNICO)[COL_TIEMPO].sum().reset_index().sort_values(COL_TIEMPO, ascending=False)
            st.plotly_chart(px.bar(res_t_sum.head(15), x=COL_TECNICO, y=COL_TIEMPO, title="Suma Total Tiempo Mantenimiento", text_auto='.2f', color_discrete_sequence=['#ff7f0e']), use_container_width=True)
            
            res_t_avg = df_f.groupby(COL_TECNICO)[COL_TIEMPO].mean().reset_index().sort_values(COL_TIEMPO, ascending=False)
            st.plotly_chart(px.bar(res_t_avg.head(15), x=COL_TECNICO, y=COL_TIEMPO, title="Promedio Tiempo Mantenimiento por OT", text_auto='.2f', color_discrete_sequence=['#d62728']), use_container_width=True)

        # --- TAB 6: DISTRIBUCIÓN OT (TORTA) ---
        with t6:
            st.subheader(f"Distribución de OT por {COL_MANTO}")
            res_pie = df_f.groupby(COL_MANTO)[COL_OT].count().reset_index()
            res_pie['Porcentaje'] = (res_pie[COL_OT] / res_pie[COL_OT].sum() * 100).map("{:.1f}%".format)
            fig_p = px.pie(res_pie, values=COL_OT, names=COL_MANTO, hole=0.4)
            fig_p.update_traces(textinfo='value')
            st.plotly_chart(fig_p, use_container_width=True)
            st.write("**Hoja de Verificación (Con Porcentajes)**")
            st.dataframe(res_pie, hide_index=True, use_container_width=True)

        # --- TAB 7: HISTOGRAMAS ---
        with t7:
            st.subheader("Histograma: Distribución de los Tiempos de Mantenimiento")
            fig_h = px.histogram(df_f, x=COL_TIEMPO, nbins=20, text_auto=True, color_discrete_sequence=['#00CC96'])
            fig_h.update_layout(bargap=0.1, xaxis_title="Rango de Tiempo", yaxis_title="Cantidad de OTs")
            fig_h.update_xaxes(nticks=20)
            st.plotly_chart(fig_h, use_container_width=True)

        # --- TAB 8: PARETOS ---
        with t8:
            st.subheader("Pareto: Tipo Mantención vs Horas Hombre")
            p_manto = df_f.groupby(COL_MANTO)[COL_HH].sum().sort_values(ascending=False).reset_index()
            p_manto['% Acumulado'] = (100 * p_manto[COL_HH].cumsum() / p_manto[COL_HH].sum())
            fig_pm = go.Figure()
            fig_pm.add_trace(go.Bar(x=p_manto[COL_MANTO], y=p_manto[COL_HH], name="Suma HH"))
            fig_pm.add_trace(go.Scatter(x=p_manto[COL_MANTO], y=p_manto['% Acumulado'], name="%", yaxis="y2", line=dict(color="red", width=3)))
            fig_pm.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0, 105]))
            st.plotly_chart(fig_pm, use_container_width=True)

        with t9:
            st.dataframe(df_f, use_container_width=True)
    else:
        st.error(f"Faltan columnas. Requeridas: {requeridos}")
else:
    st.info("Sube tu archivo Excel para iniciar el análisis.")
