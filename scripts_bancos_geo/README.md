# Laboratórios de bancos geográficos — DataGeo Academy

Scripts de instalação para Docker Desktop em modo Linux, schemas e consultas
espaciais reais. Use um ambiente de estudo novo. Nenhum script apaga volumes,
substitui bancos existentes ou contém senha fixa. Instalar exige internet,
espaço em disco e acesso às imagens oficiais. Os exemplos são sintéticos.

## PostgreSQL / PostGIS

1. Defina `POSTGRES_PASSWORD` em uma sessão PowerShell; execute
   `./instalar_postgis.ps1`. O banco será `academy`, usuário `academy_admin`,
   host `127.0.0.1`, porta 5432. A tag padrão é PostgreSQL 17 / PostGIS 3.5.
2. Aguarde `docker exec academy-postgis pg_isready -U academy_admin -d academy`.
3. Com psql instalado, rode `psql -h 127.0.0.1 -U academy_admin -d academy
   -v ON_ERROR_STOP=1 -f postgis_schema.sql` e depois `postgis_queries.sql`.
   A senha é solicitada pelo cliente. Também pode copiar os SQL ao container
   com `docker cp postgis_schema.sql academy-postgis:/tmp/schema.sql` e usar
   `docker exec academy-postgis psql -U academy_admin -d academy
   -v ON_ERROR_STOP=1 -f /tmp/schema.sql`.
4. Longitude/latitude WGS84 EPSG:4326; os buffers do exemplo usam SIRGAS 2000
   UTM 22S, EPSG:31982, somente para esta região. ST_Transform converte valores;
   ST_SetSRID apenas identifica a referência. Medidas geography são em metros.

## Oracle Spatial

1. Obtenha uma tag oficial do Oracle Database Free em
   https://container-registry.oracle.com/ords/ocr/ba/database/free e confira
   termos e recursos exigidos. Defina `ORACLE_PWD`; execute
   `./instalar_oracle.ps1 -Image container-registry.oracle.com/database/free:TAG`.
   Substitua TAG por uma tag existente; ela não é um nome executável de exemplo.
2. Aguarde a mensagem de prontidão no log e conecte SQL*Plus ou SQLcl ao
   serviço FREEPDB1, por exemplo `sqlplus system@localhost:1521/FREEPDB1`.
3. Execute `@oracle_preparar_usuario.sql`, com senha nova sem aspas duplas.
   Reconecte como `dg_academy` e execute `@oracle_schema.sql` uma única vez,
   depois `@oracle_queries.sql`. O componente SDO deve estar VALID no registry.
4. Oracle Spatial não usa a extensão PostGIS. Metadata, tolerância e índice
   espacial são próprios do Oracle; os scripts não instalam o motor fora Docker.

## MongoDB

1. Defina `MONGO_INITDB_ROOT_USERNAME` e `MONGO_INITDB_ROOT_PASSWORD`, execute
   `./instalar_mongodb.ps1`. Espere a prontidão em `docker logs academy-mongo`.
2. Rode `mongosh --host 127.0.0.1 --port 27017 --username SEU_USUARIO
   --authenticationDatabase admin` e informe senha interativamente.
3. No mongosh, execute `load('mongodb_schema.js')` e
   `load('mongodb_queries.js')` a partir da pasta dos arquivos baixados.
4. Índice 2dsphere, GeoJSON WGS84, coordenadas [longitude, latitude].
   `$geoNear` deve ser a primeira etapa da agregação; distância em metros.
   O validador checa estrutura e tipos; o índice geográfico também rejeita
   coordenadas inválidas. Se a coleção já existia, revise seu validador manualmente.

## Operação e revisão

As portas são vinculadas ao loopback. Os instaladores recusam containers com
o mesmo nome e não removem volumes. Não exponha contas administrativas em
aplicações; crie perfis com as permissões necessárias. Defina backup e teste
restauração. Senhas de ambiente não devem ir para histórico ou Git. Retire-as
da sessão com `Remove-Item Env:POSTGRES_PASSWORD` (ou variável correspondente)
após criar o container. Alterar essas variáveis não altera senha de volume existente.
As credenciais continuam inspecionáveis pelo administrador do Docker; em produção,
use o mecanismo de segredos do ambiente e sua política de acesso.

Referências oficiais: https://github.com/postgis/docker-postgis,
https://postgis.net/docs/, https://docs.oracle.com/en/database/oracle/oracle-database/26/spatl/,
https://www.mongodb.com/docs/manual/geospatial-queries/.
