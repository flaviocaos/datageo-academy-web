"""Gera dois manuais Word ilustrados e editáveis, com sumário e fontes oficiais.
Uso: python scripts_automacao/gerar_manuais_servidores.py (requer Pillow).
Os diagramas são esquemas didáticos originais, não capturas de interfaces.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import importlib.util
import xml.etree.ElementTree as ET
from PIL import Image, ImageDraw, ImageFont

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('corporativo',ROOT/'scripts_automacao/gerar_documentos_corporativos.py')
corp=importlib.util.module_from_spec(spec);spec.loader.exec_module(corp)
DEST=ROOT/'roteiros_servidores'

POSTGIS='''# Instalação e configuração do PostgreSQL / PostGIS
## Escopo, ambiente e critérios de aceite
Este roteiro instala um laboratório persistente PostgreSQL 17 com PostGIS 3.5 usando Docker Desktop em modo Linux. É destinado a dados de estudo, sem migração automática de bases de produção. Os arquivos da pasta scripts_bancos_geo são os complementos executáveis. Registre sistema operacional, versão do Docker, tag da imagem, data e responsável. Antes de iniciar, reserve espaço para imagem, volume e backups e confirme que a porta 5432 está livre. A conexão será limitada ao próprio computador.
Critérios de aceite: PostgreSQL responde a pg_isready, a extensão informa sua versão, a tabela de pontos possui dados e índice espacial, consultas retornam distâncias coerentes e um backup restaura em banco novo. Preserve cada evidência no registro de execução; uma mensagem de container ativo não demonstra por si só funcionamento do banco.
## Preparação e instalação passo a passo
1. Instale Docker Desktop pelo site oficial; no Windows habilite o backend WSL2 conforme os requisitos do fornecedor. Abra o aplicativo e aguarde o motor Linux estar pronto. Execute docker version e docker info para conferir cliente e servidor. Se houver erro de virtualização ou permissão, resolva-o antes de instalar o banco.
2. Baixe instalar_postgis.ps1, postgis_schema.sql e postgis_queries.sql para a mesma pasta. Leia o instalador: ele cria o container academy-postgis e o volume academy_postgis_data sem excluir dados. O volume é montado em /var/lib/postgresql/data, adequado à imagem PostgreSQL 17 deste roteiro. Não reutilize esse caminho indiscriminadamente para outra versão principal.
3. Abra PowerShell nessa pasta. Defina uma senha forte por entrada interativa e execute o script. A senha não deve ser incluída em documentos compartilhados ou no Git. O Read-Host deste exemplo não mascara caracteres; utilize um console privado ou seu mecanismo de segredos.
```
$env:POSTGRES_PASSWORD = Read-Host 'Senha do laboratório'
./instalar_postgis.ps1
docker exec academy-postgis pg_isready -U academy_admin -d academy
```
4. Aguarde pg_isready retornar accepting connections e confirme a publicação 127.0.0.1:5432. Se o nome já existir, o script para; inspecione o container em vez de apagar o volume. Remova a variável da sessão após a instalação. A conta Docker ainda pode inspecionar o ambiente do container; essa abordagem é de laboratório.
## Habilitação da extensão e criação do schema
Instale o cliente psql ou utilize o cliente existente no container. A opção ON_ERROR_STOP encerra execução no primeiro erro; confira o código de saída. O schema usa transação, nomes únicos e inserções de demonstração que não substituem registros existentes. CREATE EXTENSION exige privilégios adequados; faça essa etapa como administrador do laboratório.
```
docker cp postgis_schema.sql academy-postgis:/tmp/schema.sql
docker exec academy-postgis psql -U academy_admin -d academy -v ON_ERROR_STOP=1 -f /tmp/schema.sql
docker cp postgis_queries.sql academy-postgis:/tmp/queries.sql
docker exec academy-postgis psql -U academy_admin -d academy -v ON_ERROR_STOP=1 -f /tmp/queries.sql
```
Execute SELECT PostGIS_Full_Version(); e SELECT count(*) FROM academy.pontos; para registrar a versão e os três pontos sintéticos. As coordenadas são longitude/latitude em WGS84, EPSG:4326. As geometrias são Point, não polígonos de limite municipal. Identifique sempre a natureza didática no relatório e não interprete os resultados como levantamento real.
## Referência espacial, índices e medidas
ST_SetSRID identifica a referência de coordenadas existentes; não as converte. ST_Transform modifica os valores para outro CRS. Para os exemplos de Florianópolis, ST_Transform(geom,31982) usa SIRGAS 2000 / UTM 22S. Escolha a zona e o hemisfério adequados para outros locais. Não aplique cálculo de hectares diretamente sobre graus de latitude/longitude.
O schema cria índice GiST em geom e em geom::geography. ST_DWithin sobre geography recebe raio em metros e pode utilizar o índice correspondente. Verifique ST_IsValid, ST_IsEmpty, tipo e SRID antes de integrar dados externos. EXPLAIN mostra o plano, mas bases pequenas podem usar varredura sequencial legitimamente. ANALYZE atualiza estatísticas após importações.
## Conexão pelo QGIS e usuário de publicação
No QGIS, abra o Gerenciador de Fontes de Dados, PostgreSQL, Nova conexão. Nome: Academy local; host: 127.0.0.1; porta: 5432; banco: academy. Use a conta administrativa apenas para configurar o laboratório. Teste conexão, abra o schema academy e adicione pontos. Confira CRS EPSG:4326, número de feições e extensão aproximada. Não salve senha em projeto que será distribuído.
Para publicar no GeoServer, crie um usuário somente leitura separado. No psql administrativo, crie a role e use o comando interativo de senha. O default privileges abaixo vale para objetos futuros criados pelo usuário que executa o comando; repita com FOR ROLE se o proprietário das tabelas for outro.
```
CREATE ROLE academy_reader LOGIN;
\\password academy_reader
GRANT CONNECT ON DATABASE academy TO academy_reader;
GRANT USAGE ON SCHEMA academy TO academy_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA academy TO academy_reader;
ALTER DEFAULT PRIVILEGES IN SCHEMA academy GRANT SELECT ON TABLES TO academy_reader;
```
## Backup, restauração e rotina operacional
Faça um dump em formato custom dentro do container e copie o arquivo binário ao host. Evite redirecionar saída binária de pg_dump com PowerShell antigo, pois pode corromper o arquivo. Use um nome com data e retenha versões conforme sua política. O volume não substitui backup; exclusão acidental ou corrupção pode atingir todos os dados do volume.
```
docker exec academy-postgis pg_dump -U academy_admin -d academy -Fc -f /tmp/academy.dump
docker cp academy-postgis:/tmp/academy.dump ./academy.dump
docker exec academy-postgis createdb -U academy_admin academy_restore
docker exec academy-postgis pg_restore -U academy_admin -d academy_restore --exit-on-error /tmp/academy.dump
```
O banco academy_restore deve ser novo; se já existir, escolha outro nome e preserve-o. Compare contagens, SRIDs, índices e consultas após restauração. Registre tempo e versão. Para atualizar a versão principal, planeje migração por dump/restore ou ferramenta suportada; não aponte uma imagem nova para um volume antigo sem verificar compatibilidade.
## Solução de problemas e validação final
- Porta ocupada: confirme qual processo utiliza 5432; ajuste a porta publicada e os clientes de forma consistente, sem encerrar serviços desconhecidos.
- Falha de autenticação: confira usuário, banco, host e senha; mudar POSTGRES_PASSWORD não altera senha já inicializada no volume.
- Extensão ausente: confirme estar conectado ao banco academy e usando imagem PostGIS; cada banco precisa da própria extensão.
- Distância inesperada: confira ordem longitude/latitude, CRS e unidades. Buffers projetados exigem zona adequada.
- Conexão entre containers: localhost dentro do GeoServer não é o PostgreSQL; use rede compartilhada e nome do container, conforme o manual GeoServer.
Complete uma tabela de evidências com comandos, saída esperada, saída observada e decisão. Registre limitações e mantenha credenciais fora dos anexos. A instalação só deve ser considerada validada após a consulta espacial e a restauração do backup no ambiente escolhido.
## Referências oficiais e controle de versão
PostGIS: https://postgis.net/documentation/getting_started/
Imagem oficial PostGIS: https://github.com/postgis/docker-postgis
PostgreSQL 17, CREATE EXTENSION: https://www.postgresql.org/docs/17/sql-createextension.html
Docker Desktop: https://docs.docker.com/desktop/
Consulte requisitos e atualizações antes de instalar. Este roteiro fixa uma combinação didática; registre a tag efetivamente utilizada e teste alterações de versão em ambiente separado.
'''

GEOSERVER='''# Instalação, configuração e publicação no GeoServer
## Escopo, arquitetura e critérios de aceite
Este manual configura um laboratório GeoServer em Docker com catálogo persistente, conectado ao PostGIS do manual complementar. O objetivo é publicar uma camada de pontos sintéticos e validar WMS e WFS. Não pressupõe servidor público nem inclui autorização para publicar dados de terceiros. Registre versão escolhida, sistema, Docker e responsável. Para a imagem, selecione uma versão estável identificada no site oficial; não use tags nightly como 3.0.x ou 3.1.x em produção.
Critérios de aceite: página administrativa acessível localmente, senha inicial alterada, workspace criado, conexão PostGIS funcionando, camada com CRS e limites coerentes, preview WMS e resposta WFS. O catálogo deve permanecer após reinício. Em implantação externa, TLS, regras de acesso e backup também são critérios, não etapas opcionais de documentação.
## Pré-requisitos e escolha da versão
1. Instale Docker Desktop em modo Linux conforme o manual PostGIS. Confira docker info. Reserve memória para os dois serviços, espaço para imagens e catálogo e porta 8080 livre. Neste método a JVM vem na imagem; não é necessário instalar Java no host. Para instalação por WAR, confira a versão Java e o container servlet suportados pelo release escolhido.
2. Consulte https://geoserver.org/release/stable/ e a documentação do projeto Docker. Anote uma tag numérica estável existente. Substitua VERSAO_ESTAVEL no comando; o texto é um parâmetro do roteiro, não uma tag válida. Use a imagem docker.osgeo.org/geoserver fornecida pelo projeto.
3. Abra PowerShell. Crie uma rede de laboratório e conecte academy-postgis já iniciado. Se a rede já existir ou o container já estiver conectado, não repita a criação: inspecione docker network inspect academy-geo. A rede permite resolver o nome academy-postgis a partir do GeoServer.
```
docker network create academy-geo
docker network connect academy-geo academy-postgis
docker volume create academy_geoserver_data
$gsImage = 'docker.osgeo.org/geoserver:VERSAO_ESTAVEL'
docker pull $gsImage
```
## Instalação e persistência do catálogo
Após definir uma tag válida em $gsImage, execute o comando em uma linha. A porta publicada está vinculada a 127.0.0.1. O catálogo fica no volume academy_geoserver_data, montado em /opt/geoserver_data, caminho da imagem oficial. O servidor deve ser mantido local até concluir a revisão de acesso. Não reutilize um catálogo antigo sem backup ao alterar de versão.
```
docker run -d --name academy-geoserver --network academy-geo --restart unless-stopped -p 127.0.0.1:8080:8080 --mount type=volume,source=academy_geoserver_data,target=/opt/geoserver_data $gsImage
docker logs academy-geoserver
```
Abra http://localhost:8080/geoserver e aguarde a tela de boas-vindas. Consulte a credencial inicial da distribuição escolhida e altere imediatamente a senha administrativa pela área Security / Users, Groups, Roles. Não publique a credencial padrão nem a senha adotada no relatório. Registre somente o fato da alteração e a referência de custódia segura.
## Criação do workspace e conexão PostGIS
Na administração, acesse Workspaces e Add new workspace. Nome curto: academy. Namespace URI: https://datageo.example/academy; esta URI é um identificador didático, não um serviço web real. Salve e confira o workspace na listagem. Em Stores, Add new Store, escolha PostGIS. Use nome academy_postgis e workspace academy.
Preencha host academy-postgis, port 5432, database academy, schema academy e user academy_reader criado no manual PostGIS. Informe sua senha de publicação, teste a conexão e salve. O host não deve ser localhost: dentro do container esse nome aponta para o próprio GeoServer. Não marque acesso de escrita se a finalidade for somente leitura. O driver PostGIS integra a distribuição padrão; extensões de outras fontes devem corresponder exatamente à versão instalada.
## Publicação da camada e referência espacial
Na lista de recursos do store, clique Publish ao lado de pontos. Defina Name pontos, título Pontos didáticos DataGeo e resumo identificando dados sintéticos. Confirme Native SRS e Declared SRS EPSG:4326. Calcule limites a partir dos dados e depois os limites geográficos. Os pontos de exemplo estão próximos de longitude -48.55 e latitude -27.59; se a extensão estiver invertida, confira a fonte e a ordem das coordenadas antes de publicar.
Na aba Publishing, selecione estilo point compatível e salve. Abra Layer Preview, localize academy:pontos e use OpenLayers para visualizar. Confira símbolo, extensão, legenda e campos. Não force um CRS incorreto apenas para eliminar aviso: identifique a referência na fonte e use reprojeção adequada. Em WMS 1.3.0, EPSG:4326 tem particularidade de ordem de eixos; clientes devem respeitar a especificação.
## Testes de serviços WMS e WFS
Teste GetCapabilities de WMS e WFS no navegador ou cliente HTTP. Procure o nome academy:pontos, formato e CRS declarados. Depois solicite as feições em GeoJSON; count limita a resposta de estudo. O exemplo não habilita WFS-T nem altera dados.
```
http://localhost:8080/geoserver/academy/wms?service=WMS&version=1.3.0&request=GetCapabilities
http://localhost:8080/geoserver/academy/wfs?service=WFS&version=2.0.0&request=GetCapabilities
http://localhost:8080/geoserver/academy/ows?service=WFS&version=2.0.0&request=GetFeature&typeNames=academy:pontos&outputFormat=application/json&count=10
```
Confira status HTTP, Content-Type, nome da camada, quantidade e coordenadas. Abra também a conexão WMS no QGIS com URL http://localhost:8080/geoserver/academy/wms. Salve uma captura da visualização produzida em seu ambiente e anexe ao registro. Os diagramas deste manual são esquemas de orientação, não provas da instalação realizada.
## Segurança, manutenção e backup
Revise as regras de Data Security e Service Security antes de disponibilizar informações. Conceda apenas leitura aos perfis apropriados e verifique acesso anônimo com janela privada. Não exponha administração, credenciais do banco ou transações WFS sem necessidade. Em acesso externo, configure proxy reverso com HTTPS, URL pública correta e regras de firewall; teste CSRF conforme a documentação, sem desativá-lo indiscriminadamente.
Para backup consistente de laboratório, pare o GeoServer e copie o catálogo completo do container parado. Use um destino novo para preservar versões; docker cp copia diretórios mesmo com o container parado. Reinicie após a cópia. Preserve também o backup PostGIS, a tag da imagem e extensões; o catálogo isolado não contém as tabelas do banco.
```
docker stop academy-geoserver
docker cp academy-geoserver:/opt/geoserver_data ./backup_geoserver_catalogo
docker start academy-geoserver
```
Teste restauração em volume e container novos. O catálogo pode conter informações de conexão: restrinja acesso ao backup e não o publique no Git. Para atualização, faça cópia, revise compatibilidade e extensões e valide novamente preview, WMS e WFS antes de trocar o serviço principal.
## Diagnóstico e checklist de entrega
- Interface indisponível: confira docker ps, logs, porta 8080 e tempo de inicialização. O container ativo pode ainda estar carregando o catálogo.
- Store não conecta: confirme rede academy-geo, host academy-postgis, senha reader, schema e permissões SELECT. Execute consulta no banco para separar falha de rede de falha de autorização.
- Camada sem feições: confira tabela, limites, estilo e escala de visibilidade. Revise filtros e dados antes de recalcular CRS.
- WFS bloqueado: verifique regras de serviço e URL; não conceda escrita ao usuário apenas para resolver leitura.
- Erro após atualização: compare versões do catálogo e extensões com a documentação; restaure somente em ambiente isolado para diagnóstico.
Registre passos executados, resultados dos testes e versão de cada componente. A entrega deve incluir arquitetura, política de acesso, referência espacial, responsável, evidências WMS/WFS e procedimento de recuperação. Revise novamente após mudanças de senha, schema, versão ou proxy.
## Fontes oficiais e atualização do roteiro
Releases estáveis: https://geoserver.org/release/stable/
Docker oficial: https://github.com/geoserver/docker
Instalação e volume: https://docs.geoserver.org/stable/en/user/installation/docker/
Publicação PostGIS: https://docs.geoserver.org/stable/en/user/data/database/postgis.html
Administração e segurança: https://docs.geoserver.org/stable/en/user/security/
As páginas stable podem apontar a documentação em transição; confirme a tag estável no portal de releases e mantenha a documentação correspondente à versão efetivamente instalada.
'''

def diagrama(nome,titulo,etapas):
    image=Image.new('RGB',(1600,650),'#eef4f8'); d=ImageDraw.Draw(image)
    font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',30)
    title=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',38)
    d.rounded_rectangle((25,25,1575,625),radius=24,fill='#0B2F5B')
    d.text((60,55),'DataGeo Academy | '+titulo,font=title,fill='#6BD66A')
    w=340
    for i,(rotulo,linhas) in enumerate(etapas):
        x=60+i*385
        d.rounded_rectangle((x,160,x+w,500),radius=15,fill='#ffffff')
        d.text((x+20,185),f'{i+1:02d}  {rotulo}',font=font,fill='#0B2F5B')
        for j,linha in enumerate(linhas):
            d.text((x+20,265+j*50),linha,font=font,fill='#255064')
        if i<3:
            d.line((x+w+5,330,x+w+35,330),fill='#16BFD0',width=8)
            d.polygon([(x+w+35,330),(x+w+23,320),(x+w+23,340)],fill='#16BFD0')
    d.text((60,555),'Esquema didático: confira telas, versões e resultados no seu ambiente.',font=font,fill='#d4e8ef')
    path=DEST/'ilustracoes'/f'{nome}.png';image.save(path)
    return path

def ilustrar(doc,imagens):
    with ZipFile(doc) as z:parts={n:z.read(n) for n in z.namelist()}
    document=ET.fromstring(parts['word/document.xml']);body=document.find(f'{{{corp.W}}}body')
    ns='http://schemas.openxmlformats.org/package/2006/relationships'
    relationships=[]
    for i,(titulo,path) in enumerate(imagens,1):
        rid=f'rIdFigura{i}'
        relationships.append(f'<Relationship Id="{rid}" Type="{corp.R}/image" Target="media/figura{i}.png"/>')
        parts[f'word/media/figura{i}.png']=path.read_bytes()
        p=ET.fromstring(f'''<w:p xmlns:w="{corp.W}" xmlns:r="{corp.R}" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture"><w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="6000000" cy="2437500"/><wp:docPr id="{i}" name="Diagrama {i}" descr="{titulo}"/><a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture"><pic:pic><pic:nvPicPr><pic:cNvPr id="{i}" name="figura{i}.png"/><pic:cNvPicPr/></pic:nvPicPr><pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill><pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="6000000" cy="2437500"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>''')
        # Coloca figura junto ao título correspondente, mantendo o sumário original.
        destino=next(node for node in body if node.find(f'{{{corp.W}}}pPr/{{{corp.W}}}pStyle') is not None
                     and node.find(f'{{{corp.W}}}pPr/{{{corp.W}}}pStyle').get(f'{{{corp.W}}}val')=='Heading1'
                     and titulo in ''.join(node.itertext()))
        pos=list(body).index(destino)+1;body.insert(pos,p)
        caption=ET.Element(f'{{{corp.W}}}p');corp.base.element(corp.base.element(caption,'r'),'t',text=f'Figura {i} — {titulo}. Esquema didático DataGeo Academy.')
        body.insert(pos+1,caption)
    parts['word/document.xml']=corp.base.xml(document)
    # Mantém o namespace padrão do pacote, aceito por Word e LibreOffice.
    parts['word/_rels/document.xml.rels']=parts['word/_rels/document.xml.rels'].replace(b'</Relationships>',(''.join(relationships)+'</Relationships>').encode('utf-8'))
    parts['[Content_Types].xml']=parts['[Content_Types].xml'].replace(b'</Types>',b'<Default Extension="png" ContentType="image/png"/></Types>')
    with ZipFile(doc,'w',ZIP_DEFLATED) as z:
        for name,data in parts.items():z.writestr(name,data)

def main():
    (DEST/'ilustracoes').mkdir(parents=True,exist_ok=True)
    for nome,fonte,figuras in [
        ('manual_postgis',POSTGIS,[
            ('Preparação e instalação passo a passo',[('Preparar',['Docker Linux','Porta 5432 livre']),('Instalar',['Imagem PostGIS','Volume persistente']),('Conectar',['pg_isready','Banco academy']),('Validar',['Versão / dados','Consulta espacial'])]),
            ('Referência espacial, índices e medidas',[('Fonte',['WGS84 / 4326','Longitude, latitude']),('Converter',['ST_Transform','UTM 22S / 31982']),('Analisar',['GiST / geography','Metros / hectares']),('Revisar',['CRS e região','Resultados e testes'])])]),
        ('manual_geoserver',GEOSERVER,[
            ('Criação do workspace e conexão PostGIS',[('Workspace',['Nome academy','Namespace URI']),('Store',['PostGIS / academy','academy-postgis']),('Permissões',['academy_reader','Somente SELECT']),('Publicação',['Tabela pontos','CRS / extensão'])]),
            ('Testes de serviços WMS e WFS',[('PostGIS',['Dados e índice','Rede academy-geo']),('GeoServer',['Store e camada','Catálogo no volume']),('Serviços',['WMS: mapa','WFS: feições']),('Clientes',['QGIS / navegador','Validação de saída'])])])]:
        dest=DEST/f'{nome}.docx';corp.gerar(fonte,dest,'Manual profissional ilustrado · Instalação e configuração')
        ilustrar(dest,[(titulo,diagrama(f'{nome}_{i}',titulo,etapas)) for i,(titulo,etapas) in enumerate(figuras,1)])
    print('2 manuais DOCX gerados, com cabeçalho, sumário e 4 diagramas incorporados.')

if __name__=='__main__':main()
