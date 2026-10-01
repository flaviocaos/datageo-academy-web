<# DataGeo Academy: laboratório PostgreSQL/PostGIS com persistência.
Pré-requisito: Docker Desktop em execução, modo Linux.
Uso: $env:POSTGRES_PASSWORD = Read-Host 'Senha do laboratório'
     ./instalar_postgis.ps1
Não use a conta administrativa no GeoServer: crie um usuário somente leitura.
#>
param([string]$Image = 'postgis/postgis:17-3.5')
$ErrorActionPreference = 'Stop'
if (-not $env:POSTGRES_PASSWORD) { throw 'Defina POSTGRES_PASSWORD antes de executar.' }
docker info --format '{{.ServerVersion}}'
if ($LASTEXITCODE -ne 0) { throw 'Docker não está disponível.' }
$existing = docker ps -a --filter 'name=^/academy-postgis$' --format '{{.Names}}'
if ($existing) { throw 'academy-postgis já existe. Inspecione-o; este script não remove dados.' }
docker volume create academy_postgis_data
if ($LASTEXITCODE -ne 0) { throw 'Não foi possível criar o volume.' }
docker run -d --name academy-postgis --restart unless-stopped --publish 127.0.0.1:5432:5432 --env POSTGRES_DB=academy --env POSTGRES_USER=academy_admin --env POSTGRES_PASSWORD --mount type=volume,source=academy_postgis_data,target=/var/lib/postgresql/data $Image
if ($LASTEXITCODE -ne 0) { throw 'Falha ao iniciar PostgreSQL/PostGIS.' }
Write-Host 'Aguarde pg_isready: docker exec academy-postgis pg_isready -U academy_admin -d academy'
Write-Host 'Execute os SQL conforme README.md. O volume preserva os dados entre reinícios.'
