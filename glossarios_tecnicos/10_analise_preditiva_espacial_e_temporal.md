# Análise preditiva espacial e temporal

**DataGeo Academy — material técnico | edição 1.0 | 2026-10-01**

Revise os termos usados para antecipar cenários e medir a qualidade da previsão.

## Como consultar

Este glossário reúne doze conceitos e seus cuidados operacionais. As definições
são referências introdutórias para leitura e comunicação; consulte a documentação
da ferramenta e a metodologia do projeto para uma implementação específica.

## Conceitos e aplicação

### Defasagem/lag

Valor de período anterior usado como atributo; não deve incorporar informação futura.

### Horizonte

Quantidade de passos futuros previstos; erros e incerteza podem crescer com a distância temporal.

### Tendência

Componente de evolução ao longo do tempo; extrapolação não garante continuidade futura.

### Sazonalidade

Padrão associado a ciclos regulares, distinto de tendência e eventos isolados.

### Interpolação

Estimativa entre observações segundo um modelo espacial ou temporal.

### Extrapolação

Estimativa além do domínio observado, frequentemente com maior risco de erro.

### IDW

Média ponderada por distância inversa; exige escolhas de potência, vizinhança e tratamento de coincidências.

### RBF

Interpolação por funções de base radial; pressupostos e suavização influenciam a superfície.

### MAE

Média do erro absoluto; mantém unidade do alvo e reduz ênfase em grandes erros frente ao RMSE.

### RMSE

Raiz da média do erro quadrático; destaca erros grandes e mantém unidade do alvo.

### R²

Comparação do erro com variabilidade observada; pode ser negativo fora do treino e não mede causalidade.

### Backtesting

Avaliação em períodos posteriores ao treino por janelas; respeita a ordem temporal e disponibilidade dos atributos.

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
