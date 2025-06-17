import pandas as pd
import numpy as np

def cargar_y_preprocesar_dataset(ruta_csv):
    #Inicialmente se usarán estas columnas
    ruta_csv = ruta_csv.replace('\\', '/')
    columnas_usar = [
        "Flow Duration", "Total Fwd Packets", "Total Backward Packets",
        "Fwd Packet Length Mean", "Bwd Packet Length Mean",
        "Flow Bytes/s", "Flow Packets/s",
        "SYN Flag Count", "ACK Flag Count",
        "Init_Win_bytes_forward", "Init_Win_bytes_backward",
        "Active Mean", "Idle Mean", "Label"
    ]

    #Se carga el dataset
    df = pd.read_csv(ruta_csv, usecols=columnas_usar, skipinitialspace=True)

    # Se eliminan datos nulos o infintos de las columnas que se vayan a usar
    df.replace([np.inf, -np.inf], np.nan, inplace=True)
    df.dropna(inplace=True)
    # Se codifican variables
    df["Label"] = df["Label"].apply(lambda x: 1 if x == "DDoS" else 0)




    return df
