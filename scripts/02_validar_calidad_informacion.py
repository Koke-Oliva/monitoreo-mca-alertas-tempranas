# ============================================================
# Proyecto: Monitoreo de Gestión y Alertas Tempranas para MCA
# Archivo: 02_validar_calidad_informacion.py
# Objetivo: Validar la calidad de las bases sintéticas generadas
#           para detectar inconsistencias operativas.
# ============================================================

import pandas as pd
from pathlib import Path


# ------------------------------------------------------------
# Configuración general
# ------------------------------------------------------------

RUTA_BASE = Path(__file__).resolve().parent.parent
RUTA_ENTRADA = RUTA_BASE / "data" / "simulated"
RUTA_SALIDA = RUTA_BASE / "data" / "output"

RUTA_SALIDA.mkdir(parents=True, exist_ok=True)

FECHA_CORTE = pd.Timestamp("2026-05-01")


# ------------------------------------------------------------
# Funciones auxiliares
# ------------------------------------------------------------

def agregar_inconsistencia(
    registros,
    base,
    id_registro,
    id_usuario,
    tipo_inconsistencia,
    descripcion,
    nivel,
    campo,
    valor_detectado,
    recomendacion
):
    """
    Agrega una inconsistencia detectada al listado general.
    """

    registros.append({
        "base": base,
        "id_registro": id_registro,
        "id_usuario": id_usuario,
        "tipo_inconsistencia": tipo_inconsistencia,
        "descripcion": descripcion,
        "nivel": nivel,
        "campo": campo,
        "valor_detectado": valor_detectado,
        "recomendacion": recomendacion
    })


def cargar_bases():
    """
    Carga todas las bases sintéticas del proyecto.
    """

    usuarios = pd.read_csv(
        RUTA_ENTRADA / "usuarios_mca.csv",
        parse_dates=["fecha_ingreso", "fecha_ultimo_contacto"]
    )

    intervenciones = pd.read_csv(
        RUTA_ENTRADA / "intervenciones.csv",
        parse_dates=["fecha_intervencion"]
    )

    planes = pd.read_csv(
        RUTA_ENTRADA / "planes_intervencion.csv",
        parse_dates=["fecha_creacion_pii", "fecha_ultima_actualizacion"]
    )

    controles = pd.read_csv(
        RUTA_ENTRADA / "controles_audiencias.csv",
        parse_dates=["fecha_control"]
    )

    egresos = pd.read_csv(
        RUTA_ENTRADA / "egresos.csv",
        parse_dates=["fecha_egreso"]
    )

    return usuarios, intervenciones, planes, controles, egresos


# ------------------------------------------------------------
# 1. Validar base de usuarios
# ------------------------------------------------------------

def validar_usuarios(usuarios, registros):
    """
    Valida inconsistencias en la base principal de usuarios.
    """

    # IDs duplicados
    duplicados = usuarios[usuarios["id_usuario"].duplicated(keep=False)]

    for _, fila in duplicados.iterrows():
        agregar_inconsistencia(
            registros,
            base="usuarios_mca",
            id_registro=fila["id_usuario"],
            id_usuario=fila["id_usuario"],
            tipo_inconsistencia="ID duplicado",
            descripcion="El identificador del usuario aparece más de una vez en la base principal.",
            nivel="Crítico",
            campo="id_usuario",
            valor_detectado=fila["id_usuario"],
            recomendacion="Revisar duplicidad del caso y mantener un único registro válido."
        )

    # Edad fuera de rango
    edades_invalidas = usuarios[
        (usuarios["edad"].isna()) |
        (usuarios["edad"] < 14) |
        (usuarios["edad"] > 21)
    ]

    for _, fila in edades_invalidas.iterrows():
        agregar_inconsistencia(
            registros,
            base="usuarios_mca",
            id_registro=fila["id_usuario"],
            id_usuario=fila["id_usuario"],
            tipo_inconsistencia="Edad fuera de rango",
            descripcion="La edad registrada está fuera del rango esperado para el contexto simulado.",
            nivel="Crítico",
            campo="edad",
            valor_detectado=fila["edad"],
            recomendacion="Verificar edad registrada y corregir si corresponde."
        )

    # Comuna faltante
    comuna_faltante = usuarios[usuarios["comuna"].isna()]

    for _, fila in comuna_faltante.iterrows():
        agregar_inconsistencia(
            registros,
            base="usuarios_mca",
            id_registro=fila["id_usuario"],
            id_usuario=fila["id_usuario"],
            tipo_inconsistencia="Comuna faltante",
            descripcion="El usuario no tiene comuna registrada.",
            nivel="Medio",
            campo="comuna",
            valor_detectado="Sin información",
            recomendacion="Completar comuna para mejorar trazabilidad territorial."
        )

    # Profesional faltante en caso vigente
    profesional_faltante = usuarios[
        (usuarios["estado_caso"] == "Vigente") &
        (usuarios["profesional_responsable"].isna())
    ]

    for _, fila in profesional_faltante.iterrows():
        agregar_inconsistencia(
            registros,
            base="usuarios_mca",
            id_registro=fila["id_usuario"],
            id_usuario=fila["id_usuario"],
            tipo_inconsistencia="Caso vigente sin profesional responsable",
            descripcion="El caso se encuentra vigente, pero no tiene profesional responsable asignado.",
            nivel="Crítico",
            campo="profesional_responsable",
            valor_detectado="Sin información",
            recomendacion="Asignar profesional responsable para seguimiento del caso."
        )

    # Sin contacto reciente
    usuarios["dias_sin_contacto"] = (FECHA_CORTE - usuarios["fecha_ultimo_contacto"]).dt.days

    sin_contacto_reciente = usuarios[
        (usuarios["estado_caso"] == "Vigente") &
        (usuarios["dias_sin_contacto"] > 21)
    ]

    for _, fila in sin_contacto_reciente.iterrows():
        agregar_inconsistencia(
            registros,
            base="usuarios_mca",
            id_registro=fila["id_usuario"],
            id_usuario=fila["id_usuario"],
            tipo_inconsistencia="Caso vigente sin contacto reciente",
            descripcion="El usuario vigente presenta más de 21 días sin contacto registrado.",
            nivel="Medio",
            campo="fecha_ultimo_contacto",
            valor_detectado=f"{fila['dias_sin_contacto']} días sin contacto",
            recomendacion="Revisar estado del seguimiento y actualizar contacto."
        )


# ------------------------------------------------------------
# 2. Validar base de intervenciones
# ------------------------------------------------------------

def validar_intervenciones(intervenciones, usuarios, registros):
    """
    Valida inconsistencias en la base de intervenciones.
    """

    usuarios_ref = usuarios.drop_duplicates("id_usuario", keep="first")
    ids_validos = set(usuarios_ref["id_usuario"])

    # Usuario inexistente
    intervenciones_sin_usuario = intervenciones[
        ~intervenciones["id_usuario"].isin(ids_validos)
    ]

    for _, fila in intervenciones_sin_usuario.iterrows():
        agregar_inconsistencia(
            registros,
            base="intervenciones",
            id_registro=fila["id_intervencion"],
            id_usuario=fila["id_usuario"],
            tipo_inconsistencia="Intervención asociada a usuario inexistente",
            descripcion="La intervención tiene un id_usuario que no existe en la base principal.",
            nivel="Crítico",
            campo="id_usuario",
            valor_detectado=fila["id_usuario"],
            recomendacion="Verificar relación entre intervención y usuario."
        )

    # Responsable faltante
    responsable_faltante = intervenciones[intervenciones["responsable"].isna()]

    for _, fila in responsable_faltante.iterrows():
        agregar_inconsistencia(
            registros,
            base="intervenciones",
            id_registro=fila["id_intervencion"],
            id_usuario=fila["id_usuario"],
            tipo_inconsistencia="Intervención sin responsable",
            descripcion="La intervención no tiene profesional responsable registrado.",
            nivel="Medio",
            campo="responsable",
            valor_detectado="Sin información",
            recomendacion="Completar responsable de la intervención."
        )

    # Fecha de intervención anterior al ingreso
    intervenciones_merge = intervenciones.merge(
        usuarios_ref[["id_usuario", "fecha_ingreso"]],
        on="id_usuario",
        how="left"
    )

    fechas_invalidas = intervenciones_merge[
        intervenciones_merge["fecha_intervencion"] < intervenciones_merge["fecha_ingreso"]
    ]

    for _, fila in fechas_invalidas.iterrows():
        agregar_inconsistencia(
            registros,
            base="intervenciones",
            id_registro=fila["id_intervencion"],
            id_usuario=fila["id_usuario"],
            tipo_inconsistencia="Intervención anterior al ingreso",
            descripcion="La intervención fue registrada antes de la fecha de ingreso del usuario.",
            nivel="Crítico",
            campo="fecha_intervencion",
            valor_detectado=fila["fecha_intervencion"].date(),
            recomendacion="Revisar fecha de intervención o fecha de ingreso."
        )


# ------------------------------------------------------------
# 3. Validar planes de intervención
# ------------------------------------------------------------

def validar_planes(planes, usuarios, registros):
    """
    Valida inconsistencias en la base de planes de intervención.
    """

    usuarios_ref = usuarios.drop_duplicates("id_usuario", keep="first")
    ids_validos = set(usuarios_ref["id_usuario"])

    # Plan asociado a usuario inexistente
    planes_sin_usuario = planes[~planes["id_usuario"].isin(ids_validos)]

    for _, fila in planes_sin_usuario.iterrows():
        agregar_inconsistencia(
            registros,
            base="planes_intervencion",
            id_registro=fila["id_plan"],
            id_usuario=fila["id_usuario"],
            tipo_inconsistencia="Plan asociado a usuario inexistente",
            descripcion="El plan tiene un id_usuario que no existe en la base principal.",
            nivel="Crítico",
            campo="id_usuario",
            valor_detectado=fila["id_usuario"],
            recomendacion="Verificar relación entre plan y usuario."
        )

    # PII no registrado
    planes_no_registrados = planes[planes["estado_pii"] == "No registrado"]

    for _, fila in planes_no_registrados.iterrows():
        agregar_inconsistencia(
            registros,
            base="planes_intervencion",
            id_registro=fila["id_plan"],
            id_usuario=fila["id_usuario"],
            tipo_inconsistencia="PII no registrado",
            descripcion="El usuario presenta estado de plan no registrado.",
            nivel="Crítico",
            campo="estado_pii",
            valor_detectado=fila["estado_pii"],
            recomendacion="Revisar registro del Plan de Intervención Individual."
        )

    # PII vencido
    planes_vencidos = planes[planes["estado_pii"] == "Vencido"]

    for _, fila in planes_vencidos.iterrows():
        agregar_inconsistencia(
            registros,
            base="planes_intervencion",
            id_registro=fila["id_plan"],
            id_usuario=fila["id_usuario"],
            tipo_inconsistencia="PII vencido",
            descripcion="El Plan de Intervención Individual se encuentra vencido.",
            nivel="Medio",
            campo="estado_pii",
            valor_detectado=fila["estado_pii"],
            recomendacion="Actualizar o revisar estado del plan."
        )

    # Última actualización antigua
    planes["dias_desde_actualizacion"] = (
        FECHA_CORTE - planes["fecha_ultima_actualizacion"]
    ).dt.days

    planes_sin_actualizacion_reciente = planes[
        planes["dias_desde_actualizacion"] > 90
    ]

    for _, fila in planes_sin_actualizacion_reciente.iterrows():
        agregar_inconsistencia(
            registros,
            base="planes_intervencion",
            id_registro=fila["id_plan"],
            id_usuario=fila["id_usuario"],
            tipo_inconsistencia="PII sin actualización reciente",
            descripcion="El plan presenta más de 90 días desde su última actualización.",
            nivel="Medio",
            campo="fecha_ultima_actualizacion",
            valor_detectado=f"{fila['dias_desde_actualizacion']} días",
            recomendacion="Revisar necesidad de actualización del plan."
        )


# ------------------------------------------------------------
# 4. Validar controles y audiencias
# ------------------------------------------------------------

def validar_controles(controles, usuarios, registros):
    """
    Valida inconsistencias en controles, citaciones y audiencias.
    """

    usuarios_ref = usuarios.drop_duplicates("id_usuario", keep="first")
    ids_validos = set(usuarios_ref["id_usuario"])

    # Control asociado a usuario inexistente
    controles_sin_usuario = controles[~controles["id_usuario"].isin(ids_validos)]

    for _, fila in controles_sin_usuario.iterrows():
        agregar_inconsistencia(
            registros,
            base="controles_audiencias",
            id_registro=fila["id_control"],
            id_usuario=fila["id_usuario"],
            tipo_inconsistencia="Control asociado a usuario inexistente",
            descripcion="El control tiene un id_usuario que no existe en la base principal.",
            nivel="Crítico",
            campo="id_usuario",
            valor_detectado=fila["id_usuario"],
            recomendacion="Verificar relación entre control/audiencia y usuario."
        )

    # Inasistencias
    inasistencias = controles[controles["asistencia"] == "No asiste"]

    for _, fila in inasistencias.iterrows():
        agregar_inconsistencia(
            registros,
            base="controles_audiencias",
            id_registro=fila["id_control"],
            id_usuario=fila["id_usuario"],
            tipo_inconsistencia="Inasistencia registrada",
            descripcion="El usuario presenta una inasistencia a control, citación o audiencia.",
            nivel="Medio",
            campo="asistencia",
            valor_detectado=fila["asistencia"],
            recomendacion="Revisar seguimiento y justificar o reagendar si corresponde."
        )

    # Audiencia próxima
    audiencias_proximas = controles[
        (controles["tipo_control"] == "Audiencia") &
        (controles["dias_para_control"] >= 0) &
        (controles["dias_para_control"] <= 7)
    ]

    for _, fila in audiencias_proximas.iterrows():
        agregar_inconsistencia(
            registros,
            base="controles_audiencias",
            id_registro=fila["id_control"],
            id_usuario=fila["id_usuario"],
            tipo_inconsistencia="Audiencia próxima",
            descripcion="El usuario presenta audiencia próxima dentro de los próximos 7 días.",
            nivel="Informativo",
            campo="dias_para_control",
            valor_detectado=f"{fila['dias_para_control']} días",
            recomendacion="Verificar preparación y contacto previo."
        )


# ------------------------------------------------------------
# 5. Validar egresos
# ------------------------------------------------------------

def validar_egresos(egresos, usuarios, registros):
    """
    Valida inconsistencias en la base de egresos.
    """

    usuarios_ref = usuarios.drop_duplicates("id_usuario", keep="first")
    ids_validos = set(usuarios_ref["id_usuario"])

    # Egreso asociado a usuario inexistente
    egresos_sin_usuario = egresos[~egresos["id_usuario"].isin(ids_validos)]

    for _, fila in egresos_sin_usuario.iterrows():
        agregar_inconsistencia(
            registros,
            base="egresos",
            id_registro=fila["id_egreso"],
            id_usuario=fila["id_usuario"],
            tipo_inconsistencia="Egreso asociado a usuario inexistente",
            descripcion="El egreso tiene un id_usuario que no existe en la base principal.",
            nivel="Crítico",
            campo="id_usuario",
            valor_detectado=fila["id_usuario"],
            recomendacion="Verificar relación entre egreso y usuario."
        )

    # Fecha de egreso anterior al ingreso
    egresos_merge = egresos.merge(
        usuarios_ref[["id_usuario", "fecha_ingreso"]],
        on="id_usuario",
        how="left"
    )

    egresos_invalidos = egresos_merge[
        egresos_merge["fecha_egreso"] < egresos_merge["fecha_ingreso"]
    ]

    for _, fila in egresos_invalidos.iterrows():
        agregar_inconsistencia(
            registros,
            base="egresos",
            id_registro=fila["id_egreso"],
            id_usuario=fila["id_usuario"],
            tipo_inconsistencia="Egreso anterior al ingreso",
            descripcion="La fecha de egreso es anterior a la fecha de ingreso.",
            nivel="Crítico",
            campo="fecha_egreso",
            valor_detectado=fila["fecha_egreso"].date(),
            recomendacion="Revisar fecha de ingreso y egreso del caso."
        )

    # Permanencia negativa
    permanencia_negativa = egresos[egresos["dias_permanencia"] < 0]

    for _, fila in permanencia_negativa.iterrows():
        agregar_inconsistencia(
            registros,
            base="egresos",
            id_registro=fila["id_egreso"],
            id_usuario=fila["id_usuario"],
            tipo_inconsistencia="Días de permanencia negativos",
            descripcion="El registro presenta días de permanencia negativos.",
            nivel="Crítico",
            campo="dias_permanencia",
            valor_detectado=fila["dias_permanencia"],
            recomendacion="Revisar fechas utilizadas para calcular permanencia."
        )


# ------------------------------------------------------------
# 6. Exportar reporte de validación
# ------------------------------------------------------------

def exportar_reporte(registros):
    """
    Exporta el reporte de inconsistencias en formato Excel y CSV.
    """

    reporte = pd.DataFrame(registros)

    if reporte.empty:
        reporte = pd.DataFrame(columns=[
            "base",
            "id_registro",
            "id_usuario",
            "tipo_inconsistencia",
            "descripcion",
            "nivel",
            "campo",
            "valor_detectado",
            "recomendacion"
        ])

    resumen_base = (
        reporte
        .groupby("base")
        .size()
        .reset_index(name="cantidad_inconsistencias")
        .sort_values("cantidad_inconsistencias", ascending=False)
    )

    resumen_tipo = (
        reporte
        .groupby("tipo_inconsistencia")
        .size()
        .reset_index(name="cantidad")
        .sort_values("cantidad", ascending=False)
    )

    resumen_nivel = (
        reporte
        .groupby("nivel")
        .size()
        .reset_index(name="cantidad")
        .sort_values("cantidad", ascending=False)
    )

    ruta_excel = RUTA_SALIDA / "reporte_validacion.xlsx"
    ruta_csv = RUTA_SALIDA / "reporte_validacion.csv"

    with pd.ExcelWriter(ruta_excel, engine="openpyxl") as writer:
        reporte.to_excel(writer, sheet_name="detalle_inconsistencias", index=False)
        resumen_base.to_excel(writer, sheet_name="resumen_por_base", index=False)
        resumen_tipo.to_excel(writer, sheet_name="resumen_por_tipo", index=False)
        resumen_nivel.to_excel(writer, sheet_name="resumen_por_nivel", index=False)

    reporte.to_csv(ruta_csv, index=False, encoding="utf-8-sig")

    print("Validación de calidad de información finalizada.")
    print(f"Reporte Excel generado en: {ruta_excel}")
    print(f"Reporte CSV generado en: {ruta_csv}")
    print("")
    print("Resumen por nivel:")
    print(resumen_nivel)
    print("")
    print("Resumen por base:")
    print(resumen_base)


# ------------------------------------------------------------
# 7. Ejecución principal
# ------------------------------------------------------------

def ejecutar_validacion():
    """
    Ejecuta todas las validaciones del proyecto.
    """

    usuarios, intervenciones, planes, controles, egresos = cargar_bases()

    registros = []

    validar_usuarios(usuarios, registros)
    validar_intervenciones(intervenciones, usuarios, registros)
    validar_planes(planes, usuarios, registros)
    validar_controles(controles, usuarios, registros)
    validar_egresos(egresos, usuarios, registros)

    exportar_reporte(registros)


if __name__ == "__main__":
    ejecutar_validacion()