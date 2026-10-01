# Revisão de topologia e SIRGAS2000

**DataGeo Academy — material técnico | edição 1.0 | 2026-10-01**

Pratique a identificação de inconsistências sem alterar dados por suposição.

## Desafio: Consistência topológica

Os dados e resultados de referência são sintéticos para treinamento. O objetivo é
verificar operações e raciocínio, não representar uma área ou fenômeno real.

## Dados de entrada

```text
Dois quadrados em CRS métrico: A=(0,0)-(1000,1000), B=(900,0)-(1900,1000). Os números são locais para cálculo didático, não localização real.
```

## Procedimento

1. Crie os dois polígonos e declare um CRS métrico apenas para o ensaio.
2. Verifique validade geométrica e sobreposição.
3. Calcule áreas individuais, interseção e união.
4. Proponha uma correção somente após definir a regra da cobertura.
5. Documente atribuir CRS versus reprojetar em dados reais.

## Apoio técnico

```text
ST_Area(ST_Intersection(a.geom,b.geom))/10000.0; no QGIS use interseção seguida de área plana.
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

Cada polígono tem 100 ha; sobreposição=10 ha; união=190 ha. Ambos podem ser geometricamente válidos apesar da sobreposição.

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
