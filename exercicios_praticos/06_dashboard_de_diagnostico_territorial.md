# Dashboard de diagnóstico territorial

**DataGeo Academy — material técnico | edição 1.0 | 2026-10-01**

Produza indicadores e uma leitura executiva para um problema definido.

## Desafio: Dashboard

Os dados e resultados de referência são sintéticos para treinamento. O objetivo é
verificar operações e raciocínio, não representar uma área ou fenômeno real.

## Dados de entrada

```text
Fatos: A/2025=10, B/2025=20, A/2026=15, B/2026=25. Dimensão de setores com uma linha por código.
```

## Procedimento

1. Modele relação entre dimensão e fatos.
2. Crie total por ano e variação por setor.
3. Aplique filtros de ano e setor.
4. Verifique se relações duplicam linhas.
5. Escreva um resumo sem somar anos como se fossem o mesmo instante.

## Apoio técnico

```text
Variação percentual=100*(valor_atual-valor_anterior)/valor_anterior, para denominador diferente de zero.
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

Total 2025=30; total 2026=40; variação total=33,333...%. Setor A=50%; B=25%.

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
