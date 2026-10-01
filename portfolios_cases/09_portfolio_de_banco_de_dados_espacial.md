# Portfólio de banco de dados espacial

**DataGeo Academy — material técnico | edição 1.0 | 2026-10-01**

Apresente arquitetura, consultas e qualidade como diferenciais técnicos.

## Caso demonstrativo: Arquitetura de banco espacial

Este é um roteiro técnico para construir um estudo de caso, não um relato de
cliente atendido nem uma promessa de desempenho. Dados e números de exemplo são
didáticos. Para divulgar um trabalho real, substitua-os por evidências autorizadas.

## Problema e proposta

**Objetivo:** Demonstrar modelagem, integridade e consultas orientadas ao uso.

**Entradas:** Esquema de unidades, ativos e observações; diagrama e consultas SQL.

Defina o destinatário, a pergunta analítica, o período e o uso esperado. Identifique
qual decisão o resultado pode apoiar e qual decisão exige informação adicional.

## Desenvolvimento documentado

1. Definir chaves primárias e estrangeiras.
2. Escolher SRID e índices.
3. Validar inserções e consultas de relacionamento.
4. Documentar desempenho e decisões de modelagem.

## Resultado de referência e discussão

Uma junção 1:N pode duplicar unidades; agregue ativos antes de contar unidades territoriais.

## Estrutura da apresentação

1. Contexto: área, período, pergunta e relevância do problema.
2. Dados: origem, limitações, unidades, CRS e permissão de divulgação.
3. Método: sequência de operações, parâmetros, versões e escolhas do autor.
4. Evidências: mapa, tabela, consulta, métrica ou execução com referência verificável.
5. Discussão: o que foi demonstrado, o que permanece incerto e alternativas.
6. Próximo passo: validação necessária ou evolução do projeto, sem garantia de ganho.

## Pacote mínimo para portfólio

| Entrega | O que comprovar |
| --- | --- |
| Resumo executivo | Problema e contribuição claramente identificados |
| Dados demonstrativos / links permitidos | Origem, data e condições de acesso |
| Método reproduzível | Entradas, etapas e parâmetros registrados |
| Evidências de resultado | Referência aos produtos e critérios de conferência |
| Limitações | Escala, precisão, amostragem e restrições de uso |

## Revisão profissional

- [ ] Distinguir trabalho próprio, colaboração e fontes externas.
- [ ] Remover identificadores pessoais ou dados confidenciais não autorizados.
- [ ] Explicar métricas, denominadores e comparação usada.
- [ ] Não converter observação ou correlação em prova de causalidade.
- [ ] Permitir que outra pessoa confira pelo menos uma conclusão pelos dados.

## Perguntas para entrevista ou reunião

Qual decisão técnica foi mais importante? Qual alternativa foi descartada e por
quê? Que evidência suporta a conclusão? O que mudaria com uma fonte de maior
precisão? Responda com fatos do projeto, evitando atribuir ganhos não medidos.
