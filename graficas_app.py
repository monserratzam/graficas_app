import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Mantenimiento", layout="wide")

st.title("📊 Dashboard de Gestión de Mantenimiento")
st.markdown("---")

archivo = st.file_uploader("Sube tu archivo Excel homologado", type=["xlsx"])

if archivo:
    # 1. Leer archivo
    df = pd.read_excel(archivo)
    
    # 2. LIMPIEZA DE NOMBRES (Solo quita espacios invisibles)
    # Esto es para que 'Tipo de mantención ' pase a ser 'Tipo de mantención'
    df.columns = [str(col).strip() for col in df.columns]
    
    # 3. CONVERSIÓN NUMÉRICA DE TUS COLUMNAS
    columnas_num = ['Horas Hombres', 'Tiempo mantención', 'Año recepción']
    for col in columnas_num:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # --- BARRA LATERAL: FILTROS CON TUS NOMBRES ---
    st.sidebar.header("⚙️ Filtros de Reporte")
    
    # Filtros dinámicos usando tus encabezados exactos
    manto_sel = st.sidebar.multiselect("Tipo de mantención", sorted(df['Tipo de mantención'].dropna().unique()), default=df['Tipo de mantención'].dropna().unique())
    tecnico_sel = st.sidebar.multiselect("Nombre Técnico", sorted(df['Nombre Técnico'].dropna().unique()), default=df['Nombre Técnico'].dropna().unique())
    año_sel = st.sidebar.multiselect("Año recepción", sorted(df['Año recepción'].unique()), default=df['Año recepción'].unique())
    mes_sel = st.sidebar.multiselect("mes recepción", df['mes recepción'].dropna().unique(), default=df['mes recepción'].dropna().unique())

    # --- APLICACIÓN DE FILTROS ---
    df_filtrado = df[
        (df['Tipo de mantención'].isin(manto_sel)) &
        (df['Nombre Técnico'].isin(tecnico_sel)) &
        (df['Año recepción'].isin(año_sel)) &
        (df['mes recepción'].isin(mes_sel))
    ]

    # --- FUNCIÓN DE GRÁFICOS ---
    def generar_grafico(titulo, g_col, a_col, func, top=10):
        if not df_filtrado.empty:
            st.subheader(titulo)
            resumen = df_filtrado.groupby(g_col)[a_col].agg(func).reset_index()
            resumen.columns = [g_col, 'Valor']
            resumen = resumen.sort_values(by='Valor', ascending=False)
            if top: resumen = resumen.head(top)
            
            c1, c2 = st.columns([2, 1])
            with c1:
                fig = px.bar(resumen, x=g_col, y='Valor', color='Valor', color_continuous_scale='Blues', text_auto='.2f')
                fig.update_layout(xaxis={'categoryorder':'total descending'}, xaxis_title=g_col, yaxis_title=None)
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                st.info("Hoja de Verificación")
                st.dataframe(resumen, hide_index=True, use_container_width=True)
            st.markdown("---")

    # --- REPORTES FINALES ---
    if not df_filtrado.empty:
        # Usamos tus nombres de columna directamente
        generar_grafico("Top 10: Cantidad de OT por Técnico", "Nombre Técnico", "N°OT", "count")
        generar_grafico("Top 10: Suma de Horas Hombres por Técnico", "Nombre Técnico", "Horas Hombres", "sum")
        generar_grafico("Top 10: Tiempo Mantención Total por Técnico", "Nombre Técnico", "Tiempo mantención", "sum")
        generar_grafico("Top 10: Cantidad de OTs por Equipo para cada Técnico", "Nombre Técnico", "N°OT", "count")
        generar_grafico("Top 10: Promedio Tiempo Mantención por OT", "Nombre Técnico", "Tiempo mantención", "mean")
        generar_grafico("OT por Tipo de Equipo", "Equipo", "N°OT", "count", top=None)
    else:
        st.warning("No hay datos que coincidan con los filtros.")
else:
    st.info("Sube tu archivo Excel para comenzar.")
