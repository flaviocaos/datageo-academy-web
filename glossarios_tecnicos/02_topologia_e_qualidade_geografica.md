# Topologia e qualidade geográfica

**DataGeo Academy — material técnico | edição 1.0 | 2026-10-01**

Diferencie problemas geométricos, relações espaciais e critérios de aceite.

## Como consultar

Este glossário reúne doze conceitos e seus cuidados operacionais. As definições
são referências introdutórias para leitura e comunicação; consulte a documentação
da ferramenta e a metodologia do projeto para uma implementação específica.

## Conceitos e aplicação

### Validade geométrica

Conformidade interna de uma geometria com regras do modelo; não garante relações corretas entre feições.

### Topologia

Relações como conexão, adjacência e contenção; regras dependem da finalidade da base.

### Sobreposição

Área compartilhada entre feições; pode ser erro de uma partição ou relação legítima entre temas.

### Lacuna

Região sem cobertura; só é erro onde o modelo exige continuidade e não autoriza vazios.

### Sliver

Fragmento estreito frequentemente produzido por desalinhamento; não deve ser removido sem avaliação de escala e origem.

### Snapping

Ajuste de vértices segundo uma tolerância; valores excessivos podem alterar relações legítimas.

### Dangle

Extremidade sem conexão de uma linha; pode representar erro ou terminal legítimo de rede.

### Multipartes

Feição com vários componentes geométricos; sua existência não representa erro por definição.

### Autointerseção

Cruzamento da própria geometria; pode invalidar polígonos conforme o modelo adotado.

### Tolerância

Limite de comparação ou edição com unidade e justificativa; não use um número universal.

### Integridade referencial

Consistência dos vínculos entre registros, geralmente mantida por chaves e restrições.

### Exceção aprovada

Ocorrência permitida com justificativa e aprovação rastreáveis; não é erro simplesmente ocultado.

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
