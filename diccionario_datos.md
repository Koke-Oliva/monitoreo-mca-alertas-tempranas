# Diccionario de Datos

## Descripción general

Este documento describe las bases de datos sintéticas utilizadas en el proyecto **Monitoreo de Gestión y Alertas Tempranas para Programa MCA**.

Las bases no contienen información real de personas, adolescentes, instituciones ni causas judiciales. Fueron creadas exclusivamente con fines demostrativos para simular un flujo de administración, validación y análisis de información operativa.

---

## 1. Base: `usuarios_mca.csv`

Contiene información general de usuarios ficticios asociados a un programa de Medida Cautelar Ambulatoria.

| Variable | Tipo esperado | Descripción |
|---|---|---|
| `id_usuario` | Texto | Identificador único ficticio del usuario |
| `sexo` | Texto | Sexo registrado del usuario |
| `edad` | Entero | Edad del usuario |
| `tramo_edad` | Texto | Clasificación etaria del usuario |
| `comuna` | Texto | Comuna de procedencia |
| `fecha_ingreso` | Fecha | Fecha simulada de ingreso al programa |
| `causal_ingreso` | Texto | Causal general de ingreso al programa |
| `estado_caso` | Texto | Estado del caso: vigente, egresado o suspendido |
| `profesional_responsable` | Texto | Profesional asignado al seguimiento |
| `fecha_ultimo_contacto` | Fecha | Fecha del último contacto registrado |

---

## 2. Base: `intervenciones.csv`

Contiene registros simulados de intervenciones técnicas realizadas durante el seguimiento de los usuarios.

| Variable | Tipo esperado | Descripción |
|---|---|---|
| `id_intervencion` | Texto | Identificador único de la intervención |
| `id_usuario` | Texto | Identificador del usuario asociado |
| `fecha_intervencion` | Fecha | Fecha en que se registra la intervención |
| `tipo_intervencion` | Texto | Tipo de intervención realizada |
| `responsable` | Texto | Profesional responsable de la intervención |
| `resultado_intervencion` | Texto | Resultado de la intervención |
| `observacion_estado` | Texto | Observación sintética del estado de la intervención |

---

## 3. Base: `planes_intervencion.csv`

Contiene información simulada sobre el Plan de Intervención Individual asociado a cada usuario.

| Variable | Tipo esperado | Descripción |
|---|---|---|
| `id_plan` | Texto | Identificador único del plan |
| `id_usuario` | Texto | Identificador del usuario asociado |
| `fecha_creacion_pii` | Fecha | Fecha de creación del Plan de Intervención Individual |
| `fecha_ultima_actualizacion` | Fecha | Última fecha de actualización del plan |
| `estado_pii` | Texto | Estado del plan: vigente, vencido o no registrado |
| `porcentaje_avance` | Numérico | Porcentaje de avance estimado del plan |
| `resultado_pii` | Texto | Resultado del plan: logrado, parcialmente logrado, no logrado o en proceso |

---

## 4. Base: `controles_audiencias.csv`

Contiene información simulada sobre controles, citaciones o audiencias asociadas a los usuarios.

| Variable | Tipo esperado | Descripción |
|---|---|---|
| `id_control` | Texto | Identificador único del control o audiencia |
| `id_usuario` | Texto | Identificador del usuario asociado |
| `fecha_control` | Fecha | Fecha del control, citación o audiencia |
| `tipo_control` | Texto | Tipo de control registrado |
| `asistencia` | Texto | Estado de asistencia: asiste, no asiste o justificada |
| `dias_para_control` | Entero | Días restantes o transcurridos respecto al control |
| `observacion` | Texto | Observación sintética del control o audiencia |

---

## 5. Base: `egresos.csv`

Contiene información simulada sobre el cierre o egreso de casos.

| Variable | Tipo esperado | Descripción |
|---|---|---|
| `id_egreso` | Texto | Identificador único del egreso |
| `id_usuario` | Texto | Identificador del usuario asociado |
| `fecha_egreso` | Fecha | Fecha simulada de egreso |
| `causal_egreso` | Texto | Causal general de egreso |
| `dias_permanencia` | Entero | Cantidad de días de permanencia en el programa |
| `pii_logrado` | Texto | Estado de logro del Plan de Intervención Individual |

---

## 6. Variables derivadas del análisis

Durante el procesamiento de datos se generarán variables adicionales para validación, monitoreo e indicadores.

| Variable | Descripción |
|---|---|
| `dias_sin_intervencion` | Días transcurridos desde la última intervención registrada |
| `cantidad_intervenciones` | Número total de intervenciones asociadas al usuario |
| `cantidad_inasistencias` | Número total de inasistencias registradas |
| `tiene_pii_vigente` | Indica si el usuario cuenta con Plan de Intervención Individual vigente |
| `puntaje_alerta` | Puntaje total asignado según reglas de alerta temprana |
| `nivel_alerta` | Clasificación final del usuario: bajo, medio o alto |
| `inconsistencia_detectada` | Indica si el registro presenta alguna inconsistencia de calidad de datos |

---

## 7. Reglas generales de calidad de datos

Las validaciones del proyecto consideran las siguientes reglas iniciales:

| Regla | Descripción |
|---|---|
| ID duplicado | Un usuario no debe aparecer duplicado en la base principal |
| Edad fuera de rango | La edad debe encontrarse dentro de un rango coherente para el contexto simulado |
| Comuna faltante | Todo usuario debe tener comuna registrada |
| Fecha inconsistente | La fecha de egreso no puede ser anterior a la fecha de ingreso |
| Usuario sin profesional | Todo caso vigente debe tener profesional responsable |
| Usuario sin PII | Todo caso vigente debe tener Plan de Intervención Individual registrado |
| PII vencido | Un plan sin actualización reciente puede generar alerta |
| Sin intervención reciente | Un usuario vigente sin intervención reciente debe ser priorizado |
| Inasistencias reiteradas | Dos o más inasistencias pueden indicar riesgo operativo |
| Datos críticos incompletos | Registros incompletos deben ser reportados para revisión |

---

## 8. Niveles de alerta temprana

El sistema de alertas tempranas se basa en reglas simples y explicables.

| Puntaje | Nivel de alerta | Interpretación |
|---|---|---|
| 0 a 2 | Bajo | Caso sin señales relevantes de riesgo operativo |
| 3 a 5 | Medio | Caso que requiere seguimiento o revisión |
| 6 o más | Alto | Caso prioritario para revisión técnica o coordinación |