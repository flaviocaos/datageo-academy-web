# Drones e fotogrametria

**DataGeo Academy — material técnico | edição 1.0 | 2026-10-01**

Entenda os termos que conectam levantamento, processamento e produto.

## Como consultar

Este glossário reúne doze conceitos e seus cuidados operacionais. As definições
são referências introdutórias para leitura e comunicação; consulte a documentação
da ferramenta e a metodologia do projeto para uma implementação específica.

## Conceitos e aplicação

### Ortofoto

Imagem corrigida geometricamente para reduzir efeitos de perspectiva e relevo, segundo o processo empregado.

### GSD

Distância amostrada no terreno por pixel; não equivale a erro posicional validado.

### Nuvem de pontos

Conjunto de coordenadas 3D e atributos derivados de levantamento ou processamento.

### MDS

Modelo digital de superfície que pode incluir vegetação, edificações e outros objetos.

### MDT

Modelo digital do terreno, cujo objetivo é representar a superfície do solo após classificação adequada.

### Ponto de apoio

Ponto usado no ajuste; não é independente para medir a qualidade desse mesmo ajuste.

### Ponto de verificação

Ponto excluído do ajuste e reservado à avaliação independente de posição.

### Sobreposição de imagens

Cobertura comum entre imagens para reconstrução e alinhamento; exigência depende do projeto.

### Aerotriangulação

Estimativa da geometria de aquisição e correspondências entre imagens.

### RTK

Posicionamento relativo com correções em tempo real; requer condições e rastreabilidade adequadas.

### PPK

Processamento posterior de observações de posicionamento; não dispensa verificação do produto.

### RMSE posicional

Raiz da média dos quadrados dos erros em relação a referência independente; declare eixos e unidades.

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
