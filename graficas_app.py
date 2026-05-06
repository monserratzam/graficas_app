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
        t1, t2, t3, t4, t5, t6, t7, t8 = st.tabs([
            "👥 Rendimiento Técnico", 
            "📊 Consolidado Calidad",
            "📍 Dispersión (Linealidad)",
            "⚙️ Análisis de Equipos",
            "🍰 Distribución OT",
            "📈 Histogramas",
            "🎯 Paretos (Calidad)",
            "📋 Datos Crudos"
        ])

        # --- TAB 1: RENDIMIENTO TÉCNICO (Originales) ---
        with t1:
            st.subheader("Productividad por Técnico")
            # Cantidad OT
            res_ot = df_f.groupby(COL_TECNICO)[COL_OT].count().reset_index().sort_values(COL_OT, ascending=False)
            st.plotly_chart(px.bar(res_ot.head(15), x=COL_TECNICO, y=COL_OT, title="Total de OT por Técnico", text_auto=True), use_container_width=True)
            
            # Suma HH
            res_hh_sum = df_f.groupby(COL_TECNICO)[COL_HH].sum().reset_index().sort_values(COL_HH, ascending=False)
            st.plotly_chart(px.bar(res_hh_sum.head(15), x=COL_TECNICO, y=COL_HH, title="Suma Total de HH por Técnico", text_auto='.2f', color_discrete_sequence=['#2ca02c']), use_container_width=True)
            
            # Promedio HH
            res_hh_avg = df_f.groupby(COL_TECNICO)[COL_HH].mean().reset_index().sort_values(COL_HH, ascending=False)
            st.plotly_chart(px.bar(res_hh_avg.head(15), x=COL_TECNICO, y=COL_HH, title="Promedio de HH por Tarea", text_auto='.2f', color_discrete_sequence=['#9467bd']), use_container_width=True)

        # --- TAB 2: CONSOLIDADO DE CALIDAD (Tabla solicitada) ---
        with t2:
            st.subheader("Consolidado: Tiempo Promedio por Orden de Trabajo")
            consolidado = df_f.groupby(COL_TECNICO).agg({COL_OT: 'count', COL_TIEMPO: 'sum'}).reset_index()
            consolidado['Promedio Tiempo por OT'] = consolidado[COL_TIEMPO] / consolidado[COL_OT]
            consolidado.columns = ["Nombre del Técnico", "Suma de OT", "Suma Tiempo de Mantenimiento", "Promedio de Tiempo Mto por OT"]
            st.dataframe(consolidado.sort_values("Promedio de Tiempo Mto por OT", ascending=False).style.format({
                "Suma Tiempo de Mantenimiento": "{:.2f}",
                "Promedio de Tiempo Mto por OT": "{:.2f}"
            }), use_container_width=True, hide_index=True)

        # --- TAB 3: ANÁLISIS DE DISPERSIÓN (OT vs Suma HH) ---
        with t3:
            st.subheader("Análisis de Linealidad: Cantidad de OT vs Esfuerzo Total (HH)")
            dispersion_data = df_f.groupby(COL_TECNICO).agg({COL_OT: 'count', COL_HH: 'sum'}).reset_index()
            dispersion_data.columns = ["Técnico", "Cantidad de OT", "Total HH"]

            fig_disp = px.scatter(
                dispersion_data, x="Cantidad de OT", y="Total HH", text="Técnico",
                title="Relación entre Carga de Trabajo y Horas Hombre Invertidas",
                labels={"Cantidad de OT": "Número de OT", "Total HH": "Suma de Horas Hombre"},
                size="Total HH", color="Total HH", color_continuous_scale='Reds'
            )
            fig_disp.update_traces(textposition='top center')
            st.plotly_chart(fig_disp, use_container_width=True)
            st.write("**Hoja de Verificación: Datos de Dispersión**")
            st.dataframe(dispersion_data, use_container_width=True, hide_index=True)

        # --- TAB 4: EQUIPOS ---
        with t4:
            st.subheader("Carga de Trabajo por Equipo")
            res_eq = df_f.groupby(COL_EQUIPO)[COL_OT].count().reset_index().sort_values(COL_OT, ascending=False)
            st.plotly_chart(px.bar(res_eq.head(20), x=COL_EQUIPO, y=COL_OT, title="Top 20 Equipos según Cantidad de OT", text_auto=True), use_container_width=True)
            st.write("**Hoja de Verificación: Equipos**")
            st.dataframe(res_eq, use_container_width=True, hide_index=True)

        # --- TAB 5: GRÁFICO DE TORTA ---
        with t5:
            st.subheader(f"Distribución de OT por {COL_MANTO}")
            res_pie = df_f.groupby(COL_MANTO)[COL_OT].count().reset_index()
            res_pie['Porcentaje'] = (res_pie[COL_OT] / res_pie[COL_OT].sum() * 100).map("{:.1f}%".format)
            fig_p = px.pie(res_pie, values=COL_OT, names=COL_MANTO, hole=0.4)
            fig_p.update_traces(textinfo='value')
            st.plotly_chart(fig_p, use_container_width=True)
            st.write("**Hoja de Verificación**")
            st.dataframe(res_pie, hide_index=True, use_container_width=True)

        # --- TAB 6: HISTOGRAMA ---
        with t6:
            st.subheader("Distribución de Frecuencia de Tiempos")
            fig_h = px.histogram(df_f, x=COL_TIEMPO, nbins=20, text_auto=True, color_discrete_sequence=['#00CC96'])
            fig_h.update_layout(bargap=0.1, xaxis_title="Rango de Tiempo", yaxis_title="Cantidad de OTs")
            fig_h.update_xaxes(nticks=20)
            st.plotly_chart(fig_h, use_container_width=True)

        # --- TAB 7: PARETOS (HH y TIEMPO PROMEDIO) ---
        with t7:
            # Pareto 1: HH
            st.subheader("Pareto: Tipo Mantención vs Horas Hombre")
            p_hh = df_f.groupby(COL_MANTO)[COL_HH].sum().sort_values(ascending=False).reset_index()
            p_hh['% Acumulado'] = (100 * p_hh[COL_HH].cumsum() / p_hh[COL_HH].sum())
            fig_p1 = go.Figure()
            fig_p1.add_trace(go.Bar(x=p_hh[COL_MANTO], y=p_hh[COL_HH], name="Suma HH"))
            fig_p1.add_trace(go.Scatter(x=p_hh[COL_MANTO], y=p_hh['% Acumulado'], name="%", yaxis="y2", line=dict(color="red", width=3)))
            fig_p1.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0, 105]))
            st.plotly_chart(fig_p1, use_container_width=True)
            
            st.divider()

            # Pareto 2: Tiempo Promedio
            st.subheader("Pareto: Tipo Mantención vs Tiempo Promedio")
            p_tp = df_f.groupby(COL_MANTO)[COL_TIEMPO].mean().sort_values(ascending=False).reset_index()
            p_tp['% Acumulado'] = (100 * p_tp[COL_TIEMPO].cumsum() / p_tp[COL_TIEMPO].sum())
            fig_p2 = go.Figure()
            fig_p2.add_trace(go.Bar(x=p_tp[COL_MANTO], y=p_tp[COL_TIEMPO], name="Tiempo Promedio", marker_color="orange"))
            fig_p2.add_trace(go.Scatter(x=p_tp[COL_MANTO], y=p_tp['% Acumulado'], name="%", yaxis="y2", line=dict(color="red", width=3)))
            fig_p2.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0, 105]))
            st.plotly_chart(fig_p2, use_container_width=True)

        with t8:
            st.dataframe(df_f, use_container_width=True)
    else:
        st.error(f"Faltan columnas. Requeridas: {requeridos}")
else:
    st.info("Sube tu archivo Excel para iniciar el Dashboard Integral.")
