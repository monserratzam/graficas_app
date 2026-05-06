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
    xls = pd.ExcelFile(archivo)
    hoja_seleccionada = st.selectbox("1. Selecciona la hoja de datos", xls.sheet_names)
    df = pd.read_excel(archivo, sheet_name=hoja_seleccionada)

    # --- VARIABLES SEGÚN TU ESTRUCTURA ---
    COL_MANTO = "Tipo de mantención"
    COL_TECNICO = "Nombre Técnico"
    COL_OT = "N°OT"
    COL_HH = "Horas Hombres"
    COL_TIEMPO = "Tiempo mantención"
    COL_EQUIPO = "Equipo"
    COL_MES = "Mes término"
    COL_ANIO = "Año término"

    requeridos = [COL_MANTO, COL_TECNICO, COL_OT, COL_TIEMPO, COL_HH, COL_EQUIPO, COL_MES, COL_ANIO]
    
    if all(col in df.columns for col in requeridos):
        
        # --- FILTROS GLOBALES (SIDEBAR) ---
        st.sidebar.header("⚙️ Filtros de Búsqueda")
        
        # Corrección del error: Convertir a numérico y eliminar NaNs antes de ordenar
        anios_raw = pd.to_numeric(df[COL_ANIO], errors='coerce').dropna().unique()
        anios_disponibles = sorted([int(a) for a in anios_raw], reverse=True)
        anio_sel = st.sidebar.multiselect("Año de Término", anios_disponibles, default=anios_disponibles)
        
        # Aplicar lo mismo para el mes por si acaso hay datos mixtos
        meses_disponibles = sorted(df[COL_MES].dropna().astype(str).unique().tolist())
        mes_sel = st.sidebar.multiselect("Mes de Término", meses_disponibles, default=meses_disponibles)
        
        # Filtros de Categoría
        manto_sel = st.sidebar.multiselect("Tipo de Mantención", sorted(df[COL_MANTO].dropna().unique()), default=df[COL_MANTO].unique())
        tecnico_sel = st.sidebar.multiselect("Técnicos", sorted(df[COL_TECNICO].dropna().unique()), default=df[COL_TECNICO].unique())

        # --- APLICACIÓN DE FILTROS ---
        # Aseguramos que la comparación de año sea numérica
        df[COL_ANIO] = pd.to_numeric(df[COL_ANIO], errors='coerce')
        
        df_f = df[
            (df[COL_ANIO].isin(anio_sel)) & 
            (df[COL_MES].isin(mes_sel)) & 
            (df[COL_MANTO].isin(manto_sel)) & 
            (df[COL_TECNICO].isin(tecnico_sel))
        ].copy()

        # Limpieza de datos numéricos para cálculos
        for c in [COL_HH, COL_TIEMPO]:
            df_f[c] = pd.to_numeric(df_f[c], errors='coerce').fillna(0)

        # --- PESTAÑAS (9 TABS) ---
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

        # --- TAB 1: RENDIMIENTO TÉCNICO ---
        with t1:
            st.subheader("Productividad y Esfuerzo por Técnico")
            res_ot = df_f.groupby(COL_TECNICO)[COL_OT].count().reset_index().sort_values(COL_OT, ascending=False)
            st.plotly_chart(px.bar(res_ot, x=COL_TECNICO, y=COL_OT, title="Total de OT por Técnico", text_auto=True), use_container_width=True)
            
            res_hh_sum = df_f.groupby(COL_TECNICO)[COL_HH].sum().reset_index().sort_values(COL_HH, ascending=False)
            st.plotly_chart(px.bar(res_hh_sum, x=COL_TECNICO, y=COL_HH, title="Suma Total de Horas Hombre (HH)", text_auto='.2f', color_discrete_sequence=['#2ca02c']), use_container_width=True)
            
            res_hh_avg = df_f.groupby(COL_TECNICO)[COL_HH].mean().reset_index().sort_values(COL_HH, ascending=False)
            st.plotly_chart(px.bar(res_hh_avg, x=COL_TECNICO, y=COL_HH, title="Promedio de HH por OT", text_auto='.2f', color_discrete_sequence=['#9467bd']), use_container_width=True)

        # --- TAB 2: ANÁLISIS DE TIEMPOS ---
        with t2:
            st.subheader("Tiempos de Ejecución")
            res_t_sum = df_f.groupby(COL_TECNICO)[COL_TIEMPO].sum().reset_index().sort_values(COL_TIEMPO, ascending=False)
            st.plotly_chart(px.bar(res_t_sum, x=COL_TECNICO, y=COL_TIEMPO, title="Suma Total Tiempo Mantenimiento", text_auto='.2f', color_discrete_sequence=['#ff7f0e']), use_container_width=True)
            
            res_t_avg = df_f.groupby(COL_TECNICO)[COL_TIEMPO].mean().reset_index().sort_values(COL_TIEMPO, ascending=False)
            st.plotly_chart(px.bar(res_t_avg, x=COL_TECNICO, y=COL_TIEMPO, title="Promedio Tiempo Mantenimiento por OT", text_auto='.2f', color_discrete_sequence=['#d62728']), use_container_width=True)

        # --- TAB 3: CONSOLIDADO DE CALIDAD ---
        with t3:
            st.subheader("Hoja de Verificación: Desempeño por OT")
            if not df_f.empty:
                consolidado = df_f.groupby(COL_TECNICO).agg({COL_OT: 'count', COL_TIEMPO: 'sum'}).reset_index()
                consolidado['Promedio'] = consolidado[COL_TIEMPO] / consolidado[COL_OT]
                consolidado.columns = ["Técnico", "Suma de OT", "Suma Tiempo Mto", "Promedio Tiempo Mto por OT"]
                st.dataframe(consolidado.sort_values("Promedio Tiempo Mto por OT", ascending=False).style.format({
                    "Suma Tiempo Mto": "{:.2f}",
                    "Promedio Tiempo Mto por OT": "{:.2f}"
                }), use_container_width=True, hide_index=True)

        # --- TAB 4: DISPERSIÓN ---
        with t4:
            st.subheader("Linealidad: Cantidad de OT vs Esfuerzo Total (HH)")
            disp_data = df_f.groupby(COL_TECNICO).agg({COL_OT: 'count', COL_HH: 'sum'}).reset_index()
            disp_data.columns = ["Técnico", "x", "y"]

            if len(disp_data) > 1:
                m, b = np.polyfit(disp_data["x"], disp_data["y"], 1)
                linea_x = np.linspace(disp_data["x"].min(), disp_data["x"].max(), 100)
                linea_y = m * linea_x + b
                
                fig_disp = go.Figure()
                fig_disp.add_trace(go.Scatter(x=disp_data["x"], y=disp_data["y"], mode='markers+text', 
                                             text=disp_data["Técnico"], textposition="top center", 
                                             marker=dict(size=12, color='#636EFA'), name="Técnicos"))
                fig_disp.add_trace(go.Scatter(x=linea_x, y=linea_y, mode='lines', 
                                             line=dict(color='red', dash='dash'), name="Tendencia Lineal"))
                fig_disp.update_layout(xaxis_title="Número de OT", yaxis_title="Horas Hombre (HH)")
                st.plotly_chart(fig_disp, use_container_width=True)

        # --- TAB 5: ANÁLISIS DE EQUIPOS ---
        with t5:
            st.subheader("Frecuencia de Mantenimiento por Equipo")
            res_eq = df_f.groupby(COL_EQUIPO)[COL_OT].count().reset_index().sort_values(COL_OT, ascending=False)
            st.plotly_chart(px.bar(res_eq.head(20), x=COL_EQUIPO, y=COL_OT, title="Top 20 Equipos con más OT", text_auto=True), use_container_width=True)

        # --- TAB 6: DISTRIBUCIÓN OT (TORTA) ---
        with t6:
            st.subheader(f"Distribución de OT por {COL_MANTO}")
            res_pie = df_f.groupby(COL_MANTO)[COL_OT].count().reset_index()
            fig_p = px.pie(res_pie, values=COL_OT, names=COL_MANTO, hole=0.4)
            fig_p.update_traces(textinfo='value')
            st.plotly_chart(fig_p, use_container_width=True)

        # --- TAB 7: HISTOGRAMAS ---
        with t7:
            st.subheader("Histograma: Frecuencia de Tiempos")
            fig_h = px.histogram(df_f, x=COL_TIEMPO, nbins=20, text_auto=True)
            fig_h.update_layout(bargap=0.1, xaxis_title="Rango de Tiempo", yaxis_title="Cantidad de OTs")
            st.plotly_chart(fig_h, use_container_width=True)

        # --- TAB 8: PARETOS ---
        with t8:
            p_hh = df_f.groupby(COL_MANTO)[COL_HH].sum().sort_values(ascending=False).reset_index()
            if not p_hh.empty:
                p_hh['% Acumulado'] = (100 * p_hh[COL_HH].cumsum() / p_hh[COL_HH].sum())
                fig_p1 = go.Figure()
                fig_p1.add_trace(go.Bar(x=p_hh[COL_MANTO], y=p_hh[COL_HH], name="Suma HH"))
                fig_p1.add_trace(go.Scatter(x=p_hh[COL_MANTO], y=p_hh['% Acumulado'], name="%", yaxis="y2", line=dict(color="red", width=3)))
                fig_p1.update_layout(title="Pareto: Tipo Mantención vs HH", yaxis2=dict(overlaying="y", side="right", range=[0, 105]))
                st.plotly_chart(fig_p1, use_container_width=True)

        # --- TAB 9: DATOS CRUDOS ---
        with t9:
            st.subheader("Vista General de Datos Filtrados")
            st.dataframe(df_f, use_container_width=True)

    else:
        st.error(f"Error: Faltan columnas necesarias.")
else:
    st.info("Sube tu archivo Excel para iniciar el Dashboard.")
