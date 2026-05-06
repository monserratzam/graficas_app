import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Configuración de página
st.set_page_config(page_title="Dashboard Mantenimiento UV", layout="wide")

st.title("📊 Dashboard de Gestión, Calidad y Rendimiento de Mantenimiento")
st.markdown("---")

archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo:
    # 1. LECTURA INICIAL (Sin procesar para diagnóstico)
    xls = pd.ExcelFile(archivo)
    hoja_seleccionada = st.selectbox("1. Selecciona la hoja de datos", xls.sheet_names)
    df_raw = pd.read_excel(archivo, sheet_name=hoja_seleccionada)

    # --- DEFINICIÓN DE VARIABLES ---
    COL_MANTO = "Tipo de mantención"
    COL_TECNICO = "Nombre Técnico"
    COL_OT = "N°OT"
    COL_HH = "Horas Hombres"
    COL_TIEMPO = "Tiempo mantención"
    COL_EQUIPO = "Equipo"
    COL_MES = "Mes término"
    COL_ANIO = "Año término"

    requeridos = [COL_MANTO, COL_TECNICO, COL_OT, COL_TIEMPO, COL_HH, COL_EQUIPO, COL_MES, COL_ANIO]
    
    if all(col in df_raw.columns for col in requeridos):
        
        # --- NORMALIZACIÓN DE SEGURIDAD ---
        # Copia profunda para no alterar la carga original
        df = df_raw.copy()
        for c in [COL_MANTO, COL_TECNICO, COL_MES, COL_EQUIPO]:
            df[c] = df[c].astype(str).str.strip()
        
        df[COL_ANIO] = pd.to_numeric(df[COL_ANIO], errors='coerce').fillna(0).astype(int)

        # --- FILTROS GLOBALES (SIDEBAR) ---
        st.sidebar.header("⚙️ Filtros de Búsqueda")
        
        # Extraemos opciones del DF normalizado
        ops_anio = sorted(df[COL_ANIO].unique().tolist(), reverse=True)
        ops_mes = sorted(df[COL_MES].unique().tolist())
        ops_manto = sorted(df[COL_MANTO].unique().tolist())
        ops_tec = sorted(df[COL_TECNICO].unique().tolist())

        # Seteamos defaults para que NADA empiece filtrado
        anio_sel = st.sidebar.multiselect("Año de Término", ops_anio, default=ops_anio)
        mes_sel = st.sidebar.multiselect("Mes de Término", ops_mes, default=ops_mes)
        manto_sel = st.sidebar.multiselect("Tipo de Mantención", ops_manto, default=ops_manto)
        tec_sel = st.sidebar.multiselect("Técnicos", ops_tec, default=ops_tec)

        # --- APLICACIÓN DE FILTROS ---
        df_f = df[
            (df[COL_ANIO].isin(anio_sel)) & 
            (df[COL_MES].isin(mes_sel)) & 
            (df[COL_MANTO].isin(manto_sel)) & 
            (df[COL_TECNICO].isin(tec_sel))
        ].copy()

        # Asegurar tipos numéricos para cálculos
        for c in [COL_HH, COL_TIEMPO]:
            df_f[c] = pd.to_numeric(df_f[c], errors='coerce').fillna(0)

        # --- ESTRUCTURA DE 9 PESTAÑAS ---
        t1, t2, t3, t4, t5, t6, t7, t8, t9 = st.tabs([
            "👥 Rendimiento Técnico", 
            "⏱️ Análisis de Tiempos",
            "📊 Consolidado Calidad",
            "📍 Dispersión (Linealidad)",
            "⚙️ Análisis de Equipos",
            "🍰 Distribución OT",
            "📈 Histogramas",
            "🎯 Paretos (Calidad)",
            "📋 Datos Crudos"
        ])

        # --- TAB 1: RENDIMIENTO (OT, SUMA HH, PROMEDIO HH) ---
        with t1:
            st.subheader("Rendimiento y Carga de Trabajo")
            # Gráfico OT
            res_ot = df_f.groupby(COL_TECNICO)[COL_OT].count().reset_index().sort_values(COL_OT, ascending=False)
            st.plotly_chart(px.bar(res_ot, x=COL_TECNICO, y=COL_OT, title="Total de OT por Técnico", text_auto=True), use_container_width=True)
            # Gráfico Suma HH
            res_hh_s = df_f.groupby(COL_TECNICO)[COL_HH].sum().reset_index().sort_values(COL_HH, ascending=False)
            st.plotly_chart(px.bar(res_hh_s, x=COL_TECNICO, y=COL_HH, title="Suma Total de HH", color_discrete_sequence=['green'], text_auto='.2f'), use_container_width=True)
            # Gráfico Promedio HH
            res_hh_a = df_f.groupby(COL_TECNICO)[COL_HH].mean().reset_index().sort_values(COL_HH, ascending=False)
            st.plotly_chart(px.bar(res_hh_a, x=COL_TECNICO, y=COL_HH, title="Promedio de HH por OT", color_discrete_sequence=['purple'], text_auto='.2f'), use_container_width=True)

        # --- TAB 2: TIEMPOS (SUMA Y PROMEDIO) ---
        with t2:
            st.subheader("Análisis de Tiempos de Mantenimiento")
            # Suma Tiempo
            res_t_s = df_f.groupby(COL_TECNICO)[COL_TIEMPO].sum().reset_index().sort_values(COL_TIEMPO, ascending=False)
            st.plotly_chart(px.bar(res_t_s, x=COL_TECNICO, y=COL_TIEMPO, title="Suma Total Tiempo Mto", color_discrete_sequence=['orange'], text_auto='.2f'), use_container_width=True)
            # Promedio Tiempo
            res_t_a = df_f.groupby(COL_TECNICO)[COL_TIEMPO].mean().reset_index().sort_values(COL_TIEMPO, ascending=False)
            st.plotly_chart(px.bar(res_t_a, x=COL_TECNICO, y=COL_TIEMPO, title="Promedio Tiempo Mto por OT", color_discrete_sequence=['red'], text_auto='.2f'), use_container_width=True)

        # --- TAB 3: CONSOLIDADO DE CALIDAD ---
        with t3:
            st.subheader("Hoja de Verificación de Rendimiento")
            if not df_f.empty:
                conso = df_f.groupby(COL_TECNICO).agg({COL_OT: 'count', COL_TIEMPO: 'sum'}).reset_index()
                conso['Promedio Tiempo/OT'] = conso[COL_TIEMPO] / conso[COL_OT]
                conso.columns = ["Técnico", "Suma de OT", "Suma Tiempo Mto", "Promedio Tiempo Mto por OT"]
                st.dataframe(conso.sort_values("Promedio Tiempo Mto por OT", ascending=False).style.format({"Suma Tiempo Mto": "{:.2f}", "Promedio Tiempo Mto por OT": "{:.2f}"}), use_container_width=True, hide_index=True)

        # --- TAB 4: DISPERSIÓN (Linealidad OT vs HH) ---
        with t4:
            st.subheader("Búsqueda de Linealidad: Carga vs Esfuerzo")
            disp = df_f.groupby(COL_TECNICO).agg({COL_OT: 'count', COL_HH: 'sum'}).reset_index()
            if len(disp) > 1:
                m, b = np.polyfit(disp[COL_OT], disp[COL_HH], 1)
                fig_d = px.scatter(disp, x=COL_OT, y=COL_HH, text=COL_TECNICO, title="Comparativa OT vs Suma HH")
                fig_d.add_trace(go.Scatter(x=disp[COL_OT], y=m*disp[COL_OT]+b, mode='lines', name='Tendencia Lineal', line=dict(color='red', dash='dash')))
                fig_d.update_traces(marker=dict(size=12))
                st.plotly_chart(fig_d, use_container_width=True)
            else:
                st.info("Agregue más técnicos en el filtro para ver la tendencia.")

        # --- TAB 5: EQUIPOS ---
        with t5:
            st.subheader("Frecuencia de OT por Equipo")
            res_eq = df_f.groupby(COL_EQUIPO)[COL_OT].count().reset_index().sort_values(COL_OT, ascending=False)
            st.plotly_chart(px.bar(res_eq.head(20), x=COL_EQUIPO, y=COL_OT, title="Top 20 Equipos Atendidos", text_auto=True), use_container_width=True)

        # --- TAB 6: DISTRIBUCIÓN (TORTA) ---
        with t6:
            st.subheader("Distribución de OT por Tipo")
            res_p = df_f.groupby(COL_MANTO)[COL_OT].count().reset_index()
            fig_p = px.pie(res_p, values=COL_OT, names=COL_MANTO, hole=0.4)
            fig_p.update_traces(textinfo='value')
            st.plotly_chart(fig_p, use_container_width=True)

        # --- TAB 7: HISTOGRAMA ---
        with t7:
            st.subheader("Distribución de Frecuencia de Tiempos")
            st.plotly_chart(px.histogram(df_f, x=COL_TIEMPO, nbins=20, text_auto=True), use_container_width=True)

        # --- TAB 8: PARETOS (HH Y PROMEDIO) ---
        with t8:
            # Pareto HH
            p_hh = df_f.groupby(COL_MANTO)[COL_HH].sum().sort_values(ascending=False).reset_index()
            if not p_hh.empty:
                p_hh['% Acum'] = 100 * p_hh[COL_HH].cumsum() / p_hh[COL_HH].sum()
                f1 = go.Figure()
                f1.add_trace(go.Bar(x=p_hh[COL_MANTO], y=p_hh[COL_HH], name="HH"))
                f1.add_trace(go.Scatter(x=p_hh[COL_MANTO], y=p_hh['% Acum'], yaxis="y2", name="% Acumulado", line=dict(color="red")))
                f1.update_layout(title="Pareto: Mantenimiento vs HH", yaxis2=dict(overlaying="y", side="right", range=[0, 105]))
                st.plotly_chart(f1, use_container_width=True)
            
            # Pareto Promedio
            p_tp = df_f.groupby(COL_MANTO)[COL_TIEMPO].mean().sort_values(ascending=False).reset_index()
            if not p_tp.empty:
                p_tp['% Acum'] = 100 * p_tp[COL_TIEMPO].cumsum() / p_tp[COL_TIEMPO].sum()
                f2 = go.Figure()
                f2.add_trace(go.Bar(x=p_tp[COL_MANTO], y=p_tp[COL_TIEMPO], name="Promedio", marker_color="orange"))
                f2.add_trace(go.Scatter(x=p_tp[COL_MANTO], y=p_tp['% Acum'], yaxis="y2", name="% Acumulado", line=dict(color="red")))
                f2.update_layout(title="Pareto: Mantenimiento vs Tiempo Promedio", yaxis2=dict(overlaying="y", side="right", range=[0, 105]))
                st.plotly_chart(f2, use_container_width=True)

        # --- TAB 9: DIAGNÓSTICO (IMPORTANTE) ---
        with t9:
            st.subheader("📋 Auditoría de Carga de Datos")
            st.write(f"Filas totales detectadas en el Excel: **{len(df_raw)}**")
            st.write("Conteo directo por columna 'Tipo de mantención' (Sin filtros):")
            st.write(df_raw[COL_MANTO].value_counts())
            st.markdown("---")
            st.write("Datos que están pasando los filtros actuales:")
            st.dataframe(df_f, use_container_width=True)

    else:
        st.error(f"El archivo no tiene las columnas: {requeridos}")
else:
    st.info("Por favor, sube el archivo Excel para activar el dashboard.")
