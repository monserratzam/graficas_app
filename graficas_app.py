import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Mantenimiento", layout="wide")

st.title("📊 Dashboard de Gestión de Mantenimiento")
st.markdown("---")

archivo = st.file_uploader("Sube tu archivo Excel homologado", type=["xlsx"])

if archivo:
    # 1. Leer el archivo
    df = pd.read_excel(archivo)

    # 2. RENOMBRADO FORZOSO POR POSICIÓN
    # No importa cómo se llamen en Excel, nosotros les daremos el nombre correcto
    # según el orden que me pasaste (25 columnas en total)
    nuevos_nombres = [
        "Estado UEM", "Servicio o Unidad", "Equipo", "Marca", "Modelo", 
        "Fecha recepcion OT", "mes recepción", "Año recepción", "N°OT", 
        "Clasificación", "Tipo de mantención", "Trabajo realizado en", 
        "Fecha de asignación", "Mes asignación", "Año asignación", 
        "Nombre Técnico", "Cambio de Repuesto", "Horas Hombres", 
        "Fecha Termino", "Mes término", "Año término", "Trabajo Conforme", 
        "Tiempo asignación", "Tiempo mantención", "Tiempo total"
    ]

    # Solo renombramos si el número de columnas coincide o es cercano
    if len(df.columns) >= len(nuevos_nombres):
        df.columns = nuevos_nombres[:len(df.columns)]
    else:
        st.error(f"El Excel tiene {len(df.columns)} columnas, pero se esperaban al menos {len(nuevos_nombres)}.")
        st.stop()

    # 3. CONVERSIÓN NUMÉRICA SEGURA
    cols_a_numero = ["Horas Hombres", "Tiempo mantención", "Año recepción"]
    for c in cols_a_numero:
        df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

    # --- FILTROS (SIDEBAR) ---
    st.sidebar.header("⚙️ Filtros de Reporte")
    
    # Ahora usamos los nombres que NOSOTROS asignamos, eliminando el KeyError
    manto_opciones = sorted(df["Tipo de mantención"].dropna().unique())
    manto_sel = st.sidebar.multiselect("Tipo de mantención", manto_opciones, default=manto_opciones)
    
    tecnico_opciones = sorted(df["Nombre Técnico"].dropna().unique())
    tecnico_sel = st.sidebar.multiselect("Nombre Técnico", tecnico_opciones, default=tecnico_opciones)
    
    año_opciones = sorted(df["Año recepción"].unique())
    año_sel = st.sidebar.multiselect("Año recepción", año_opciones, default=año_opciones)
    
    mes_opciones = df["mes recepción"].dropna().unique().tolist()
    mes_sel = st.sidebar.multiselect("mes recepción", mes_opciones, default=mes_opciones)

    # --- APLICACIÓN DE FILTROS ---
    df_filtrado = df[
        (df["Tipo de mantención"].isin(manto_sel)) &
        (df["Nombre Técnico"].isin(tecnico_sel)) &
        (df["Año recepción"].isin(año_sel)) &
        (df["mes recepción"].isin(mes_sel))
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

    # --- RENDERIZADO ---
    if not df_filtrado.empty:
        generar_grafico("Top 10: Cantidad de OT por Técnico", "Nombre Técnico", "N°OT", "count")
        generar_grafico("Top 10: Suma de Horas Hombres por Técnico", "Nombre Técnico", "Horas Hombres", "sum")
        generar_grafico("Top 10: Tiempo Mantención Total por Técnico", "Nombre Técnico", "Tiempo mantención", "sum")
        generar_grafico("Top 10: Cantidad de OTs por Equipo para cada Técnico", "Nombre Técnico", "N°OT", "count")
        generar_grafico("Top 10: Promedio Tiempo Mantención por OT", "Nombre Técnico", "Tiempo mantención", "mean")
        generar_grafico("Distribución de OT por Tipo de Equipo", "Equipo", "N°OT", "count", top=None)
    else:
        st.warning("Selecciona criterios en los filtros para visualizar los datos.")

else:
    st.info("Sube tu archivo Excel para iniciar el análisis.")
