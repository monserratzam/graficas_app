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

    requeridos = [COL_MANTO, COL_TECNICO, COL_OT, COL_TIEMPO, COL_HH]
    
    if all(col in df.columns for col in requeridos):
        
        # --- FILTROS GLOBALES ---
        st.sidebar.header("⚙️ Filtros Globales")
        manto_sel = st.sidebar.multiselect("Tipo de Mantención", sorted(df[COL_MANTO].unique()), default=df[COL_MANTO].unique())
        tecnico_sel = st.sidebar.multiselect("Técnicos", sorted(df[COL_TECNICO].unique()), default=df[COL_TECNICO].unique())

        # Limpieza y filtrado
        df_f = df[(df[COL_MANTO].isin(manto_sel)) & (df[COL_TECNICO].isin(tecnico_sel))].copy()
        for c in [COL_HH, COL_TIEMPO]:
            df_f[c] = pd.to_numeric(df_f[c], errors='coerce').fillna(0)

        # --- CREACIÓN DE PESTAÑAS PARA ORGANIZAR TODO ---
        t1, t2, t3, t4, t5, t6, t7 = st.tabs([
            "👥 Rendimiento Técnico", 
            "📊 Consolidado Calidad",
            "⏱️ Análisis de Tiempos",
            "🍰 Distribución OT",
            "📉 Histogramas",
            "🎯 Paretos (Calidad)",
            "📋 Datos Crudos"
        ])

        # --- TAB 1: RENDIMIENTO TÉCNICO (GRÁFICOS ORIGINALES) ---
        with t1:
            st.subheader("Productividad y Carga de Trabajo")
            
            # Gráfico 1: Suma de OT por Técnico
            res_ot = df_f.groupby(COL_TECNICO)[COL_OT].count().reset_index().sort_values(COL_OT, ascending=False)
            st.plotly_chart(px.bar(res_ot.head(15), x=COL_TECNICO, y=COL_OT, title="Total de Órdenes de Trabajo (OT) por Técnico", text_auto=True, color_discrete_sequence=['#1f77b4']), use_container_width=True)
            st.write("**Hoja de Verificación: Cantidad de OT**")
            st.dataframe(res_ot, hide_index=True, use_container_width=True)
            st.divider()

            # Gráfico 2: Suma de Horas Hombres (HH) por Técnico
            res_hh_sum = df_f.groupby(COL_TECNICO)[COL_HH].sum().reset_index().sort_values(COL_HH, ascending=False)
            st.plotly_chart(px.bar(res_hh_sum.head(15), x=COL_TECNICO, y=COL_HH, title="Suma Total de Horas Hombres (HH) por Técnico", text_auto='.2f', color_discrete_sequence=['#2ca02c']), use_container_width=True)
            st.write("**Hoja de Verificación: Suma HH**")
            st.dataframe(res_hh_sum, hide_index=True, use_container_width=True)
            st.divider()

            # Gráfico 3: Promedio de HH por Técnico
            res_hh_avg = df_f.groupby(COL_TECNICO)[COL_HH].mean().reset_index().sort_values(COL_HH, ascending=False)
            st.plotly_chart(px.bar(res_hh_avg.head(15), x=COL_TECNICO, y=COL_HH, title="Promedio de Horas Hombres (HH) por Tarea", text_auto='.2f', color_discrete_sequence=['#9467bd']), use_container_width=True)
            st.write("**Hoja de Verificación: Promedio HH**")
            st.dataframe(res_hh_avg, hide_index=True, use_container_width=True)

        # --- TAB 2: CONSOLIDADO DE CALIDAD (LA TABLA ESPECIAL QUE PEDISTE) ---
        with t2:
            st.subheader("Hoja de Verificación: Desempeño por OT")
            # Agrupación solicitada: OT, Suma Tiempo, Promedio
            consolidado = df_f.groupby(COL_TECNICO).agg({
                COL_OT: 'count',
                COL_TIEMPO: 'sum'
            }).reset_index()
            
            # Cálculo de la columna 4: Promedio = Suma Tiempo / Cantidad OT
            consolidado['Promedio Tiempo por OT'] = consolidado[COL_TIEMPO] / consolidado[COL_OT]
            consolidado = consolidado.sort_values('Promedio Tiempo por OT', ascending=False)
            
            # Renombrar para que coincida con tu solicitud
            consolidado.columns = ["Nombre del Técnico", "Suma de OT", "Suma Tiempo de Mantenimiento", "Promedio de Tiempo Mto por OT"]
            
            st.dataframe(consolidado.style.format({
                "Suma Tiempo de Mantenimiento": "{:.2f}",
                "Promedio de Tiempo Mto por OT": "{:.2f}"
            }), use_container_width=True, hide_index=True)
            
            st.info("💡 Esta tabla es fundamental para identificar qué técnicos tardan más por cada orden asignada.")

        # --- TAB 3: ANÁLISIS DE TIEMPOS ---
        with t3:
            st.subheader("Análisis de Tiempos de Mantención")
            
            # Gráfico 4: Suma de Tiempo de Mantención
            res_t_sum = df_f.groupby(COL_TECNICO)[COL_TIEMPO].sum().reset_index().sort_values(COL_TIEMPO, ascending=False)
            st.plotly_chart(px.bar(res_t_sum.head(15), x=COL_TECNICO, y=COL_TIEMPO, title="Suma Total de Tiempo de Mantenimiento", text_auto='.2f', color_discrete_sequence=['#ff7f0e']), use_container_width=True)
            st.write("**Hoja de Verificación: Suma Tiempos**")
            st.dataframe(res_t_sum, hide_index=True, use_container_width=True)
            st.divider()

            # Gráfico 5: Promedio de Tiempo de Mantención
            res_t_avg = df_f.groupby(COL_TECNICO)[COL_TIEMPO].mean().reset_index().sort_values(COL_TIEMPO, ascending=False)
            st.plotly_chart(px.bar(res_t_avg.head(15), x=COL_TECNICO, y=COL_TIEMPO, title="Promedio de Tiempo de Mantenimiento por OT", text_auto='.2f', color_discrete_sequence=['#d62728']), use_container_width=True)
            st.write("**Hoja de Verificación: Promedio Tiempo**")
            st.dataframe(res_t_avg, hide_index=True, use_container_width=True)

        # --- TAB 4: DISTRIBUCIÓN OT (GRÁFICO DE TORTA) ---
        with t4:
            st.subheader(f"Distribución de OT por {COL_MANTO}")
            res_pie = df_f.groupby(COL_MANTO)[COL_OT].count().reset_index()
            res_pie.columns = [COL_MANTO, 'Cantidad']
            res_pie['Porcentaje'] = (res_pie['Cantidad'] / res_pie['Cantidad'].sum() * 100).map("{:.1f}%".format)
            
            fig_p = px.pie(res_pie, values='Cantidad', names=COL_MANTO, hole=0.4)
            fig_p.update_traces(textinfo='value') # Solo valores en el gráfico como pediste
            st.plotly_chart(fig_p, use_container_width=True)
            
            st.write("**Hoja de Verificación (Incluye Porcentaje)**")
            st.dataframe(res_pie, hide_index=True, use_container_width=True)

        # --- TAB 5: HISTOGRAMAS ---
        with t5:
            st.subheader("Distribución de Frecuencia de Tiempos")
            fig_h = px.histogram(df_f, x=COL_TIEMPO, nbins=20, text_auto=True, color_discrete_sequence=['#00CC96'])
            fig_h.update_layout(bargap=0.1, xaxis_title="Rangos de Tiempo (Eje X)", yaxis_title="Frecuencia (Cantidad de OTs)")
            fig_h.update_xaxes(nticks=20) # Más etiquetas en el eje X
            st.plotly_chart(fig_h, use_container_width=True)
            
            st.write("**Hoja de Verificación: Rangos de Frecuencia**")
            # Crear tabla de frecuencias para la hoja de verificación
            df_f['Rango'] = pd.cut(df_f[COL_TIEMPO], bins=10).astype(str)
            res_h = df_f['Rango'].value_counts().reset_index().sort_values('Rango')
            st.dataframe(res_h, hide_index=True, use_container_width=True)

        # --- TAB 6: PARETOS (CALIDAD) ---
        with t6:
            # Pareto 1: Tipo Manto vs HH
            st.subheader(f"Diagrama de Pareto: {COL_MANTO} vs Horas Hombre")
            p_manto = df_f.groupby(COL_MANTO)[COL_HH].sum().sort_values(ascending=False).reset_index()
            p_manto['CumSum'] = p_manto[COL_HH].cumsum()
            p_manto['% Acumulado'] = (100 * p_manto['CumSum'] / p_manto[COL_HH].sum())
            
            fig_pm = go.Figure()
            fig_pm.add_trace(go.Bar(x=p_manto[COL_MANTO], y=p_manto[COL_HH], name="HH"))
            fig_pm.add_trace(go.Scatter(x=p_manto[COL_MANTO], y=p_manto['% Acumulado'], name="% Acumulado", yaxis="y2", line=dict(color="red", width=3)))
            fig_pm.update_layout(yaxis=dict(title="Horas Hombres"), yaxis2=dict(title="%", overlaying="y", side="right", range=[0, 105]))
            st.plotly_chart(fig_pm, use_container_width=True)
            st.write("**Hoja de Verificación: Pareto HH**")
            st.dataframe(p_manto, hide_index=True, use_container_width=True)
            
            st.divider()

            # Pareto 2: Tipo Manto vs Tiempo Promedio
            st.subheader(f"Diagrama de Pareto: {COL_MANTO} vs Tiempo Promedio")
            p_time = df_f.groupby(COL_MANTO)[COL_TIEMPO].mean().sort_values(ascending=False).reset_index()
            p_time['CumSum'] = p_time[COL_TIEMPO].cumsum()
            p_time['% Acumulado'] = (100 * p_time['CumSum'] / p_time[COL_TIEMPO].sum())
            
            fig_pt = go.Figure()
            fig_pt.add_trace(go.Bar(x=p_time[COL_MANTO], y=p_time[COL_TIEMPO], name="Tiempo Promedio", marker_color="orange"))
            fig_pt.add_trace(go.Scatter(x=p_time[COL_MANTO], y=p_time['% Acumulado'], name="% Acumulado", yaxis="y2", line=dict(color="red", width=3)))
            fig_pt.update_layout(yaxis=dict(title="Tiempo Promedio"), yaxis2=dict(title="%", overlaying="y", side="right", range=[0, 105]))
            st.plotly_chart(fig_pt, use_container_width=True)
            st.write("**Hoja de Verificación: Pareto Tiempo**")
            st.dataframe(p_time, hide_index=True, use_container_width=True)

        # --- TAB 7: DATOS ---
        with t7:
            st.subheader("Base de Datos Filtrada")
            st.dataframe(df_f, use_container_width=True)

    else:
        st.error(f"Faltan columnas requeridas. Asegúrate de que existan: {requeridos}")
else:
    st.info("Sube tu archivo Excel para iniciar el Dashboard Integral.")
