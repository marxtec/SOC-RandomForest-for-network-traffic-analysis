import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# Configuración inicial
st.set_page_config(page_title="SOC Dashboard", layout="wide", page_icon="🛡️")

# Refrescar cada 5 segundos automáticamente
st_autorefresh(interval=5000, key="auto-refresh")

# Obtener ruta absoluta desde donde está este archivo
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
log_path = os.path.join(BASE_DIR, "logs", "traffic_log.csv")

# Título
st.title("🧠 **SOC Dashboard - Threat Intelligence**")
st.caption("Dashboard de Operaciones de Seguridad - Proyecto PACD")
st.markdown(f"🕒 **Hora actual:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`")
st.divider()

# Cargar logs
def cargar_logs():
    if os.path.exists(log_path):
        df = pd.read_csv(log_path)
        df["timestamp"] = pd.to_datetime(df["timestamp"])

        # Normalizar valores
        df["resultado"] = df["resultado"].str.strip().str.capitalize()
        df["tipo_simulado"] = df["tipo_simulado"].str.strip().str.capitalize()
        return df
    else:
        return pd.DataFrame(columns=["timestamp", "tipo_simulado", "resultado", "probabilidad"])

# Cargar datos
df = cargar_logs()

# Si los datos están disponibles
if not df.empty:
    # Métricas Generales
    total = len(df)
    benignos = len(df[df["resultado"] == "Benigno"])
    ataques = len(df[df["resultado"] == "Ddos"])
    ultima = df.iloc[-1]["resultado"]

    # 1. **Panel de Métricas Principales**
    st.subheader("📊 **Métricas del Sistema**")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Total de eventos procesados", total)
    col2.metric("🛡️ Eventos Benignos", benignos)
    col3.metric("☠️ Ataques DDoS", ataques)
    col4.metric("🧪 Última Clasificación", ultima)

    # 2. **Gráfico de Evolución Temporal**
    df["minuto"] = df["timestamp"].dt.strftime('%H:%M')
    por_tiempo = df.groupby(["minuto", "resultado"]).size().reset_index(name="cuenta")
    fig_line = go.Figure()
    for label in por_tiempo['resultado'].unique():
        fig_line.add_trace(go.Scatter(x=por_tiempo[por_tiempo['resultado'] == label]['minuto'],
                                     y=por_tiempo[por_tiempo['resultado'] == label]['cuenta'],
                                     mode='lines', name=label))
    fig_line.update_layout(title="📈 **Evolución Temporal del Tráfico**", xaxis_title="Hora", yaxis_title="Número de Eventos")
    st.plotly_chart(fig_line, use_container_width=True)

    # 3. **Gráfico de Distribución de Tráfico**
    fig_pie = go.Figure(data=[go.Pie(labels=df["resultado"].unique(), values=df["resultado"].value_counts(), hole=0.3)])
    fig_pie.update_layout(title="🌀 **Distribución Actual de Tráfico**")
    st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()

    # 4. **Matriz de Confusión**
    st.subheader("🔬 **Matriz de Confusión**")
    conf_matrix = pd.crosstab(df["tipo_simulado"], df["resultado"])
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues", ax=ax)
    ax.set_title('🧪 **Matriz de Confusión**')
    st.pyplot(fig)

    st.divider()

    # 5. **Gráfico de Probabilidad (Confianza del modelo)**
    st.subheader("📡 **Confianza del Clasificador por Tiempo**")
    fig_prob = px.scatter(df, x="timestamp", y="probabilidad", color="resultado", title="🔍 **Confianza del Modelo (Probabilidad)**")
    st.plotly_chart(fig_prob, use_container_width=True)

    st.divider()

    # 6. **Análisis de Falsos Positivos y Negativos**
    fp = len(df[(df["tipo_simulado"] == "Benigno") & (df["resultado"] == "Ddos")])
    fn = len(df[(df["tipo_simulado"] == "Malicioso") & (df["resultado"] == "Benigno")])
    total_benignos = len(df[df["tipo_simulado"] == "Benigno"])
    total_maliciosos = len(df[df["tipo_simulado"] == "Malicioso"])
    fpr = (fp / total_benignos) * 100 if total_benignos else 0
    fnr = (fn / total_maliciosos) * 100 if total_maliciosos else 0

    st.subheader("🚨 **Métricas de Error**")
    col5, col6 = st.columns(2)
    col5.metric("❗ **Falsos Positivos**", f"{fpr:.2f}%")
    col6.metric("❗ **Falsos Negativos**", f"{fnr:.2f}%")

    st.divider()

    # 7. **Últimos Eventos Clasificados**
    st.subheader("📋 **Últimos Paquetes Clasificados**")
    st.dataframe(df.sort_values(by="timestamp", ascending=False).head(20), use_container_width=True)

else:
    st.warning("⚠️ **Aún no hay tráfico clasificado. Corre el simulador para comenzar.**")
