# ============================================================
# Proyecto: Monitoreo de Gestión y Alertas Tempranas para MCA
# Archivo: 06_crear_base_sqlite.py
# Objetivo: Crear una base SQLite con las tablas principales
#           del proyecto para consultas SQL de indicadores.
# ============================================================

import sqlite3
import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# Configuración general
# ------------------------------------------------------------

RUTA_BASE = Path(__file__).resolve().parent.parent
RUTA_SIMULATED = RUTA_BASE / "data" / "simulated"
RUTA_OUTPUT = RUTA_BASE / "data" / "output"

RUTA_DB = RUTA_OUTPUT / "mca_monitoreo.db"


# ------------------------------------------------------------
# Cargar archivos CSV
# ------------------------------------------------------------

def cargar_archivos():
    """
    Carga las bases CSV generadas durante el proyecto.
    """

    tablas = {
        "usuarios_mca": pd.read_csv(RUTA_SIMULATED / "usuarios_mca.csv"),
        "intervenciones": pd.read_csv(RUTA_SIMULATED / "intervenciones.csv"),
        "planes_intervencion": pd.read_csv(RUTA_SIMULATED / "planes_intervencion.csv"),
        "controles_audiencias": pd.read_csv(RUTA_SIMULATED / "controles_audiencias.csv"),
        "egresos": pd.read_csv(RUTA_SIMULATED / "egresos.csv"),
        "base_consolidada_mca": pd.read_csv(RUTA_OUTPUT / "base_consolidada_mca.csv"),
        "indicadores_gestion": pd.read_csv(RUTA_OUTPUT / "indicadores_gestion.csv"),
        "alertas_tempranas": pd.read_csv(RUTA_OUTPUT / "alertas_tempranas.csv")
    }

    return tablas


# ------------------------------------------------------------
# Crear base SQLite
# ------------------------------------------------------------

def crear_base_sqlite():
    """
    Crea una base SQLite y carga las tablas principales.
    """

    tablas = cargar_archivos()

    conexion = sqlite3.connect(RUTA_DB)

    for nombre_tabla, dataframe in tablas.items():
        dataframe.to_sql(
            nombre_tabla,
            conexion,
            if_exists="replace",
            index=False
        )

    conexion.close()

    print("Base SQLite generada correctamente.")
    print(f"Archivo creado en: {RUTA_DB}")
    print("")
    print("Tablas cargadas:")

    for nombre_tabla, dataframe in tablas.items():
        print(f"- {nombre_tabla}: {dataframe.shape[0]} filas, {dataframe.shape[1]} columnas")


# ------------------------------------------------------------
# Ejecución principal
# ------------------------------------------------------------

if __name__ == "__main__":
    crear_base_sqlite()