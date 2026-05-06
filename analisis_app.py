import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Plataforma de Análisis", layout="wide")

st.title("📊 Plataforma de Análisis de Datos")

# -----------------------------
# CARGA ARCHIVO
# -----------------------------
archivo = st.file_uploader("Sube tu archivo Excel", type=["xlsx"])

if archivo:

    xls = pd.ExcelFile(archivo)
    hojas = xls.sheet_names

    hoja = st.selectbox("Selecciona la hoja", hojas)

    df = pd.read_excel(archivo, sheet_name=hoja)

    st.subheader("Vista previa")
    st.dataframe(df.head())

    # -----------------------------
    # TIPO DE GRÁFICO
    # -----------------------------
    tipo_grafico = st.selectbox(
        "Tipo de gráfico",
        ["Torta", "Histograma Top 10", "Gráfico de Control", "Dispersión"]
    )

    # -----------------------------
    # VARIABLES
    # -----------------------------
    columnas = df.columns.tolist()

    col_x = st.selectbox("Variable principal (X)", columnas)

    operacion = st.selectbox(
        "Operación",
        ["Recuento", "Suma", "Promedio"]
    )

    col_y = None
    if operacion in ["Suma", "Promedio"] or tipo_grafico == "Dispersión":
        col_y = st.selectbox("Variable numérica (Y)", columnas)

    # -----------------------------
    # FILTROS (hasta 5)
    # -----------------------------
    st.subheader("Filtros")

    df_filtrado = df.copy()

    for i in range(5):
        usar_filtro = st.checkbox(f"Usar filtro {i+1}", key=f"filtro_{i}")

        if usar_filtro:
            col_filtro = st.selectbox(
                f"Columna filtro {i+1}",
                columnas,
                key=f"col_{i}"
            )

            valores_filtro = df[col_filtro].dropna().astype(str).unique()

            val_filtro = st.selectbox(
                f"Valor filtro {i+1}",
                valores_filtro,
                key=f"val_{i}"
            )

            df_filtrado = df_filtrado[
                df_filtrado[col_filtro].astype(str) == val_filtro
            ]

    # -----------------------------
    # PROCESAMIENTO
    # -----------------------------
    if st.button("Generar gráfico"):

        if operacion == "Recuento":
            data = df_filtrado.groupby(col_x).size().reset_index(name="valor")

        elif operacion == "Suma":
            data = df_filtrado.groupby(col_x)[col_y].sum().reset_index(name="valor")

        elif operacion == "Promedio":
            data = df_filtrado.groupby(col_x)[col_y].mean().reset_index(name="valor")

        # ordenar
        data = data.sort_values("valor", ascending=False)

        # top 10 para histograma
        if tipo_grafico == "Histograma Top 10":
            data = data.head(10)

        # -----------------------------
        # GRAFICAR
        # -----------------------------
        fig, ax = plt.subplots()

        if tipo_grafico == "Torta":
            ax.pie(data["valor"], labels=data[col_x], autopct="%1.1f%%")

        elif tipo_grafico == "Histograma Top 10":
            ax.barh(data[col_x].astype(str), data["valor"])
            ax.invert_yaxis()

        elif tipo_grafico == "Gráfico de Control":
            ax.plot(data[col_x].astype(str), data["valor"], marker="o")

        elif tipo_grafico == "Dispersión":
            ax.scatter(df_filtrado[col_x], df_filtrado[col_y])

        ax.set_title("Resultado del análisis")

        st.pyplot(fig)

        # -----------------------------
        # TABLA RESULTADO
        # -----------------------------
        st.subheader("Datos utilizados")
        st.dataframe(data)