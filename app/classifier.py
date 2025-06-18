import joblib
import numpy as np
import pandas as pd

# Cargar el modelo entrenado
modelo = joblib.load("models/modelo_clasificador_trafico_red.pkl")

# Definir el orden exacto de las variables que el modelo espera
columnas_modelo = [
    "Flow Duration", "Total Fwd Packets", "Total Backward Packets",
    "Fwd Packet Length Mean", "Bwd Packet Length Mean",
    "Flow Bytes/s", "Flow Packets/s",
    "SYN Flag Count", "ACK Flag Count",
    "Init_Win_bytes_forward", "Init_Win_bytes_backward",
    "Active Mean", "Idle Mean"
]

# Función para predecir la clase de un paquete simulado
def clasificar_paquete(paquete):
    # Asegurar que las claves estén en el orden correcto
    valores = [paquete.get(col, 0) for col in columnas_modelo]

    # Convertir a DataFrame (formato que sklearn necesita)
    entrada = pd.DataFrame([valores], columns=columnas_modelo)

    # Clasificar
    pred = modelo.predict(entrada)[0]
    prob = modelo.predict_proba(entrada)[0][int(pred)]

    return {
        "resultado": "DDoS" if pred == 1 else "Benigno",
        "probabilidad": round(prob, 4)
    }
