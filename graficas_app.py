import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Mantenimiento", layout="wide")

st.title("📊 Dashboard de Gestión de Mantenimiento")

# --- CARGA DE ARCHIVO ---
archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo:
    # 1. Obtener nombres de las hojas
    xls = pd.ExcelFile(archivo)
    hoja_seleccionada = st.selectbox("1. Selecciona la hoja de datos", xls.sheet_names)
    
    # 2. Leer la hoja elegida
    df = pd.read_excel(archivo, sheet_name=hoja_seleccionada)

    # --- SECCIÓN DE PREVISUALIZACIÓN ---
    st.header("🔍 Previsualización de Datos")
    st.write(f"Hoja actual: **{hoja_seleccionada}** | Columnas detectadas: **{len(df.columns)}**")
    st.dataframe(df.head(10)) 
    
    with st.expander("Ver nombres exactos de las columnas en esta hoja"):
        st.write(list(df.columns))
    st.divider()

    # --- CONFIGURACIÓN DE NOMBRES ESPECÍFICOS ---
    # Definimos los nombres exactos que debe buscar el código
    COL_MANTO = "Tipo de mantención"
    COL_TECNICO = "Nombre Técnico"
    COL_OT = "N°OT"
    COL_HH = "Horas Hombres"
    COL_TIEMPO = "Tiempo mantención"
    COL_EQUIPO = "Equipo"
    COL_MES = "mes recepción"
    COL_AÑO = "Año recepción"

    # --- VALIDACIÓN DE EXISTENCIA ---
    nombres_requeridos = [COL_MANTO, COL_TECNICO, COL_OT, COL_HH, COL_TIEMPO]
    faltantes = [col for col in nombres_requeridos if col not in df.columns]

    if faltantes:
        st.error(f"❌ No se encontraron las columnas exactas: {faltantes}")
        st.info("Asegúrate de que la hoja seleccionada sea la correcta y que los nombres coincidan letra por letra.")
    else:
        # --- FILTROS (SIDEBAR) ---
        st.sidebar.header("⚙️ Filtros")
        
        # Filtros con nombres específicos
        manto_opciones = sorted(df[COL_MANTO].dropna().unique())
        manto_sel = st.sidebar.multiselect(f"Filtrar {COL_MANTO}", manto_opciones, default=manto_opciones)
        
        tecnico_opciones = sorted(df[COL_TECNICO].dropna().unique())
        tecnico_sel = st.sidebar.multiselect(f"Filtrar {COL_TECNICO}", tecnico_opciones, default=tecnico_opciones)

        # Aplicar Filtros
        df_filtrado = df[
            (df[COL_MANTO].isin(manto_sel)) &
            (df[COL_TECNICO].isin(tecnico_sel))
        ].copy()

        # Conversión numérica de columnas de cálculo
        for c in [COL_HH, COL_TIEMPO]:
            df_filtrado[c] = pd.to_numeric(df_filtrado[c], errors='coerce').fillna(0)

        # --- FUNCIÓN DE GRÁFICOS ---
        def generar_seccion(titulo, g_col, a_col, func, top=10):
            if not df_filtrado.empty:
                st.subheader(titulo)
                # Agrupación
                resumen = df_filtrado.groupby(g_col)[a_col].agg(func).reset_index()
                resumen.columns = [g_col, 'Valor']
                resumen = resumen.sort_values(by='Valor', ascending=False)
                
                if top:
                    resumen = resumen.head(top)
                
                c1, c2 = st.columns([2, 1])
                with c1:
                    fig = px.bar(resumen, x=g_col, y='Valor', color='Valor', 
                                 color_continuous_scale='Blues', text_auto='.2f')
                    fig.update_layout(xaxis={'categoryorder':'total descending'}, xaxis_title=None)
                    st.plotly_chart(fig, use_container_width=True)
                with c2:
                    st.write("**Datos del reporte**")
                    st.dataframe(resumen, hide_index=True, use_container_width=True)
                st.divider()

        # --- RENDERIZADO DE REPORTES ---
        if not df_filtrado.empty:
            generar_seccion("Top 10: Cantidad de OT por Técnico", COL_TECNICO, COL_OT, "count")
            generar_seccion("Top 10: Suma de Horas Hombres por Técnico", COL_TECNICO, COL_HH, "sum")
            generar_seccion("Top 10: Tiempo Mantención Total por Técnico", COL_TECNICO, COL_TIEMPO, "sum")
            generar_seccion("Top 10: Promedio Tiempo Mantención por Técnico", COL_TECNICO, COL_TIEMPO, "mean")
            
            if COL_EQUIPO in df.columns:
                generar_seccion("Distribución de OT por Tipo de Equipo", COL_EQUIPO, COL_OT, "count", top=None)
        else:
            st.warning("No hay datos que coincidan con los filtros seleccionados.")

else:
    st.info("Sube tu archivo Excel para comenzar.")
