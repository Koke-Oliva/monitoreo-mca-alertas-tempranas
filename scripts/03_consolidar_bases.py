# ============================================================
# Proyecto: Monitoreo de Gestión y Alertas Tempranas para MCA
# Archivo: 03_consolidar_bases.py
# Objetivo: Consolidar bases sintéticas para generar una base
#           maestra de seguimiento operativo.
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
# 1. Cargar bases
# ------------------------------------------------------------

def cargar_bases():
    """
    Carga las bases sintéticas necesarias para la consolidación.
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
# 2. Preparar base de usuarios
# ------------------------------------------------------------

def preparar_usuarios(usuarios):
    """
    Prepara la base principal de usuarios para evitar duplicaciones
    en la consolidación.
    """

    ids_duplicados = usuarios[
        usuarios["id_usuario"].duplicated(keep=False)
    ]["id_usuario"].unique()

    usuarios_ref = usuarios.drop_duplicates(
        subset="id_usuario",
        keep="first"
    ).copy()

    usuarios_ref["id_usuario_duplicado"] = usuarios_ref["id_usuario"].isin(ids_duplicados)

    usuarios_ref["dias_sin_contacto"] = (
        FECHA_CORTE - usuarios_ref["fecha_ultimo_contacto"]
    ).dt.days

    usuarios_ref["dias_desde_ingreso"] = (
        FECHA_CORTE - usuarios_ref["fecha_ingreso"]
    ).dt.days

    return usuarios_ref


# ------------------------------------------------------------
# 3. Consolidar intervenciones
# ------------------------------------------------------------

def consolidar_intervenciones(intervenciones):
    """
    Resume información de intervenciones por usuario.
    """

    resumen = (
        intervenciones
        .groupby("id_usuario")
        .agg(
            cantidad_intervenciones=("id_intervencion", "count"),
            ultima_intervencion=("fecha_intervencion", "max"),
            intervenciones_no_asiste=("resultado_intervencion", lambda x: (x == "No asiste").sum()),
            intervenciones_realizadas=("resultado_intervencion", lambda x: (x == "Realizada").sum())
        )
        .reset_index()
    )

    resumen["dias_sin_intervencion"] = (
        FECHA_CORTE - resumen["ultima_intervencion"]
    ).dt.days

    return resumen


# ------------------------------------------------------------
# 4. Consolidar planes de intervención
# ------------------------------------------------------------

def consolidar_planes(planes):
    """
    Obtiene el último registro de plan por usuario.
    """

    planes_ordenados = planes.sort_values(
        by=["id_usuario", "fecha_ultima_actualizacion"]
    )

    ultimo_plan = planes_ordenados.drop_duplicates(
        subset="id_usuario",
        keep="last"
    ).copy()

    ultimo_plan = ultimo_plan[
        [
            "id_usuario",
            "id_plan",
            "fecha_creacion_pii",
            "fecha_ultima_actualizacion",
            "estado_pii",
            "porcentaje_avance",
            "resultado_pii"
        ]
    ]

    ultimo_plan["dias_desde_actualizacion_pii"] = (
        FECHA_CORTE - ultimo_plan["fecha_ultima_actualizacion"]
    ).dt.days

    ultimo_plan["tiene_pii_vigente"] = ultimo_plan["estado_pii"] == "Vigente"

    return ultimo_plan


# ------------------------------------------------------------
# 5. Consolidar controles y audiencias
# ------------------------------------------------------------

def consolidar_controles(controles):
    """
    Resume controles, citaciones y audiencias por usuario.
    """

    resumen = (
        controles
        .groupby("id_usuario")
        .agg(
            cantidad_controles=("id_control", "count"),
            cantidad_inasistencias=("asistencia", lambda x: (x == "No asiste").sum()),
            cantidad_asistencias=("asistencia", lambda x: (x == "Asiste").sum()),
            proximo_control=("fecha_control", lambda x: x[x >= FECHA_CORTE].min() if any(x >= FECHA_CORTE) else pd.NaT),
            ultima_fecha_control=("fecha_control", "max")
        )
        .reset_index()
    )

    resumen["dias_para_proximo_control"] = (
        resumen["proximo_control"] - FECHA_CORTE
    ).dt.days

    resumen["tiene_control_proximo_7_dias"] = (
        (resumen["dias_para_proximo_control"] >= 0) &
        (resumen["dias_para_proximo_control"] <= 7)
    )

    return resumen


# ------------------------------------------------------------
# 6. Consolidar egresos
# ------------------------------------------------------------

def consolidar_egresos(egresos):
    """
    Prepara información de egresos por usuario.
    """

    columnas = [
        "id_usuario",
        "id_egreso",
        "fecha_egreso",
        "causal_egreso",
        "dias_permanencia",
        "pii_logrado"
    ]

    egresos_ref = egresos[columnas].copy()

    return egresos_ref


# ------------------------------------------------------------
# 7. Crear base consolidada
# ------------------------------------------------------------

def crear_base_consolidada():
    """
    Ejecuta la consolidación completa de las bases.
    """

    usuarios, intervenciones, planes, controles, egresos = cargar_bases()

    usuarios_ref = preparar_usuarios(usuarios)
    resumen_intervenciones = consolidar_intervenciones(intervenciones)
    resumen_planes = consolidar_planes(planes)
    resumen_controles = consolidar_controles(controles)
    resumen_egresos = consolidar_egresos(egresos)

    base = usuarios_ref.merge(
        resumen_intervenciones,
        on="id_usuario",
        how="left"
    )

    base = base.merge(
        resumen_planes,
        on="id_usuario",
        how="left"
    )

    base = base.merge(
        resumen_controles,
        on="id_usuario",
        how="left"
    )

    base = base.merge(
        resumen_egresos,
        on="id_usuario",
        how="left"
    )

    # --------------------------------------------------------
    # Completar valores faltantes en variables numéricas
    # --------------------------------------------------------

    columnas_numericas = [
        "cantidad_intervenciones",
        "intervenciones_no_asiste",
        "intervenciones_realizadas",
        "cantidad_controles",
        "cantidad_inasistencias",
        "cantidad_asistencias",
        "porcentaje_avance"
    ]

    for columna in columnas_numericas:
        if columna in base.columns:
            base[columna] = base[columna].fillna(0)

    # --------------------------------------------------------
    # Variables derivadas de gestión
    # --------------------------------------------------------

    base["caso_vigente"] = base["estado_caso"] == "Vigente"

    base["caso_sin_contacto_reciente"] = (
        (base["caso_vigente"]) &
        (base["dias_sin_contacto"] > 21)
    )

    base["caso_sin_intervencion_reciente"] = (
        (base["caso_vigente"]) &
        (base["dias_sin_intervencion"] > 21)
    )

    base["pii_vencido_o_no_registrado"] = base["estado_pii"].isin(
        ["Vencido", "No registrado"]
    )

    base["caso_con_inasistencias"] = base["cantidad_inasistencias"] >= 1

    base["caso_con_inasistencias_reiteradas"] = base["cantidad_inasistencias"] >= 2

    base["caso_sin_profesional"] = base["profesional_responsable"].isna()

    base["registro_con_datos_criticos_faltantes"] = (
        base["comuna"].isna() |
        base["profesional_responsable"].isna() |
        base["estado_pii"].isna()
    )

    # Para casos vigentes, usamos días desde ingreso como permanencia actual.
    # Para casos egresados, usamos los días de permanencia registrados en egresos.
    base["dias_permanencia_estimados"] = base["dias_permanencia"]

    base.loc[
        base["dias_permanencia_estimados"].isna(),
        "dias_permanencia_estimados"
    ] = base.loc[
        base["dias_permanencia_estimados"].isna(),
        "dias_desde_ingreso"
    ]

    base["permanencia_prolongada"] = base["dias_permanencia_estimados"] > 240

    return base


# ------------------------------------------------------------
# 8. Crear resúmenes de consolidación
# ------------------------------------------------------------

def crear_resumenes(base):
    """
    Crea tablas resumen para revisión rápida.
    """

    resumen_estado = (
        base
        .groupby("estado_caso")
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

    resumen_pii = (
        base
        .groupby("estado_pii", dropna=False)
        .size()
        .reset_index(name="cantidad")
        .sort_values("cantidad", ascending=False)
    )

    resumen_seguimiento = pd.DataFrame({
        "indicador": [
            "Total usuarios consolidados",
            "Casos vigentes",
            "Casos sin contacto reciente",
            "Casos sin intervención reciente",
            "Casos con PII vencido o no registrado",
            "Casos con inasistencias reiteradas",
            "Casos sin profesional responsable",
            "Registros con datos críticos faltantes"
        ],
        "valor": [
            len(base),
            base["caso_vigente"].sum(),
            base["caso_sin_contacto_reciente"].sum(),
            base["caso_sin_intervencion_reciente"].sum(),
            base["pii_vencido_o_no_registrado"].sum(),
            base["caso_con_inasistencias_reiteradas"].sum(),
            base["caso_sin_profesional"].sum(),
            base["registro_con_datos_criticos_faltantes"].sum()
        ]
    })

    return resumen_estado, resumen_comuna, resumen_pii, resumen_seguimiento


# ------------------------------------------------------------
# 9. Exportar resultados
# ------------------------------------------------------------

def exportar_consolidacion(base):
    """
    Exporta la base consolidada y sus resúmenes.
    """

    resumen_estado, resumen_comuna, resumen_pii, resumen_seguimiento = crear_resumenes(base)

    ruta_excel = RUTA_SALIDA / "base_consolidada_mca.xlsx"
    ruta_csv = RUTA_SALIDA / "base_consolidada_mca.csv"

    with pd.ExcelWriter(ruta_excel, engine="openpyxl") as writer:
        base.to_excel(writer, sheet_name="base_consolidada", index=False)
        resumen_seguimiento.to_excel(writer, sheet_name="resumen_seguimiento", index=False)
        resumen_estado.to_excel(writer, sheet_name="resumen_estado", index=False)
        resumen_comuna.to_excel(writer, sheet_name="resumen_comuna", index=False)
        resumen_pii.to_excel(writer, sheet_name="resumen_pii", index=False)

    base.to_csv(ruta_csv, index=False, encoding="utf-8-sig")

    print("Consolidación de bases finalizada.")
    print(f"Base consolidada Excel generada en: {ruta_excel}")
    print(f"Base consolidada CSV generada en: {ruta_csv}")
    print("")
    print("Resumen general de seguimiento:")
    print(resumen_seguimiento)


# ------------------------------------------------------------
# 10. Ejecución principal
# ------------------------------------------------------------

def ejecutar_consolidacion():
    """
    Ejecuta el proceso completo de consolidación.
    """

    base = crear_base_consolidada()
    exportar_consolidacion(base)


if __name__ == "__main__":
    ejecutar_consolidacion()