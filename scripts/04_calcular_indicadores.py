# ============================================================
# Proyecto: Monitoreo de Gestión y Alertas Tempranas para MCA
# Archivo: 04_calcular_indicadores.py
# Objetivo: Calcular indicadores de gestión técnica y operativa
#           a partir de la base consolidada del programa MCA.
# ============================================================

import pandas as pd
import numpy as np
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
    Convierte una serie a valores booleanos de forma robusta.
    Sirve cuando los archivos CSV guardan True/False como texto.
    """

    return serie.astype(str).str.lower().isin(["true", "1", "sí", "si"])


def porcentaje(numerador, denominador):
    """
    Calcula porcentaje evitando división por cero.
    """

    if denominador == 0:
        return 0

    return round((numerador / denominador) * 100, 2)


def promedio(serie):
    """
    Calcula promedio controlando valores faltantes.
    """

    if len(serie.dropna()) == 0:
        return 0

    return round(serie.mean(), 2)


def clasificar_semaforo(resultado, meta, sentido):
    """
    Clasifica el resultado del indicador según meta y sentido esperado.

    sentido = 'mayor_mejor': valores altos son positivos.
    sentido = 'menor_mejor': valores bajos son positivos.
    """

    if sentido == "mayor_mejor":
        if resultado >= meta:
            return "Cumple"
        elif resultado >= meta * 0.8:
            return "En observación"
        else:
            return "Crítico"

    if sentido == "menor_mejor":
        if resultado <= meta:
            return "Cumple"
        elif resultado <= meta * 1.2:
            return "En observación"
        else:
            return "Crítico"

    return "Sin clasificación"


def crear_indicador(
    lista,
    dimension,
    indicador,
    formula,
    resultado,
    unidad,
    meta,
    sentido,
    periodicidad,
    fuente,
    interpretacion
):
    """
    Agrega un indicador calculado a la tabla final.
    """

    estado = clasificar_semaforo(resultado, meta, sentido)

    lista.append({
        "dimension": dimension,
        "indicador": indicador,
        "formula": formula,
        "resultado": resultado,
        "unidad": unidad,
        "meta_referencial": meta,
        "sentido_esperado": sentido,
        "estado": estado,
        "periodicidad_sugerida": periodicidad,
        "fuente_simulada": fuente,
        "interpretacion": interpretacion
    })


# ------------------------------------------------------------
# 1. Cargar base consolidada
# ------------------------------------------------------------

def cargar_base_consolidada():
    """
    Carga la base consolidada generada en el paso anterior.
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
# 2. Preparar variables para indicadores
# ------------------------------------------------------------

def preparar_base(base):
    """
    Asegura formatos adecuados para calcular indicadores.
    """

    columnas_booleanas = [
        "id_usuario_duplicado",
        "tiene_pii_vigente",
        "tiene_control_proximo_7_dias",
        "caso_vigente",
        "caso_sin_contacto_reciente",
        "caso_sin_intervencion_reciente",
        "pii_vencido_o_no_registrado",
        "caso_con_inasistencias",
        "caso_con_inasistencias_reiteradas",
        "caso_sin_profesional",
        "registro_con_datos_criticos_faltantes",
        "permanencia_prolongada"
    ]

    for columna in columnas_booleanas:
        if columna in base.columns:
            base[columna] = convertir_a_booleano(base[columna])

    columnas_numericas = [
        "edad",
        "dias_sin_contacto",
        "dias_desde_ingreso",
        "cantidad_intervenciones",
        "intervenciones_no_asiste",
        "intervenciones_realizadas",
        "dias_sin_intervencion",
        "porcentaje_avance",
        "dias_desde_actualizacion_pii",
        "cantidad_controles",
        "cantidad_inasistencias",
        "cantidad_asistencias",
        "dias_para_proximo_control",
        "dias_permanencia",
        "dias_permanencia_estimados"
    ]

    for columna in columnas_numericas:
        if columna in base.columns:
            base[columna] = pd.to_numeric(base[columna], errors="coerce")

    return base


# ------------------------------------------------------------
# 3. Calcular indicadores
# ------------------------------------------------------------

def calcular_indicadores(base):
    """
    Calcula indicadores de gestión técnica y operativa.
    """

    indicadores = []

    total_usuarios = len(base)
    casos_vigentes = base["caso_vigente"].sum()
    base_vigentes = base[base["caso_vigente"]].copy()

    total_controles = base["cantidad_controles"].sum()
    total_inasistencias = base["cantidad_inasistencias"].sum()

    # --------------------------------------------------------
    # Cobertura y estado de casos
    # --------------------------------------------------------

    crear_indicador(
        indicadores,
        dimension="Cobertura",
        indicador="Casos vigentes",
        formula="Total de usuarios con estado de caso vigente",
        resultado=int(casos_vigentes),
        unidad="casos",
        meta=50,
        sentido="mayor_mejor",
        periodicidad="Mensual",
        fuente="base_consolidada_mca",
        interpretacion="Cantidad de casos activos que requieren seguimiento operativo."
    )

    crear_indicador(
        indicadores,
        dimension="Cobertura",
        indicador="% de casos vigentes sobre el total consolidado",
        formula="Casos vigentes / total de usuarios consolidados * 100",
        resultado=porcentaje(casos_vigentes, total_usuarios),
        unidad="%",
        meta=60,
        sentido="mayor_mejor",
        periodicidad="Mensual",
        fuente="base_consolidada_mca",
        interpretacion="Proporción de usuarios que se encuentran activos dentro del programa."
    )

    # --------------------------------------------------------
    # Seguimiento
    # --------------------------------------------------------

    crear_indicador(
        indicadores,
        dimension="Seguimiento",
        indicador="Promedio de intervenciones por caso vigente",
        formula="Total de intervenciones en casos vigentes / total de casos vigentes",
        resultado=promedio(base_vigentes["cantidad_intervenciones"]),
        unidad="intervenciones",
        meta=3,
        sentido="mayor_mejor",
        periodicidad="Mensual",
        fuente="intervenciones",
        interpretacion="Mide intensidad promedio del seguimiento técnico registrado."
    )

    crear_indicador(
        indicadores,
        dimension="Seguimiento",
        indicador="% de casos vigentes con intervención reciente",
        formula="Casos vigentes sin más de 21 días desde última intervención / casos vigentes * 100",
        resultado=porcentaje(
            casos_vigentes - base_vigentes["caso_sin_intervencion_reciente"].sum(),
            casos_vigentes
        ),
        unidad="%",
        meta=80,
        sentido="mayor_mejor",
        periodicidad="Semanal/Mensual",
        fuente="intervenciones",
        interpretacion="Evalúa oportunidad del seguimiento técnico reciente."
    )

    crear_indicador(
        indicadores,
        dimension="Seguimiento",
        indicador="% de casos vigentes sin contacto reciente",
        formula="Casos vigentes con más de 21 días sin contacto / casos vigentes * 100",
        resultado=porcentaje(
            base_vigentes["caso_sin_contacto_reciente"].sum(),
            casos_vigentes
        ),
        unidad="%",
        meta=15,
        sentido="menor_mejor",
        periodicidad="Semanal",
        fuente="usuarios_mca",
        interpretacion="Identifica casos activos que requieren revisión por falta de contacto reciente."
    )

    # --------------------------------------------------------
    # Plan de Intervención Individual
    # --------------------------------------------------------

    crear_indicador(
        indicadores,
        dimension="Plan de Intervención Individual",
        indicador="% de casos vigentes con PII vigente",
        formula="Casos vigentes con PII vigente / casos vigentes * 100",
        resultado=porcentaje(
            base_vigentes["tiene_pii_vigente"].sum(),
            casos_vigentes
        ),
        unidad="%",
        meta=85,
        sentido="mayor_mejor",
        periodicidad="Mensual",
        fuente="planes_intervencion",
        interpretacion="Mide cobertura de planes vigentes en casos activos."
    )

    crear_indicador(
        indicadores,
        dimension="Plan de Intervención Individual",
        indicador="% de casos con PII vencido o no registrado",
        formula="Casos con PII vencido o no registrado / total usuarios consolidados * 100",
        resultado=porcentaje(
            base["pii_vencido_o_no_registrado"].sum(),
            total_usuarios
        ),
        unidad="%",
        meta=10,
        sentido="menor_mejor",
        periodicidad="Mensual",
        fuente="planes_intervencion",
        interpretacion="Detecta brechas de actualización o registro del plan de intervención."
    )

    crear_indicador(
        indicadores,
        dimension="Plan de Intervención Individual",
        indicador="Promedio de avance PII en casos vigentes",
        formula="Promedio del porcentaje de avance PII en casos vigentes",
        resultado=promedio(base_vigentes["porcentaje_avance"]),
        unidad="%",
        meta=50,
        sentido="mayor_mejor",
        periodicidad="Mensual",
        fuente="planes_intervencion",
        interpretacion="Entrega una aproximación del avance técnico registrado para casos activos."
    )

    # --------------------------------------------------------
    # Asistencia y controles
    # --------------------------------------------------------

    crear_indicador(
        indicadores,
        dimension="Asistencia y controles",
        indicador="Tasa de inasistencia a controles/audiencias",
        formula="Total de inasistencias / total de controles registrados * 100",
        resultado=porcentaje(total_inasistencias, total_controles),
        unidad="%",
        meta=20,
        sentido="menor_mejor",
        periodicidad="Mensual",
        fuente="controles_audiencias",
        interpretacion="Mide la proporción de inasistencias registradas en controles, citaciones o audiencias."
    )

    crear_indicador(
        indicadores,
        dimension="Asistencia y controles",
        indicador="Casos con inasistencias reiteradas",
        formula="Total de usuarios con dos o más inasistencias registradas",
        resultado=int(base["caso_con_inasistencias_reiteradas"].sum()),
        unidad="casos",
        meta=5,
        sentido="menor_mejor",
        periodicidad="Semanal/Mensual",
        fuente="controles_audiencias",
        interpretacion="Identifica casos que requieren priorización por reiteración de inasistencias."
    )

    # --------------------------------------------------------
    # Calidad de información
    # --------------------------------------------------------

    crear_indicador(
        indicadores,
        dimension="Calidad de información",
        indicador="% de registros con datos críticos faltantes",
        formula="Registros con datos críticos faltantes / total usuarios consolidados * 100",
        resultado=porcentaje(
            base["registro_con_datos_criticos_faltantes"].sum(),
            total_usuarios
        ),
        unidad="%",
        meta=5,
        sentido="menor_mejor",
        periodicidad="Mensual",
        fuente="usuarios_mca / planes_intervencion",
        interpretacion="Evalúa presencia de campos críticos incompletos para seguimiento y trazabilidad."
    )

    crear_indicador(
        indicadores,
        dimension="Calidad de información",
        indicador="Casos sin profesional responsable",
        formula="Total de casos sin profesional responsable asignado",
        resultado=int(base["caso_sin_profesional"].sum()),
        unidad="casos",
        meta=0,
        sentido="menor_mejor",
        periodicidad="Semanal",
        fuente="usuarios_mca",
        interpretacion="Controla asignación mínima de responsable para seguimiento de casos."
    )

    crear_indicador(
        indicadores,
        dimension="Calidad de información",
        indicador="IDs duplicados detectados",
        formula="Total de usuarios marcados con id_usuario duplicado",
        resultado=int(base["id_usuario_duplicado"].sum()),
        unidad="casos",
        meta=0,
        sentido="menor_mejor",
        periodicidad="Mensual",
        fuente="usuarios_mca",
        interpretacion="Permite monitorear duplicidades en la base principal de usuarios."
    )

    # --------------------------------------------------------
    # Permanencia
    # --------------------------------------------------------

    crear_indicador(
        indicadores,
        dimension="Permanencia",
        indicador="Promedio de días de permanencia estimada",
        formula="Promedio de días entre ingreso y fecha de corte o egreso",
        resultado=promedio(base["dias_permanencia_estimados"]),
        unidad="días",
        meta=180,
        sentido="menor_mejor",
        periodicidad="Mensual",
        fuente="usuarios_mca / egresos",
        interpretacion="Aproxima duración promedio de los casos en seguimiento."
    )

    crear_indicador(
        indicadores,
        dimension="Permanencia",
        indicador="Casos con permanencia prolongada",
        formula="Total de casos con más de 240 días de permanencia estimada",
        resultado=int(base["permanencia_prolongada"].sum()),
        unidad="casos",
        meta=10,
        sentido="menor_mejor",
        periodicidad="Mensual",
        fuente="usuarios_mca / egresos",
        interpretacion="Identifica casos que podrían requerir revisión por extensión del seguimiento."
    )

    tabla_indicadores = pd.DataFrame(indicadores)

    return tabla_indicadores


# ------------------------------------------------------------
# 4. Crear resúmenes complementarios
# ------------------------------------------------------------

def crear_resumenes(base, tabla_indicadores):
    """
    Crea tablas resumen para apoyar la revisión de indicadores.
    """

    resumen_dimension = (
        tabla_indicadores
        .groupby(["dimension", "estado"])
        .size()
        .reset_index(name="cantidad_indicadores")
        .sort_values(["dimension", "estado"])
    )

    resumen_estado_indicadores = (
        tabla_indicadores
        .groupby("estado")
        .size()
        .reset_index(name="cantidad_indicadores")
        .sort_values("cantidad_indicadores", ascending=False)
    )

    resumen_estado_casos = (
        base
        .groupby("estado_caso")
        .size()
        .reset_index(name="cantidad")
        .sort_values("cantidad", ascending=False)
    )

    resumen_pii = (
        base
        .groupby("estado_pii", dropna=False)
        .size()
        .reset_index(name="cantidad")
        .sort_values("cantidad", ascending=False)
    )

    resumen_comuna = (
        base
        .groupby("comuna", dropna=False)
        .size()
        .reset_index(name="cantidad")
        .sort_values("cantidad", ascending=False)
    )

    return (
        resumen_dimension,
        resumen_estado_indicadores,
        resumen_estado_casos,
        resumen_pii,
        resumen_comuna
    )


# ------------------------------------------------------------
# 5. Exportar indicadores
# ------------------------------------------------------------

def exportar_indicadores(base, tabla_indicadores):
    """
    Exporta indicadores en formato Excel y CSV.
    """

    (
        resumen_dimension,
        resumen_estado_indicadores,
        resumen_estado_casos,
        resumen_pii,
        resumen_comuna
    ) = crear_resumenes(base, tabla_indicadores)

    ruta_excel = RUTA_SALIDA / "indicadores_gestion.xlsx"
    ruta_csv = RUTA_SALIDA / "indicadores_gestion.csv"

    with pd.ExcelWriter(ruta_excel, engine="openpyxl") as writer:
        tabla_indicadores.to_excel(writer, sheet_name="indicadores", index=False)
        resumen_estado_indicadores.to_excel(writer, sheet_name="resumen_estados", index=False)
        resumen_dimension.to_excel(writer, sheet_name="resumen_dimension", index=False)
        resumen_estado_casos.to_excel(writer, sheet_name="resumen_casos", index=False)
        resumen_pii.to_excel(writer, sheet_name="resumen_pii", index=False)
        resumen_comuna.to_excel(writer, sheet_name="resumen_comuna", index=False)

    tabla_indicadores.to_csv(ruta_csv, index=False, encoding="utf-8-sig")

    print("Cálculo de indicadores de gestión finalizado.")
    print(f"Indicadores Excel generados en: {ruta_excel}")
    print(f"Indicadores CSV generados en: {ruta_csv}")
    print("")
    print("Resumen de indicadores por estado:")
    print(resumen_estado_indicadores)
    print("")
    print("Indicadores calculados:")
    print(tabla_indicadores[["dimension", "indicador", "resultado", "unidad", "estado"]])


# ------------------------------------------------------------
# 6. Ejecución principal
# ------------------------------------------------------------

def ejecutar_calculo_indicadores():
    """
    Ejecuta el cálculo completo de indicadores.
    """

    base = cargar_base_consolidada()
    base = preparar_base(base)

    tabla_indicadores = calcular_indicadores(base)

    exportar_indicadores(base, tabla_indicadores)


if __name__ == "__main__":
    ejecutar_calculo_indicadores()