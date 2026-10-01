# Previsão temporal de indicadores

**DataGeo Academy — material técnico | edição 1.0 | 2026-10-01**

Treine um modelo e compare previsões com observações fora do treino.

## Desafio: Previsão temporal

Os dados e resultados de referência são sintéticos para treinamento. O objetivo é
verificar operações e raciocínio, não representar uma área ou fenômeno real.

## Dados de entrada

```text
Observado=[10,12,14]; previsto=[9,12,16]. Série de treino regular=[2,4,6,8,10].
```

## Procedimento

1. Separe treino passado e teste futuro.
2. Calcule MAE, RMSE e R² da previsão fornecida.
3. Ajuste uma tendência linear à série de treino.
4. Compare com referência do último valor.
5. Explique limites da extrapolação.

## Apoio técnico

```text
MAE=mean(abs(y-p)); RMSE=sqrt(mean((y-p)**2)); R²=1-sum((y-p)**2)/sum((y-mean(y))**2).
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

MAE=1; RMSE=sqrt(5/3)=1,290994...; R²=1-5/8=0,375. Tendência linear prevê 12 no próximo passo.

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
