# SQL, PostGIS e bancos espaciais

**DataGeo Academy — material técnico | edição 1.0 | 2026-10-01**

Revise conceitos essenciais para modelar dados e conversar sobre consultas.

## Como consultar

Este glossário reúne doze conceitos e seus cuidados operacionais. As definições
são referências introdutórias para leitura e comunicação; consulte a documentação
da ferramenta e a metodologia do projeto para uma implementação específica.

## Conceitos e aplicação

### Chave primária

Identificador único não nulo de um registro; não confundir com posição atual na tabela.

### Chave estrangeira

Vínculo que referencia uma chave de outra tabela e ajuda a manter integridade.

### JOIN

Combinação de registros por condição; relações 1:N podem multiplicar linhas.

### SRID

Identificador de referência espacial associado à geometria; atribuir não transforma coordenadas.

### Índice GiST

Estrutura usada por PostGIS para acelerar consultas espaciais compatíveis; confirme benefício no plano.

### ST_Within

Testa interior/contenção segundo relações topológicas; pontos apenas na borda não estão within.

### ST_Covers

Relação inclusiva de cobertura que pode incluir a borda; pode gerar múltiplas correspondências.

### ST_Intersects

Testa se geometrias compartilham pelo menos um ponto, incluindo contato na borda.

### ST_Transform

Transforma coordenadas para outro SRID; exige CRS de origem correto.

### ST_SetSRID

Atribui referência à geometria sem transformar valores de coordenadas.

### Transação

Unidade de operações com confirmação ou reversão; use para evitar estados parcialmente atualizados.

### GeoPackage

Contêiner SQLite para dados geoespaciais com estruturas padronizadas; não é um servidor PostGIS.

## Uso em uma análise

Escolha três termos relevantes ao projeto. Escreva onde cada um aparece no seu
fluxo de trabalho, qual entrada depende dele e qual erro de interpretação pode
alterar o resultado. Acrescente uma evidência: propriedade de camada, consulta,
parâmetro, cálculo ou saída de validação.

## Revisão rápida

- Diferencie unidade, valor medido e indicador derivado.
- Informe fonte, período e pressuposto antes de comparar resultados.
- Não interprete coincidência, associação ou aparência como prova de causalidade.
- Registre versões e critérios: nomes semelhantes podem ter implementações diferentes.
- Explique termos ao destinatário sem retirar as limitações relevantes.

## Autoavaliação

1. Qual par de conceitos deste glossário é frequentemente confundido?
2. Que erro prático essa confusão pode causar no seu projeto?
3. Qual registro permitiria a um revisor detectar o problema?

Responda com um exemplo pequeno e verificável. A consulta do glossário não
substitui a validação das operações nem confirma qualidade dos dados de origem.

Referências para aprofundamento: https://docs.qgis.org/3.44/en/docs/user_manual/ ;
https://postgis.net/docs/ ; https://scikit-learn.org/stable/user_guide.html ;
https://www.ibge.gov.br/geociencias/informacoes-sobre-posicionamento-geodesico/sirgas.html
