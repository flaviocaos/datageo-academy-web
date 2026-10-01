# IA e Machine Learning

**DataGeo Academy — material técnico | edição 1.0 | 2026-10-01**

Entenda o vocabulário de modelos e avaliação em aplicações territoriais.

## Como consultar

Este glossário reúne doze conceitos e seus cuidados operacionais. As definições
são referências introdutórias para leitura e comunicação; consulte a documentação
da ferramenta e a metodologia do projeto para uma implementação específica.

## Conceitos e aplicação

### Atributo/feature

Variável usada pelo modelo; deve estar disponível no instante e local da previsão.

### Alvo

Variável que se deseja estimar; defina unidade, classe e modo de obtenção.

### Treino

Dados usados para ajustar parâmetros do modelo e pré-processamento.

### Validação

Dados ou procedimento para escolher e avaliar configurações sem contaminar o teste final.

### Teste

Conjunto reservado para estimar generalização após decisões de modelagem.

### Vazamento

Uso indevido de informação futura, do teste ou de vizinhos dependentes durante o ajuste.

### Hiperparâmetro

Configuração escolhida fora do ajuste interno; seleção deve respeitar a divisão dos dados.

### Overfitting

Ajuste excessivo a padrões do treino com generalização insuficiente.

### Classificação

Predição de categorias; avaliação por classe pode ser mais informativa que acurácia global.

### Regressão

Predição de valores contínuos; métricas devem informar a unidade e a distribuição dos erros.

### Agrupamento

Organização não supervisionada por similaridade; grupos não têm significado causal automático.

### Validação espacial

Separação por blocos ou regiões para reduzir dependência entre treino e teste.

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
