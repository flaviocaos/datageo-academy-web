# DataGeo Academy Web

Landing page responsiva da **DataGeo Academy**, com o slogan **“Conhecimento que gera decisões”**. O projeto combina HTML, CSS e JavaScript com scripts Python que leem o acervo local e geram as seções de materiais no `index.html`.

O painel de mini-cursos contém **6 abas, 32 cursos e 127 PDFs**, organizados a partir da estrutura de pastas. Cada curso apresenta o botão **Acessar Material**, que abre uma lista de PDFs dentro do próprio card. Os links abrem os arquivos reais em uma nova aba.

## Recursos da página

- Cabeçalho com logotipo, seção principal e apresentação institucional.
- Seis frentes de trabalho, com cards e ícones lineares.
- Dois livros técnicos com links para os PDFs.
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

Os scripts esperam a pasta `ENTREGA` no mesmo nível de `SITE`:

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
│   └── mini_cursos_acervo.json
└── ENTREGA/                      # Acervo externo ao repositório
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

Os PDFs e as imagens em `ENTREGA` precisam ser disponibilizados separadamente. Clonar este repositório fornece o site e os scripts; os links para o acervo dependem dessa estrutura externa.

## Visualizar localmente

Para visualizar somente a página, abra `SITE/index.html` no navegador.

Para testar também os links relativos por HTTP, execute na pasta que contém **SITE e ENTREGA**:

```powershell
python -m http.server 8000
```

Acesse **http://localhost:8000/SITE/**. Assim, os caminhos `../ENTREGA/...` apontam para o acervo servido pelo mesmo endereço.

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

1. Identifica as seis pastas de áreas em `ENTREGA/Mini_Cursos/AREAS`.
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

Para publicar com os materiais funcionando, preserve a relação entre `SITE` e `ENTREGA` no servidor ou adapte os caminhos do HTML e dos scripts à estrutura de hospedagem. Publicar somente a raiz deste repositório não disponibiliza os arquivos externos referenciados por `../ENTREGA/...`.

## Licença

Consulte o arquivo [LICENSE](LICENSE) para os termos aplicáveis ao projeto.
