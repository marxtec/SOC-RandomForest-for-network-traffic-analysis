import sys
import os
import time
import pandas as pd
import csv
from datetime import datetime
import random

# Para importar desde app/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.classifier import clasificar_paquete


class TrafficSimulator:
    def __init__(self, dataset_path):
        # Cargar dataset
        self.df = pd.read_csv(dataset_path)
        self.df = self.df.replace([float("inf"), -float("inf")], float("nan")).dropna()

        # Mezclar filas aleatoriamente
        self.df = self.df.sample(frac=1, random_state=42).reset_index(drop=True)
        self.total = len(self.df)
        self.counter = 0

        # Ruta del log de tráfico
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.log_path = os.path.join(base_dir, "logs", "traffic_log.csv")
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

        conteo = self.df["Label"].value_counts()
        print("✅ Distribución original de etiquetas:")
        print(conteo)


    def registrar_evento(self, tipo_real, resultado):
        fila = {
            "timestamp": datetime.now().isoformat(),
            "tipo_simulado": tipo_real,
            "resultado": resultado["resultado"],
            "probabilidad": round(float(resultado["probabilidad"]), 4)
        }

        archivo_existe = os.path.isfile(self.log_path)
        with open(self.log_path, mode="a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fila.keys())
            if not archivo_existe:
                writer.writeheader()
            writer.writerow(fila)

    def simular_trafico_desde_dataset(self, delay=0.3, max_paquetes=100):
        #Queremos que siempre funcione
        while True:
            fila = self.df.sample(n=1).iloc[0]
            # Determinar tipo a partir de la etiqueta real
            valor = int(fila["Label"])
            tipo_simulado = "BENIGNO" if valor == 0 else "MALICIOSO"


            # Eliminar la etiqueta antes de clasificar
            paquete = fila.drop(labels=["Label"]).to_dict()
            resultado = clasificar_paquete(paquete)

            self.registrar_evento(tipo_simulado, resultado)
            print(f"[{tipo_simulado}] → {resultado}")
            self.counter += 1
            time.sleep(delay)


if __name__ == "__main__":
    dataset_path = os.path.join(os.path.dirname(__file__), "..", "data", "processed", "clean_dataset.csv")
    sim = TrafficSimulator(dataset_path)
    sim.simular_trafico_desde_dataset(delay=0.3, max_paquetes=100)
