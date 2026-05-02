# ============================================================
# Proyecto: Monitoreo de Gestión y Alertas Tempranas para MCA
# Archivo: 07_ejecutar_consultas_sql.py
# Objetivo: Ejecutar consultas SQL sobre la base SQLite del
#           proyecto y exportar los resultados a Excel.
# ============================================================

import re
import sqlite3
import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# Configuración general
# ------------------------------------------------------------

RUTA_BASE = Path(__file__).resolve().parent.parent

RUTA_DB = RUTA_BASE / "data" / "output" / "mca_monitoreo.db"
RUTA_SQL = RUTA_BASE / "sql" / "consultas_indicadores.sql"
RUTA_SALIDA = RUTA_BASE / "data" / "output" / "resultados_consultas_sql.xlsx"


# ------------------------------------------------------------
# Funciones auxiliares
# ------------------------------------------------------------

def limpiar_nombre_hoja(nombre):
    """
    Limpia y acorta el nombre de una hoja Excel.
    Excel permite máximo 31 caracteres por nombre de hoja.
    """

    nombre = re.sub(r"[\[\]\:\*\?\/\\]", "", nombre)
    nombre = nombre.replace(" ", "_")
    nombre = nombre.lower()

    return nombre[:31]


def leer_consultas_sql(ruta_sql):
    """
    Lee el archivo .sql y separa las consultas usando los títulos
    comentados del tipo: -- 1. Nombre de la consulta
    """

    if not ruta_sql.exists():
        raise FileNotFoundError(f"No se encontró el archivo SQL: {ruta_sql}")

    consultas = []
    nombre_actual = None
    lineas_consulta = []

    with open(ruta_sql, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            linea_limpia = linea.strip()

            # Detectar título de consulta en comentarios SQL
            coincidencia = re.match(r"--\s*(\d+)\.\s*(.+)", linea_limpia)

            if coincidencia:
                numero = coincidencia.group(1)
                titulo = coincidencia.group(2)
                nombre_actual = f"{numero}_{titulo}"
                continue

            # Ignorar comentarios y líneas vacías
            if linea_limpia.startswith("--") or linea_limpia == "":
                continue

            lineas_consulta.append(linea)

            # Cerrar consulta al encontrar punto y coma
            if ";" in linea_limpia:
                consulta_sql = "".join(lineas_consulta).strip()

                if nombre_actual is None:
                    nombre_actual = f"consulta_{len(consultas) + 1}"

                consultas.append({
                    "nombre": nombre_actual,
                    "sql": consulta_sql
                })

                nombre_actual = None
                lineas_consulta = []

    return consultas


def ejecutar_consultas(consultas):
    """
    Ejecuta las consultas SQL sobre la base SQLite.
    """

    if not RUTA_DB.exists():
        raise FileNotFoundError(
            f"No se encontró la base SQLite: {RUTA_DB}\n"
            "Primero ejecuta: python 06_crear_base_sqlite.py"
        )

    conexion = sqlite3.connect(RUTA_DB)

    resultados = []
    resumen = []

    for consulta in consultas:
        nombre = consulta["nombre"]
        sql = consulta["sql"]

        try:
            dataframe = pd.read_sql_query(sql, conexion)

            resultados.append({
                "nombre": nombre,
                "dataframe": dataframe
            })

            resumen.append({
                "consulta": nombre,
                "estado": "Ejecutada correctamente",
                "filas_resultado": dataframe.shape[0],
                "columnas_resultado": dataframe.shape[1],
                "mensaje": ""
            })

        except Exception as error:
            resumen.append({
                "consulta": nombre,
                "estado": "Error",
                "filas_resultado": 0,
                "columnas_resultado": 0,
                "mensaje": str(error)
            })

    conexion.close()

    return resultados, pd.DataFrame(resumen)


def exportar_resultados(resultados, resumen):
    """
    Exporta los resultados de las consultas a un archivo Excel.
    """

    with pd.ExcelWriter(RUTA_SALIDA, engine="openpyxl") as writer:
        resumen.to_excel(writer, sheet_name="resumen_ejecucion", index=False)

        for resultado in resultados:
            nombre_hoja = limpiar_nombre_hoja(resultado["nombre"])
            resultado["dataframe"].to_excel(
                writer,
                sheet_name=nombre_hoja,
                index=False
            )

    print("Consultas SQL ejecutadas correctamente.")
    print(f"Archivo Excel generado en: {RUTA_SALIDA}")
    print("")
    print("Resumen de ejecución:")
    print(resumen)


# ------------------------------------------------------------
# Ejecución principal
# ------------------------------------------------------------

def ejecutar_proceso_sql():
    """
    Ejecuta el proceso completo:
    1. Lee consultas SQL.
    2. Ejecuta consultas sobre SQLite.
    3. Exporta resultados a Excel.
    """

    consultas = leer_consultas_sql(RUTA_SQL)

    print(f"Consultas detectadas: {len(consultas)}")

    resultados, resumen = ejecutar_consultas(consultas)

    exportar_resultados(resultados, resumen)


if __name__ == "__main__":
    ejecutar_proceso_sql()