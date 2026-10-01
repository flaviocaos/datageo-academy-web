# Sensoriamento remoto e sensores

**DataGeo Academy — material técnico | edição 1.0 | 2026-10-01**

Conecte o vocabulário de aquisição de imagens à interpretação dos produtos.

## Como consultar

Este glossário reúne doze conceitos e seus cuidados operacionais. As definições
são referências introdutórias para leitura e comunicação; consulte a documentação
da ferramenta e a metodologia do projeto para uma implementação específica.

## Conceitos e aplicação

### Resolução espacial

Dimensão do elemento amostrado; tamanho de pixel não garante precisão da posição.

### Resolução espectral

Detalhe de discriminação de faixas do espectro captadas pelo sensor.

### Resolução temporal

Frequência de observação; revisita nominal não assegura cenas sem nuvens.

### Resolução radiométrica

Capacidade de quantizar sinal; número de bits não determina sozinho qualidade da informação.

### Reflectância

Razão relacionada à energia refletida; compare produtos calibrados e processamento compatível.

### Radiância

Energia radiativa medida por unidade de área, ângulo sólido e faixa; difere de reflectância.

### NDVI

Índice (NIR-vermelho)/(NIR+vermelho); exige bandas corretas e tratamento de nodata e denominador zero.

### Máscara de nuvem

Identificação de pixels não utilizáveis por cobertura atmosférica; revise critérios e sombras.

### Classificação supervisionada

Atribuição de classes com exemplos rotulados; qualidade depende das amostras e avaliação independente.

### Matriz de confusão

Contagem de referências versus previsões por classe, usada para calcular métricas.

### Nodata

Código ou máscara de ausência de observação; não deve ser interpretado como zero físico.

### Composição de bandas

Representação conjunta de bandas em canais de cor; cores falsas não indicam valores naturais.

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
