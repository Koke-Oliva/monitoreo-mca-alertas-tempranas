# ============================================================
# Proyecto: Monitoreo de Gestión y Alertas Tempranas para MCA
# Archivo: 05_generar_alertas_tempranas.py
# Objetivo: Generar un sistema de alertas tempranas basado en
#           reglas simples, trazables e interpretables.
# ============================================================

import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# Configuración general
# ------------------------------------------------------------

RUTA_BASE = Path(__file__).resolve().parent.parent
RUTA_ENTRADA = RUTA_BASE / "data" / "output"
RUTA_SALIDA = RUTA_BASE / "data" / "output"

RUTA_SALIDA.mkdir(parents=True, exist_ok=True)

FECHA_CORTE = pd.Timestamp("2026-05-01")


# ------------------------------------------------------------
# Funciones auxiliares
# ------------------------------------------------------------

def convertir_a_booleano(serie):
    """
    Convierte valores True/False almacenados como texto en valores booleanos.
    """

    return serie.astype(str).str.lower().isin(["true", "1", "sí", "si"])


def clasificar_nivel_alerta(puntaje):
    """
    Clasifica el nivel de alerta según puntaje total.
    """

    if puntaje >= 6:
        return "Alto"
    elif puntaje >= 3:
        return "Medio"
    else:
        return "Bajo"


def definir_accion_sugerida(nivel_alerta):
    """
    Define una acción sugerida según el nivel de alerta.
    """

    if nivel_alerta == "Alto":
        return "Priorizar revisión técnica y coordinación del caso."
    elif nivel_alerta == "Medio":
        return "Revisar antecedentes y actualizar seguimiento."
    else:
        return "Mantener seguimiento regular."


# ------------------------------------------------------------
# 1. Cargar base consolidada
# ------------------------------------------------------------

def cargar_base_consolidada():
    """
    Carga la base consolidada generada en el paso 6.
    """

    base = pd.read_csv(
        RUTA_ENTRADA / "base_consolidada_mca.csv",
        parse_dates=[
            "fecha_ingreso",
            "fecha_ultimo_contacto",
            "ultima_intervencion",
            "fecha_creacion_pii",
            "fecha_ultima_actualizacion",
            "proximo_control",
            "ultima_fecha_control",
            "fecha_egreso"
        ]
    )

    return base


# ------------------------------------------------------------
# 2. Preparar variables
# ------------------------------------------------------------

def preparar_base(base):
    """
    Asegura formatos adecuados para calcular alertas.
    """

    columnas_booleanas = [
        "caso_vigente",
        "caso_sin_contacto_reciente",
        "caso_sin_intervencion_reciente",
        "pii_vencido_o_no_registrado",
        "caso_con_inasistencias",
        "caso_con_inasistencias_reiteradas",
        "caso_sin_profesional",
        "registro_con_datos_criticos_faltantes",
        "permanencia_prolongada",
        "tiene_control_proximo_7_dias",
        "id_usuario_duplicado"
    ]

    for columna in columnas_booleanas:
        if columna in base.columns:
            base[columna] = convertir_a_booleano(base[columna])

    columnas_numericas = [
        "edad",
        "dias_sin_contacto",
        "cantidad_intervenciones",
        "dias_sin_intervencion",
        "porcentaje_avance",
        "dias_desde_actualizacion_pii",
        "cantidad_controles",
        "cantidad_inasistencias",
        "dias_para_proximo_control",
        "dias_permanencia_estimados"
    ]

    for columna in columnas_numericas:
        if columna in base.columns:
            base[columna] = pd.to_numeric(base[columna], errors="coerce")

    return base


# ------------------------------------------------------------
# 3. Calcular puntaje de alerta por caso
# ------------------------------------------------------------

def calcular_alerta_fila(fila):
    """
    Calcula el puntaje de alerta para un usuario según reglas operativas.
    """

    puntaje = 0
    motivos = []

    # Regla 1: Caso vigente sin intervención reciente
    if fila.get("caso_sin_intervencion_reciente", False):
        puntaje += 3
        motivos.append("Más de 21 días sin intervención reciente")

    # Regla 2: Inasistencias reiteradas
    if fila.get("cantidad_inasistencias", 0) >= 2:
        puntaje += 3
        motivos.append("Dos o más inasistencias registradas")

    # Regla 3: PII vencido o no registrado
    if fila.get("pii_vencido_o_no_registrado", False):
        puntaje += 2
        motivos.append("PII vencido o no registrado")

    # Regla 4: Audiencia/control próximo sin contacto reciente
    if (
        fila.get("tiene_control_proximo_7_dias", False)
        and fila.get("caso_sin_contacto_reciente", False)
    ):
        puntaje += 2
        motivos.append("Control o audiencia próxima sin contacto reciente")

    # Regla 5: Datos críticos faltantes
    if fila.get("registro_con_datos_criticos_faltantes", False):
        puntaje += 1
        motivos.append("Datos críticos incompletos")

    # Regla 6: Permanencia prolongada
    if fila.get("permanencia_prolongada", False):
        puntaje += 1
        motivos.append("Permanencia prolongada")

    # Regla 7: Caso sin profesional responsable
    if fila.get("caso_sin_profesional", False):
        puntaje += 2
        motivos.append("Caso sin profesional responsable")

    # Regla 8: Caso vigente sin contacto reciente
    if fila.get("caso_sin_contacto_reciente", False):
        puntaje += 2
        motivos.append("Más de 21 días sin contacto reciente")

    # Regla 9: ID duplicado detectado
    if fila.get("id_usuario_duplicado", False):
        puntaje += 1
        motivos.append("ID de usuario duplicado en base original")

    if len(motivos) == 0:
        motivos_texto = "Sin señales relevantes de alerta"
    else:
        motivos_texto = "; ".join(motivos)

    nivel_alerta = clasificar_nivel_alerta(puntaje)
    accion_sugerida = definir_accion_sugerida(nivel_alerta)

    return pd.Series({
        "puntaje_alerta": puntaje,
        "nivel_alerta": nivel_alerta,
        "motivos_alerta": motivos_texto,
        "accion_sugerida": accion_sugerida
    })


# ------------------------------------------------------------
# 4. Generar tabla de alertas
# ------------------------------------------------------------

def generar_alertas(base):
    """
    Genera la tabla final de alertas tempranas.
    """

    columnas_base = [
        "id_usuario",
        "sexo",
        "edad",
        "tramo_edad",
        "comuna",
        "estado_caso",
        "profesional_responsable",
        "fecha_ingreso",
        "fecha_ultimo_contacto",
        "dias_sin_contacto",
        "cantidad_intervenciones",
        "dias_sin_intervencion",
        "estado_pii",
        "porcentaje_avance",
        "cantidad_controles",
        "cantidad_inasistencias",
        "dias_para_proximo_control",
        "dias_permanencia_estimados",
        "caso_vigente"
    ]

    columnas_disponibles = [
        columna for columna in columnas_base if columna in base.columns
    ]

    alertas_calculadas = base.apply(calcular_alerta_fila, axis=1)

    alertas = pd.concat(
        [
            base[columnas_disponibles],
            alertas_calculadas
        ],
        axis=1
    )

    # Ordenar por prioridad
    orden_nivel = {
        "Alto": 1,
        "Medio": 2,
        "Bajo": 3
    }

    alertas["orden_alerta"] = alertas["nivel_alerta"].map(orden_nivel)

    alertas = alertas.sort_values(
        by=["orden_alerta", "puntaje_alerta", "dias_sin_contacto"],
        ascending=[True, False, False]
    )

    alertas = alertas.drop(columns=["orden_alerta"])

    return alertas


# ------------------------------------------------------------
# 5. Crear resúmenes
# ------------------------------------------------------------

def crear_resumenes(alertas):
    """
    Crea tablas resumen del sistema de alertas.
    """

    resumen_nivel = (
        alertas
        .groupby("nivel_alerta")
        .size()
        .reset_index(name="cantidad_casos")
    )

    orden = pd.CategoricalDtype(
        categories=["Alto", "Medio", "Bajo"],
        ordered=True
    )

    resumen_nivel["nivel_alerta"] = resumen_nivel["nivel_alerta"].astype(orden)

    resumen_nivel = resumen_nivel.sort_values("nivel_alerta")

    resumen_comuna = (
        alertas
        .groupby(["comuna", "nivel_alerta"], dropna=False)
        .size()
        .reset_index(name="cantidad_casos")
        .sort_values(["nivel_alerta", "cantidad_casos"], ascending=[True, False])
    )

    resumen_profesional = (
        alertas
        .groupby(["profesional_responsable", "nivel_alerta"], dropna=False)
        .size()
        .reset_index(name="cantidad_casos")
        .sort_values(["nivel_alerta", "cantidad_casos"], ascending=[True, False])
    )

    casos_alta = alertas[alertas["nivel_alerta"] == "Alto"].copy()

    casos_priorizados = casos_alta[
        [
            "id_usuario",
            "comuna",
            "estado_caso",
            "profesional_responsable",
            "puntaje_alerta",
            "motivos_alerta",
            "accion_sugerida"
        ]
    ].copy()

    return resumen_nivel, resumen_comuna, resumen_profesional, casos_priorizados


# ------------------------------------------------------------
# 6. Exportar alertas
# ------------------------------------------------------------

def exportar_alertas(alertas):
    """
    Exporta la tabla de alertas y sus resúmenes.
    """

    resumen_nivel, resumen_comuna, resumen_profesional, casos_priorizados = crear_resumenes(alertas)

    ruta_excel = RUTA_SALIDA / "alertas_tempranas.xlsx"
    ruta_csv = RUTA_SALIDA / "alertas_tempranas.csv"
    ruta_casos_alta = RUTA_SALIDA / "usuarios_alerta_alta.csv"

    with pd.ExcelWriter(ruta_excel, engine="openpyxl") as writer:
        alertas.to_excel(writer, sheet_name="detalle_alertas", index=False)
        resumen_nivel.to_excel(writer, sheet_name="resumen_nivel", index=False)
        resumen_comuna.to_excel(writer, sheet_name="resumen_comuna", index=False)
        resumen_profesional.to_excel(writer, sheet_name="resumen_profesional", index=False)
        casos_priorizados.to_excel(writer, sheet_name="casos_priorizados", index=False)

    alertas.to_csv(ruta_csv, index=False, encoding="utf-8-sig")
    casos_priorizados.to_csv(ruta_casos_alta, index=False, encoding="utf-8-sig")

    print("Sistema de alertas tempranas generado correctamente.")
    print(f"Archivo Excel generado en: {ruta_excel}")
    print(f"Archivo CSV generado en: {ruta_csv}")
    print(f"Casos de alerta alta exportados en: {ruta_casos_alta}")
    print("")
    print("Resumen por nivel de alerta:")
    print(resumen_nivel)
    print("")
    print("Casos priorizados con alerta alta:")
    print(casos_priorizados.head(10))


# ------------------------------------------------------------
# 7. Ejecución principal
# ------------------------------------------------------------

def ejecutar_alertas_tempranas():
    """
    Ejecuta el proceso completo de generación de alertas tempranas.
    """

    base = cargar_base_consolidada()
    base = preparar_base(base)

    alertas = generar_alertas(base)

    exportar_alertas(alertas)


if __name__ == "__main__":
    ejecutar_alertas_tempranas()