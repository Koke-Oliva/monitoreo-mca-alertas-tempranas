# ============================================================
# Proyecto: Monitoreo de Gestión y Alertas Tempranas para MCA
# Archivo: 01_generar_datos_sinteticos.py
# Objetivo: Generar bases sintéticas para simular información
#           operativa de un programa de Medida Cautelar Ambulatoria.
# ============================================================

import pandas as pd
import numpy as np
from pathlib import Path


# ------------------------------------------------------------
# Configuración general
# ------------------------------------------------------------

np.random.seed(42)

RUTA_BASE = Path(__file__).resolve().parent.parent
RUTA_SALIDA = RUTA_BASE / "data" / "simulated"

RUTA_SALIDA.mkdir(parents=True, exist_ok=True)

FECHA_CORTE = pd.Timestamp("2026-05-01")


# ------------------------------------------------------------
# Funciones auxiliares
# ------------------------------------------------------------

def generar_fechas_aleatorias(fecha_inicio, fecha_fin, cantidad):
    """
    Genera fechas aleatorias entre dos fechas.
    """
    fecha_inicio = pd.Timestamp(fecha_inicio)
    fecha_fin = pd.Timestamp(fecha_fin)

    dias = (fecha_fin - fecha_inicio).days
    dias_aleatorios = np.random.randint(0, dias + 1, cantidad)

    return fecha_inicio + pd.to_timedelta(dias_aleatorios, unit="D")


def clasificar_tramo_edad(edad):
    """
    Clasifica la edad en tramos simples.
    """
    if pd.isna(edad):
        return "Sin información"
    elif edad < 14:
        return "Fuera de rango"
    elif edad <= 15:
        return "14-15"
    elif edad <= 17:
        return "16-17"
    elif edad <= 21:
        return "18-21"
    else:
        return "Fuera de rango"


# ------------------------------------------------------------
# 1. Generar base de usuarios MCA
# ------------------------------------------------------------

def generar_usuarios_mca(cantidad_usuarios=80):
    """
    Genera una base sintética de usuarios MCA.
    """

    ids_usuario = [f"U{str(i).zfill(3)}" for i in range(1, cantidad_usuarios + 1)]

    comunas = [
        "Coronel",
        "Concepción",
        "San Pedro de la Paz",
        "Lota",
        "Talcahuano",
        "Chiguayante",
        "Hualpén"
    ]

    causales_ingreso = [
        "Delitos contra la propiedad",
        "Ley de drogas",
        "Ley de control de armas",
        "Delitos contra las personas",
        "Otra causal"
    ]

    profesionales = [
        "Profesional A",
        "Profesional B",
        "Profesional C",
        "Profesional D"
    ]

    fechas_ingreso = generar_fechas_aleatorias(
        "2025-01-01",
        "2026-04-15",
        cantidad_usuarios
    )

    dias_desde_ultimo_contacto = np.random.randint(1, 60, cantidad_usuarios)
    fechas_ultimo_contacto = FECHA_CORTE - pd.to_timedelta(
        dias_desde_ultimo_contacto,
        unit="D"
    )

    usuarios = pd.DataFrame({
        "id_usuario": ids_usuario,
        "sexo": np.random.choice(["Masculino", "Femenino"], cantidad_usuarios, p=[0.72, 0.28]),
        "edad": np.random.randint(14, 21, cantidad_usuarios),
        "comuna": np.random.choice(comunas, cantidad_usuarios),
        "fecha_ingreso": fechas_ingreso,
        "causal_ingreso": np.random.choice(causales_ingreso, cantidad_usuarios),
        "estado_caso": np.random.choice(["Vigente", "Egresado", "Suspendido"], cantidad_usuarios, p=[0.70, 0.22, 0.08]),
        "profesional_responsable": np.random.choice(profesionales, cantidad_usuarios),
        "fecha_ultimo_contacto": fechas_ultimo_contacto
    })

    usuarios["tramo_edad"] = usuarios["edad"].apply(clasificar_tramo_edad)

    # Reordenar columnas
    usuarios = usuarios[
        [
            "id_usuario",
            "sexo",
            "edad",
            "tramo_edad",
            "comuna",
            "fecha_ingreso",
            "causal_ingreso",
            "estado_caso",
            "profesional_responsable",
            "fecha_ultimo_contacto"
        ]
    ]

    # --------------------------------------------------------
    # Inconsistencias controladas para validar en el paso 5
    # --------------------------------------------------------

    usuarios.loc[2, "edad"] = 13
    usuarios.loc[2, "tramo_edad"] = "Fuera de rango"

    usuarios.loc[7, "edad"] = 22
    usuarios.loc[7, "tramo_edad"] = "Fuera de rango"

    usuarios.loc[10, "comuna"] = np.nan
    usuarios.loc[15, "profesional_responsable"] = np.nan

    # ID duplicado intencional
    usuarios.loc[20, "id_usuario"] = usuarios.loc[19, "id_usuario"]

    return usuarios


# ------------------------------------------------------------
# 2. Generar base de intervenciones
# ------------------------------------------------------------

def generar_intervenciones(usuarios):
    """
    Genera intervenciones simuladas asociadas a usuarios.
    """

    tipos_intervencion = [
        "Individual",
        "Familiar",
        "Coordinación con red",
        "Judicial",
        "Seguimiento telefónico"
    ]

    resultados = [
        "Realizada",
        "Pendiente",
        "No asiste",
        "Reprogramada"
    ]

    responsables = [
        "Profesional A",
        "Profesional B",
        "Profesional C",
        "Profesional D"
    ]

    registros = []
    contador = 1

    for _, fila in usuarios.iterrows():
        cantidad_intervenciones = np.random.randint(1, 7)

        for _ in range(cantidad_intervenciones):
            fecha_intervencion = fila["fecha_ingreso"] + pd.to_timedelta(
                np.random.randint(5, 240),
                unit="D"
            )

            if fecha_intervencion > FECHA_CORTE:
                fecha_intervencion = FECHA_CORTE - pd.to_timedelta(
                    np.random.randint(1, 30),
                    unit="D"
                )

            registros.append({
                "id_intervencion": f"I{str(contador).zfill(4)}",
                "id_usuario": fila["id_usuario"],
                "fecha_intervencion": fecha_intervencion,
                "tipo_intervencion": np.random.choice(tipos_intervencion),
                "responsable": np.random.choice(responsables),
                "resultado_intervencion": np.random.choice(resultados, p=[0.70, 0.10, 0.12, 0.08]),
                "observacion_estado": "Registro sintético generado para análisis"
            })

            contador += 1

    intervenciones = pd.DataFrame(registros)

    # Inconsistencia controlada: intervención sin responsable
    if len(intervenciones) > 5:
        intervenciones.loc[5, "responsable"] = np.nan

    return intervenciones


# ------------------------------------------------------------
# 3. Generar base de planes de intervención
# ------------------------------------------------------------

def generar_planes_intervencion(usuarios):
    """
    Genera planes de intervención individual simulados.
    """

    estados_pii = [
        "Vigente",
        "Vencido",
        "No registrado"
    ]

    resultados_pii = [
        "Logrado",
        "Parcialmente logrado",
        "No logrado",
        "En proceso"
    ]

    registros = []

    for i, fila in usuarios.iterrows():
        fecha_creacion = fila["fecha_ingreso"] + pd.to_timedelta(
            np.random.randint(5, 30),
            unit="D"
        )

        fecha_actualizacion = fecha_creacion + pd.to_timedelta(
            np.random.randint(10, 180),
            unit="D"
        )

        if fecha_actualizacion > FECHA_CORTE:
            fecha_actualizacion = FECHA_CORTE - pd.to_timedelta(
                np.random.randint(1, 45),
                unit="D"
            )

        registros.append({
            "id_plan": f"P{str(i + 1).zfill(3)}",
            "id_usuario": fila["id_usuario"],
            "fecha_creacion_pii": fecha_creacion,
            "fecha_ultima_actualizacion": fecha_actualizacion,
            "estado_pii": np.random.choice(estados_pii, p=[0.70, 0.20, 0.10]),
            "porcentaje_avance": np.random.randint(0, 101),
            "resultado_pii": np.random.choice(resultados_pii)
        })

    planes = pd.DataFrame(registros)

    # Inconsistencias controladas
    planes.loc[8, "estado_pii"] = "No registrado"
    planes.loc[12, "estado_pii"] = "Vencido"

    return planes


# ------------------------------------------------------------
# 4. Generar base de controles y audiencias
# ------------------------------------------------------------

def generar_controles_audiencias(usuarios):
    """
    Genera controles, citaciones o audiencias simuladas.
    """

    tipos_control = [
        "Audiencia",
        "Control técnico",
        "Citación",
        "Revisión de medida"
    ]

    asistencias = [
        "Asiste",
        "No asiste",
        "Justificada"
    ]

    registros = []
    contador = 1

    for _, fila in usuarios.iterrows():
        cantidad_controles = np.random.randint(1, 5)

        for _ in range(cantidad_controles):
            fecha_control = fila["fecha_ingreso"] + pd.to_timedelta(
                np.random.randint(15, 300),
                unit="D"
            )

            dias_para_control = (fecha_control - FECHA_CORTE).days

            registros.append({
                "id_control": f"C{str(contador).zfill(4)}",
                "id_usuario": fila["id_usuario"],
                "fecha_control": fecha_control,
                "tipo_control": np.random.choice(tipos_control),
                "asistencia": np.random.choice(asistencias, p=[0.72, 0.18, 0.10]),
                "dias_para_control": dias_para_control,
                "observacion": "Registro sintético de control o audiencia"
            })

            contador += 1

    controles = pd.DataFrame(registros)

    # Inasistencias controladas para generar alertas posteriores
    controles.loc[0, "asistencia"] = "No asiste"
    controles.loc[1, "asistencia"] = "No asiste"

    return controles


# ------------------------------------------------------------
# 5. Generar base de egresos
# ------------------------------------------------------------

def generar_egresos(usuarios):
    """
    Genera registros de egreso para usuarios con estado egresado.
    """

    usuarios_egresados = usuarios[usuarios["estado_caso"] == "Egresado"].copy()

    causales_egreso = [
        "Cumplimiento de medida",
        "Derivación",
        "Incumplimiento",
        "Otra causal"
    ]

    registros = []

    for i, fila in usuarios_egresados.iterrows():
        fecha_egreso = fila["fecha_ingreso"] + pd.to_timedelta(
            np.random.randint(60, 360),
            unit="D"
        )

        if fecha_egreso > FECHA_CORTE:
            fecha_egreso = FECHA_CORTE - pd.to_timedelta(
                np.random.randint(1, 30),
                unit="D"
            )

        dias_permanencia = (fecha_egreso - fila["fecha_ingreso"]).days

        registros.append({
            "id_egreso": f"E{str(i + 1).zfill(3)}",
            "id_usuario": fila["id_usuario"],
            "fecha_egreso": fecha_egreso,
            "causal_egreso": np.random.choice(causales_egreso),
            "dias_permanencia": dias_permanencia,
            "pii_logrado": np.random.choice(["Sí", "No", "Parcial"], p=[0.55, 0.20, 0.25])
        })

    egresos = pd.DataFrame(registros)

    # Inconsistencia controlada: egreso antes del ingreso
    if len(egresos) > 0:
        primer_id = egresos.loc[egresos.index[0], "id_usuario"]
        fecha_ingreso = usuarios.loc[usuarios["id_usuario"] == primer_id, "fecha_ingreso"].iloc[0]
        egresos.loc[egresos.index[0], "fecha_egreso"] = fecha_ingreso - pd.to_timedelta(10, unit="D")
        egresos.loc[egresos.index[0], "dias_permanencia"] = -10

    return egresos


# ------------------------------------------------------------
# 6. Exportar bases
# ------------------------------------------------------------

def exportar_bases():
    """
    Ejecuta la generación completa y exporta archivos CSV.
    """

    usuarios = generar_usuarios_mca()
    intervenciones = generar_intervenciones(usuarios)
    planes = generar_planes_intervencion(usuarios)
    controles = generar_controles_audiencias(usuarios)
    egresos = generar_egresos(usuarios)

    usuarios.to_csv(RUTA_SALIDA / "usuarios_mca.csv", index=False, encoding="utf-8-sig")
    intervenciones.to_csv(RUTA_SALIDA / "intervenciones.csv", index=False, encoding="utf-8-sig")
    planes.to_csv(RUTA_SALIDA / "planes_intervencion.csv", index=False, encoding="utf-8-sig")
    controles.to_csv(RUTA_SALIDA / "controles_audiencias.csv", index=False, encoding="utf-8-sig")
    egresos.to_csv(RUTA_SALIDA / "egresos.csv", index=False, encoding="utf-8-sig")

    print("Bases sintéticas generadas correctamente.")
    print(f"Archivos guardados en: {RUTA_SALIDA}")
    print("")
    print("Resumen de archivos generados:")
    print(f"- usuarios_mca.csv: {usuarios.shape[0]} filas, {usuarios.shape[1]} columnas")
    print(f"- intervenciones.csv: {intervenciones.shape[0]} filas, {intervenciones.shape[1]} columnas")
    print(f"- planes_intervencion.csv: {planes.shape[0]} filas, {planes.shape[1]} columnas")
    print(f"- controles_audiencias.csv: {controles.shape[0]} filas, {controles.shape[1]} columnas")
    print(f"- egresos.csv: {egresos.shape[0]} filas, {egresos.shape[1]} columnas")


# ------------------------------------------------------------
# Ejecución principal
# ------------------------------------------------------------

if __name__ == "__main__":
    exportar_bases()