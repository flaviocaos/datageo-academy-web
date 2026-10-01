# Análise de proximidade e cobertura

**DataGeo Academy — material técnico | edição 1.0 | 2026-10-01**

Compare alternativas de atendimento com critérios espaciais explícitos.

## Desafio: Proximidade

Os dados e resultados de referência são sintéticos para treinamento. O objetivo é
verificar operações e raciocínio, não representar uma área ou fenômeno real.

## Dados de entrada

```text
Dois pontos em metros: P=(0,0), Q=(300,400); raio de cobertura=500 m.
```

## Procedimento

1. Calcule distância euclidiana.
2. Construa buffer circular em CRS métrico.
3. Compare predicados estrito e inclusivo.
4. Repita com ponto a 501 m.
5. Explique diferença entre proximidade em linha reta e rede.

## Apoio técnico

```text
distancia=((x2-x1)**2+(y2-y1)**2)**0.5
Em PostGIS, ST_DWithin(geom_p,geom_q,500) usa distância inclusiva em unidades do CRS.
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

Distância P-Q=500 m. Em cálculo analítico Q está no limite; aproximação poligonal do buffer pode alterar relação. Use distância<=500 para o teste inclusivo.

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
