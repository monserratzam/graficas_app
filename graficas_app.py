import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard Mantenimiento Avanzado", layout="wide")

st.title("📊 Control de Calidad y Gestión de Mantenimiento")
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

    requeridos = [COL_MANTO, COL_TECNICO, COL_OT, COL_TIEMPO, COL_HH]
    
    if all(col in df.columns for col in requeridos):
        
        # --- FILTROS GLOBALES ---
        st.sidebar.header("⚙️ Filtros")
        manto_sel = st.sidebar.multiselect("Tipo de Mantención", sorted(df[COL_MANTO].unique()), default=df[COL_MANTO].unique())
        tecnico_sel = st.sidebar.multiselect("Técnicos", sorted(df[COL_TECNICO].unique()), default=df[COL_TECNICO].unique())

        # Limpieza y filtrado
        df_f = df[(df[COL_MANTO].isin(manto_sel)) & (df[COL_TECNICO].isin(tecnico_sel))].copy()
        for c in [COL_HH, COL_TIEMPO]:
            df_f[c] = pd.to_numeric(df_f[c], errors='coerce').fillna(0)

        # --- PESTAÑAS ---
        t1, t2, t3, t4, t5, t6, t7 = st.tabs([
            "👤 Rendimiento Técnico", 
            "📊 Consolidado Técnico",
            "🍰 Distribución OT",
            "📈 Histograma Tiempos",
            "🎯 Pareto Calidad",
            "🕒 Pareto Tiempos",
            "📋 Datos"
        ])

        # --- TAB 1: RENDIMIENTO TÉCNICO ---
        with t1:
            st.subheader("Productividad por Técnico")
            res_ot = df_f.groupby(COL_TECNICO)[COL_OT].count().reset_index().sort_values(COL_OT, ascending=False)
            st.plotly_chart(px.bar(res_ot.head(10), x=COL_TECNICO, y=COL_OT, title="Top 10: Cantidad de OT", text_auto=True), use_container_width=True)
            st.write("**Hoja de Verificación: Cantidad OT**")
            st.dataframe(res_ot, hide_index=True, use_container_width=True)

        # --- TAB 2: CONSOLIDADO TÉCNICO (Lo que pediste específicamente) ---
        with t2:
            st.subheader("Consolidado de Tiempos por Orden de Trabajo")
            # Agregamos los datos según tu requerimiento
            consolidado = df_f.groupby(COL_TECNICO).agg({
                COL_OT: 'count',
                COL_TIEMPO: 'sum'
            }).reset_index()
            
            # Cálculo de la columna 4: Promedio = Suma Tiempo / Suma OT
            consolidado['Promedio Tiempo por OT'] = consolidado[COL_TIEMPO] / consolidado[COL_OT]
            
            # Ordenar por el promedio más alto (cuellos de botella)
            consolidado = consolidado.sort_values('Promedio Tiempo por OT', ascending=False)
            
            # Renombrar para mayor claridad en la hoja de verificación
            consolidado.columns = ["Técnico", "Suma de OT", "Suma Tiempo Mantenimiento", "Promedio Tiempo Mto por OT"]
            
            st.write("Esta tabla muestra el tiempo real invertido por cada orden gestionada:")
            st.dataframe(consolidado.style.format({
                "Suma Tiempo Mantenimiento": "{:.2f}",
                "Promedio Tiempo Mto por OT": "{:.2f}"
            }), use_container_width=True, hide_index=True)
            
            # Gráfico de apoyo para ver quién tiene el promedio más alto
            st.plotly_chart(px.bar(consolidado, x="Técnico", y="Promedio Tiempo Mto por OT", 
                                   title="Comparativa: Promedio de Tiempo por cada OT", color="Promedio Tiempo Mto por OT"), use_container_width=True)

        # --- TAB 3: DISTRIBUCIÓN OT (Torta) ---
        with t3:
            st.subheader("Distribución de Carga por Tipo de Mantención")
            res_pie = df_f.groupby(COL_MANTO)[COL_OT].count().reset_index()
            res_pie.columns = [COL_MANTO, 'Cantidad']
            res_pie['Porcentaje'] = (res_pie['Cantidad'] / res_pie['Cantidad'].sum() * 100).map("{:.1f}%".format)
            fig_p = px.pie(res_pie, values='Cantidad', names=COL_MANTO, hole=0.4)
            fig_p.update_traces(textinfo='value')
            st.plotly_chart(fig_p, use_container_width=True)
            st.write("**Hoja de Verificación**")
            st.dataframe(res_pie, hide_index=True, use_container_width=True)

        # --- TAB 4: HISTOGRAMA ---
        with t4:
            st.subheader("Histograma de Frecuencia de Tiempos")
            fig_h = px.histogram(df_f, x=COL_TIEMPO, nbins=20, text_auto=True, color_discrete_sequence=['#00CC96'])
            fig_h.update_layout(bargap=0.1, xaxis_title="Rango de Tiempo (Horas/Minutos)", yaxis_title="Frecuencia (N° de OTs)")
            fig_h.update_xaxes(nticks=20)
            st.plotly_chart(fig_h, use_container_width=True)

        # --- TAB 5: PARETO POR TIPO MANTENCIÓN ---
        with t5:
            st.subheader("Análisis de Pareto: Tipo de Mantención vs HH")
            p_manto = df_f.groupby(COL_MANTO)[COL_HH].sum().sort_values(ascending=False).reset_index()
            p_manto['CumSum'] = p_manto[COL_HH].cumsum()
            p_manto['% Acumulado'] = (100 * p_manto['CumSum'] / p_manto[COL_HH].sum())
            fig_pm = go.Figure()
            fig_pm.add_trace(go.Bar(x=p_manto[COL_MANTO], y=p_manto[COL_HH], name="Total HH"))
            fig_pm.add_trace(go.Scatter(x=p_manto[COL_MANTO], y=p_manto['% Acumulado'], name="% Acumulado", yaxis="y2", line=dict(color="red", width=3)))
            fig_pm.update_layout(yaxis=dict(title="HH"), yaxis2=dict(title="%", overlaying="y", side="right", range=[0, 105]))
            st.plotly_chart(fig_pm, use_container_width=True)

        # --- TAB 6: PARETO TIEMPOS PROMEDIO ---
        with t6:
            st.subheader("Análisis de Pareto: Tiempos Críticos por Tipo de Manto")
            p_time = df_f.groupby(COL_MANTO)[COL_TIEMPO].mean().sort_values(ascending=False).reset_index()
            p_time['CumSum'] = p_time[COL_TIEMPO].cumsum()
            p_time['% Acumulado'] = (100 * p_time['CumSum'] / p_time[COL_TIEMPO].sum())
            fig_pt = go.Figure()
            fig_pt.add_trace(go.Bar(x=p_time[COL_MANTO], y=p_time[COL_TIEMPO], name="Tiempo Promedio", marker_color="orange"))
            fig_pt.add_trace(go.Scatter(x=p_time[COL_MANTO], y=p_time['% Acumulado'], name="% Acumulado", yaxis="y2", line=dict(color="red", width=3)))
            fig_pt.update_layout(yaxis=dict(title="Tiempo Promedio"), yaxis2=dict(title="%", overlaying="y", side="right", range=[0, 105]))
            st.plotly_chart(fig_pt, use_container_width=True)

        # --- TAB 7: DATOS ---
        with t7:
            st.subheader("Datos de la Hoja Seleccionada")
            st.dataframe(df_f, use_container_width=True)

    else:
        st.error(f"Faltan columnas requeridas en el Excel: {requeridos}")
else:
    st.info("Sube tu archivo Excel para activar el análisis")
