import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Dashboard Mantenimiento OT", layout="wide")

st.title("📊 Dashboard de Gestión de Mantenimiento")
st.markdown("---")

# --- CARGA DE DATOS ---
archivo = st.file_uploader("Sube el archivo Excel homologado", type=["xlsx"])

if archivo:
    # Leer el archivo
    df = pd.read_excel(archivo)
    
    # Pre-procesamiento: Asegurar que las columnas de medida sean numéricas para evitar errores en cálculos
    columnas_meticas = ['Horas Hombres', 'Tiempo mantención', 'Tiempo total']
    for col in columnas_meticas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # --- BARRA LATERAL: SISTEMA DE FILTROS ---
    st.sidebar.header("⚙️ Filtros Globales")
    
    # Filtro 1: Tipo de mantención (T1, T2, T3, T4)
    tipos_manto = sorted(df['Tipo de mantención'].dropna().unique())
    manto_sel = st.sidebar.multiselect("Tipo de mantención", tipos_manto, default=tipos_manto)
    
    # Filtro 2: Nombre de Técnico
    tecnicos = sorted(df['Nombre Técnico'].dropna().unique())
    tecnico_sel = st.sidebar.multiselect("Técnico Responsable", tecnicos, default=tecnicos)
    
    # Filtro 3: Mes y Año (Basado en tus encabezados del Excel)
    años = sorted(df['Año recepción'].dropna().unique())
    año_sel = st.sidebar.multiselect("Año de Recepción", años, default=años)
    
    meses = df['mes recepción'].dropna().unique()
    mes_sel = st.sidebar.multiselect("Mes de Recepción", meses, default=meses)

    # Aplicación de filtros al DataFrame maestro
    df_filtrado = df[
        (df['Tipo de mantención'].isin(manto_sel)) &
        (df['Nombre Técnico'].isin(tecnico_sel)) &
        (df['Año recepción'].isin(año_sel)) &
        (df['mes recepción'].isin(mes_sel))
    ]

    # --- FUNCIÓN MAESTRA DE VISUALIZACIÓN ---
    def generar_grafico_y_tabla(titulo, groupby_col, agg_col, agg_func, top_n=10):
        """
        Genera una sección con título, gráfico de barras ordenado y su hoja de verificación.
        """
        st.subheader(titulo)
        
        # Agrupación y cálculo
        resumen = df_filtrado.groupby(groupby_col)[agg_col].agg(agg_func).reset_index()
        resumen.columns = [groupby_col, 'Valor']
        
        # Ordenamiento de mayor a menor
        resumen = resumen.sort_values(by='Valor', ascending=False)
        
        # Aplicar Top 10 si se requiere
        if top_n:
            resumen = resumen.head(top_n)
        
        # Layout de dos columnas para gráfico y tabla
        col_viz, col_tbl = st.columns([2, 1])
        
        with col_viz:
            # Gráfico de barras con Plotly
            fig = px.bar(
                resumen, 
                x=groupby_col, 
                y='Valor', 
                color='Valor',
                color_continuous_scale='Blues',
                text_auto='.2f'
            )
            # Forzar el orden descendente visualmente
            fig.update_layout(
                xaxis_title=groupby_col,
                yaxis_title=None,
                xaxis={'categoryorder':'total descending'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with col_tbl:
            st.info("📋 **Hoja de Verificación**")
            # Mostrar tabla concentrada
            st.dataframe(resumen, hide_index=True, use_container_width=True)
        st.markdown("---")

    # --- EJECUCIÓN DE LAS 6 MÉTRICAS SOLICITADAS ---

    if not df_filtrado.empty:
        # 1. Top 10 suma de N° OT por técnico
        generar_grafico_y_tabla("Top 10: Suma de N° OT por Técnico", "Nombre Técnico", "N°OT", "count")

        # 2. Top 10 suma de HH por técnico
        generar_grafico_y_tabla("Top 10: Suma de Horas Hombres por Técnico", "Nombre Técnico", "Horas Hombres", "sum")

        # 3. Top 10 suma de tiempo de mantenimiento por técnico
        generar_grafico_y_tabla("Top 10: Tiempo de Mantención Total por Técnico", "Nombre Técnico", "Tiempo mantención", "sum")

        # 4. Top 10 cantidad de OTs por equipo (según cada técnico)
        generar_grafico_y_tabla("Top 10: Cantidad de OTs asociadas a Equipos por Técnico", "Nombre Técnico", "N°OT", "count")

        # 5. Top 10 promedio de tiempo de mantenimiento por OT
        generar_grafico_y_tabla("Top 10: Promedio de Tiempo de Manto. por Técnico", "Nombre Técnico", "Tiempo mantención", "mean")

        # 6. Cantidad de OT por tipo de equipo (Sin límite de Top 10 para ver todo el parque)
        generar_grafico_y_tabla("Distribución de OT por Tipo de Equipo", "Equipo", "N°OT", "count", top_n=None)
    else:
        st.error("No hay datos disponibles para los filtros seleccionados.")

else:
    st.info("👋 Bienvenida. Por favor, sube tu archivo Excel para generar los gráficos y hojas de verificación.")