import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Mantenimiento", layout="wide")

st.title("📊 Dashboard con Inspección de Datos")

archivo = st.file_uploader("Sube tu archivo Excel homologado", type=["xlsx"])

if archivo:
    # 1. Carga inicial
    df = pd.read_excel(archivo)
    
    # --- SECCIÓN DE PREVISUALIZACIÓN Y DIAGNÓSTICO ---
    st.header("🔍 Diagnóstico de Estructura")
    col_diag1, col_diag2 = st.columns(2)
    
    with col_diag1:
        st.write(f"**Total de columnas detectadas:** {len(df.columns)}")
        # Creamos un mapa de indices para que el usuario vea la ubicación real
        mapa_columnas = pd.DataFrame({
            "Índice (Posición)": range(len(df.columns)),
            "Nombre detectado": df.columns
        })
        st.dataframe(mapa_columnas, height=300)

    with col_diag2:
        st.write("**Previsualización de los primeros datos:**")
        st.dataframe(df.head(5))

    st.divider()

    # --- CONFIGURACIÓN DE UBICACIÓN ---
    # Si tu Excel tiene 23 o 25 columnas, aquí definimos cuál es cuál por su posición (empezando en 0)
    # Según tu lista, estas serían las posiciones estándar:
    try:
        # Usamos .iloc para referenciar por posición y evitar el KeyError de nombres
        # Ajusta estos números si en el diagnóstico ves que están movidos
        idx_equipo = 2
        idx_mes = 6
        idx_año = 7
        idx_ot = 8
        idx_tipo_manto = 10
        idx_tecnico = 15
        idx_hh = 17
        idx_tiempo_manto = 23

        # Creamos variables con los nombres REALES que detectó pandas en esas posiciones
        col_manto = df.columns[idx_tipo_manto]
        col_tecnico = df.columns[idx_tecnico]
        col_ot = df.columns[idx_ot]
        col_hh = df.columns[idx_hh]
        col_tiempo = df.columns[idx_tiempo_manto]
        col_año = df.columns[idx_año]
        col_mes = df.columns[idx_mes]
        col_equipo = df.columns[idx_equipo]

        # --- FILTROS ---
        st.sidebar.header("⚙️ Filtros")
        
        # Limpieza de nulos para los filtros
        manto_opciones = sorted(df[col_manto].dropna().unique())
        manto_sel = st.sidebar.multiselect(f"Filtrar {col_manto}", manto_opciones, default=manto_opciones)
        
        tecnico_opciones = sorted(df[col_tecnico].dropna().unique())
        tecnico_sel = st.sidebar.multiselect(f"Filtrar {col_tecnico}", tecnico_opciones, default=tecnico_opciones)

        # Aplicar Filtro
        df_filtrado = df[
            (df[col_manto].isin(manto_sel)) &
            (df[col_tecnico].isin(tecnico_sel))
        ]

        # --- CONVERSIÓN NUMÉRICA ---
        for c in [col_hh, col_tiempo, col_año]:
            df_filtrado[c] = pd.to_numeric(df_filtrado[c], errors='coerce').fillna(0)

        # --- FUNCIÓN DE GRÁFICOS ---
        def graficar_seccion(titulo, g_col, a_col, func, top=10):
            if not df_filtrado.empty:
                st.subheader(titulo)
                resumen = df_filtrado.groupby(g_col)[a_col].agg(func).reset_index()
                resumen.columns = [g_col, 'Valor']
                resumen = resumen.sort_values(by='Valor', ascending=False)
                if top: resumen = resumen.head(top)
                
                c1, c2 = st.columns([2, 1])
                with c1:
                    fig = px.bar(resumen, x=g_col, y='Valor', color='Valor', text_auto='.2f')
                    fig.update_layout(xaxis={'categoryorder':'total descending'}, xaxis_title=None)
                    st.plotly_chart(fig, use_container_width=True)
                with c2:
                    st.write("**Datos del gráfico**")
                    st.dataframe(resumen, hide_index=True)
                st.markdown("---")

        # --- RENDERIZADO ---
        if not df_filtrado.empty:
            graficar_seccion("Top 10: Cantidad de OT por Técnico", col_tecnico, col_ot, "count")
            graficar_seccion("Top 10: Suma de HH por Técnico", col_tecnico, col_hh, "sum")
            graficar_seccion("Top 10: Tiempo Mantención Total por Técnico", col_tecnico, col_tiempo, "sum")
            graficar_seccion("Top 10: Promedio Tiempo Mantención por Técnico", col_tecnico, col_tiempo, "mean")
            graficar_seccion("OT por Tipo de Equipo", col_equipo, col_ot, "count", top=None)
        else:
            st.warning("No hay datos para los filtros seleccionados.")

    except IndexError:
        st.error("❌ El archivo no tiene suficientes columnas para las posiciones configuradas.")
        st.info("Revisa la tabla de diagnóstico arriba para ver cuántas columnas cargó realmente Streamlit.")

else:
    st.info("Sube tu archivo Excel para iniciar el diagnóstico y análisis.")
