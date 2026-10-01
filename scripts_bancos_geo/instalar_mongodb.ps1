<# DataGeo Academy: MongoDB 8.0 em Docker Linux com autenticação.
Uso: defina $env:MONGO_INITDB_ROOT_USERNAME e $env:MONGO_INITDB_ROOT_PASSWORD;
execute ./instalar_mongodb.ps1. Crie depois usuário de aplicação com readWrite
apenas no banco academy; não utilize root na aplicação.
#>
param([string]$Image = 'mongo:8.0')
$ErrorActionPreference = 'Stop'
if (-not $env:MONGO_INITDB_ROOT_USERNAME -or -not $env:MONGO_INITDB_ROOT_PASSWORD) { throw 'Defina usuário e senha do MongoDB nas variáveis de ambiente.' }
docker info --format '{{.ServerVersion}}'
if ($LASTEXITCODE -ne 0) { throw 'Docker não está disponível.' }
$existing = docker ps -a --filter 'name=^/academy-mongo$' --format '{{.Names}}'
if ($existing) { throw 'academy-mongo já existe; este script não remove dados.' }
docker volume create academy_mongo_data
if ($LASTEXITCODE -ne 0) { throw 'Falha ao criar volume MongoDB.' }
docker run -d --name academy-mongo --restart unless-stopped --publish 127.0.0.1:27017:27017 --env MONGO_INITDB_ROOT_USERNAME --env MONGO_INITDB_ROOT_PASSWORD --mount type=volume,source=academy_mongo_data,target=/data/db $Image
if ($LASTEXITCODE -ne 0) { throw 'Falha ao iniciar MongoDB.' }
Write-Host 'Use mongosh com --authenticationDatabase admin e senha interativa. Consulte README.md.'
