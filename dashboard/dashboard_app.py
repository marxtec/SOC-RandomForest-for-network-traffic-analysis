import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="SOC Dashboard | Network Threat Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CONSTANTES ---
# Para evitar errores de tipeo y facilitar el mantenimiento
COL_TIMESTAMP = "timestamp"
COL_TIPO_SIMULADO = "tipo_simulado"
COL_RESULTADO = "resultado"
COL_PROBABILIDAD = "probabilidad"
VAL_ATAQUE = "Ddos"
VAL_BENIGNO = "Benigno"

# Paleta de colores para consistencia visual
COLOR_MAP = {VAL_ATAQUE: "#EF553B", VAL_BENIGNO: "#636EFA"} # Rojo para ataques, Azul para benignos

# --- CARGA Y PROCESAMIENTO DE DATOS ---
@st.cache_data(ttl=10) # Cache para no recargar el archivo en cada refresh si no ha cambiado
def cargar_y_preprocesar_logs():
    """Carga los logs desde el CSV y realiza una limpieza básica."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    log_path = os.path.join(base_dir, "logs", "traffic_log.csv")
    
    if not os.path.exists(log_path):
        st.error(f"⚠️ El archivo de log no se encontró en la ruta: {log_path}")
        return pd.DataFrame()

    try:
        df = pd.read_csv(log_path)
        # Limpieza y normalización de datos
        df[COL_TIMESTAMP] = pd.to_datetime(df[COL_TIMESTAMP])
        for col in [COL_RESULTADO, COL_TIPO_SIMULADO]:
            if col in df.columns:
                df[col] = df[col].str.strip().str.capitalize()
        
        # Asegurarse de que las columnas clave existen
        required_cols = [COL_TIMESTAMP, COL_TIPO_SIMULADO, COL_RESULTADO, COL_PROBABILIDAD]
        if not all(col in df.columns for col in required_cols):
             st.warning("El archivo CSV no contiene todas las columnas requeridas (timestamp, tipo_simulado, resultado, probabilidad).")
             return pd.DataFrame()

        return df.sort_values(by=COL_TIMESTAMP)
    
    except Exception as e:
        st.error(f"Ocurrió un error al cargar o procesar el archivo de logs: {e}")
        return pd.DataFrame()

# --- FUNCIONES DE VISUALIZACIÓN ---

def mostrar_kpis_generales(df_filtrado):
    """Muestra las métricas principales en tarjetas."""
    total = len(df_filtrado)
    benignos = len(df_filtrado[df_filtrado[COL_RESULTADO] == VAL_BENIGNO])
    ataques = len(df_filtrado[df_filtrado[COL_RESULTADO] == VAL_ATAQUE])
    
    # Preparar la métrica del último resultado con color dinámico
    if not df_filtrado.empty:
        ultimo_resultado = df_filtrado.iloc[-1][COL_RESULTADO]
        color = "red" if ultimo_resultado == VAL_ATAQUE else "green"
        icono = "🚨" if ultimo_resultado == VAL_ATAQUE else "✅"
        ultimo_resultado_display = f"""
        <div style="
            background-color: {'#262730' if ultimo_resultado == VAL_BENIGNO else '#A02C2C'};
            padding: 10px;
            border-radius: 5px;">
            <h3 style="color: white; margin:0;">{icono} {ultimo_resultado}</h3>
        </div>
        """
    else:
        ultimo_resultado_display = "N/A"

    st.subheader("📊 Métricas Generales del Periodo")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Total de Eventos", total)
    col2.metric(f"🛡️ {VAL_BENIGNO} Detectado", benignos)
    col3.metric(f"☠️ {VAL_ATAQUE} Detectado", ataques)
    with col4:
        st.markdown("**Último Evento Clasificado**")
        st.markdown(ultimo_resultado_display, unsafe_allow_html=True)

def mostrar_matriz_confusion_plotly(df_filtrado):
    """Genera y muestra una matriz de confusión interactiva con Plotly."""
    st.subheader("🔬 Matriz de Confusión")
    conf_matrix = pd.crosstab(df_filtrado[COL_TIPO_SIMULADO], df_filtrado[COL_RESULTADO])
    
    # Asegurar que ambas categorías estén presentes para una matriz cuadrada
    all_labels = sorted(list(set(df_filtrado[COL_TIPO_SIMULADO].unique()) | set(df_filtrado[COL_RESULTADO].unique())))
    conf_matrix = conf_matrix.reindex(index=all_labels, columns=all_labels, fill_value=0)

    z = conf_matrix.values
    x = conf_matrix.columns.tolist()
    y = conf_matrix.index.tolist()
    
    # El texto que va dentro de cada celda
    z_text = [[str(y) for y in x] for x in z]

    fig = go.Figure(data=go.Heatmap(
        z=z, x=x, y=y,
        hoverongaps=False,
        text=z_text,
        texttemplate="%{text}",
        colorscale="Blues"
    ))
    fig.update_layout(
        title_text='Real vs. Clasificado',
        xaxis_title='Clasificación del Modelo',
        yaxis_title='Tipo Real Simulado'
    )
    st.plotly_chart(fig, use_container_width=True)


# --- INTERFAZ PRINCIPAL ---

# Título principal
st.title("🛡️ SOC: Network Threat Intelligence Dashboard")

# Auto-refresh (esencial para un SOC)
refresh_interval = st.sidebar.select_slider(
    "Intervalo de Refresco (segundos)",
    options=[5, 10, 30, 60],
    value=10
)
st_autorefresh(interval=refresh_interval * 1000, key="auto-refresh-widget")

# Cargar datos
df_original = cargar_y_preprocesar_logs()

if df_original.empty:
    st.warning("⚠️ No se han encontrado datos de tráfico. Ejecuta el simulador para empezar a poblar el dashboard.")
    st.stop() # Detiene la ejecución del script si no hay datos

# --- BARRA LATERAL (SIDEBAR) ---
st.sidebar.header("Filtros y Controles")

# Filtro de tiempo
min_date = df_original[COL_TIMESTAMP].min().to_pydatetime()
max_date = df_original[COL_TIMESTAMP].max().to_pydatetime()

time_range = st.sidebar.slider(
    "Selecciona un Rango de Tiempo",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD HH:mm"
)

# Filtrar el DataFrame principal según el rango seleccionado
df_filtrado = df_original[
    (df_original[COL_TIMESTAMP] >= time_range[0]) & 
    (df_original[COL_TIMESTAMP] <= time_range[1])
]

# Información del autor en la barra lateral
st.sidebar.markdown("---")
st.sidebar.info("Creado por Dani | Proyecto PACD")
st.sidebar.markdown(f"🕒 **Hora Actual:** `{datetime.now().strftime('%H:%M:%S')}`")

# --- CUERPO PRINCIPAL DEL DASHBOARD ---

if df_filtrado.empty:
    st.warning("⚠️ No hay datos en el rango de tiempo seleccionado.")
else:
    # Mostrar KPIs principales en la parte superior
    mostrar_kpis_generales(df_filtrado)
    st.markdown("---")

    # Organizar contenido en pestañas para una mejor UX
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Resumen de Tráfico", "🎯 Análisis de Rendimiento", "🚨 Alertas Críticas", "📋 Explorador de Datos"])

    with tab1:
        st.header("Evolución y Distribución del Tráfico")
        
        # Gráfico de evolución temporal
        df_temporal = df_filtrado.resample('T', on=COL_TIMESTAMP).size().reset_index(name='cuenta')
        df_temporal_por_tipo = df_filtrado.groupby([pd.Grouper(key=COL_TIMESTAMP, freq='T'), COL_RESULTADO]).size().reset_index(name='cuenta')
        
        fig_line = px.line(
            df_temporal_por_tipo, 
            x=COL_TIMESTAMP, 
            y="cuenta", 
            color=COL_RESULTADO,
            title="Evolución Temporal del Tráfico (Eventos por minuto)",
            color_discrete_map=COLOR_MAP,
            labels={'cuenta': 'Nº de Eventos', COL_TIMESTAMP: 'Tiempo'}
        )
        st.plotly_chart(fig_line, use_container_width=True)

        # Gráficos de distribución
        col1, col2 = st.columns(2)
        with col1:
            fig_pie = px.pie(
                df_filtrado, 
                names=COL_RESULTADO, 
                hole=0.4, 
                title="Distribución de Tráfico Clasificado",
                color=COL_RESULTADO,
                color_discrete_map=COLOR_MAP
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        with col2:
            df_dist_real = df_filtrado[COL_TIPO_SIMULADO].value_counts().reset_index()
            fig_pie_real = px.pie(
                df_dist_real, 
                names='index', 
                values=COL_TIPO_SIMULADO, 
                hole=0.4, 
                title="Distribución de Tráfico Real (Simulado)",
                color='index',
                color_discrete_map=COLOR_MAP
            )
            st.plotly_chart(fig_pie_real, use_container_width=True)


    with tab2:
        st.header("Rendimiento y Confianza del Modelo")
        
        # Métricas de rendimiento
        df_filtrado["match"] = df_filtrado[COL_TIPO_SIMULADO] == df_filtrado[COL_RESULTADO]
        accuracy = df_filtrado["match"].mean()
        
        fp = len(df_filtrado[(df_filtrado[COL_TIPO_SIMULADO] == VAL_BENIGNO) & (df_filtrado[COL_RESULTADO] == VAL_ATAQUE)])
        fn = len(df_filtrado[(df_filtrado[COL_TIPO_SIMULADO] == VAL_ATAQUE) & (df_filtrado[COL_RESULTADO] == VAL_BENIGNO)])
        
        total_reales_benignos = len(df_filtrado[df_filtrado[COL_TIPO_SIMULADO] == VAL_BENIGNO])
        total_reales_ataques = len(df_filtrado[df_filtrado[COL_TIPO_SIMULADO] == VAL_ATAQUE])
        
        fpr = (fp / total_reales_benignos) * 100 if total_reales_benignos > 0 else 0
        fnr = (fn / total_reales_ataques) * 100 if total_reales_ataques > 0 else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("🎯 Accuracy del Clasificador", f"{accuracy * 100:.2f}%")
        col2.metric("❗ Tasa de Falsos Positivos (FPR)", f"{fpr:.2f}%", help="Porcentaje de tráfico benigno clasificado incorrectamente como ataque.")
        col3.metric("❗ Tasa de Falsos Negativos (FNR)", f"{fnr:.2f}%", help="Porcentaje de ataques no detectados (clasificados como benignos).")

        st.markdown("---")
        
        # Matriz de confusión y gráfico de confianza
        col1_perf, col2_perf = st.columns(2)
        with col1_perf:
            mostrar_matriz_confusion_plotly(df_filtrado)
            
        with col2_perf:
            st.subheader("📡 Confianza del Modelo")
            fig_prob = px.scatter(
                df_filtrado, 
                x=COL_TIMESTAMP, 
                y=COL_PROBABILIDAD, 
                color=COL_RESULTADO,
                title="Confianza del Clasificador por Evento",
                color_discrete_map=COLOR_MAP,
                labels={'probabilidad': 'Probabilidad de la Clasificación', 'timestamp': 'Tiempo'}
            )
            st.plotly_chart(fig_prob, use_container_width=True)

    with tab3:
        st.header("Alertas Críticas: Ataques Detectados")
        st.info("Esta sección muestra todos los eventos que han sido clasificados como un ataque DDoS en el periodo seleccionado.")
        
        alertas_df = df_filtrado[df_filtrado[COL_RESULTADO] == VAL_ATAQUE].sort_values(by=COL_TIMESTAMP, ascending=False)
        
        if alertas_df.empty:
            st.success("✅ No se han detectado ataques en el periodo seleccionado.")
        else:
            st.dataframe(
                alertas_df[[COL_TIMESTAMP, COL_TIPO_SIMULADO, COL_RESULTADO, COL_PROBABILIDAD]],
                use_container_width=True,
                # Estilo para la tabla
                hide_index=True
            )

    with tab4:
        st.header("Explorador de Todos los Datos")
        st.info("Aquí puedes ver y buscar en la tabla completa de eventos del periodo seleccionado.")
        
        # Función para colorear filas de ataques
        def highlight_attacks(row):
            color = 'background-color: #A02C2C; color: white;' if row[COL_RESULTADO] == VAL_ATAQUE else ''
            return [color] * len(row)
        
        st.dataframe(
            df_filtrado.sort_values(by=COL_TIMESTAMP, ascending=False).style.apply(highlight_attacks, axis=1),
            use_container_width=True
        )
