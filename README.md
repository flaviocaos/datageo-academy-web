# DataGeo Academy Web

Landing page responsiva da **DataGeo Academy**, com o slogan **“Conhecimento que gera decisões”**. O projeto combina HTML, CSS e JavaScript com scripts Python que leem o acervo local e geram as seções de materiais no `index.html`.

O painel de mini-cursos contém **6 abas, 32 cursos e 127 PDFs**, organizados a partir da estrutura de pastas. Cada curso apresenta o botão **Acessar Material**, que abre uma lista de PDFs dentro do próprio card. Os links abrem os arquivos reais em uma nova aba.

## Recursos da página

- Cabeçalho com logotipo, seção principal e apresentação institucional.
- Seis frentes de trabalho, com cards e ícones lineares.
- Trinta livros acadêmicos em PDF, com 40 a 60 páginas, organizados nas mesmas seis áreas dos minicursos, com cinco livros por aba e capas integradas.
- 49 apresentações técnicas com capas reais em formato horizontal: três cards iniciais e 46 na grade expansível.
- Mini-cursos organizados por área, com navegação por teclado entre as abas.
- 14 infográficos horizontais: três cards iniciais e 11 na grade expansível.
- Diferenciais, linha do tempo, chamada comercial para WhatsApp e formulário de contato.
- Rodapé com links institucionais e contatos.

A identidade visual utiliza azul escuro `#0B2F5B`, verde `#6BD66A` e ciano `#16BFD0`. O CSS e o JavaScript estão embutidos no HTML; a página não exige compilação ou um servidor de aplicação.

## Áreas e acervo de mini-cursos

| Área | Cursos | PDFs |
| --- | ---: | ---: |
| IA e Machine Learning | 4 | 22 |
| Geotecnologias | 18 | 72 |
| BI - Business Intelligence | 1 | 5 |
| Ciência de Dados | 2 | 8 |
| Programação para Dados | 6 | 16 |
| Análise Preditiva | 1 | 4 |
| **Total** | **32** | **127** |

Os números representam o acervo mapeado atualmente. A execução do script atualiza o conteúdo quando novos cursos e PDFs são adicionados.

## Estrutura de arquivos

O acervo de origem está incluído na pasta `ENTREGA`: 127 PDFs dos mini-cursos, dois livros em PDF e suas capas, 49 apresentações e suas capas, e 14 infográficos. A seção de Livros Acadêmicos usa os 30 arquivos PDF de `livros_academicos`. Os scripts de origem priorizam a pasta local e também suportam a estrutura legada com `ENTREGA` no diretório pai.

```text
DATAGEO_ACADEMY/
├── SITE/                         # Este repositório
│   ├── index.html
│   ├── LOGOMARCA_2.png
│   ├── README.md
│   ├── LICENSE
│   ├── gerar_capas.py
│   ├── gerar_capas_apresentacoes.py
│   ├── atualizar_apresentacoes.py
│   ├── mapear_mini_cursos.py
│   ├── mini_cursos_acervo.json
│   └── ENTREGA/
│       ├── Livros_Tecnicos/       # 2 PDFs e 2 capas PNG
│       ├── Apresentacoes_Tecnicas/ # 49 PDFs e 49 capas PNG
│       ├── Infograficos/          # 14 PNGs
│       └── Mini_Cursos/
│           └── AREAS/
│               └── AREA N - Nome da Área/
│                   └── Nome do Curso/
│                       └── pdf/
│                           └── *.pdf  # 127 PDFs versionados
└── ENTREGA/                      # Alternativa legada, opcional
    ├── Livros_Tecnicos/
    │   ├── *.pdf
    │   ├── capa_cartografia.png
    │   └── capa_ia.png
    ├── Apresentacoes_Tecnicas/
    │   ├── Nome_do_Arquivo.pdf
    │   └── Nome_do_Arquivo_capa.png
    ├── Infograficos/
    │   └── *.png
    └── Mini_Cursos/
        └── AREAS/
            └── AREA N - Nome da Área/
                └── Nome do Curso/
                    ├── pdf/
                    │   └── *.pdf
                    └── ppt/     # Ignorada pelo mapeamento
```

Clonar este repositório fornece o site, os scripts e todos os materiais. Os links do HTML apontam para `ENTREGA/...`, dentro da raiz do projeto.

## Visualizar localmente

Para visualizar somente a página, abra `SITE/index.html` no navegador.

Para testar também os links relativos por HTTP, execute na raiz deste repositório:

```powershell
python -m http.server 8000
```

Acesse **http://localhost:8000/**. Assim, os caminhos `ENTREGA/...` apontam para o acervo servido pelo mesmo endereço.

## Scripts Python

Use Python 3.10 ou superior. O mapeamento dos cursos e a atualização do HTML usam apenas a biblioteca padrão. A geração de capas utiliza **PyMuPDF**; a validação das capas dos livros também utiliza **Pillow**.

Para instalar as dependências no seu ambiente Python:

```powershell
python -m pip install PyMuPDF Pillow
```

Os scripts de capas também procuram PyMuPDF em `.capas-deps`, caso exista uma instalação local nessa pasta.

Execute os comandos abaixo dentro de `SITE`.

### Atualizar mini-cursos

```powershell
python mapear_mini_cursos.py
```

O script:

1. Identifica as seis pastas de áreas em `SITE/ENTREGA/Mini_Cursos/AREAS`; se essa pasta não existir, usa `ENTREGA/Mini_Cursos/AREAS` no diretório pai.
2. Inclui somente cursos com uma subpasta direta chamada `pdf`.
3. Coleta os PDFs nessa subpasta e em seus subdiretórios, ignorando pastas `ppt`.
4. Gera títulos amigáveis e links relativos com espaços e acentos codificados.
5. Atualiza a seção de mini-cursos com seis abas e listas de materiais por curso.
6. Salva o inventário em `mini_cursos_acervo.json`, incluindo nomes, caminhos e URLs.

Cada execução preserva as demais seções do HTML. O script espera exatamente seis áreas, numeradas pelas pastas `AREA 1` a `AREA 6`.

### Gerar capas dos livros

```powershell
python gerar_capas.py
```

Renderiza a primeira página dos dois livros configurados no script em **300 DPI** e salva `capa_cartografia.png` e `capa_ia.png` na pasta `Livros_Tecnicos`. Esse script gera as imagens; ele não altera os cards dos livros no HTML.

### Gerar capas e atualizar apresentações

```powershell
python gerar_capas_apresentacoes.py
python atualizar_apresentacoes.py
```

O primeiro comando converte a primeira página de cada PDF em PNG a **300 DPI**, com o nome original seguido de `_capa.png`. O segundo verifica as capas e atualiza os cards com títulos amigáveis, imagens e links para os PDFs.

As apresentações são ordenadas alfabeticamente pelo nome do arquivo. Os três primeiros cards ficam visíveis e os restantes entram na grade expansível. Gere as capas antes de atualizar o HTML.

## Contato e publicação

O WhatsApp e o e-mail ficam na configuração `CONTACT` do JavaScript em `index.html`, além dos links do rodapé. O formulário prepara um e-mail no aplicativo do visitante; o envio deve ser confirmado nesse aplicativo. A página não possui backend para envio automático.

Publique a raiz deste repositório incluindo `index.html`, o logotipo e a pasta `ENTREGA`. Todos os materiais utilizam caminhos relativos locais e acompanham a publicação do site. Preserve nomes de arquivos, acentos e estrutura de subpastas para manter os links funcionando.

## Acervo de 30 livros acadêmicos

A seção mantém seis abas de conhecimento. A primeira se chama
**Inteligência Artificial e Data Science**; as outras cinco mantêm nomes e ordem
dos minicursos. Cada aba contém
exatamente cinco livros, com miniatura em HTML/CSS no padrão azul-escuro,
logotipo DataGeo e detalhes verdes. Todos os botões usam `download` e arquivos
PDF locais; a navegação por teclado e as abas são independentes das demais seções.

Os 28 volumes não oficiais possuem **42 páginas cada**, autoria institucional DataGeo
Academy, capa, folha de rosto, controle documental, sumário com 12 capítulos,
introdução, tabelas comparativas, laboratórios e exercícios comentados.
Cada capítulo reúne fundamentos, laboratório reproduzível e exercícios.
O texto é pesquisável e os marcadores do PDF levam às páginas corretas.

Os PDFs oficiais de Cartografia (53 páginas) e Inteligência Artificial Aplicada
(60 páginas) foram copiados de `ENTREGA/Livros_Tecnicos` **sem alteração binária**.
Os 28 DOCX antigos de seis páginas foram removidos após conferir sua paginação.
Os dois DOCX legados de Cartografia (48 páginas) e IA (60 páginas) foram
preservados por não se enquadrarem na remoção de materiais com menos de 40 páginas;
eles não são usados nos botões. `limpeza_documental.json` registra essa auditoria.

O arquivo `livros_academicos/catalogo.json` registra áreas, nomes, páginas e hashes.
O compilador preserva os dois PDFs oficiais e interrompe se encontrar uma cópia
divergente. O gerador antigo de DOCX foi bloqueado para não recriar livros curtos.
Os quatro provisórios da primeira aba foram removidos e substituídos por
manuscritos independentes, com **12 capítulos próprios e 12 laboratórios reais
por livro**:

- Ciência de Dados Espaciais com GeoPandas: CRS, qualidade geométrica, joins,
  overlays, buffers, agregação, índices, proximidade, interpolação e GeoPackage.
- Machine Learning Territorial com Scikit-Learn: validação por blocos, pipelines,
  atributos mistos, logística, árvores, florestas, métricas, busca, calibração,
  custos e interpretação.
- Deep Learning Geoespacial com CNNs: tensores multiespectrais, normalização,
  convoluções, encoder-decoder, treino, perdas mascaradas, augmentação, métricas,
  validação por cena, mosaicos e checkpoints PyTorch.
- Análise Preditiva de Expansão Urbana: transições, covariáveis históricas,
  propensão, backtesting, demanda, autômatos celulares, cenários, FoM, ensembles,
  taxas temporais e GeoTIFF.

As fontes estão em `scripts_automacao/livros_ia`. Os exemplos usam dados
sintéticos declarados, APIs das bibliotecas dos respectivos temas e asserções;
os PDFs incorporam códigos, fonte editorial, requisitos e resultados calculados.
`substituicao_ia.json` registra arquivos removidos, hashes e ambiente utilizado.
Os outros 25 PDFs, incluindo Cartografia, permanecem intactos.

Para regenerar somente os quatro volumes desta edição e atualizar o HTML:

```powershell
python -m pip install -r scripts_automacao/livros_ia/requirements.txt
python scripts_automacao/gerar_livros_ia.py --integrar
python scripts_automacao/atualizar_livros_academicos.py
python tests/verificar_livros_ia.py
python tests/verificar_livros_pdf.py
```

A compilação e verificação usam **PyMuPDF**, GeoPandas, Scikit-Learn, PyTorch CPU
e Rasterio. Para instalar PyTorch CPU, consulte o índice oficial
`https://download.pytorch.org/whl/cpu`. O ambiente de referência e suas versões
ficam registrados no PDF. Foram conferidas 1.289 páginas
no acervo, a identidade dos dois originais e a execução dos **336 laboratórios**
dos livros não oficiais, incluindo os 48 especializados da nova edição.
O gerador legado bloqueia geração em lote após essa substituição para não
recriar provisórios; `--somente` continua disponível para os outros 24 volumes.
Os exemplos são de estudo e não resultados de cliente.
Para extrair anexos em uma pasta nova:

```powershell
python scripts_automacao/extrair_laboratorios_pdf.py "livros_academicos/Machine Learning Territorial com Scikit-Learn.pdf" "laboratorios_ml"
```

## Central de Materiais Premium & Carreira

A Central tem **três abas independentes**, 41 links de download direto e
13 portais de emprego. As coleções expansíveis e os filtros de portais mantêm
a interface compacta e responsiva, sem interferir nas seis abas dos minicursos.

| Aba | Conteúdo |
| --- | --- |
| Materiais Práticos | Seis kits existentes de automação, dez scripts topográficos e onze arquivos de bancos geográficos (instaladores, SQL, consultas mongosh e guia) |
| Guias de Carreira | Template Word de relatório técnico, oito portais nacionais e cinco canais internacionais / remotos de GIS |
| Desafios e Gamificação | Checklist técnico existente, dez exercícios Python com TODOs e verificações, dois manuais Word ilustrados de GeoServer e PostGIS |

Os scripts de `scripts_topografia` são independentes e usam apenas a biblioteca
padrão Python. Execute `python scripts_topografia/02_azimute.py --exemplo` para
ver o JSON de entrada; depois passe um arquivo JSON ao script. Os cálculos usam
coordenadas planas em metros, azimutes a partir do norte e graus decimais.
O memorial é uma minuta de cálculo que precisa de revisão profissional.

Em `scripts_bancos_geo`, consulte o README antes de instalar: Docker Desktop
em modo Linux, credenciais por ambiente, portas locais e volumes persistentes.
PostGIS e Oracle usam SQL; MongoDB usa JavaScript no mongosh, seu formato nativo.
Os instaladores não são executados pelo site. Os três motores não foram
instalados durante esta atualização; a execução das consultas depende do seu
laboratório. Os scripts não removem volumes existentes.

Os exercícios de `desafios_python` estão **deliberadamente incompletos**:
substitua o `NotImplementedError` em `resolver()` e execute o arquivo para
rodar os casos de verificação. Não são kits prontos de produção.
Os manuais em `roteiros_servidores` são DOCX editáveis com cabeçalho DataGeo
Academy, sumário, comandos, critérios de aceite e diagramas incorporados.
As ilustrações são esquemas didáticos, não capturas de uma instalação real.

Regeneração dos novos materiais:

```powershell
python scripts_automacao/gerar_biblioteca_refinada.py
python scripts_automacao/gerar_manuais_servidores.py
python scripts_automacao/atualizar_central_refinada.py
python tests/verificar_central_refinada.py
```

A geração dos manuais exige Pillow; os cálculos e a verificação acima não
exigem dependências externas. Portais conferidos em outubro de 2026: são
canais de busca, sem garantia de vaga disponível ou de elegibilidade global.

## Biblioteca anterior preservada

Os 60 materiais anteriores foram retirados da Central para evitar repetição.
Seus arquivos continuam preservados no repositório: dez projetos QGIS `.qgz`,
dez bases `.gpkg`, quarenta documentos Word `.docx` e dez estilos `.qml`.

Os projetos foram gerados e reabertos no QGIS 3.28.2 e incorporam os dados,
estilos e instruções dentro do QGZ. Podem ser copiados sem transportar pastas
externas. Os GeoPackages usam o perfil 1.3, SIRGAS 2000 / UTM 22S e **dados
sintéticos identificados** para exercícios. Não são levantamentos oficiais.

Os documentos Word contêm cabeçalho DataGeo Academy, controle documental,
sumário navegável, texto técnico, tabelas e revisão. O sumário pode ser atualizado
no Word após a edição. Documentos demonstrativos não constituem laudos assinados.
Os quarenta Markdown anteriores foram substituídos pelos DOCX.

Para regenerar os documentos, execute `python scripts_automacao/gerar_documentos_corporativos.py`.
O conteúdo de origem está incorporado em cada DOCX. Para regenerar os projetos,
execute `scripts_automacao/gerar_projetos_qgis_premium.py` com o Python do QGIS;
as instruções TXT preservadas em `templates_gis` são usadas como fonte.

Valide os arquivos da biblioteca anterior com `python tests/verificar_materiais_premium.py`
em um ambiente com GeoPandas e Pyogrio. O gerador legado de Markdown bloqueia a
substituição dos formatos corporativos atuais.

## Licença

Consulte o arquivo [LICENSE](LICENSE) para os termos aplicáveis ao projeto.
