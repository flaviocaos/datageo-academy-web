<# DataGeo Academy: instala laboratório Oracle Database Free em container.
Docker Linux e imagem OFICIAL previamente obtida no Oracle Container Registry.
Consulte termos, requisitos e tag no registry. Não baixa instaladores de terceiros.
Uso: $env:ORACLE_PWD = Read-Host 'Senha administrativa'
 ./instalar_oracle.ps1 -Image 'container-registry.oracle.com/database/free:TAG_VALIDADA'
Spatial integra o Oracle; não existe CREATE EXTENSION postgis neste banco.
#>
param([Parameter(Mandatory=$true)][string]$Image)
$ErrorActionPreference = 'Stop'
if ($Image -notmatch '^container-registry\.oracle\.com/database/free:[\w.\-]+$') { throw 'Informe uma tag oficial do Oracle Database Free.' }
if (-not $env:ORACLE_PWD) { throw 'Defina ORACLE_PWD antes de executar.' }
docker info --format '{{.ServerVersion}}'
if ($LASTEXITCODE -ne 0) { throw 'Docker não está disponível.' }
$existing = docker ps -a --filter 'name=^/academy-oracle$' --format '{{.Names}}'
if ($existing) { throw 'academy-oracle já existe; nenhuma instância será removida.' }
docker volume create academy_oracle_data
if ($LASTEXITCODE -ne 0) { throw 'Falha ao criar volume Oracle.' }
docker run -d --name academy-oracle --restart unless-stopped --publish 127.0.0.1:1521:1521 --env ORACLE_PWD --mount type=volume,source=academy_oracle_data,target=/opt/oracle/oradata $Image
if ($LASTEXITCODE -ne 0) { throw 'Falha ao iniciar Oracle. Verifique a tag e o acesso ao registry.' }
Write-Host 'Aguarde DATABASE IS READY TO USE em docker logs academy-oracle.'
Write-Host 'Conecte ao serviço FREEPDB1 e execute oracle_preparar_usuario.sql como administrador.'
