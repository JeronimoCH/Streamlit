import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# Configuración de la página
st.set_page_config(page_title="Panel Académico", page_icon="🎓", layout="wide")

st.title("🎓 Análisis Interactivo de Promedios Académicos")
st.markdown("Esta aplicación simula datos de estudiantes, realiza un análisis cuantitativo y muestra visualizaciones dinámicas basadas en las interacciones del usuario.")

# 1. Simulación de Datos
@st.cache_data
def generar_datos(num_estudiantes=500):
    np.random.seed(42)  # Para resultados reproducibles
    
    carreras = ["Ingeniería", "Medicina", "Derecho", "Arquitectura", "Administración", "Diseño"]
    
    # Generar calificaciones (escala 0.0 a 5.0, típica en Colombia)
    promedios = np.random.normal(loc=3.4, scale=0.8, size=num_estudiantes)
    promedios = np.clip(promedios, 0.0, 5.0)
    
    datos = {
        "ID_Estudiante": [f"EST-{i:04d}" for i in range(1, num_estudiantes + 1)],
        "Carrera": np.random.choice(carreras, num_estudiantes),
        "Semestre": np.random.randint(1, 11, num_estudiantes),
        "Promedio": np.round(promedios, 2),
        "Créditos_Aprobados": np.random.randint(20, 160, num_estudiantes)
    }
    return pd.DataFrame(datos)

df = generar_datos()

# --- INTERACCIÓN DINÁMICA (BARRA LATERAL) ---
st.sidebar.header("⚙️ Filtros Dinámicos")

# Filtro por carrera
carreras_disponibles = df["Carrera"].unique()
carreras_seleccionadas = st.sidebar.multiselect(
    "Seleccionar Carrera(s)", 
    options=carreras_disponibles, 
    default=carreras_disponibles
)

# Filtro por rango de promedios
rango_promedio = st.sidebar.slider(
    "Rango de Promedio", 
    min_value=0.0, 
    max_value=5.0, 
    value=(0.0, 5.0), 
    step=0.1
)

# Filtro interactivo de nota aprobatoria
nota_aprobatoria = st.sidebar.number_input(
    "Definir Nota Mínima Aprobatoria", 
    min_value=0.0, 
    max_value=5.0, 
    value=3.0, 
    step=0.1
)

# Aplicar filtros
df_filtrado = df[
    (df["Carrera"].isin(carreras_seleccionadas)) & 
    (df["Promedio"] >= rango_promedio[0]) & 
    (df["Promedio"] <= rango_promedio[1])
].copy()

# Determinar estado académico basado en la interacción
df_filtrado["Estado"] = np.where(df_filtrado["Promedio"] >= nota_aprobatoria, "Aprobado", "Reprobado")

# 2. Análisis Cuantitativo
st.header("📊 Análisis Cuantitativo")

if df_filtrado.empty:
    st.warning("⚠️ No hay datos que coincidan con los filtros seleccionados. Ajusta los parámetros en la barra lateral.")
else:
    # Métricas principales
    col1, col2, col3, col4 = st.columns(4)
    
    total_estudiantes = len(df_filtrado)
    promedio_global = df_filtrado["Promedio"].mean()
    aprobados = len(df_filtrado[df_filtrado["Estado"] == "Aprobado"])
    tasa_aprobacion = (aprobados / total_estudiantes) * 100
    
    col1.metric("Total de Estudiantes", f"{total_estudiantes:,}")
    col2.metric("Promedio Global", f"{promedio_global:.2f}")
    col3.metric("Tasa de Aprobación", f"{tasa_aprobacion:.1f}%")
    col4.metric("Mejor Promedio", f"{df_filtrado['Promedio'].max():.2f}")

    # Mostrar tabla de datos
    with st.expander("Ver Datos Detallados (Simulación)"):
        st.dataframe(
            df_filtrado.style.applymap(
                lambda x: 'color: green' if x == 'Aprobado' else 'color: red', 
                subset=['Estado']
            ),
            use_container_width=True
        )

    # 3. Análisis Gráfico
    st.header("📈 Análisis Gráfico")
    
    tab1, tab2, tab3 = st.tabs(["Distribución de Promedios", "Comparativa por Carrera", "Dispersión Semestral"])
    
    with tab1:
        st.subheader("Distribución General de Promedios")
        fig_hist = px.histogram(
            df_filtrado, 
            x="Promedio", 
            color="Estado",
            nbins=20,
            color_discrete_map={"Aprobado": "#2ecc71", "Reprobado": "#e74c3c"},
            title=f"Histograma de Promedios (Nota de corte: {nota_aprobatoria})",
            labels={"Promedio": "Promedio Académico", "count": "Cantidad de Estudiantes"}
        )
        fig_hist.add_vline(x=nota_aprobatoria, line_dash="dash", line_color="black", annotation_text="Corte")
        st.plotly_chart(fig_hist, use_container_width=True)

    with tab2:
        st.subheader("Desempeño Medio por Carrera")
        # Preparar datos agregados
        df_agrupado = df_filtrado.groupby("Carrera")["Promedio"].mean().reset_index().sort_values("Promedio", ascending=False)
        fig_bar = px.bar(
            df_agrupado, 
            x="Carrera", 
            y="Promedio", 
            color="Carrera",
            title="Promedio Académico Medio según Carrera",
            text_auto='.2f'
        )
        fig_bar.update_yaxes(range=[0, 5])
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab3:
        st.subheader("Relación: Avance Semestral vs Promedio")
        fig_scatter = px.scatter(
            df_filtrado, 
            x="Semestre", 
            y="Promedio", 
            color="Estado",
            size="Créditos_Aprobados",
            color_discrete_map={"Aprobado": "#2ecc71", "Reprobado": "#e74c3c"},
            hover_name="ID_Estudiante",
            hover_data=["Carrera"],
            title="Dispersión por Semestre (El tamaño indica créditos aprobados)"
        )
        # Añadir una línea de tendencia (OLS) opcional global
        fig_scatter_trend = px.scatter(
            df_filtrado, x="Semestre", y="Promedio", trendline="ols", title="Tendencia General: Semestre vs Promedio"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
app.py
Mostrando app.py.
