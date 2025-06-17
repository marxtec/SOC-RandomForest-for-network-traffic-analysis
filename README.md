# 🧠 Proyecto Programación avanzada para la ciencia de datos: Simulación y Clasificación de Tráfico de Red

Este proyecto implementa una simulación de tráfico de red en tiempo real, clasifica paquetes como **benignos** o **maliciosos (DDoS)** utilizando un modelo de machine learning, y presenta los resultados en un dashboard interactivo tipo **SOC (Security Operations Center)**.

---

## 🔧 Estructura del Proyecto

ProyectoPACD/
├── app/
│ ├── simulator.py # Simula tráfico real desde el dataset
│ ├── classifier.py # Clasificador de paquetes con modelo ML
├── models/
│ └── traffic_model.pkl # Modelo entrenado (ej. Random Forest)
├── data/
│ └── processed/
│ └── clean_dataset.csv # Dataset limpio y normalizado
├── logs/
│ └── traffic_log.csv # Archivo generado automáticamente
├── dashboard.py # Dashboard Streamlit interactivo
├── requirements.txt # Dependencias del entorno
└── README.md

---

## 🚀 ¿Cómo ejecutar el proyecto?

### 1. Instalar dependencias

pip install -r requirements.txt
2. Ejecutar el simulador en una terminal
bash
Copiar
Editar
python -m app.simulator
Esto comenzará a generar tráfico aleatorio a partir del dataset y clasificará cada paquete como benigno o malicioso usando el modelo entrenado. Los resultados se guardan automáticamente en logs/traffic_log.csv.

3. Ejecutar el dashboard en otra terminal
bash
Copiar
Editar
streamlit run dashboard.py
Esto abrirá una interfaz web interactiva donde podrás visualizar:

Tráfico en tiempo real

Distribución de predicciones

Accuracy del modelo

Falsos positivos/negativos

Matriz de confusión

Tabla de eventos recientes

Autoactualización automática cada 5 segundos

¿Qué incluye el dashboard?
Auto-refresh cada 5 segundos

Métricas clave (total, benignos, DDoS, accuracy)

Comparación de predicción vs realidad

Evolución temporal del tráfico

Gráfico de pastel y barras

Dispersión de confianza del modelo

Matriz de confusión y tasa de errores

Tabla de últimos eventos

Tecnologías usadas
Python 3.10.0

Streamlit

Pandas

Plotly

Seaborn

Matplotlib

Scikit-learn

Joblib

👨‍💻 Autores
Daniel Sebastián Cabrera Lazo
Universidad del Pacífico
Proyecto final — Programación Avanzada para Ciencia de Datos
