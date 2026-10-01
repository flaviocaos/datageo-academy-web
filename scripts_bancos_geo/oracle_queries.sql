-- Execute após oracle_schema.sql. SRID geodésico; tolerância em metros.
SELECT id,nome,SDO_UTIL.TO_WKTGEOMETRY(geom) AS wkt FROM dg_pontos ORDER BY id;
SELECT nome FROM dg_pontos p WHERE SDO_WITHIN_DISTANCE(p.geom,
 MDSYS.SDO_GEOMETRY(2001,4326,MDSYS.SDO_POINT_TYPE(-48.55,-27.59,NULL),NULL,NULL),
 'distance=1 unit=KM')='TRUE';
SELECT nome,SDO_GEOM.SDO_DISTANCE(geom,
 MDSYS.SDO_GEOMETRY(2001,4326,MDSYS.SDO_POINT_TYPE(-48.55,-27.59,NULL),NULL,NULL),
 0.005,'unit=M') AS distancia_m FROM dg_pontos;
SELECT id,SDO_GEOM.VALIDATE_GEOMETRY_WITH_CONTEXT(geom,0.005) AS validacao FROM dg_pontos;
-- Bind SQL*Plus: dados separados da estrutura da consulta.
VARIABLE categoria VARCHAR2(40)
BEGIN :categoria := 'escola'; END;
/
SELECT id,nome FROM dg_pontos WHERE categoria=:categoria;
