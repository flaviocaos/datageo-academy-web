# Checklist de Consistência Topológica e SIRGAS 2000

**DataGeo Academy · Material prático de revisão geoespacial**

Use este guia antes de entregar uma base vetorial, publicar um mapa ou calcular indicadores espaciais. Marque os itens aplicáveis e registre evidências. Um item não aplicável deve receber justificativa; não o trate como um teste aprovado.

## 1. Identificação e critérios de qualidade

| Campo | Registro |
| --- | --- |
| Projeto / responsável / revisor | |
| Camadas, fontes e datas de aquisição | |
| Versão do QGIS e formato dos dados | |
| SRC original e SRC de entrega | |
| Escala de uso e precisão esperada | |
| Regras de topologia e exceções permitidas | |
| Tolerância de edição e unidade | |
| Data, versão e local da cópia de segurança | |

- [ ] Criar uma cópia de trabalho e preservar os dados originais.
- [ ] Definir a finalidade da base: cadastro, rede, cobertura contínua, pontos de interesse ou análise temática.
- [ ] Estabelecer critérios mensuráveis de aceitação antes de editar.
- [ ] Definir tolerâncias com base na precisão da fonte e no uso pretendido; não usar um valor universal.
- [ ] Registrar quantidade de feições, extensão espacial, esquema de atributos e identificadores iniciais.

## 2. Referência espacial e SIRGAS 2000

SIRGAS2000 é o referencial geodésico oficial brasileiro; o período de transição encerrou-se em 25 de fevereiro de 2015. A realização está associada à época 2000,4. Confirme a referência efetiva dos dados antes de transformá-los. Fontes: [IBGE — mudança de referencial](https://www.ibge.gov.br/geociencias/informacoes-sobre-posicionamento-geodesico/sirgas/16691-projeto-mudanca-do-referencial-geodesico-pmrg.html) e [IBGE — ProGriD](https://www.ibge.gov.br/geociencias/informacoes-sobre-posicionamento-geodesico/servicos-para-posicionamento-geodesico/16312-progrid.html).

- [ ] Conferir o SRC de **cada camada** nas propriedades, não apenas o SRC do projeto.
- [ ] Confirmar datum, projeção, fuso, hemisfério, unidades e ordem das coordenadas com os metadados da fonte.
- [ ] Verificar a extensão e coordenadas de amostra contra pontos ou bases confiáveis.
- [ ] Conferir arquivos de referência e metadados: `.prj` no Shapefile ou definição de SRC no GeoPackage.
- [ ] Investigar camadas sem SRC; não atribuir SIRGAS2000 por suposição.
- [ ] Distinguir **atribuir SRC** (interpretar números existentes) de **reprojetar** (transformar coordenadas).
- [ ] Usar atribuição apenas quando o SRC verdadeiro é conhecido e foi rotulado incorretamente ou omitido.
- [ ] Confirmar a operação de transformação ao converter uma base antiga; registrar parâmetros, grades e precisão declarada.
- [ ] Verificar se as grades de transformação necessárias estão instaladas; registrar qualquer operação alternativa de menor precisão.
- [ ] Não presumir equivalência exata entre WGS 84 e SIRGAS2000 em trabalhos de alta precisão; conferir realização, época e procedimento adequado.
- [ ] Para dados GNSS de precisão, documentar época de observação e eventuais operações dependentes do tempo.

### Escolha do sistema para análise

O código **EPSG:4674** identifica coordenadas geográficas SIRGAS2000. Coordenadas geográficas usam graus. Para uma projeção UTM, selecione o fuso e hemisfério correspondentes à área; **EPSG:31983** é SIRGAS2000 / UTM 23S, e não serve como padrão para todo o Brasil. Consulte a tabela do [Perfil de Metadados do IBGE](https://www.ibge.gov.br/biblioteca/visualizacao/livros/liv101802.pdf).

- [ ] Para tolerâncias métricas e operações planas, trabalhar em uma projeção adequada à área e conferir as unidades.
- [ ] Para áreas que cruzam fusos ou extensões nacionais, avaliar projeção ou método geodésico adequado ao objetivo.
- [ ] Documentar se áreas e distâncias são calculadas em plano projetado ou com método elipsoidal.
- [ ] Separar referência horizontal da vertical: SIRGAS2000 horizontal não define sozinho o tipo de altitude.
- [ ] Em dados 3D, identificar altitude elipsoidal ou altitude física, modelo utilizado, unidade e referência vertical.

## 3. Integridade de geometrias

No QGIS, use as ferramentas de verificação de validade e, quando disponíveis, Geometry Checker e Topology Checker. Uma geometria válida não garante que as relações entre feições estejam corretas. Consulte o [Geometry Checker do QGIS](https://doc.qgis.org/3.44/en/docs/user_manual/plugins/core_plugins/plugins_geometry_checker.html).

- [ ] Remover filtros de exibição ou registrar seu efeito antes de validar a base inteira.
- [ ] Garantir que a ferramenta processe todas as feições, e não apenas a seleção ativa.
- [ ] Executar a verificação de validade e salvar as saídas de erros.
- [ ] Identificar geometrias nulas, vazias, degeneradas ou incompatíveis com o tipo declarado.
- [ ] Revisar autointerseções, anéis inválidos e componentes colapsados.
- [ ] Conferir uso de multipartes conforme a modelagem; multiparte não é erro por definição.
- [ ] Identificar feições duplicadas; distinguir duplicação geométrica de coincidências legítimas.
- [ ] Conferir coordenadas Z/M quando necessárias e seu tratamento nas ferramentas usadas.

## 4. Regras para polígonos

Aplique regras de acordo com o modelo da base. Sobreposições e lacunas só são erros quando contrariem os requisitos: uma cobertura contínua difere de um inventário de áreas isoladas. Referência: [Topology Checker do QGIS](https://docs.qgis.org/3.44/en/docs/user_manual/plugins/core_plugins/plugins_topology_checker.html).

- [ ] Verificar sobreposições dentro de coberturas que devem ser mutuamente exclusivas.
- [ ] Verificar lacunas internas onde a cobertura deve ser contínua.
- [ ] Distinguir lacunas de áreas externas à cobertura e de vazios permitidos, como lagos ou exclusões.
- [ ] Conferir encaixe e coincidência de limites compartilhados.
- [ ] Examinar fragmentos estreitos e polígonos residuais; comparar com a escala e a realidade representada.
- [ ] Verificar se parcelas, setores ou classes estão dentro do limite de referência quando exigido.
- [ ] Para partições, comparar a união das feições com a área esperada, considerando exceções documentadas.
- [ ] Revisar áreas antes e depois das correções; investigar alterações além da tolerância acordada.

## 5. Regras para linhas e redes

- [ ] Conferir continuidade entre trechos que devem estar conectados.
- [ ] Revisar pontas soltas; registrar extremidades legítimas da rede.
- [ ] Procurar trechos curtos que não alcançam a conexão esperada e prolongamentos indevidos.
- [ ] Verificar cruzamentos que precisam de nós compartilhados.
- [ ] Distinguir cruzamentos reais de passagens em níveis diferentes, como pontes e túneis.
- [ ] Identificar duplicações, sobreposições e autointerseções contrárias ao modelo.
- [ ] Conferir direção, atributos de fluxo e conectividade quando houver análise de rede.
- [ ] Documentar tolerância de ajuste de vértices e conferir se ela não conecta elementos indevidamente.

## 6. Pontos e relações entre camadas

- [ ] Investigar pontos coincidentes; ocorrências múltiplas no mesmo local podem ser legítimas.
- [ ] Verificar se pontos estão dentro de polígonos ou sobre linhas conforme a regra de negócio.
- [ ] Conferir pontos fora do limite de estudo e deslocamentos sistemáticos.
- [ ] Definir o tratamento de pontos exatamente na borda: contido, coberto ou associado por tolerância.
- [ ] Validar relacionamentos entre camadas usando identificadores estáveis, não posição das linhas na tabela.
- [ ] Conferir vínculos entre rede, equipamentos e áreas atendidas quando aplicáveis.

## 7. Atributos e consistência temática

- [ ] Garantir identificadores obrigatórios, únicos e persistentes.
- [ ] Conferir valores nulos, domínios, tipos de campo, datas e unidades.
- [ ] Identificar registros sem correspondência em relacionamentos obrigatórios.
- [ ] Conferir nomes, classes e códigos com o dicionário de dados.
- [ ] Revisar áreas e comprimentos armazenados após mudanças geométricas.
- [ ] Preservar códigos com zeros à esquerda e caracteres acentuados na exportação.
- [ ] Verificar compatibilidade entre atributos e geometria com uma amostra representativa.

## 8. Correção controlada no QGIS

- [ ] Registrar erro, ID da feição, regra, localização e evidência antes de corrigir.
- [ ] Corrigir em cópia de trabalho; revisar resultados de ferramentas automáticas.
- [ ] Configurar ajuste de vértices (snapping) em unidades apropriadas e habilitar edição topológica quando fizer sentido.
- [ ] Aplicar ferramentas de reparo sem assumir que elas preservam quantidade, tipos e limites das feições.
- [ ] Comparar geometrias e atributos antes e depois; registrar divisões, fusões e exclusões.
- [ ] Evitar ajustes globais que movam limites legítimos ou apaguem detalhes importantes.
- [ ] Executar novamente validade, regras topológicas e controle de atributos após a correção.

## 9. Evidências, entrega e aceite

| Regra | Feições testadas | Erros iniciais | Corrigidos | Exceções justificadas | Erros restantes | Evidência |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| SRC e transformação | | | | | | |
| Validade geométrica | | | | | | |
| Sobreposições / lacunas | | | | | | |
| Conectividade / relações | | | | | | |
| Atributos | | | | | | |

- [ ] Reabrir os arquivos exportados e conferir SRC, geometria, atributos, extensão e quantidade de feições.
- [ ] Para Shapefile, entregar o conjunto de arquivos necessário, incluindo `.shp`, `.shx`, `.dbf` e `.prj`, com informações de codificação quando aplicáveis.
- [ ] Para GeoPackage, verificar nomes de camadas e integridade dos relacionamentos.
- [ ] Anexar metadados, critérios de tolerância, operações de transformação e relatório de exceções.
- [ ] Registrar aprovação do revisor e bloquear a versão final contra alterações não rastreadas.

**Aceite:** nenhum erro impeditivo aberto; tolerâncias atendidas; exceções justificadas e aprovadas; rastreabilidade da fonte, do SRC e das correções preservada.

## Referências e manutenção

As referências oficiais estão vinculadas nas seções correspondentes. Os nomes de ferramentas podem variar por versão e idioma do QGIS. Registre a versão utilizada e adapte as regras às exigências do projeto.

Revisão deste guia: **01/10/2026**.
