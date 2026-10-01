# BI, dashboards e indicadores

**DataGeo Academy — material técnico | edição 1.0 | 2026-10-01**

Comunique requisitos e resultados com conceitos claros de análise de negócio.

## Como consultar

Este glossário reúne doze conceitos e seus cuidados operacionais. As definições
são referências introdutórias para leitura e comunicação; consulte a documentação
da ferramenta e a metodologia do projeto para uma implementação específica.

## Conceitos e aplicação

### KPI

Indicador vinculado a objetivo e decisão; declare fórmula, unidade, período e responsável.

### Granularidade

Nível de detalhe de cada registro; determina agregações e relações válidas.

### Dimensão

Entidade descritiva usada para filtrar ou agrupar fatos, como território e tempo.

### Fato

Registro de ocorrência ou medida no nível definido; evite misturar granularidades.

### Medida

Cálculo de resultado sob contexto de filtros; diferencie valor armazenado de expressão calculada.

### Denominador

Base de uma taxa; zero ou períodos incompatíveis exigem tratamento explícito.

### Filtro

Restrição de contexto; verifique sua propagação no modelo e nas visualizações.

### Drill-down

Navegação para níveis mais detalhados; exige hierarquia e dados disponíveis coerentes.

### Dashboard

Conjunto de visualizações orientado a perguntas e ações, não apenas coleção de gráficos.

### Narrativa analítica

Sequência de explicação de contexto, evidência e implicação com limites declarados.

### Atualização

Reprocessamento dos dados; registre origem, falhas e data da informação exibida.

### Acessibilidade

Condições para compreender e operar o painel, incluindo contraste, rótulos e alternativas à cor.

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
