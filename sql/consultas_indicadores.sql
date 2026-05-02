-- ============================================================
-- Proyecto: Monitoreo de Gestión y Alertas Tempranas para MCA
-- Archivo: consultas_indicadores.sql
-- Objetivo: Consultas SQL para revisar indicadores operativos,
--           calidad de información y alertas tempranas.
-- ============================================================


-- ============================================================
-- 1. Total de usuarios por estado de caso
-- ============================================================

SELECT
    estado_caso,
    COUNT(*) AS cantidad_usuarios
FROM base_consolidada_mca
GROUP BY estado_caso
ORDER BY cantidad_usuarios DESC;


-- ============================================================
-- 2. Casos vigentes por comuna
-- ============================================================

SELECT
    comuna,
    COUNT(*) AS casos_vigentes
FROM base_consolidada_mca
WHERE caso_vigente = 1
GROUP BY comuna
ORDER BY casos_vigentes DESC;


-- ============================================================
-- 3. Casos vigentes sin contacto reciente
-- ============================================================

SELECT
    id_usuario,
    comuna,
    profesional_responsable,
    estado_caso,
    dias_sin_contacto
FROM base_consolidada_mca
WHERE caso_vigente = 1
  AND dias_sin_contacto > 21
ORDER BY dias_sin_contacto DESC;


-- ============================================================
-- 4. Casos vigentes sin intervención reciente
-- ============================================================

SELECT
    id_usuario,
    comuna,
    profesional_responsable,
    cantidad_intervenciones,
    dias_sin_intervencion
FROM base_consolidada_mca
WHERE caso_vigente = 1
  AND dias_sin_intervencion > 21
ORDER BY dias_sin_intervencion DESC;


-- ============================================================
-- 5. Estado de PII por cantidad de usuarios
-- ============================================================

SELECT
    estado_pii,
    COUNT(*) AS cantidad_usuarios
FROM base_consolidada_mca
GROUP BY estado_pii
ORDER BY cantidad_usuarios DESC;


-- ============================================================
-- 6. Casos con PII vencido o no registrado
-- ============================================================

SELECT
    id_usuario,
    comuna,
    profesional_responsable,
    estado_caso,
    estado_pii,
    dias_desde_actualizacion_pii
FROM base_consolidada_mca
WHERE estado_pii IN ('Vencido', 'No registrado')
ORDER BY dias_desde_actualizacion_pii DESC;


-- ============================================================
-- 7. Tasa de inasistencia general
-- ============================================================

SELECT
    ROUND(
        SUM(cantidad_inasistencias) * 100.0 / NULLIF(SUM(cantidad_controles), 0),
        2
    ) AS tasa_inasistencia_porcentaje
FROM base_consolidada_mca;


-- ============================================================
-- 8. Casos con inasistencias reiteradas
-- ============================================================

SELECT
    id_usuario,
    comuna,
    profesional_responsable,
    cantidad_controles,
    cantidad_inasistencias
FROM base_consolidada_mca
WHERE cantidad_inasistencias >= 2
ORDER BY cantidad_inasistencias DESC;


-- ============================================================
-- 9. Distribución de alertas tempranas
-- ============================================================

SELECT
    nivel_alerta,
    COUNT(*) AS cantidad_casos
FROM alertas_tempranas
GROUP BY nivel_alerta
ORDER BY
    CASE nivel_alerta
        WHEN 'Alto' THEN 1
        WHEN 'Medio' THEN 2
        WHEN 'Bajo' THEN 3
        ELSE 4
    END;


-- ============================================================
-- 10. Casos priorizados con alerta alta
-- ============================================================

SELECT
    id_usuario,
    comuna,
    estado_caso,
    profesional_responsable,
    puntaje_alerta,
    motivos_alerta,
    accion_sugerida
FROM alertas_tempranas
WHERE nivel_alerta = 'Alto'
ORDER BY puntaje_alerta DESC;


-- ============================================================
-- 11. Alertas altas por comuna
-- ============================================================

SELECT
    comuna,
    COUNT(*) AS cantidad_alertas_altas
FROM alertas_tempranas
WHERE nivel_alerta = 'Alto'
GROUP BY comuna
ORDER BY cantidad_alertas_altas DESC;


-- ============================================================
-- 12. Alertas altas por profesional responsable
-- ============================================================

SELECT
    profesional_responsable,
    COUNT(*) AS cantidad_alertas_altas
FROM alertas_tempranas
WHERE nivel_alerta = 'Alto'
GROUP BY profesional_responsable
ORDER BY cantidad_alertas_altas DESC;


-- ============================================================
-- 13. Indicadores críticos
-- ============================================================

SELECT
    dimension,
    indicador,
    resultado,
    unidad,
    meta_referencial,
    estado,
    interpretacion
FROM indicadores_gestion
WHERE estado = 'Crítico'
ORDER BY dimension;


-- ============================================================
-- 14. Indicadores que cumplen meta
-- ============================================================

SELECT
    dimension,
    indicador,
    resultado,
    unidad,
    meta_referencial,
    estado
FROM indicadores_gestion
WHERE estado = 'Cumple'
ORDER BY dimension;


-- ============================================================
-- 15. Resumen de indicadores por estado
-- ============================================================

SELECT
    estado,
    COUNT(*) AS cantidad_indicadores
FROM indicadores_gestion
GROUP BY estado
ORDER BY cantidad_indicadores DESC;