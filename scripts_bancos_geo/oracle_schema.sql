-- Oracle Spatial, SQL*Plus / SQLcl, usuário DG_ACADEMY no FREEPDB1.
-- Executar UMA VEZ em laboratório novo; DDL Oracle faz commit implícito.
WHENEVER SQLERROR EXIT SQL.SQLCODE
CREATE TABLE dg_pontos (
 id NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 nome VARCHAR2(120) NOT NULL,
 categoria VARCHAR2(40) NOT NULL,
 geom MDSYS.SDO_GEOMETRY NOT NULL
);
INSERT INTO dg_pontos(nome,categoria,geom) VALUES
('Escola didática','escola',MDSYS.SDO_GEOMETRY(2001,4326,MDSYS.SDO_POINT_TYPE(-48.55,-27.59,NULL),NULL,NULL));
INSERT INTO dg_pontos(nome,categoria,geom) VALUES
('Parque didático','parque',MDSYS.SDO_GEOMETRY(2001,4326,MDSYS.SDO_POINT_TYPE(-48.54,-27.585,NULL),NULL,NULL));
INSERT INTO user_sdo_geom_metadata(table_name,column_name,diminfo,srid) VALUES
('DG_PONTOS','GEOM',MDSYS.SDO_DIM_ARRAY(
 MDSYS.SDO_DIM_ELEMENT('Longitude',-180,180,0.005),
 MDSYS.SDO_DIM_ELEMENT('Latitude',-90,90,0.005)),4326);
COMMIT;
CREATE INDEX dg_pontos_sidx ON dg_pontos(geom) INDEXTYPE IS MDSYS.SPATIAL_INDEX_V2;
COMMENT ON TABLE dg_pontos IS 'Dados sintéticos DataGeo Academy. WGS84 EPSG:4326; longitude/latitude.';
