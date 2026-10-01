# Mapa temático de indicadores

**DataGeo Academy — material técnico | edição 1.0 | 2026-10-01**

Construa uma composição que comunica diferenças territoriais com clareza.

## Desafio: Mapa de indicadores

Os dados e resultados de referência são sintéticos para treinamento. O objetivo é
verificar operações e raciocínio, não representar uma área ou fenômeno real.

## Dados de entrada

```text
Tabela: setor A, população 2000, serviços 2; setor B, população 4000, serviços 2; setor C, população 0, serviços 1.
```

## Procedimento

1. Relacione a tabela por código estável.
2. Calcule serviços por 1.000 habitantes.
3. Represente valores com legenda e unidade.
4. Trate o setor C como sem taxa calculável.
5. Revise dados fonte e denominador.

## Apoio técnico

```text
CASE WHEN "populacao">0 THEN 1000.0*"servicos"/"populacao" ELSE NULL END
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

A=1,0; B=0,5; C=NULL. Não registrar infinito nem zero para a taxa de C.

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
