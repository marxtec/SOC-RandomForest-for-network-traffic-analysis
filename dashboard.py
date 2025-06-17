import streamlit as st
import pandas as pd
import os
from datetime import datetime
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from streamlit_autorefresh import st_autorefresh

# 🧠 Configuración inicial
st.set_page_config(page_title="SOC Dashboard", layout="wide")

# 🔁 Refrescar cada 5 segundos automáticamente
st_autorefresh(interval=5000, key="auto-refresh")

# 📍 Ruta del archivo de logs
log_path = os.path.join("logs", "traffic_log.csv")

# 🧭 Título
st.title("🧠 Network Threat Intelligence Dashboard")
st.caption("Creado por Dani | Proyecto PACD")
st.markdown(f"🕒 **Hora actual:** `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`")
st.divider()

# 📦 Cargar logs
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

# 📈 Cargar datos
df = cargar_logs()

if not df.empty:

    # 🔢 Métricas principales
    total = len(df)
    benignos = len(df[df["resultado"] == "Benigno"])
    ataques = len(df[df["resultado"] == "Ddos"])
    ultima = df.iloc[-1]["resultado"]

    st.subheader("📊 Métricas Generales")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📦 Total procesados", total)
    col2.metric("🛡️ Benignos detectados", benignos)
    col3.metric("☠️ Ataques DDoS detectados", ataques)
    col4.metric("🧪 Último resultado", ultima)

    # 🎯 Comparación real vs clasificado
    df["match"] = df["tipo_simulado"] == df["resultado"]
    accuracy = df["match"].mean()
    st.metric("🎯 Accuracy del clasificador", f"{accuracy * 100:.2f}%")

    st.divider()

    # 📈 Evolución temporal de tráfico
    df["minuto"] = df["timestamp"].dt.strftime('%H:%M')
    por_tiempo = df.groupby(["minuto", "resultado"]).size().reset_index(name="cuenta")
    fig_line = px.line(por_tiempo, x="minuto", y="cuenta", color="resultado", title="Evolución temporal del tráfico")
    st.plotly_chart(fig_line, use_container_width=True)

    # 🍩 Gráfico de distribución
    fig_pie = px.pie(df, names="resultado", hole=0.5, title="Distribución actual de tráfico")
    st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()

    # 🔍 Matriz de confusión
    st.subheader("🔬 Matriz de Confusión")
    conf_matrix = pd.crosstab(df["tipo_simulado"], df["resultado"])
    fig, ax = plt.subplots()
    sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues", ax=ax)
    st.pyplot(fig)

    # 📊 Gráfico de barras: real vs predicho
    st.subheader("📊 Distribución Real vs Clasificado")
    st.bar_chart(conf_matrix)

    st.divider()

    # 📈 Dispersión: probabilidad por predicción
    st.subheader("📡 Confianza del modelo por tiempo")
    fig_prob = px.scatter(df, x="timestamp", y="probabilidad", color="resultado",
                          title="Confianza del clasificador (probabilidad)")
    st.plotly_chart(fig_prob, use_container_width=True)

    st.divider()

    # ❌ Falsos positivos y negativos
    fp = len(df[(df["tipo_simulado"] == "Benigno") & (df["resultado"] == "Ddos")])
    fn = len(df[(df["tipo_simulado"] == "Malicioso") & (df["resultado"] == "Benigno")])
    total_benignos = len(df[df["tipo_simulado"] == "Benigno"])
    total_maliciosos = len(df[df["tipo_simulado"] == "Malicioso"])
    fpr = (fp / total_benignos) * 100 if total_benignos else 0
    fnr = (fn / total_maliciosos) * 100 if total_maliciosos else 0

    st.subheader("🚨 Métricas de error")
    col5, col6 = st.columns(2)
    col5.metric("❗ Falsos positivos", f"{fpr:.2f}%")
    col6.metric("❗ Falsos negativos", f"{fnr:.2f}%")

    st.divider()

    # 🧾 Últimos paquetes
    st.subheader("📋 Últimos paquetes clasificados")
    st.dataframe(df.sort_values(by="timestamp", ascending=False).head(20), use_container_width=True)

else:
    st.warning("⚠️ Aún no hay tráfico clasificado. Corre el simulador para comenzar.")
