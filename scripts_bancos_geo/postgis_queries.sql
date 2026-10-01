-- Consultas reais. Requer postgis_schema.sql. Distâncias geográficas em metros.
-- Longitude primeiro! Não use ST_SetSRID para converter coordenadas.
SELECT id,nome,ST_AsGeoJSON(geom) AS geojson FROM academy.pontos ORDER BY id;

-- Busca por raio com índice geography; centro didático em Florianópolis.
SELECT nome,ST_Distance(geom::geography,
    ST_SetSRID(ST_MakePoint(-48.55,-27.59),4326)::geography) AS distancia_m
FROM academy.pontos
WHERE ST_DWithin(geom::geography,
    ST_SetSRID(ST_MakePoint(-48.55,-27.59),4326)::geography,1000)
ORDER BY distancia_m;

-- SIRGAS 2000 / UTM 22S é adequado a este exemplo regional, não a todo o Brasil.
SELECT nome, ST_AsText(ST_Transform(geom,31982)) AS utm_22s,
    ST_Area(ST_Buffer(ST_Transform(geom,31982),100))/10000 AS buffer_ha
FROM academy.pontos;

-- Vizinho mais próximo usando operador KNN em geometria (ordenação em graus).
SELECT nome FROM academy.pontos
ORDER BY geom <-> ST_SetSRID(ST_MakePoint(-48.55,-27.59),4326) LIMIT 3;
SELECT id,ST_IsValidReason(geom) FROM academy.pontos WHERE NOT ST_IsValid(geom);

-- Parâmetros separados do SQL; substitua pelo binding da biblioteca do cliente.
PREPARE academy_por_categoria(text) AS
SELECT id,nome FROM academy.pontos WHERE categoria=$1 ORDER BY id;
EXECUTE academy_por_categoria('escola');
DEALLOCATE academy_por_categoria;
EXPLAIN SELECT id FROM academy.pontos WHERE geom && ST_MakeEnvelope(-48.56,-27.60,-48.53,-27.58,4326);
