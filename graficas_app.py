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
    # 1. Leer el archivo
    df = pd.read_excel(archivo)
    
    # 2. LIMPIEZA DE COLUMNAS (Previene el KeyError)
    # Quitamos espacios invisibles y convertimos a texto
    df.columns = [str(col).strip() for col in df.columns]
    
    # 3. LIMPIEZA DE DATOS NUMÉRICOS
    columnas_metricas = ['Horas Hombres', 'Tiempo mantención', 'Tiempo total']
    for col in columnas_metricas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # --- BARRA LATERAL: FILTROS DESPLEGABLES ---
    st.sidebar.header("⚙️ Filtros de Reporte")
    
    # Función auxiliar para obtener opciones limpias
    def obtener_opciones(columna):
        if columna in df.columns:
            return sorted(df[columna].dropna().unique().tolist())
        return []

    # Filtro 1: Tipo de mantención
    opciones_manto = obtener_opciones('Tipo de mantención')
    manto_sel = st.sidebar.multiselect(
        "Seleccione Tipo de Mantención", 
        options=opciones_manto, 
        default=opciones_manto
    )
    
    # Filtro 2: Nombre de Técnico
    opciones_tecnico = obtener_opciones('Nombre Técnico')
    tecnico_sel = st.sidebar.multiselect(
        "Seleccione Técnicos", 
        options=opciones_tecnico, 
        default=opciones_tecnico
    )
    
    # Filtro 3: Año de Recepción
    opciones_año = obtener_opciones('Año recepción')
    año_sel = st.sidebar.multiselect(
        "Seleccione Año", 
        options=opciones_año, 
        default=opciones_año
    )
    
    # Filtro 4: Mes de Recepción
    opciones_mes = obtener_opciones('mes recepción')
    mes_sel = st.sidebar.multiselect(
        "Seleccione Mes", 
        options=opciones_mes, 
        default=opciones_mes
    )

    # --- APLICACIÓN DE FILTROS ---
    df_filtrado = df[
        (df['Tipo de mantención'].isin(manto_sel)) &
        (df['Nombre Técnico'].isin(tecnico_sel)) &
        (df['Año recepción'].isin(año_sel)) &
        (df['mes recepción'].isin(mes_sel))
    ]

    # --- FUNCIÓN DE VISUALIZACIÓN ---
    def generar_reporte(titulo, groupby_col, agg_col, agg_func, top_n=10):
        st.subheader(titulo)
        
        # Agrupación
        resumen = df_filtrado.groupby(groupby_col)[agg_col].agg(agg_func).reset_index()
        resumen.columns = [groupby_col, 'Valor']
        
        # Ordenamiento descendente
        resumen = resumen.sort_values(by='Valor', ascending=False)
        
        if top_n:
            resumen = resumen.head(top_n)
        
        col_graf, col_tbl = st.columns([2, 1])
        
        with col_graf:
            fig = px.bar(
                resumen, 
                x=groupby_col, 
                y='Valor', 
                color='Valor',
                color_continuous_scale='Blues',
                text_auto='.2f'
            )
            fig.update_layout(
                xaxis_title=groupby_col,
                yaxis_title=None,
                xaxis={'categoryorder':'total descending'}
            )
            st.plotly_chart(fig, use_container_width=True)
            
        with col_tbl:
            st.info("📋 **Hoja de Verificación**")
            st.dataframe(resumen, hide_index=True, use_container_width=True)
        st.markdown("---")

    # --- RENDERIZADO DE MÉTRICAS ---
    if not df_filtrado.empty:
        # 1. Cantidad de OT por técnico
        generar_reporte("Top 10: Suma de N° OT por Técnico", "Nombre Técnico", "N°OT", "count")

        # 2. Suma de HH por técnico
        generar_reporte("Top 10: Suma de Horas Hombres por Técnico", "Nombre Técnico", "Horas Hombres", "sum")

        # 3. Suma de tiempo de mantenimiento por técnico
        generar_reporte("Top 10: Tiempo de Mantención Total por Técnico", "Nombre Técnico", "Tiempo mantención", "sum")

        # 4. Cantidad de OTs por equipo para cada técnico
        generar_reporte("Top 10: Cantidad de OTs asociadas a Equipos por Técnico", "Nombre Técnico", "N°OT", "count")

        # 5. Promedio de tiempo de mantenimiento por OT por técnico
        generar_reporte("Top 10: Promedio de Tiempo de Manto. por Técnico", "Nombre Técnico", "Tiempo mantención", "mean")

        # 6. Gráfico por tipo de equipo
        generar_reporte("Distribución de OT por Tipo de Equipo", "Equipo", "N°OT", "count", top_n=None)
    else:
        st.warning("No hay datos que coincidan con los filtros seleccionados.")

else:
    st.info("Sube tu archivo Excel para generar automáticamente los gráficos y las hojas de verificación.")