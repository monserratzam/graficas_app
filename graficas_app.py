import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Mantenimiento", layout="wide")

st.title("📊 Dashboard de Gestión de Mantenimiento")

# --- CARGA DE DATOS ---
archivo = st.file_uploader("Sube tu archivo Excel homologado", type=["xlsx"])

if archivo:
    # Leer el archivo (sin renombrar nada aún)
    df = pd.read_excel(archivo)
    
    # --- DIAGNÓSTICO VISUAL ---
    st.subheader("🔍 Inspección de Datos Cargados")
    col_info, col_prev = st.columns([1, 2])
    
    with col_info:
        st.write(f"**Columnas detectadas:** {len(df.columns)}")
        # Mostramos la tabla de índices para que verifiques si coinciden con tu lista
        inspeccion = pd.DataFrame({"Índice": range(len(df.columns)), "Nombre en Excel": df.columns})
        st.dataframe(inspeccion, height=250)

    with col_prev:
        st.write("**Vista previa (Primeras 5 filas):**")
        st.dataframe(df.head(5))

    # --- CONFIGURACIÓN POR UBICACIÓN (ÍNDICES) ---
    # Usamos exactamente la lista que me pasaste:
    try:
        # Mapeo según tu lista numerada
        idx_equipo       = 0
        idx_mes_rec      = 4
        idx_año_rec      = 5
        idx_ot           = 6
        idx_tipo_manto   = 8  # "Tipo de mantención"
        idx_nombre_tec   = 13 # "Nombre Técnico"
        idx_hh           = 15 # "Horas Hombres"
        idx_tiempo_manto = 21 # "Tiempo mantención"

        # Extraemos los nombres REALES que Pandas leyó en esas posiciones
        col_manto   = df.columns[idx_tipo_manto]
        col_tecnico = df.columns[idx_nombre_tec]
        col_ot      = df.columns[idx_ot]
        col_hh      = df.columns[idx_hh]
        col_tiempo  = df.columns[idx_tiempo_manto]
        col_año     = df.columns[idx_año_rec]
        col_equipo  = df.columns[idx_equipo]

        # --- FILTROS (SIDEBAR) ---
        st.sidebar.header("⚙️ Filtros de Reporte")
        
        manto_opciones = sorted(df[col_manto].dropna().unique())
        manto_sel = st.sidebar.multiselect(f"Seleccionar {col_manto}", manto_opciones, default=manto_opciones)
        
        tecnico_opciones = sorted(df[col_tecnico].dropna().unique())
        tecnico_sel = st.sidebar.multiselect(f"Seleccionar {col_tecnico}", tecnico_opciones, default=tecnico_opciones)

        # Aplicar Filtro al DataFrame
        df_filtrado = df[
            (df[col_manto].isin(manto_sel)) &
            (df[col_tecnico].isin(tecnico_sel))
        ]

        # Convertir a número para cálculos (HH y Tiempos)
        for c in [col_hh, col_tiempo]:
            df_filtrado[c] = pd.to_numeric(df_filtrado[c], errors='coerce').fillna(0)

        # --- FUNCIÓN DE GRÁFICOS ---
        def generar_seccion(titulo, g_col, a_col, func, top=10):
            if not df_filtrado.empty:
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

        # --- GENERACIÓN DE LOS 6 REPORTES ---
        if not df_filtrado.empty:
            generar_seccion("Top 10: Suma de N° OT por Técnico", col_tecnico, col_ot, "count")
            generar_seccion("Top 10: Suma de Horas Hombres por Técnico", col_tecnico, col_hh, "sum")
            generar_seccion("Top 10: Tiempo Mantención Total por Técnico", col_tecnico, col_tiempo, "sum")
            generar_seccion("Top 10: Cantidad de OTs por Equipo/Técnico", col_tecnico, col_ot, "count")
            generar_seccion("Top 10: Promedio Tiempo Mantención por OT", col_tecnico, col_tiempo, "mean")
            generar_seccion("Distribución de OT por Tipo de Equipo", col_equipo, col_ot, "count", top=None)
        else:
            st.warning("No hay datos para los filtros seleccionados.")

    except IndexError:
        st.error("❌ El archivo no tiene la cantidad de columnas esperada.")
        st.info("Verifica en la tabla de inspección si la columna 'Tipo de mantención' realmente está en la posición 8.")

else:
    st.info("Sube tu archivo Excel para iniciar el análisis.")
