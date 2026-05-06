import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard Mantenimiento Pro", layout="wide")

st.title("📊 Gestión de Mantenimiento y Control de Calidad")
st.markdown("---")

archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo:
    xls = pd.ExcelFile(archivo)
    hoja_seleccionada = st.selectbox("1. Selecciona la hoja de datos", xls.sheet_names)
    df = pd.read_excel(archivo, sheet_name=hoja_seleccionada)

    # --- CONFIGURACIÓN DE NOMBRES ---
    COL_MANTO = "Tipo de mantención"
    COL_TECNICO = "Nombre Técnico"
    COL_OT = "N°OT"
    COL_HH = "Horas Hombres"
    COL_TIEMPO = "Tiempo mantención"
    COL_EQUIPO = "Equipo"

    # Verificar columnas básicas
    requeridos = [COL_MANTO, COL_TECNICO, COL_OT, COL_TIEMPO, COL_HH]
    if all(col in df.columns for col in requeridos):
        
        # --- FILTROS EN SIDEBAR ---
        st.sidebar.header("⚙️ Filtros Globales")
        manto_sel = st.sidebar.multiselect("Tipo de Mantención", sorted(df[COL_MANTO].unique()), default=df[COL_MANTO].unique())
        tecnico_sel = st.sidebar.multiselect("Técnicos", sorted(df[COL_TECNICO].unique()), default=df[COL_TECNICO].unique())

        # Aplicar filtros y limpiar datos
        df_f = df[(df[COL_MANTO].isin(manto_sel)) & (df[COL_TECNICO].isin(tecnico_sel))].copy()
        for c in [COL_HH, COL_TIEMPO]:
            df_f[c] = pd.to_numeric(df_f[c], errors='coerce').fillna(0)

        # --- CREACIÓN DE PESTAÑAS ---
        t1, t2, t3, t4, t5, t6, t7 = st.tabs([
            "📈 Rendimiento Técnico", 
            "⏱️ Análisis de Tiempos", 
            "🍰 Distribución OT",
            "📊 Histograma Tiempos",
            "🎯 Pareto (Calidad)",
            "⚙️ Equipos",
            "📋 Datos Filtrados"
        ])

        # --- TABA 1: RENDIMIENTO TÉCNICO (Gráficos originales) ---
        with t1:
            st.subheader("Productividad por Técnico")
            # Cantidad de OT
            res_ot = df_f.groupby(COL_TECNICO)[COL_OT].count().reset_index().sort_values(COL_OT, ascending=False)
            st.plotly_chart(px.bar(res_ot.head(10), x=COL_TECNICO, y=COL_OT, title="Top 10: Cantidad de OT", text_auto=True), use_container_width=True)
            st.write("**Hoja de Verificación: Cantidad OT**")
            st.dataframe(res_ot, hide_index=True, use_container_width=True)
            
            st.divider()
            
            # Suma de HH
            res_hh = df_f.groupby(COL_TECNICO)[COL_HH].sum().reset_index().sort_values(COL_HH, ascending=False)
            st.plotly_chart(px.bar(res_hh.head(10), x=COL_TECNICO, y=COL_HH, title="Top 10: Total Horas Hombres", text_auto='.2f'), use_container_width=True)
            st.write("**Hoja de Verificación: Horas Hombres**")
            st.dataframe(res_hh, hide_index=True, use_container_width=True)

        # --- TABA 2: ANÁLISIS DE TIEMPOS ---
        with t2:
            st.subheader("Análisis de Tiempos de Respuesta")
            res_time = df_f.groupby(COL_TECNICO)[COL_TIEMPO].mean().reset_index().sort_values(COL_TIEMPO, ascending=False)
            st.plotly_chart(px.bar(res_time.head(10), x=COL_TECNICO, y=COL_TIEMPO, title="Promedio Tiempo de Mantención", text_auto='.2f'), use_container_width=True)
            st.write("**Hoja de Verificación: Promedios de Tiempo**")
            st.dataframe(res_time, hide_index=True, use_container_width=True)

        # --- TABA 3: GRÁFICO DE TORTA ---
        with t3:
            st.subheader(f"Distribución de OT por {COL_MANTO}")
            res_pie = df_f.groupby(COL_MANTO)[COL_OT].count().reset_index()
            res_pie.columns = [COL_MANTO, 'Cantidad']
            res_pie['Porcentaje'] = (res_pie['Cantidad'] / res_pie['Cantidad'].sum() * 100).map("{:.1f}%".format)
            
            fig_p = px.pie(res_pie, values='Cantidad', names=COL_MANTO, hole=0.4)
            fig_p.update_traces(textinfo='value') # Solo valores en el gráfico
            st.plotly_chart(fig_p, use_container_width=True)
            
            st.write("**Hoja de Verificación (Incluye %)**")
            st.dataframe(res_pie, hide_index=True, use_container_width=True)

        # --- TABA 4: HISTOGRAMA ---
        with t4:
            st.subheader("Distribución de Frecuencia de Tiempos")
            fig_h = px.histogram(df_f, x=COL_TIEMPO, nbins=20, text_auto=True, color_discrete_sequence=['#00CC96'])
            fig_h.update_layout(bargap=0.1, xaxis_title="Rangos de Tiempo (Eje X)", yaxis_title="Cantidad de OTs")
            # Forzamos que se vean más etiquetas en el eje X
            fig_h.update_xaxes(nticks=20)
            st.plotly_chart(fig_h, use_container_width=True)
            st.write("**Hoja de Verificación: Frecuencias de Tiempo**")
            # Creamos los rangos para la tabla
            df_f['Rango'] = pd.cut(df_f[COL_TIEMPO], bins=10)
            res_h = df_f['Rango'].value_counts().reset_index().sort_values('Rango')
            st.dataframe(res_h, hide_index=True, use_container_width=True)

        # --- TABA 5: PARETO (CALIDAD) ---
        with t5:
            st.subheader("Diagrama de Pareto: Horas Hombre por Técnico")
            st.info("Herramienta de Calidad: Identifica el 20% de técnicos que concentran el 80% de la carga de HH.")
            p_data = df_f.groupby(COL_TECNICO)[COL_HH].sum().sort_values(ascending=False).reset_index()
            p_data['CumSum'] = p_data[COL_HH].cumsum()
            p_data['% Acumulado'] = 100 * p_data['CumSum'] / p_data[COL_HH].sum()

            fig_pareto = go.Figure()
            fig_pareto.add_trace(go.Bar(x=p_data[COL_TECNICO], y=p_data[COL_HH], name="HH", marker_color='blue'))
            fig_pareto.add_trace(go.Scatter(x=p_data[COL_TECNICO], y=p_data['% Acumulado'], name="% Acumulado", yaxis="y2", line=dict(color="red", width=3)))
            fig_pareto.update_layout(yaxis=dict(title="HH Totales"), yaxis2=dict(title="%", overlaying="y", side="right", range=[0, 105]))
            st.plotly_chart(fig_pareto, use_container_width=True)
            st.write("**Hoja de Verificación: Pareto**")
            st.dataframe(p_data, hide_index=True, use_container_width=True)

        # --- TABA 6: EQUIPOS ---
        with t6:
            st.subheader("Distribución por Equipo")
            res_eq = df_f.groupby(COL_EQUIPO)[COL_OT].count().reset_index().sort_values(COL_OT, ascending=False)
            st.plotly_chart(px.bar(res_eq, x=COL_EQUIPO, y=COL_OT, text_auto=True), use_container_width=True)
            st.write("**Hoja de Verificación: Equipos**")
            st.dataframe(res_eq, hide_index=True, use_container_width=True)

        # --- TABA 7: DATOS CRUDOS ---
        with t7:
            st.subheader("Registros Filtrados")
            st.dataframe(df_f, use_container_width=True)

    else:
        st.error(f"Faltan columnas. Asegúrate de que existan: {requeridos}")
else:
    st.info("Sube tu archivo Excel para activar el Dashboard.")
