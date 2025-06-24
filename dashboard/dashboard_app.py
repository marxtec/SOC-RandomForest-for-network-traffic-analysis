import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go # Usaremos esto para gráficos más personalizados

# --- 1. CONFIGURACIÓN INICIAL Y ESTILO (LA CLAVE DEL LOOK & FEEL) ---

# Configuración de la página: layout ancho y título.
st.set_page_config(page_title="SOC Dashboard", layout="wide", initial_sidebar_state="expanded")

# CSS personalizado para replicar el look del SOC.
# Lo inyectamos con st.markdown. Este es el "secreto" para el diseño.
st.markdown("""
<style>
    /* Cambia el color de fondo principal */
    .main {
        background-color: #0E1117;
    }
    /* Estilo para las "tarjetas" o contenedores */
    .st-emotion-cache-1r6slb0, .st-emotion-cache-1aehpvj {
        background-color: #161A25; /* Color de fondo de la tarjeta */
        border: 1px solid #2A3146; /* Borde sutil */
        border-radius: 10px; /* Bordes redondeados */
        padding: 20px;
    }
    /* Estilo para las métricas de Streamlit */
    .st-emotion-cache-1tpl0xr p {
        font-size: 1rem; /* Tamaño de la etiqueta de la métrica */
    }
    .st-emotion-cache-1tpl0xr div[data-testid="stMetricValue"] {
        font-size: 2.5rem; /* Tamaño del valor de la métrica */
        color: #FFFFFF; /* Color blanco para el valor */
    }
    /* Ocultar la decoración de los gráficos de Plotly */
    .stPlotlyChart {
        border-radius: 10px;
        overflow: hidden;
    }
    /* Títulos de las secciones */
    h2 {
        color: #FFFFFF;
        border-bottom: 2px solid #2A3146;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)


# --- 2. BARRA LATERAL (SIDEBAR) PARA NAVEGACIÓN Y CONTROLES ---

with st.sidebar:
    st.title("🛡️ SOC Dashboard")
    st.caption("Creado por Dani | Proyecto PACD")
    
    # Podrías agregar filtros aquí, como un selector de fecha
    # date_filter = st.date_input("Seleccionar rango de fechas")
    
    st.markdown("---")
    st.markdown(f"🕒 **Hora actual:** {datetime.now().strftime('%H:%M:%S')}")
    # El autorefresh es útil para producción
    # from streamlit_autorefresh import st_autorefresh
    # st_autorefresh(interval=15000, key="auto-refresh")


# --- 3. CARGA DE DATOS (SIN CAMBIOS, TU FUNCIÓN ES CORRECTA) ---

# Obtener ruta absoluta
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
log_path = os.path.join(BASE_DIR, "logs", "traffic_log.csv")

def cargar_logs():
    if os.path.exists(log_path):
        df = pd.read_csv(log_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["resultado"] = df["resultado"].str.strip().str.capitalize()
        df["tipo_simulado"] = df["tipo_simulado"].str.strip().str.capitalize()
        return df
    else:
        # Creamos un DataFrame de ejemplo si no hay datos
        return pd.DataFrame({
            "timestamp": [], "tipo_simulado": [], "resultado": [], "probabilidad": []
        })

df = cargar_logs()

# --- 4. CUERPO PRINCIPAL DEL DASHBOARD ---

st.header("SOC Monitoring Summary")
st.markdown("Resumen general de la actividad de red en tiempo real.")

if df.empty:
    st.warning("⚠️ Aún no hay tráfico clasificado. Corre el simulador para comenzar.")
else:
    # --- MÉTRICAS PRINCIPALES (KPIs) ---
    total_procesados = len(df)
    benignos = len(df[df["resultado"] == "Benigno"])
    ataques_ddos = len(df[df["resultado"] == "Ddos"])
    # Asumimos que tienes 'Malicioso' y 'Benigno' como tipos simulados
    tipos_reales = df["tipo_simulado"].unique()
    total_reales_benignos = len(df[df["tipo_simulado"] == "Benigno"])
    total_reales_maliciosos = len(df[(df["tipo_simulado"] == "Malicioso") | (df["tipo_simulado"] == "Ddos")])
    
    # Usamos columnas para organizar las métricas como en el ejemplo
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📦 Total de Eventos", total_procesados)
    with col2:
        st.metric("🛡️ Tráfico Benigno", benignos)
    with col3:
        st.metric("☠️ Alertas de Ataque", ataques_ddos)
    with col4:
        accuracy = (df["tipo_simulado"] == df["resultado"]).mean()
        st.metric("🎯 Precisión del Modelo", f"{accuracy:.2%}")

    st.markdown("<br>", unsafe_allow_html=True) # Espacio vertical

    # --- VISUALIZACIONES EN TARJETAS ---
    col_a, col_b = st.columns(2)

    with col_a:
        with st.container(border=True):
            st.subheader("Alertas por Tipo")
            # Gráfico de dona (pie con un agujero)
            fig_pie = px.pie(df, names="resultado", hole=0.6,
                             title="Distribución de Tráfico Clasificado",
                             color_discrete_map={"Benigno": "#2ECC71", "Ddos": "#E74C3C"})
            fig_pie.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend_title_text=''
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with col_b:
        with st.container(border=True):
            st.subheader("Tendencia de Detección")
            df["minuto"] = df["timestamp"].dt.floor('T') # Agrupar por minuto
            detecciones_por_minuto = df.groupby(['minuto', 'resultado']).size().reset_index(name='cuenta')
            fig_line = px.line(detecciones_por_minuto, x='minuto', y='cuenta', color='resultado',
                               title="Evolución de Detecciones por Minuto",
                               color_discrete_map={"Benigno": "#2ECC71", "Ddos": "#E74C3C"})
            fig_line.update_layout(
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis_title="Tiempo",
                yaxis_title="Número de Eventos"
            )
            st.plotly_chart(fig_line, use_container_width=True)
            
    st.markdown("<br>", unsafe_allow_html=True)

    # --- MATRIZ DE CONFUSIÓN Y ERRORES ---
    col_c, col_d = st.columns([0.4, 0.6]) # Damos más espacio a la tabla

    with col_c:
        with st.container(border=True):
            st.subheader("Análisis de Precisión")
            conf_matrix = pd.crosstab(df["tipo_simulado"], df["resultado"])
            
            # Usar Plotly para la matriz de confusión para mantener el estilo
            fig_heatmap = go.Figure(data=go.Heatmap(
                z=conf_matrix.values,
                x=conf_matrix.columns,
                y=conf_matrix.index,
                colorscale="Blues",
                text=conf_matrix.values,
                texttemplate="%{text}"
            ))
            fig_heatmap.update_layout(
                title="Matriz de Confusión",
                xaxis_title="Predicción del Modelo",
                yaxis_title="Tipo Real",
                template="plotly_dark",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_heatmap, use_container_width=True)

            # Métricas de error
            fp = conf_matrix.loc['Benigno', 'Ddos'] if 'Benigno' in conf_matrix.index and 'Ddos' in conf_matrix.columns else 0
            fn = conf_matrix.loc['Ddos', 'Benigno'] if 'Ddos' in conf_matrix.index and 'Benigno' in conf_matrix.columns else 0
            
            st.metric("❗ Falsos Positivos (FP)", fp)
            st.metric("❗ Falsos Negativos (FN)", fn)

    # --- TABLA DE EVENTOS RECIENTES ---
    with col_d:
        with st.container(border=True):
            st.subheader("📋 Últimos Eventos Registrados")
            st.dataframe(df.sort_values(by="timestamp", ascending=False).head(20),
                         use_container_width=True,
                         height=550) # Ajustar altura para que quepa bien
