# Consulta espacial no PostGIS

**DataGeo Academy — material técnico | edição 1.0 | 2026-10-01**

Investigue relações entre camadas usando consultas verificáveis.

## Desafio: Consulta espacial

Os dados e resultados de referência são sintéticos para treinamento. O objetivo é
verificar operações e raciocínio, não representar uma área ou fenômeno real.

## Dados de entrada

```text
Dois polígonos adjacentes: A=(0,0)-(100,100), B=(100,0)-(200,100); pontos P1=(25,25), P2=(150,50), P3=(100,50).
```

## Procedimento

1. Crie geometrias no mesmo CRS.
2. Compare ST_Within e ST_Covers.
3. Relacione pontos a polígonos.
4. Identifique ambiguidade na borda.
5. Defina regra de associação para não duplicar contagem.

## Apoio técnico

```text
SELECT p.id,u.id FROM pontos p JOIN unidades u ON ST_Covers(u.geom,p.geom);
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

P1 está dentro de A; P2 dentro de B; P3 está na borda de ambos: Within é falso e Covers é verdadeiro para os dois.

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
