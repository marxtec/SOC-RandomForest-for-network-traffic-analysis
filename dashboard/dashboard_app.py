import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# --- 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILO ---
st.set_page_config(
    page_title="SOC Operations Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INYECCIÓN DE CSS PERSONALIZADO (LA MAGIA VISUAL) ---
st.markdown("""
<style>
    /* Tema oscuro principal */
    [data-testid="stAppViewContainer"] > .main {
        background-color: #0E1117;
    }
    /* Estilo para las tarjetas (contenedores) */
    .st-emotion-cache-1r6slb0 { /* Clase común para contenedores en Streamlit > 1.30 */
        background-color: #161A25;
        border: 1px solid #2A3146;
        border-radius: 10px;
        padding: 25px !important; /* Usar !important si es necesario para anular estilos */
    }
    [data-testid="stVerticalBlock"] > [data-testid="stHorizontalBlock"] > [data-testid="stVerticalBlock"] {
        background-color: #161A25;
        border: 1px solid #2A3146;
        border-radius: 10px;
        padding: 25px;
    }
    /* Títulos de las tarjetas */
    h3 {
        color: #FFFFFF;
        font-weight: bold;
        margin-bottom: 10px;
    }
    /* Estilo para las métricas de Streamlit */
    [data-testid="stMetric"] {
        background-color: #0E1117; /* Fondo ligeramente diferente para métricas */
        border: 1px solid #2A3146;
        border-radius: 10px;
        padding: 10px;
    }
    [data-testid="stMetricLabel"] {
        color: #A0AEC0; /* Gris claro para las etiquetas */
    }
    [data-testid="stMetricValue"] {
        color: #FFFFFF; /* Blanco brillante para el valor */
        font-size: 2.2rem;
    }
    /* Estilo para la barra lateral */
    [data-testid="stSidebar"] {
        background-color: #161A25;
    }
</style>
""", unsafe_allow_html=True)


# --- 2. GENERACIÓN DE DATOS DE EJEMPLO (SI ES NECESARIO) ---
def generate_dummy_data(num_records=500):
    """Genera un DataFrame realista si no existe un log."""
    now = datetime.now()
    timestamps = [now - timedelta(minutes=i * 5) for i in range(num_records)]
    
    event_names = ["Traffic to Malware C2", "Port Scan Detected", "Anomalous Login", "SQL Injection Attempt", "Device stopped sending logs"]
    severities = ["Low", "Medium", "High", "Critical"]
    statuses = ["New", "In Progress", "Triaged", "Escalated"]
    categories = ["Malware", "Recon", "Access", "Attack", "Logging"]
    source_ips = [f"10.1.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}" for _ in range(num_records)]
    dest_ips = [f"148.81.{np.random.randint(1, 255)}.{np.random.randint(1, 255)}" for _ in range(num_records)]

    data = {
        "timestamp": np.random.choice(timestamps, num_records),
        "event_id": range(34000, 34000 + num_records),
        "event_name": np.random.choice(event_names, num_records, p=[0.3, 0.2, 0.2, 0.2, 0.1]),
        "severity": np.random.choice(severities, num_records, p=[0.4, 0.3, 0.2, 0.1]),
        "status": np.random.choice(statuses, num_records, p=[0.5, 0.2, 0.2, 0.1]),
        "category": np.random.choice(categories, num_records, p=[0.3, 0.2, 0.2, 0.2, 0.1]),
        "source_ip": source_ips,
        "destination_ip": dest_ips
    }
    return pd.DataFrame(data).sort_values("timestamp", ascending=False)

# --- 3. CARGA DE DATOS ---
@st.cache_data(ttl=60)
def load_data():
    log_path = "traffic_log.csv"
    if os.path.exists(log_path):
        df = pd.read_csv(log_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        return df
    else:
        st.sidebar.info("Archivo `traffic_log.csv` no encontrado. Generando datos de demostración.")
        return generate_dummy_data()

df = load_data()

# --- 4. BARRA LATERAL (SIDEBAR) ---
with st.sidebar:
    # st.image("https://i.imgur.com/g0y4RzA.png", width=70) # Un logo genérico
    st.title("SOC AS-A-SERVICE")
    st.markdown("---")
    
    # Menú de navegación (funcionalidad de ejemplo)
    # Se han comentado las siguientes líneas para evitar el error.
    # Si en el futuro creas una app multi-página, puedes descomentarlas
    # y apuntar a los archivos correctos dentro de una carpeta "pages".
    st.subheader("Dashboard")
    st.write("Alerts")
    st.write("Service Requests")
    st.write("My Assets")
    st.write("Reports")
    
    st.markdown("---")
    date_filter = st.selectbox(
        "Filtrar por Tiempo",
        ("Últimas 24 Horas", "Últimos 7 Días", "Últimos 30 Días", "Todo"),
        index=3 # Default a "Todo"
    )
    st.markdown("---")
    st.info(f"Creado por Dani | Proyecto PACD\n\nHora: {datetime.now().strftime('%H:%M:%S')}")


# --- 5. CUERPO PRINCIPAL DEL DASHBOARD (EL RESTO DEL CÓDIGO PERMANECE IGUAL) ---

st.header("SOC Monitoring Summary")
st.markdown("Análisis de eventos de seguridad y estado operativo de la red.")

total_events = len(df)
high_critical_alerts = len(df[df['severity'].isin(['High', 'Critical'])])
escalated_alerts = len(df[df['status'] == 'Escalated'])
monitored_devices = 5

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="🖥️ Monitored Devices", value=monitored_devices)
with col2:
    st.metric(label="Processed Logs", value=f"{total_events / 1000:.1f}K")
with col3:
    st.metric(label="⚠️ Security Alerts (High+)", value=high_critical_alerts)
with col4:
    st.metric(label="🚨 Escalated Alerts", value=escalated_alerts)

st.markdown("<br>", unsafe_allow_html=True)

col5, col6, col7 = st.columns(3)

with col5:
    with st.container(border=True):
        st.subheader("Alerts by Severity")
        severity_counts = df['severity'].value_counts()
        fig = go.Figure(data=[go.Pie(labels=severity_counts.index, values=severity_counts.values, hole=.7, marker_colors=['#F9C80E', '#F86624', '#EA3546', '#662E9B'])])
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5), height=300, margin=dict(t=30, b=80))
        fig.add_annotation(text=f"{high_critical_alerts}", x=0.5, y=0.5, font_size=30, showarrow=False)
        fig.add_annotation(text="Alerts", x=0.5, y=0.38, font_size=14, showarrow=False, opacity=0.7)
        st.plotly_chart(fig, use_container_width=True)

with col6:
    with st.container(border=True):
        st.subheader("Alerts by Status")
        status_counts = df['status'].value_counts()
        fig = go.Figure(data=[go.Pie(labels=status_counts.index, values=status_counts.values, hole=.7, marker_colors=['#43BCCD', '#F8961E', '#90BE6D', '#F94144'])])
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.4, xanchor="center", x=0.5), height=300, margin=dict(t=30, b=80))
        fig.add_annotation(text=f"{total_events}", x=0.5, y=0.5, font_size=30, showarrow=False)
        fig.add_annotation(text="Total", x=0.5, y=0.38, font_size=14, showarrow=False, opacity=0.7)
        st.plotly_chart(fig, use_container_width=True)

with col7:
    with st.container(border=True):
        st.subheader("Open Alerts by Category")
        category_counts = df['category'].value_counts()
        fig = px.bar(category_counts, y=category_counts.index, x=category_counts.values, orientation='h', labels={'y': 'Category', 'x': 'Count'}, color=category_counts.index)
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, height=300, margin=dict(t=30, b=0), yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

col8, col9 = st.columns(2)

with col8:
    with st.container(border=True):
        st.subheader("Threat Detection Trend")
        df_time = df.set_index('timestamp').resample('H').size().reset_index(name='count')
        fig = px.line(df_time, x='timestamp', y='count', title=None)
        fig.update_traces(line_color='#00BFA5', fill='tozeroy', fillcolor='rgba(0,191,165,0.1)')
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(t=30, b=0), xaxis_title=None, yaxis_title="Events per Hour")
        st.plotly_chart(fig, use_container_width=True)

with col9:
    with st.container(border=True):
        st.subheader("Severity Breakdown Over Time")
        df_sev_time = df.set_index('timestamp').groupby('severity').resample('H').size().reset_index(name='count')
        fig = px.area(df_sev_time, x='timestamp', y='count', color='severity', title=None, color_discrete_map={'Critical': '#EA3546', 'High': '#F86624', 'Medium': '#F9C80E', 'Low': '#43BCCD'})
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(t=30, b=0), xaxis_title=None, yaxis_title="Event Count")
        st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

col10, col11 = st.columns(2)

with col10:
     with st.container(border=True):
        st.subheader("Top 10 Source IPs")
        top_src_ips = df['source_ip'].value_counts().nlargest(10)
        fig = px.bar(top_src_ips, x=top_src_ips.values, y=top_src_ips.index, orientation='h', color=top_src_ips.values, color_continuous_scale='Reds')
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(t=30), xaxis_title="Count", yaxis_title="Source IP", yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

with col11:
     with st.container(border=True):
        st.subheader("Top 10 Destination IPs")
        top_dest_ips = df['destination_ip'].value_counts().nlargest(10)
        fig = px.bar(top_dest_ips, x=top_dest_ips.values, y=top_dest_ips.index, orientation='h', color=top_dest_ips.values, color_continuous_scale='Blues')
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300, margin=dict(t=30), xaxis_title="Count", yaxis_title="Destination IP", yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

with st.container(border=True):
    st.subheader(f"List of Open Alerts ({total_events})")
    st.dataframe(df.head(100), use_container_width=True, height=400) # Mostramos solo los primeros 100 por rendimiento

st.markdown("<br>", unsafe_allow_html=True)
col12, col13 = st.columns([0.6, 0.4])

with col12:
    with st.container(border=True):
        st.subheader("Threat Origin Map (Simulated)")
        df['lat'] = np.random.uniform(20, 50, len(df))
        df['lon'] = np.random.uniform(-120, -70, len(df))
        df_high_sev = df[df['severity'].isin(['High', 'Critical'])]
        
        fig = px.scatter_geo(df_high_sev, lat='lat', lon='lon', color='severity', hover_name='source_ip', size_max=15, projection="natural earth", color_discrete_map={'Critical': '#EA3546', 'High': '#F86624'})
        fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', geo=dict(bgcolor='rgba(0,0,0,0)', lakecolor='rgba(0,0,0,0)', landcolor='#2A3146', subunitcolor='#444'), height=400, margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)

with col13:
    with st.container(border=True):
        st.subheader("Event Name Summary")
        event_summary = df.groupby('event_name').agg(Count=('event_id', 'count'), Critical=('severity', lambda x: (x == 'Critical').sum()), High=('severity', lambda x: (x == 'High').sum())).sort_values('Count', ascending=False)
        st.dataframe(event_summary, use_container_width=True, height=350)
