import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Mantenimiento", layout="wide")

st.title("📊 Dashboard de Gestión de Mantenimiento")

# --- CARGA DE ARCHIVO ---
archivo = st.file_uploader("Sube tu archivo Excel homologado", type=["xlsx"])

if archivo:
    # 1. Cargar el objeto Excel para ver las hojas disponibles
    xls = pd.ExcelFile(archivo)
    hojas = xls.sheet_names
    
    # Selector de hoja para evitar buscar en la hoja equivocada
    hoja_seleccionada = st.selectbox("Selecciona la hoja donde están los datos", hojas)
    
    # 2. Leer la hoja seleccionada
    df = pd.read_excel(archivo, sheet_name=hoja_seleccionada)
    
    # 3. LIMPIEZA DE COLUMNAS (Crucial para evitar KeyError)
    # Quitamos espacios al inicio/final y saltos de línea internos
    df.columns = [str(col).strip().replace('\n', ' ') for col in df.columns]

    # --- BUSCADOR INTELIGENTE POR NOMBRE ---
    # Esta función busca la columna que contenga la palabra clave, ignorando mayúsculas/minúsculas
    def encontrar_columna(keywords):
        for col in df.columns:
            if any(k.lower() in col.lower() for k in keywords):
                return col
        return None

    # Mapeo automático basado en tus nombres reales
    c_manto   = encontrar_columna(['Tipo de mantención', 'Tipo de mantencion', 'mantenimiento'])
    c_tecnico = encontrar_columna(['Nombre Técnico', 'Nombre Tecnico', 'Técnico'])
    c_ot      = encontrar_columna(['N°OT', 'N° OT', 'OT'])
    c_hh      = encontrar_columna(['Horas Hombres', 'HH'])
    c_tiempo  = encontrar_columna(['Tiempo mantención', 'Tiempo mantencion', 'tiempo total'])
    c_mes     = encontrar_columna(['mes recepción', 'mes recepcion', 'mes'])
    c_año     = encontrar_columna(['Año recepción', 'Año recepcion', 'año'])
    c_equipo  = encontrar_columna(['Equipo'])

    # --- VALIDACIÓN DE SEGURIDAD ---
    columnas_criticas = {"Tipo Mantención": c_manto, "Técnico": c_tecnico, "N° OT": c_ot}
    faltantes = [k for k, v in columnas_criticas.items() if v is None]

    if faltantes:
        st.error(f"❌ No se encontraron las columnas: {', '.join(faltantes)}")
        with st.expander("Ver todas las columnas detectadas en esta hoja"):
            st.write(list(df.columns))
    else:
        # --- FILTROS (SIDEBAR) ---
        st.sidebar.header("⚙️ Filtros")
        
        manto_opciones = sorted(df[c_manto].dropna().unique())
        manto_sel = st.sidebar.multiselect(f"Filtrar {c_manto}", manto_opciones, default=manto_opciones)
        
        tecnico_opciones = sorted(df[c_tecnico].dropna().unique())
        tecnico_sel = st.sidebar.multiselect(f"Filtrar {c_tecnico}", tecnico_opciones, default=tecnico_opciones)

        # Aplicar Filtros
        df_filtrado = df[
            (df[c_manto].isin(manto_sel)) &
            (df[c_tecnico].isin(tecnico_sel))
        ]

        # Conversión numérica de HH y Tiempos
        for c in [c_hh, c_tiempo]:
            if c:
                df_filtrado[c] = pd.to_numeric(df_filtrado[c], errors='coerce').fillna(0)

        # --- FUNCIÓN DE GRÁFICOS ---
        def generar_seccion(titulo, g_col, a_col, func, top=10):
            if not df_filtrado.empty and g_col and a_col:
                st.subheader(titulo)
                resumen = df_filtrado.groupby(g_col)[a_col].agg(func).reset_index()
                resumen.columns = [g_col, 'Valor']
                resumen = resumen.sort_values(by='Valor', ascending=False)
                if top: resumen = resumen.head(top)
                
                c1, c2 = st.columns([2, 1])
                with c1:
                    fig = px.bar(resumen, x=g_col, y='Valor', color='Valor', 
                                 color_continuous_scale='Blues', text_auto='.2f')
                    fig.update_layout(xaxis={'categoryorder':'total descending'}, xaxis_title=None)
                    st.plotly_chart(fig, use_container_width=True)
                with c2:
                    st.info("Hoja de Verificación")
                    st.dataframe(resumen, hide_index=True, use_container_width=True)
                st.divider()

        # --- EJECUCIÓN DE REPORTES ---
        if not df_filtrado.empty:
            generar_seccion("Top 10: Suma de N° OT por Técnico", c_tecnico, c_ot, "count")
            generar_seccion("Top 10: Suma de Horas Hombres por Técnico", c_tecnico, c_hh, "sum")
            generar_seccion("Top 10: Tiempo Mantención Total por Técnico", c_tecnico, c_tiempo, "sum")
            generar_seccion("Top 10: Cantidad de OTs por Equipo/Técnico", c_tecnico, c_ot, "count")
            generar_seccion("Top 10: Promedio Tiempo Mantención por Técnico", c_tecnico, c_tiempo, "mean")
            if c_equipo:
                generar_seccion("Distribución de OT por Tipo de Equipo", c_equipo, c_ot, "count", top=None)
        else:
            st.warning("No hay datos para los filtros seleccionados.")

else:
    st.info("Sube tu archivo Excel para comenzar el análisis.")
