-- DataGeo Academy. PostgreSQL 17 / PostGIS 3.5+. Execute em banco de laboratório.
-- psql -v ON_ERROR_STOP=1 -U academy_admin -d academy -f postgis_schema.sql
-- CREATE EXTENSION exige permissões administrativas. Dados são SINTÉTICOS.
BEGIN;
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE SCHEMA IF NOT EXISTS academy;
CREATE TABLE IF NOT EXISTS academy.pontos (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    codigo text NOT NULL UNIQUE,
    nome text NOT NULL CHECK (length(trim(nome))>0),
    categoria text NOT NULL,
    geom geometry(Point,4326) NOT NULL,
    criado_em timestamptz NOT NULL DEFAULT now(),
    CHECK (ST_IsValid(geom) AND NOT ST_IsEmpty(geom))
);
CREATE INDEX IF NOT EXISTS pontos_geom_gix ON academy.pontos USING gist(geom);
CREATE INDEX IF NOT EXISTS pontos_geography_gix ON academy.pontos USING gist((geom::geography));
CREATE INDEX IF NOT EXISTS pontos_categoria_idx ON academy.pontos(categoria);
INSERT INTO academy.pontos(codigo,nome,categoria,geom) VALUES
('DEMO01','Escola didática','escola',ST_SetSRID(ST_MakePoint(-48.55,-27.59),4326)),
('DEMO02','Unidade didática','saude',ST_SetSRID(ST_MakePoint(-48.545,-27.592),4326)),
('DEMO03','Parque didático','parque',ST_SetSRID(ST_MakePoint(-48.54,-27.585),4326))
ON CONFLICT(codigo) DO NOTHING;
COMMENT ON TABLE academy.pontos IS 'Dados sintéticos para exercícios DataGeo Academy; longitude/latitude EPSG:4326.';
COMMIT;
ANALYZE academy.pontos;
SELECT PostGIS_Full_Version();
