# Monitoreo de Gestión y Alertas Tempranas para Programa MCA

## Descripción del proyecto

Este mini proyecto simula un flujo de administración, validación y análisis de información operativa para un programa de Medida Cautelar Ambulatoria (MCA).

El objetivo es construir un sistema básico de monitoreo de gestión que permita trabajar con datos sintéticos, validar la calidad de la información, calcular indicadores clave y generar alertas tempranas exportables a formatos revisables por equipos técnicos o administrativos.

El proyecto está orientado a demostrar competencias en gestión de información, análisis de datos, control de consistencia, reportería e indicadores operativos en un contexto institucional.

---

## Objetivo general

Diseñar un flujo de monitoreo de gestión para un programa MCA, utilizando datos sintéticos para consolidar información, detectar inconsistencias, calcular indicadores y generar alertas tempranas de apoyo a la toma de decisiones.

---

## Objetivos específicos

- Simular bases operativas asociadas a usuarios, intervenciones, planes de intervención, controles/audiencias y egresos.
- Validar la calidad de los datos mediante reglas simples y trazables.
- Consolidar información proveniente de distintas fuentes simuladas.
- Calcular indicadores de gestión técnica y operativa.
- Clasificar casos mediante un sistema de alertas tempranas basado en reglas.
- Exportar resultados en formatos compatibles con flujos administrativos, como CSV y Excel.
- Documentar el proceso de forma clara para revisión técnica y no técnica.

---

## Alcance del proyecto

Este proyecto utiliza datos sintéticos y no contiene información real de personas, adolescentes, instituciones ni causas judiciales.

La finalidad es exclusivamente demostrativa y profesional, orientada a mostrar una propuesta de trabajo replicable para procesos de administración y análisis de información.

---

## Tecnologías utilizadas

- Python
- Pandas
- NumPy
- SQL / SQLite
- Excel / CSV
- Markdown
- Git y GitHub
- GitHub Pages

---

## Estructura del proyecto

```text
monitoreo-mca-alertas-tempranas/
│
├── data/
│   ├── simulated/
│   └── output/
│
├── scripts/
│
├── sql/
│
├── report/
│
├── docs/
│
├── README.md
├── requirements.txt
└── diccionario_datos.md
```

---

## Flujo general de trabajo

```text
Datos operativos simulados
        ↓
Validación de calidad de información
        ↓
Consolidación de bases
        ↓
Cálculo de indicadores de gestión
        ↓
Generación de alertas tempranas
        ↓
Exportación de resultados
        ↓
Informe ejecutivo
```

---

## Bases simuladas consideradas

| Base | Descripción |
|---|---|
| `usuarios_mca.csv` | Información general de usuarios ficticios del programa |
| `intervenciones.csv` | Registro de intervenciones técnicas simuladas |
| `planes_intervencion.csv` | Estado y avance de planes de intervención individual |
| `controles_audiencias.csv` | Registro de controles, citaciones o audiencias |
| `egresos.csv` | Información simulada de cierre o egreso de casos |

---

## Indicadores propuestos

| Dimensión | Indicador |
|---|---|
| Cobertura | Casos vigentes |
| Seguimiento | Promedio de intervenciones por usuario |
| Oportunidad | Usuarios con intervención reciente |
| Calidad de información | Registros con inconsistencias |
| Plan de intervención | Usuarios con PII vigente |
| Cumplimiento | Egresos con PII logrado |
| Asistencia | Tasa de inasistencia a controles/audiencias |
| Riesgo operativo | Usuarios con alerta media o alta |

---

## Sistema de alertas tempranas

El sistema de alertas se basa en reglas simples, interpretables y trazables.

Ejemplos de criterios utilizados:

- Más de 21 días sin intervención registrada.
- Dos o más inasistencias.
- Plan de intervención vencido o no registrado.
- Audiencia próxima sin contacto reciente.
- Datos críticos incompletos.
- Caso sin profesional asignado.

Los casos se clasifican en tres niveles:

| Puntaje | Nivel de alerta |
|---|---|
| 0 a 2 | Bajo |
| 3 a 5 | Medio |
| 6 o más | Alto |

---

## Entregables esperados

| Entregable | Descripción |
|---|---|
| Bases sintéticas | Archivos CSV simulados |
| Reporte de validación | Inconsistencias detectadas |
| Base consolidada | Información integrada para análisis |
| Indicadores de gestión | Métricas operativas calculadas |
| Alertas tempranas | Clasificación de casos según nivel de alerta |
| Informe final | Reporte ejecutivo del proyecto |
| Documentación | README y diccionario de datos |

---

## Valor del proyecto

Este proyecto busca demostrar la capacidad de transformar registros operativos en información útil para la gestión institucional, combinando validación de datos, indicadores, alertas tempranas y reportabilidad.

El foco no está en desarrollar un sistema complejo, sino en construir un flujo claro, ordenado y útil para apoyar procesos de seguimiento, control y toma de decisiones.

---

## Resultados generados

Durante la ejecución del proyecto se generaron las siguientes salidas principales:

| Archivo | Descripción |
|---|---|
| `usuarios_mca.csv` | Base sintética de usuarios del programa |
| `intervenciones.csv` | Registro simulado de intervenciones técnicas |
| `planes_intervencion.csv` | Información simulada de planes de intervención individual |
| `controles_audiencias.csv` | Registro de controles, citaciones y audiencias |
| `egresos.csv` | Información simulada de egresos |
| `reporte_validacion.xlsx` | Reporte de inconsistencias de calidad de datos |
| `base_consolidada_mca.xlsx` | Base maestra consolidada para seguimiento operativo |
| `indicadores_gestion.xlsx` | Tabla de indicadores de gestión técnica y operativa |
| `alertas_tempranas.xlsx` | Clasificación de casos según nivel de alerta |
| `usuarios_alerta_alta.csv` | Casos priorizados con alerta alta |
| `mca_monitoreo.db` | Base SQLite con las tablas principales del proyecto |
| `resultados_consultas_sql.xlsx` | Resultados exportados de consultas SQL |
| `informe_mca_monitoreo.html` | Informe ejecutivo del proyecto |

---

## Principales resultados del ejercicio

A partir de los datos sintéticos generados, el flujo permitió consolidar una base maestra de seguimiento y obtener resultados operativos como:

| Resultado | Valor |
|---|---:|
| Usuarios consolidados | 79 |
| Casos vigentes | 59 |
| Casos sin contacto reciente | 40 |
| Casos sin intervención reciente | 44 |
| Casos con PII vencido o no registrado | 15 |
| Casos con inasistencias reiteradas | 7 |
| Casos sin profesional responsable | 1 |
| Registros con datos críticos faltantes | 2 |

---

## Distribución de alertas tempranas

El sistema de alertas tempranas clasificó los casos según reglas operativas simples y trazables.

| Nivel de alerta | Cantidad de casos |
|---|---:|
| Alto | 27 |
| Medio | 22 |
| Bajo | 30 |

Los casos con alerta alta fueron exportados en el archivo:

```text
data/output/usuarios_alerta_alta.csv
```

---

## Indicadores de gestión

El proyecto generó una tabla de indicadores con dimensión, fórmula, resultado, unidad, meta referencial, estado, periodicidad sugerida, fuente simulada e interpretación.

Resumen de indicadores por estado:

| Estado | Cantidad de indicadores |
|---|---:|
| Crítico | 8 |
| Cumple | 5 |
| En observación | 2 |

---

## Consultas SQL

Además del procesamiento con Python, se creó una base SQLite llamada:

```text
data/output/mca_monitoreo.db
```

Sobre esta base se ejecutaron consultas SQL para revisar:

- Casos vigentes por comuna.
- Casos sin contacto reciente.
- Casos sin intervención reciente.
- Estado de planes de intervención.
- Tasa de inasistencia.
- Casos con alertas altas.
- Indicadores críticos.
- Resumen de indicadores por estado.

Los resultados fueron exportados a:

```text
data/output/resultados_consultas_sql.xlsx
```

---

## Cómo ejecutar el proyecto

Los scripts deben ejecutarse desde la carpeta `scripts/` en el siguiente orden:

```bash
python 01_generar_datos_sinteticos.py
python 02_validar_calidad_informacion.py
python 03_consolidar_bases.py
python 04_calcular_indicadores.py
python 05_generar_alertas_tempranas.py
python 06_crear_base_sqlite.py
python 07_ejecutar_consultas_sql.py
python 08_generar_informe_html.py
```

---

## Informe ejecutivo publicado

El informe HTML del proyecto está publicado mediante GitHub Pages y puede revisarse en el siguiente enlace:

[Ver informe ejecutivo](https://koke-oliva.github.io/monitoreo-mca-alertas-tempranas/)

El archivo utilizado para la publicación se encuentra en:

```text
docs/index.html

---

## Enfoque profesional del proyecto

Este proyecto fue diseñado como una simulación aplicada a un contexto institucional, priorizando la administración de información, validación de registros, cálculo de indicadores, generación de alertas tempranas y entrega de resultados en formatos revisables por equipos técnicos o administrativos.

El uso de Python y SQL funciona como apoyo para automatizar el flujo, mientras que el valor principal del proyecto está en la organización, trazabilidad y utilidad operativa de la información.
