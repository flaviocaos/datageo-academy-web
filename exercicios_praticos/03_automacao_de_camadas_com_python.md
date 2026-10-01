# Automação de camadas com Python

**DataGeo Academy — material técnico | edição 1.0 | 2026-10-01**

Planeje e implemente uma rotina que organiza entradas e saídas geográficas.

## Desafio: Automação com Python

Os dados e resultados de referência são sintéticos para treinamento. O objetivo é
verificar operações e raciocínio, não representar uma área ou fenômeno real.

## Dados de entrada

```text
CSV: id,classe,valor
1,A,10
2,B,20
3,A,30
4,B,40
```

## Procedimento

1. Leia o CSV sem perder IDs.
2. Selecione classe A.
3. Exporte resultado para arquivo novo.
4. Registre contagem inicial e final.
5. Teste uma classe ausente e uma coluna obrigatória ausente.

## Apoio técnico

```text
import pandas as pd
df=pd.read_csv('entrada.csv')
saida=df.loc[df['classe'].eq('A')].copy()
saida.to_csv('resultado.csv',index=False)
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

Entrada=4 linhas; filtro A=2 linhas; soma de valor=40. Classe ausente deve produzir tabela vazia com esquema mantido.

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
