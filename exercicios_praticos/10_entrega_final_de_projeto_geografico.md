# Entrega final de projeto geográfico

**DataGeo Academy — material técnico | edição 1.0 | 2026-10-01**

Integre análise, documentação e revisão em uma entrega de portfólio.

## Desafio: Entrega integrada

Os dados e resultados de referência são sintéticos para treinamento. O objetivo é
verificar operações e raciocínio, não representar uma área ou fenômeno real.

## Dados de entrada

```text
Use os dados sintéticos de bancos_dados e escolha uma pergunta territorial com unidade e critério de qualidade.
```

## Procedimento

1. Inventarie fontes e declare que são sintéticas.
2. Produza uma análise com operações documentadas.
3. Gere mapa, tabela e relatório.
4. Reabra dados exportados e repita verificações.
5. Apresente conclusões proporcionais à demonstração.

## Apoio técnico

```text
Manifesto: caminho, tipo, versão, data, responsável, CRS, contagem e checksum opcional.
```

As expressões são orientações específicas da ferramenta indicada. Em arquivos de
texto, blocos de código não são executados automaticamente. Registre software e
versão e adapte nomes de campos à estrutura criada.

## Entrega exigida

1. Uma tabela ou camada de entrada identificada, com unidade e CRS quando aplicável.
2. Registro das etapas, parâmetros e decisões de tratamento de erros.
3. Tabela de resultado e pelo menos uma evidência verificável.
4. Resposta que explique o significado do resultado e as limitações.
5. Revisão de contagem, valores ausentes e consistência dos vínculos.

## Gabarito comentado

Entrega mínima: GeoPackage verificável, mapa com referências, tabela de resultados, relatório de método e limitações, manifesto e checklist.

## Testes adicionais

- Execute com uma entrada vazia ou sem correspondência e descreva o comportamento.
- Verifique o efeito de valores ausentes e de registros duplicados.
- Em operações geométricas, compare unidades e método de medição.
- Se usar amostras para modelo, separe treino e avaliação antes do ajuste.
- Reabra a saída exportada para conferir que preserva valores e metadados.

## Critérios de revisão

O resultado precisa coincidir com a referência quando há valor determinístico.
Aceite diferenças de arredondamento justificadas, mantendo o cálculo original.
Registre divergências de predicados e aproximações geométricas quando o software
emprega modelos distintos. Um mapa visualmente plausível não substitui a conferência.

## Extensão do desafio

Altere uma hipótese ou um parâmetro e explique o impacto. Escolha um caso em que
o método deixa de ser adequado; proponha uma alternativa e o teste necessário
para compará-la. Anexe a resposta ao seu portfólio como exercício demonstrativo.
