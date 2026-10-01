# Classificação de imagens de satélite

**DataGeo Academy — material técnico | edição 1.0 | 2026-10-01**

Aplique uma sequência de classificação e avalie os resultados obtidos.

## Desafio: Classificação sintética

Os dados e resultados de referência são sintéticos para treinamento. O objetivo é
verificar operações e raciocínio, não representar uma área ou fenômeno real.

## Dados de entrada

```text
Atributos de treino: (0,0)->0; (0,1)->0; (1,0)->1; (1,1)->1. Matriz de avaliação independente didática: [[8,2],[1,9]].
```

## Procedimento

1. Separe atributos e classe.
2. Treine um classificador com os quatro exemplos para entender a API.
3. Explique por que o conjunto pequeno não valida uso real.
4. Calcule métricas usando a matriz independente fornecida.
5. Discuta classes e amostragem necessárias numa cena real.

## Apoio técnico

```text
from sklearn.tree import DecisionTreeClassifier
modelo=DecisionTreeClassifier(random_state=42).fit([[0,0],[0,1],[1,0],[1,1]],[0,0,1,1])
print(modelo.predict([[1,.5]]))  # [1]
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

Acurácia=0,85. Precisão da classe 1=9/11; revocação da classe 1=9/10. O treino minúsculo não constitui avaliação independente.

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
