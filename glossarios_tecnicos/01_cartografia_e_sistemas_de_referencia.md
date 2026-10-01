# Cartografia e sistemas de referência

**DataGeo Academy — material técnico | edição 1.0 | 2026-10-01**

Organize o vocabulário de mapas e coordenadas usado em projetos territoriais.

## Como consultar

Este glossário reúne doze conceitos e seus cuidados operacionais. As definições
são referências introdutórias para leitura e comunicação; consulte a documentação
da ferramenta e a metodologia do projeto para uma implementação específica.

## Conceitos e aplicação

### Datum

Referência geodésica que estabelece como coordenadas se relacionam à Terra; não é sinônimo de projeção.

### CRS/SRC

Sistema que combina referência e eixos/unidades; registre a definição completa e não apenas um nome informal.

### SIRGAS2000

Referencial adotado oficialmente no Brasil; sua realização e época devem ser consideradas em trabalhos de precisão.

### EPSG:4674

SIRGAS2000 em coordenadas geográficas; longitude e latitude são angulares, não distâncias em metros.

### Projeção

Transformação da superfície para um plano, com distorções que devem ser adequadas ao objetivo.

### UTM

Família de projeções por fusos; exige fuso e hemisfério compatíveis com a região.

### Atribuir CRS

Rotular a interpretação das coordenadas existentes; não altera seus números.

### Reprojetar

Calcular coordenadas em outro CRS mediante operação definida; difere de trocar metadados.

### Escala

Relação entre representação e terreno; ampliar visualização não aumenta a precisão da fonte.

### Época

Instante ao qual coordenadas ou realização se referem, relevante para movimentos e alta precisão.

### Altitude elipsoidal

Distância referida ao elipsoide, diferente de altitudes físicas associadas ao campo de gravidade.

### Precisão

Dispersão ou qualidade especificada de medida; não equivale automaticamente à exatidão em relação à referência.

## Uso em uma análise

Escolha três termos relevantes ao projeto. Escreva onde cada um aparece no seu
fluxo de trabalho, qual entrada depende dele e qual erro de interpretação pode
alterar o resultado. Acrescente uma evidência: propriedade de camada, consulta,
parâmetro, cálculo ou saída de validação.

## Revisão rápida

- Diferencie unidade, valor medido e indicador derivado.
- Informe fonte, período e pressuposto antes de comparar resultados.
- Não interprete coincidência, associação ou aparência como prova de causalidade.
- Registre versões e critérios: nomes semelhantes podem ter implementações diferentes.
- Explique termos ao destinatário sem retirar as limitações relevantes.

## Autoavaliação

1. Qual par de conceitos deste glossário é frequentemente confundido?
2. Que erro prático essa confusão pode causar no seu projeto?
3. Qual registro permitiria a um revisor detectar o problema?

Responda com um exemplo pequeno e verificável. A consulta do glossário não
substitui a validação das operações nem confirma qualidade dos dados de origem.

Referências para aprofundamento: https://docs.qgis.org/3.44/en/docs/user_manual/ ;
https://postgis.net/docs/ ; https://scikit-learn.org/stable/user_guide.html ;
https://www.ibge.gov.br/geociencias/informacoes-sobre-posicionamento-geodesico/sirgas.html
