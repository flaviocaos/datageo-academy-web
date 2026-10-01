# Interpolação de variáveis ambientais

**DataGeo Academy — material técnico | edição 1.0 | 2026-10-01**

Experimente superfícies e avalie o efeito das escolhas do método.

## Desafio: Interpolação IDW

Os dados e resultados de referência são sintéticos para treinamento. O objetivo é
verificar operações e raciocínio, não representar uma área ou fenômeno real.

## Dados de entrada

```text
Amostras: (0,0)=10, (1000,0)=20. Destino=(500,0); potência=2.
```

## Procedimento

1. Calcule distâncias e pesos.
2. Normalize os pesos.
3. Estime o ponto central.
4. Teste coincidência exata com uma amostra.
5. Discuta ausência de extrapolação confiável com apenas duas amostras.

## Apoio técnico

```text
peso_i=1/(distancia_i**potencia)
estimativa=sum(peso_i*valor_i)/sum(peso_i)
Distância zero exige tratamento específico.
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

No centro, pesos iguais e estimativa=15. Na coordenada (0,0), retorne 10 diretamente para evitar divisão por zero.

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
