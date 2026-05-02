# ============================================================
# Proyecto: Monitoreo de Gestión y Alertas Tempranas para MCA
# Archivo: 08_generar_informe_html.py
# Objetivo: Generar un informe HTML ejecutivo a partir de los
#           resultados del proyecto.
# ============================================================

import pandas as pd
from pathlib import Path
from datetime import datetime


# ------------------------------------------------------------
# Configuración general
# ------------------------------------------------------------

RUTA_BASE = Path(__file__).resolve().parent.parent

RUTA_OUTPUT = RUTA_BASE / "data" / "output"
RUTA_REPORT = RUTA_BASE / "report"
RUTA_DOCS = RUTA_BASE / "docs"

RUTA_REPORT.mkdir(parents=True, exist_ok=True)
RUTA_DOCS.mkdir(parents=True, exist_ok=True)

RUTA_INFORME_REPORT = RUTA_REPORT / "informe_mca_monitoreo.html"
RUTA_INFORME_DOCS = RUTA_DOCS / "index.html"


# ------------------------------------------------------------
# Funciones auxiliares
# ------------------------------------------------------------

def convertir_a_booleano(serie):
    """
    Convierte valores booleanos guardados como texto.
    """

    return serie.astype(str).str.lower().isin(["true", "1", "sí", "si"])


def cargar_archivos():
    """
    Carga los archivos generados durante el proyecto.
    """

    base = pd.read_csv(RUTA_OUTPUT / "base_consolidada_mca.csv")
    indicadores = pd.read_csv(RUTA_OUTPUT / "indicadores_gestion.csv")
    alertas = pd.read_csv(RUTA_OUTPUT / "alertas_tempranas.csv")
    validacion = pd.read_csv(RUTA_OUTPUT / "reporte_validacion.csv")

    return base, indicadores, alertas, validacion


def tabla_html(dataframe, columnas=None, max_filas=20):
    """
    Convierte un DataFrame a tabla HTML con formato estándar.
    """

    if dataframe.empty:
        return "<p>No hay registros disponibles.</p>"

    df = dataframe.copy()

    if columnas is not None:
        columnas_disponibles = [col for col in columnas if col in df.columns]
        df = df[columnas_disponibles]

    df = df.head(max_filas)

    return df.to_html(
        index=False,
        classes="tabla",
        border=0,
        justify="left"
    )


def tarjeta_kpi(titulo, valor, subtitulo):
    """
    Crea una tarjeta KPI en HTML.
    """

    return f"""
    <div class="kpi-card">
        <div class="kpi-title">{titulo}</div>
        <div class="kpi-value">{valor}</div>
        <div class="kpi-subtitle">{subtitulo}</div>
    </div>
    """


def preparar_resumenes(base, indicadores, alertas, validacion):
    """
    Prepara resúmenes principales para el informe.
    """

    if "caso_vigente" in base.columns:
        base["caso_vigente"] = convertir_a_booleano(base["caso_vigente"])

    total_usuarios = len(base)
    casos_vigentes = int(base["caso_vigente"].sum()) if "caso_vigente" in base.columns else 0

    total_inconsistencias = len(validacion)
    inconsistencias_criticas = int((validacion["nivel"] == "Crítico").sum())

    resumen_alertas = (
        alertas
        .groupby("nivel_alerta")
        .size()
        .reset_index(name="cantidad_casos")
    )

    resumen_indicadores = (
        indicadores
        .groupby("estado")
        .size()
        .reset_index(name="cantidad_indicadores")
    )

    resumen_inconsistencias = (
        validacion
        .groupby(["nivel", "tipo_inconsistencia"])
        .size()
        .reset_index(name="cantidad")
        .sort_values("cantidad", ascending=False)
    )

    indicadores_criticos = indicadores[
        indicadores["estado"] == "Crítico"
    ].copy()

    casos_alerta_alta = alertas[
        alertas["nivel_alerta"] == "Alto"
    ].copy()

    return {
        "total_usuarios": total_usuarios,
        "casos_vigentes": casos_vigentes,
        "total_inconsistencias": total_inconsistencias,
        "inconsistencias_criticas": inconsistencias_criticas,
        "resumen_alertas": resumen_alertas,
        "resumen_indicadores": resumen_indicadores,
        "resumen_inconsistencias": resumen_inconsistencias,
        "indicadores_criticos": indicadores_criticos,
        "casos_alerta_alta": casos_alerta_alta
    }


# ------------------------------------------------------------
# Generar informe HTML
# ------------------------------------------------------------

def generar_html(base, indicadores, alertas, validacion, resumenes):
    """
    Genera el contenido HTML completo del informe.
    """

    fecha_generacion = datetime.now().strftime("%d-%m-%Y %H:%M")

    total_alertas_altas = int(
        (alertas["nivel_alerta"] == "Alto").sum()
    )

    total_indicadores_criticos = int(
        (indicadores["estado"] == "Crítico").sum()
    )

    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Monitoreo de Gestión y Alertas Tempranas MCA</title>

    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            background-color: #f4f6f8;
            color: #222;
            line-height: 1.6;
        }}

        header {{
            background-color: #1f2937;
            color: white;
            padding: 40px 60px;
        }}

        header h1 {{
            margin: 0;
            font-size: 32px;
        }}

        header p {{
            margin-top: 12px;
            font-size: 16px;
            max-width: 900px;
        }}

        main {{
            max-width: 1100px;
            margin: 30px auto;
            padding: 0 20px;
        }}

        section {{
            background-color: white;
            margin-bottom: 24px;
            padding: 28px;
            border-radius: 10px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        }}

        h2 {{
            color: #1f2937;
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 8px;
        }}

        h3 {{
            color: #374151;
            margin-top: 24px;
        }}

        .kpi-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 18px;
            margin-top: 20px;
        }}

        .kpi-card {{
            background-color: #f9fafb;
            border-left: 5px solid #1f2937;
            padding: 18px;
            border-radius: 8px;
        }}

        .kpi-title {{
            font-size: 14px;
            color: #4b5563;
            margin-bottom: 8px;
        }}

        .kpi-value {{
            font-size: 30px;
            font-weight: bold;
            color: #111827;
        }}

        .kpi-subtitle {{
            font-size: 13px;
            color: #6b7280;
            margin-top: 6px;
        }}

        .tabla {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
            font-size: 14px;
        }}

        .tabla th {{
            background-color: #1f2937;
            color: white;
            padding: 10px;
            text-align: left;
        }}

        .tabla td {{
            border-bottom: 1px solid #e5e7eb;
            padding: 9px;
            vertical-align: top;
        }}

        .tabla tr:nth-child(even) {{
            background-color: #f9fafb;
        }}

        .nota {{
            background-color: #eef2ff;
            border-left: 5px solid #4338ca;
            padding: 14px;
            margin-top: 16px;
            border-radius: 6px;
        }}

        .advertencia {{
            background-color: #fff7ed;
            border-left: 5px solid #f97316;
            padding: 14px;
            margin-top: 16px;
            border-radius: 6px;
        }}

        footer {{
            text-align: center;
            padding: 24px;
            color: #6b7280;
            font-size: 13px;
        }}
    </style>
</head>

<body>

<header>
    <h1>Monitoreo de Gestión y Alertas Tempranas para Programa MCA</h1>
    <p>
        Mini proyecto de administración, validación y análisis de información operativa
        para un programa de Medida Cautelar Ambulatoria, utilizando datos sintéticos.
    </p>
</header>

<main>

<section>
    <h2>1. Resumen ejecutivo</h2>

    <p>
        Este proyecto simula un flujo de trabajo orientado a la gestión de información
        de un programa MCA. El proceso considera generación de datos sintéticos,
        validación de calidad, consolidación de bases, cálculo de indicadores,
        generación de alertas tempranas y exportación de resultados a formatos
        revisables por equipos técnicos o administrativos.
    </p>

    <div class="kpi-container">
        {tarjeta_kpi("Usuarios consolidados", resumenes["total_usuarios"], "Base maestra sin duplicados")}
        {tarjeta_kpi("Casos vigentes", resumenes["casos_vigentes"], "Casos activos que requieren seguimiento")}
        {tarjeta_kpi("Alertas altas", total_alertas_altas, "Casos priorizados para revisión")}
        {tarjeta_kpi("Indicadores críticos", total_indicadores_criticos, "Indicadores bajo umbral esperado")}
        {tarjeta_kpi("Inconsistencias detectadas", resumenes["total_inconsistencias"], "Registros observados en validación")}
        {tarjeta_kpi("Inconsistencias críticas", resumenes["inconsistencias_criticas"], "Errores de mayor prioridad")}
    </div>

    <div class="nota">
        El proyecto no utiliza datos reales de adolescentes, instituciones ni causas judiciales.
        Toda la información fue generada de forma sintética para fines demostrativos.
    </div>
</section>


<section>
    <h2>2. Flujo general del proyecto</h2>

    <p>El flujo aplicado fue el siguiente:</p>

    <ol>
        <li>Generación de bases sintéticas operativas.</li>
        <li>Validación de calidad de información.</li>
        <li>Consolidación de bases en una tabla maestra.</li>
        <li>Cálculo de indicadores de gestión.</li>
        <li>Generación de alertas tempranas basadas en reglas.</li>
        <li>Creación de base SQLite y ejecución de consultas SQL.</li>
        <li>Exportación de resultados a CSV, Excel e informe HTML.</li>
    </ol>
</section>


<section>
    <h2>3. Indicadores de gestión</h2>

    <p>
        Los indicadores fueron definidos con dimensión, fórmula, resultado,
        unidad, meta referencial, periodicidad sugerida, fuente simulada
        e interpretación.
    </p>

    <h3>Resumen de indicadores por estado</h3>
    {tabla_html(resumenes["resumen_indicadores"])}

    <h3>Indicadores críticos</h3>
    {tabla_html(
        resumenes["indicadores_criticos"],
        columnas=[
            "dimension",
            "indicador",
            "resultado",
            "unidad",
            "meta_referencial",
            "estado",
            "interpretacion"
        ],
        max_filas=20
    )}
</section>


<section>
    <h2>4. Calidad de información</h2>

    <p>
        La validación de calidad permite identificar problemas de registro,
        duplicidades, datos faltantes, inconsistencias temporales y brechas
        de seguimiento operativo.
    </p>

    <h3>Principales inconsistencias detectadas</h3>
    {tabla_html(
        resumenes["resumen_inconsistencias"],
        columnas=[
            "nivel",
            "tipo_inconsistencia",
            "cantidad"
        ],
        max_filas=15
    )}

    <div class="advertencia">
        Las inconsistencias fueron generadas de forma controlada para demostrar
        la capacidad del flujo de detectar problemas operativos y de calidad de datos.
    </div>
</section>


<section>
    <h2>5. Sistema de alertas tempranas</h2>

    <p>
        El sistema de alertas tempranas se basa en reglas simples, explicables
        y trazables. Cada caso recibe un puntaje según criterios operativos
        como ausencia de intervención reciente, inasistencias, PII vencido,
        falta de contacto, permanencia prolongada o datos críticos incompletos.
    </p>

    <h3>Distribución por nivel de alerta</h3>
    {tabla_html(resumenes["resumen_alertas"])}

    <h3>Casos priorizados con alerta alta</h3>
    {tabla_html(
        resumenes["casos_alerta_alta"],
        columnas=[
            "id_usuario",
            "comuna",
            "estado_caso",
            "profesional_responsable",
            "puntaje_alerta",
            "motivos_alerta",
            "accion_sugerida"
        ],
        max_filas=15
    )}
</section>


<section>
    <h2>6. Componente SQL</h2>

    <p>
        Además del procesamiento en Python, se creó una base SQLite llamada
        <strong>mca_monitoreo.db</strong>, cargando las tablas principales del proyecto.
        Sobre esta base se ejecutaron consultas SQL orientadas a revisar indicadores,
        casos sin seguimiento reciente, PII vencidos, inasistencias, distribución
        de alertas e indicadores críticos.
    </p>

    <p>
        Los resultados de las consultas fueron exportados al archivo:
        <strong>resultados_consultas_sql.xlsx</strong>.
    </p>
</section>


<section>
    <h2>7. Entregables generados</h2>

    <ul>
        <li><strong>usuarios_mca.csv</strong>: base sintética de usuarios.</li>
        <li><strong>intervenciones.csv</strong>: intervenciones técnicas simuladas.</li>
        <li><strong>planes_intervencion.csv</strong>: planes de intervención individual.</li>
        <li><strong>controles_audiencias.csv</strong>: controles, citaciones y audiencias.</li>
        <li><strong>egresos.csv</strong>: egresos simulados.</li>
        <li><strong>reporte_validacion.xlsx</strong>: reporte de inconsistencias.</li>
        <li><strong>base_consolidada_mca.xlsx</strong>: base maestra de seguimiento.</li>
        <li><strong>indicadores_gestion.xlsx</strong>: indicadores calculados.</li>
        <li><strong>alertas_tempranas.xlsx</strong>: clasificación de alertas por caso.</li>
        <li><strong>mca_monitoreo.db</strong>: base SQLite del proyecto.</li>
        <li><strong>resultados_consultas_sql.xlsx</strong>: resultados de consultas SQL.</li>
    </ul>
</section>


<section>
    <h2>8. Conclusiones</h2>

    <p>
        El proyecto demuestra un flujo de trabajo práctico para transformar
        registros operativos en información útil para la gestión institucional.
        La propuesta permite validar datos, consolidar fuentes, calcular indicadores,
        identificar brechas de seguimiento y priorizar casos mediante alertas tempranas.
    </p>

    <p>
        El foco del proyecto no está en construir un sistema complejo, sino en mostrar
        una metodología ordenada, reproducible y compatible con flujos administrativos
        habituales, donde los resultados puedan ser revisados mediante Excel, CSV,
        SQL e informe ejecutivo.
    </p>
</section>

</main>

<footer>
    Informe generado automáticamente el {fecha_generacion}.
</footer>

</body>
</html>
"""

    return html


# ------------------------------------------------------------
# Exportar informe
# ------------------------------------------------------------

def exportar_informe(html):
    """
    Exporta el informe HTML en report/ y docs/.
    """

    with open(RUTA_INFORME_REPORT, "w", encoding="utf-8") as archivo:
        archivo.write(html)

    with open(RUTA_INFORME_DOCS, "w", encoding="utf-8") as archivo:
        archivo.write(html)

    print("Informe HTML generado correctamente.")
    print(f"Informe local: {RUTA_INFORME_REPORT}")
    print(f"Informe para GitHub Pages: {RUTA_INFORME_DOCS}")


# ------------------------------------------------------------
# Ejecución principal
# ------------------------------------------------------------

def ejecutar_generacion_informe():
    """
    Ejecuta la generación completa del informe HTML.
    """

    base, indicadores, alertas, validacion = cargar_archivos()

    resumenes = preparar_resumenes(
        base,
        indicadores,
        alertas,
        validacion
    )

    html = generar_html(
        base,
        indicadores,
        alertas,
        validacion,
        resumenes
    )

    exportar_informe(html)


if __name__ == "__main__":
    ejecutar_generacion_informe()