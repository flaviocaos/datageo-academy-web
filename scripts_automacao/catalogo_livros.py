"""Catálogo editorial: seis áreas, cinco obras por área, 28 documentos novos.
Cada tema tem contexto, procedimento e estudo de aplicação próprios.
"""
AREAS = ['IA e Machine Learning','Geotecnologias','BI - Business Intelligence',
         'Ciência de Dados','Programação para Dados','Análise Preditiva']

# título, descrição / contexto, caso de estudo, etapas técnicas progressivas.
CATALOGO = [
 [
  ('Inteligência Artificial Aplicada','Conceitos e aplicações de inteligência artificial na análise territorial.',None,[]),
  ('Machine Learning Geoespacial','Aprendizagem supervisionada e não supervisionada aplicada a observações que possuem localização. A proximidade entre amostras exige planejamento de validação e atenção à dependência espacial.',
   'Classificar áreas com maior propensão a expansão urbana a partir de cobertura do solo, distâncias a vias e indicadores demográficos.',[
   ('Problema, alvo e unidade espacial','Defina se a resposta representa classe, valor contínuo ou agrupamento. Uma célula de grade, lote ou município exige atributos e interpretação diferentes. Registre o período de validade do alvo e exclua variáveis que só seriam conhecidas depois do evento.'),
   ('Construção de atributos geográficos','Harmonize CRS, período e escala. Calcule distâncias em unidade adequada; agregue indicadores sem duplicar observações em joins. Separe ausência real, valor zero e informação indisponível.'),
   ('Treinamento e baseline','Compare um modelo simples com árvores ou ensembles. Ajuste transformações somente no treino e preserve identificadores para auditoria. Use Pipeline para aplicar o mesmo procedimento aos conjuntos de avaliação.'),
   ('Validação espacial e interpretação','Separe regiões ou blocos no treino e teste. Informe métricas por bloco, matriz de confusão e desempenho por classe. Importância de atributos não demonstra causalidade e pode ser instável com variáveis correlacionadas.'),
   ('Aplicação e monitoramento','Gere o mapa de predição com máscara para locais sem suporte de dados. Registre versão do modelo, CRS, fontes e domínio de aplicação. Compare novos períodos com o treinamento para detectar mudança de distribuição.')]),
  ('Deep Learning para Sensoriamento Remoto','Redes profundas aprendem representações de imagens e séries multiespectrais. Resolução, alinhamento de bandas, rótulos e partição de cenas determinam a utilidade do resultado.',
   'Segmentar áreas construídas em recortes de imagens multiespectrais e avaliar regiões não vistas no treinamento.',[
   ('Imagens, bandas e rótulos','Confira resolução, aquisição, nodata e qualidade radiométrica. Rótulos precisam representar o mesmo período da imagem. Preserve metadados e critérios de anotação em um inventário.'),
   ('Recortes e organização do dataset','Divida cenas em patches preservando localização. Separe treino e teste por cena ou região antes de criar patches; recortes vizinhos não devem atravessar a separação. Evite sobreposição de pixels entre grupos.'),
   ('Arquitetura e treinamento','Diferencie classificação de cena e segmentação por pixel. Documente normalização por banda, função de perda, pesos de classe e sementes. Aumento de dados deve manter a coerência do problema geográfico.'),
   ('Métricas e análise de erros','Calcule precisão, revocação e IoU por classe com uma matriz de confusão. Inspecione bordas, objetos pequenos e regiões com nuvens. Métricas globais podem esconder ausência de detecção em classes raras.'),
   ('Inferência e mosaico','Faça inferência em blocos com sobreposição quando necessário, combinando bordas sem costuras artificiais. Grave o raster final com CRS, transformação afim e nodata corretos. Revise os polígonos derivados antes da entrega.')]),
  ('IA Explicável para Análises Geográficas','Explicações ajudam a examinar decisões de modelos territoriais, mas não substituem validação. O contexto espacial e a correlação entre atributos alteram a leitura de importância e efeitos.',
   'Auditar um modelo de risco de inundação, comparando explicações locais entre bacias com diferentes características.',[
   ('Pergunta de auditoria','Especifique quem precisa entender a previsão e para qual decisão. Distingua explicação global, individual e análise de sensibilidade. Selecione regiões e casos de erro para a revisão.'),
   ('Dependência entre variáveis','Identifique correlações entre declividade, altitude, distância à drenagem e uso do solo. Uma variável pode compartilhar informação com outra; redução de importância isolada não significa irrelevância do grupo.'),
   ('Métodos de explicação','Compare importância por permutação em dados de teste com gráficos de efeito. Registre limitações de perturbar combinações pouco plausíveis. SHAP depende do modelo, do conjunto de referência e das hipóteses adotadas.'),
   ('Explicações no território','Mapeie resíduos e explicações junto ao suporte amostral. Compare blocos espaciais e classes, sem interpretar padrões apenas pela estética do mapa. Documente diferenças entre casos corretos e incorretos.'),
   ('Relatório de transparência','Descreva fonte, uso pretendido, métrica, limitações e condições de aplicação. Evite afirmar causalidade a partir de explicações preditivas. Apresente exemplos verificáveis e revisões de especialistas.')]),
  ('IA Generativa na Inteligência Territorial','Modelos generativos podem apoiar redação, recuperação de documentos e elaboração de código. Respostas precisam de rastreabilidade, validação e controle das fontes antes de orientar decisões territoriais.',
   'Construir um assistente que responde a perguntas sobre um conjunto autorizado de relatórios técnicos e referencia os trechos consultados.',[
   ('Escopo e corpus autorizado','Inventarie documentos, versões e permissões. Separe dados públicos, restritos e pessoais. Defina perguntas atendidas pelo corpus e a conduta quando a resposta não estiver documentada.'),
   ('Recuperação de evidências','Segmente documentos preservando título, página e contexto. Compare busca lexical e semântica; avalie recuperação antes da geração. Textos recuperados devem ser tratados como dados, não instruções confiáveis.'),
   ('Geração com referências','Solicite resposta sustentada pelos trechos recuperados e links rastreáveis. Verifique se cada referência suporta a afirmação associada. Uma citação presente não comprova automaticamente que o conteúdo está correto.'),
   ('Avaliação e revisão humana','Monte perguntas com respostas documentadas e casos sem resposta. Meça acerto, fidelidade às fontes e abstinência adequada. Revise código gerado em ambiente isolado antes de executá-lo.'),
   ('Operação e versionamento','Registre modelo, prompt, corpus e resultado de avaliação. Evite enviar credenciais ou dados restritos a serviços sem autorização. Planeje atualização das fontes e canal para correção de respostas.')]),
 ],
 [
  ('Cartografia Básica Aplicada às Geotecnologias','Fundamentos de mapas, escalas, coordenadas e projeções cartográficas.',None,[]),
  ('Sistemas de Informação Geográfica na Prática','SIG integra dados, referência espacial, análise e comunicação cartográfica. O projeto precisa preservar origem, unidades e critérios de processamento para que seus resultados sejam reproduzíveis.',
   'Organizar um projeto municipal com escolas, vias e setores censitários para analisar cobertura de atendimento.',[
   ('Inventário e referência espacial','Liste fontes, datas, licenças, geometria e CRS. A reprojeção visual do projeto não altera as coordenadas gravadas nos arquivos. Valide a referência de cada camada antes das análises.'),
   ('Organização do projeto','Use nomes claros, grupos e caminhos relativos. Diferencie dados de origem, intermediários e produtos. GeoPackage pode reunir camadas e atributos, mas ainda exige dicionário de dados e política de cópia.'),
   ('Consultas e geoprocessamento','Selecione por atributo e localização. Revise cardinalidade de joins e geometria resultante de interseções. Buffers exigem unidade adequada e não representam automaticamente tempo de viagem.'),
   ('Qualidade e cartografia','Examine duplicatas, geometrias inválidas, lacunas e sobreposições conforme a regra do tema. Escolha símbolos e classes que comuniquem a distribuição. Legenda, escala e fonte precisam ser legíveis.'),
   ('Entrega e rastreabilidade','Empacote projeto e dados permitidos; teste uma cópia em outra pasta. Registre versões, parâmetros e limitações. Diferencie cobertura estimada de atendimento efetivamente observado.')]),
  ('Sensoriamento Remoto Aplicado','Dados orbitais permitem observar mudanças no território em diferentes escalas. A escolha de sensor, produto e processamento precisa corresponder ao fenômeno, ao período e ao nível de detalhe pretendido.',
   'Comparar cobertura vegetal em duas datas usando imagens de reflectância de superfície e máscaras de qualidade.',[
   ('Sensor e produto','Compare resolução espacial, espectral, temporal e radiométrica. Verifique se o produto representa reflectância ou números digitais. Identifique cobertura de nuvens e nível de processamento.'),
   ('Preparação das imagens','Aplique máscaras de qualidade e alinhe bandas na mesma grade. Reamostragem não cria detalhe novo; escolha o método conforme dado contínuo ou categórico. Registre nodata e transformação espacial.'),
   ('Índices e interpretação','NDVI usa (NIR-vermelho)/(NIR+vermelho), tratando denominador zero e pixels inválidos. O índice é sensível ao contexto e não mede sozinho biomassa ou biodiversidade. Compare distribuições antes de escolher limiares.'),
   ('Classificação e acurácia','Separe amostras de treinamento e validação independentes. Analise matriz de confusão, erros de omissão e comissão. Documente origem dos rótulos e diferenças de escala entre referência e imagem.'),
   ('Mudança e entrega','Mantenha grades e classes comparáveis entre datas. Diferencie mudança territorial de variação sazonal ou falha de observação. Entregue rasters, mapas, tabela de áreas e método de avaliação.')]),
  ('Drones e Fotogrametria para Mapeamento','Produtos fotogramétricos dependem de planejamento, orientação das imagens e validação externa. Um ortomosaico visualmente contínuo pode ainda apresentar erros de posição ou deformação.',
   'Planejar um levantamento didático e revisar ortomosaico, modelo de superfície e pontos independentes de checagem.',[
   ('Objetivo e planejamento','Defina produto, resolução desejada, área, restrições operacionais e referência espacial. Planeje sobreposição e distribuição de controle segundo o projeto. Consulte regras de voo aplicáveis antes de operações reais.'),
   ('Controle e aquisição','Diferencie pontos de controle e pontos de checagem. Registre método, precisão e datum das coordenadas. Confirme exposição, foco e consistência das imagens; controle mal distribuído pode mascarar deformações.'),
   ('Processamento fotogramétrico','Revise alinhamento, calibração, nuvem de pontos e filtragem. Modelo digital de superfície inclui vegetação e edificações; modelo de terreno precisa de classificação e verificação adicional.'),
   ('Validação independente','Calcule resíduos em pontos não usados no ajuste e descreva distribuição e amostra. RMSE depende dos dados e não é certificação automática de exatidão. Inspecione bordas, sombras e áreas com pouca textura.'),
   ('Ortomosaico e documentação','Entregue CRS, resolução, nodata, controle utilizado e relatório de processamento. Diferencie coordenadas geodésicas e projetadas, alturas elipsoidais e altitudes referidas a um modelo vertical apropriado.')]),
  ('Bancos de Dados Geográficos','Modelos espaciais relacionam geometria, atributos e regras de integridade. Índices e referência espacial precisam ser planejados junto às consultas e ao ciclo de atualização dos dados.',
   'Estruturar pontos de equipamentos públicos no PostGIS com chaves, índices e consultas de proximidade.',[
   ('Modelo lógico e dicionário','Defina entidades, chaves e cardinalidade. Geometria não substitui identificador de negócio. Documente domínio, nulidade, unidade, origem e periodicidade de atualização dos atributos.'),
   ('Geometria e referência','Escolha tipo e SRID explícitos. ST_SetSRID atribui referência; ST_Transform converte valores. Geography e geometry têm comportamento e unidades distintos. Valide extensão e ordem de coordenadas.'),
   ('Integridade e carga','Use transações, restrições e staging para revisar a importação. Separe geometrias vazias, inválidas e ausentes. Não corrija um erro geométrico sem verificar se o resultado ainda representa o objeto original.'),
   ('Índices e consultas','Crie GiST conforme as consultas e examine EXPLAIN. ST_DWithin pode acelerar buscas por raio com índice compatível. Evite funções sobre a coluna indexada quando elas impedirem o plano pretendido.'),
   ('Operação e recuperação','Separe roles de carga e leitura, registre alterações e teste backups em banco novo. Índices melhoram acesso, mas não garantem qualidade temática ou disponibilidade. Planeje migração e retenção.')]),
 ],
 [
  ('BI Geográfico para Decisões Estratégicas','Business Intelligence geográfico conecta indicadores à localização e ao contexto da decisão. A interpretação depende de denominadores, escala, período e consistência das dimensões territoriais.',
   'Comparar cobertura de serviços por município sem confundir totais absolutos com taxas populacionais.',[
   ('Pergunta e decisão','Defina quem usa o indicador, com que frequência e para qual ação. Diferencie diagnóstico, acompanhamento e previsão. Cada medida deve ter fórmula, unidade, fonte e responsável.'),
   ('Dados e dimensões','Harmonize códigos territoriais e versões de limites. Use chaves estáveis para conectar fatos e dimensões. Registre o nível de detalhe e evite multiplicar fatos ao unir tabelas com granularidades distintas.'),
   ('Indicadores comparáveis','Calcule taxas com denominador pertinente ao mesmo período. Agregações precisam respeitar o significado da medida: médias de taxas sem peso podem induzir erro. Diferencie ausência de dado e valor zero.'),
   ('Visualização e filtros','Combine mapa, série e tabela para permitir conferência. Use classes e escalas consistentes; documente efeitos de filtros. Tamanho territorial não deve dominar leitura de indicadores populacionais.'),
   ('Governança e uso','Teste medidas contra fonte independente e registre atualização. Mostre limitações e datas de referência. Defina responsável por alertas, correções e interpretação antes de automatizar decisões.')]),
  ('Power BI para Indicadores Territoriais','Um modelo semântico territorial organiza fatos, datas e locais para produzir medidas verificáveis. Relacionamentos e contexto de filtro são centrais para a leitura correta do dashboard.',
   'Criar medidas de atendimento por município e mês, comparando demanda e capacidade instalada.',[
   ('Preparação no Power Query','Uniformize tipos, códigos e datas antes do carregamento. Identificadores com zeros à esquerda devem permanecer texto. Registre tratamentos de nulos e mantenha trilha de transformação.'),
   ('Modelo estrela','Separe fatos de atendimento, dimensão município e calendário. Revise cardinalidade e direção de filtros. Uma dimensão territorial deve ter chave única; atributos repetidos no fato aumentam inconsistência.'),
   ('Medidas e contexto','Diferencie coluna calculada e medida. DIVIDE trata denominador nulo conforme a regra definida; CALCULATE altera contexto. Teste totais e filtros com casos pequenos conhecidos.'),
   ('Mapas e comunicação','Associe códigos, coordenadas ou geometrias corretos e confira localidades ambíguas. Configure títulos que explicitem período e unidade. Considere disponibilidade, requisitos e privacidade do visual de mapas utilizado.'),
   ('Publicação e atualização','Valide credenciais, gateway quando necessário e política de atualização. Controle acesso por perfil e confirme medidas após refresh. Registre versão e responsável pelo conjunto de dados.')]),
  ('Dashboards Estratégicos Geoespaciais','Dashboards devem reduzir esforço de decisão com métricas rastreáveis, hierarquia visual e interação previsível. A presença de um mapa não basta para tornar uma análise territorialmente correta.',
   'Desenhar um painel de manutenção urbana com chamados, tempo de atendimento e distribuição por distrito.',[
   ('Usuários e tarefas','Mapeie decisões recorrentes e perguntas prioritárias. Defina a leitura inicial e a sequência de aprofundamento. Evite incluir gráficos sem ação ou interpretação associada.'),
   ('Indicadores e contratos','Especifique numerador, denominador, frequência e tratamento de atrasos. Use a mesma definição em cards, tabelas e mapas. Dados de períodos incompletos precisam de identificação explícita.'),
   ('Hierarquia visual','Organize síntese, comparação e detalhe. Escolha cor acessível e escala consistente. Diferencie alertas operacionais de categorias; não dependa apenas de cor para comunicar uma condição.'),
   ('Interação e acessibilidade','Mostre filtros ativos, estado vazio e caminho de retorno. Verifique navegação por teclado e leitura em telas pequenas. Preserve contexto ao alternar mapa e tabela.'),
   ('Teste e desempenho','Compare números com consultas de origem e meça tempo de resposta. Teste filtros combinados e dados ausentes. Registre feedback dos usuários e corrija ambiguidades antes da publicação.')]),
  ('Modelagem Dimensional de Dados Geográficos','A modelagem dimensional explicita o grão do fato e o contexto territorial de cada medida. Mudanças de limites e de códigos exigem estratégias de histórico para evitar comparações falsas.',
   'Construir um esquema estrela de ocorrências mensais ligado a dimensões de tempo, categoria e território.',[
   ('Grão e evento','Escreva o que uma linha representa antes de escolher colunas. Evento individual e agregado mensal não podem compartilhar medidas sem regras claras. Preserve chaves de origem para reconciliação.'),
   ('Dimensões conformadas','Crie dimensões tempo, território e categoria com chaves únicas. Diferencie código oficial, chave técnica e nome de exibição. Compartilhe dimensões entre fatos somente quando a semântica for compatível.'),
   ('Histórico territorial','Registre vigência de limites e classificações. Mudança de município ou bairro não deve ser tratada como simples alteração de nome. Avalie dimensões lentamente mutáveis e tabelas de correspondência.'),
   ('Fatos e agregações','Defina medidas aditivas, semi-aditivas e não aditivas. População e estoque requerem tratamento por período; taxas precisam de componentes. Evite média simples de médias com amostras diferentes.'),
   ('Carga e reconciliação','Teste unicidade, integridade referencial e totais por período. Registre linhas rejeitadas e exceções. Faça carga incremental com estratégia explícita para correção tardia e reprocessamento.')]),
  ('Geointeligência para Negócios','A localização apoia análise de mercado, cobertura e logística quando combinada a dados confiáveis e objetivos mensuráveis. Resultados precisam distinguir associação, estimativa e efeito comprovado.',
   'Comparar locais candidatos a um serviço considerando demanda, concorrência e acesso por rede viária.',[
   ('Objetivo comercial','Defina a decisão, alternativas e restrições de orçamento ou atendimento. Diferencie potencial de mercado e demanda observada. Registre horizonte e critérios de sucesso.'),
   ('Dados de mercado','Confira origem, atualização e granularidade dos indicadores. Amostras de clientes podem refletir canais existentes, não toda a população. Dados pessoais exigem finalidade e tratamento adequados.'),
   ('Cobertura e acessibilidade','Compare distância euclidiana e distância ou tempo pela rede. Isócronas dependem de modo, horários e qualidade da rede. Registre hipóteses de deslocamento e áreas não atendidas.'),
   ('Comparação de cenários','Normalize critérios e justifique pesos. Faça análise de sensibilidade para verificar mudanças no ranking. Uma pontuação composta expressa hipóteses, não certeza de retorno comercial.'),
   ('Validação e acompanhamento','Compare previsão com resultados após implantação. Mantenha registros das escolhas e limitações. Atualize dados e critérios quando o mercado ou a rede mudar.')]),
 ],
 [
  ('Fundamentos de Ciência de Dados Geoespaciais','A ciência de dados espacial integra preparação, análise e avaliação considerando localização e suporte das observações. A organização dos dados deve preceder a escolha de modelos.',
   'Preparar uma base de indicadores socioambientais com coordenadas, datas e dicionário de dados.',[
   ('Pergunta e unidade de análise','Defina população, observação e variável de interesse. Diferencie ponto amostral e agregado territorial. Mudanças de suporte espacial alteram variância e interpretação.'),
   ('Tipos e referências','Padronize tipos, unidades, CRS e datas. Preserve códigos com zeros à esquerda e classifique ausências. Latitude/longitude não devem ser usadas como metros em distâncias planas.'),
   ('Preparação reproduzível','Separe origem imutável e derivados, documentando filtros e joins. Verifique cardinalidade e valores após cada transformação. Transformações para modelos devem aprender parâmetros somente no treino.'),
   ('Análise e avaliação','Combine estatísticas, mapas e distribuição dos resíduos. Examine concentração amostral e dependência espacial. Faça avaliação coerente com locais e períodos de aplicação.'),
   ('Comunicação e manutenção','Entregue código, versão dos dados, resultados e limitações. Uma conclusão deve ser proporcional ao desenho amostral. Defina critérios para atualização e correção da base.')]),
  ('Estatística Espacial Aplicada','A localização altera hipóteses de independência e interpretação estatística. Vizinhança, escala e processo amostral precisam ser conhecidos antes de avaliar padrões territoriais.',
   'Investigar agrupamentos de um indicador municipal e avaliar sensibilidade à definição de vizinhança.',[
   ('Suporte e distribuição','Examine tamanho das unidades, assimetria, zeros e denominadores. Diferenças entre municípios podem decorrer de tamanho populacional ou amostragem. Mapeie cobertura antes de inferir padrões.'),
   ('Matriz de vizinhança','Compare contiguidade, distância e k vizinhos. Registre padronização de pesos e tratamento de ilhas. Uma escolha de vizinhança representa hipótese sobre interação espacial.'),
   ('Autocorrelação global','Interprete estatísticas como Moran em relação ao indicador e aos pesos utilizados. Documente procedimento de permutação e hipótese nula. Significância não mede magnitude do efeito nem causalidade.'),
   ('Padrões locais','Analise clusters locais com atenção a múltiplos testes. Compare mapas de valor e estatística, distinguindo outlier espacial de erro de dado. Verifique estabilidade sob outra matriz de pesos.'),
   ('Relatório e limites','Apresente unidade, vizinhança, resultados e sensibilidade. Discuta agregação territorial e viés ecológico. Não transfira relações de áreas para indivíduos sem evidência apropriada.')]),
  ('Qualidade e Governança de Dados Geográficos','Qualidade geográfica envolve consistência, completude, atualidade, precisão e adequação ao uso. Correções técnicas precisam preservar o significado da informação e a rastreabilidade.',
   'Revisar uma base de parcelas com chaves, CRS, domínios, sobreposições e histórico de origem.',[
   ('Critérios de uso','Defina finalidade, tolerâncias e regras do tema. Sobreposição pode ser erro em parcelas exclusivas e ser legítima em zonas de interesse. Não aplique regras universais sem contexto.'),
   ('Inventário e dicionário','Registre fonte, data, licença, escala e responsável. Cada campo precisa de domínio, unidade e significado de nulo. Documente versões e limitações conhecidas.'),
   ('Validação geométrica','Verifique tipo, SRID, geometrias vazias e validade. Separar validação individual de topologia entre feições é essencial. Revise manualmente mudanças produzidas por reparos automáticos.'),
   ('Consistência de atributos','Teste unicidade, integridade referencial, domínios e datas. Preserve relatório de rejeições, em vez de excluir linhas sem registro. Compare totais antes e depois do processamento.'),
   ('Governança e auditoria','Defina roles, rotina de revisão e controle de mudanças. Versione regras e registros de qualidade. Uma base aprovada para uma finalidade pode ser inadequada para outra mais precisa.')]),
  ('Análise Exploratória de Dados Geoespaciais','A exploração revela distribuição, relações e problemas antes da modelagem. Mapas devem ser lidos junto a estatísticas e ao desenho de coleta para evitar interpretações enganosas.',
   'Explorar medidas ambientais e identificar áreas com pouca amostragem, valores extremos e diferenças sazonais.',[
   ('Inspeção inicial','Confira esquema, extensão, tipos, ausências e duplicatas. Examine datas e origem das medidas. Observe se amostras se concentram em áreas acessíveis ou períodos específicos.'),
   ('Distribuição univariada','Use histogramas, quantis e medidas robustas. Diferencie erro de registro e extremo plausível. Registre transformações e não descarte extremos apenas para tornar o gráfico mais uniforme.'),
   ('Relações entre variáveis','Compare dispersão e correlação com estratificação por região ou período. Relações agregadas podem diferir das locais. Correlação é descrição, não demonstração de mecanismo causal.'),
   ('Mapas e escala','Use projeção e unidades adequadas. Compare pontos originais, agregados e densidades com legenda clara. Escolha de classes e tamanho de grade afeta o padrão percebido.'),
   ('Hipóteses e próximos passos','Formule perguntas testáveis a partir da exploração e separe-as de resultados confirmatórios. Registre lacunas de coleta e hipóteses alternativas. Planeje avaliação fora das amostras usadas para explorar.')]),
  ('Engenharia de Dados Geoespaciais','Pipelines geográficos precisam preservar referência, schema e qualidade ao mover dados entre fontes e produtos. Execuções reprodutíveis dependem de contratos e estratégias de recuperação.',
   'Organizar ingestão periódica de equipamentos públicos, validação e carga incremental em banco espacial.',[
   ('Contrato de dados','Defina campos, tipos, chave, CRS, periodicidade e limites aceitáveis. Registre comportamento para fontes vazias ou indisponíveis. Uma alteração de schema precisa de detecção explícita.'),
   ('Ingestão e staging','Armazene cópia da origem com data, hash e metadados. Trate encoding, separadores e paginação. Evite sobrescrever o único arquivo de origem durante limpeza.'),
   ('Transformação e qualidade','Normalize schema e reprojete de maneira explícita. Gere métricas de rejeição e separação de registros inválidos. Execute joins com validação da cardinalidade prevista.'),
   ('Carga incremental','Use chaves e estratégia de upsert ou particionamento. Uma execução repetida não deve duplicar resultados. Planeje transação e recuperação caso o processo pare no meio.'),
   ('Observabilidade e entrega','Registre duração, volumes, erros e versões. Teste produtos com contagens e consultas de referência. Defina alertas para atrasos e mudanças na distribuição, além de falhas técnicas.')]),
 ],
 [
  ('Python para Geociências','Python permite automatizar tarefas geográficas com código verificável e reutilizável. A leitura de arquivos, referência espacial e tratamento de erros são parte do método, não detalhes acessórios.',
   'Ler uma camada de pontos, validar campos, reprojetar para CRS métrico adequado e gerar resumo por categoria.',[
   ('Ambiente e organização','Use ambiente isolado e registre versões. Separe funções, configuração e execução principal. Caminhos devem ser explícitos e portáveis; evite depender do diretório de trabalho ocultamente.'),
   ('Leitura e schema','GeoPandas organiza atributos e geometria. Confira CRS, tipo e campos antes de processar. Uma coluna com números armazenados como texto exige conversão com relatório de falhas.'),
   ('Operações geográficas','Use to_crs para transformar coordenadas e set_crs somente para atribuir referência conhecida. Distâncias e áreas dependem do CRS. Verifique cardinalidade de spatial joins e preserve identificadores.'),
   ('Funções e verificações','Implemente funções pequenas com contratos de entrada e saída. Teste casos vazios, nulos e geometrias inválidas. Não capture todas as exceções para continuar silenciosamente com dados incompletos.'),
   ('Exportação e documentação','Grave produtos com schema e CRS corretos, evitando sobrescrita acidental. Registre número de feições e transformações. Um README com comandos e dependências permite reproduzir o processamento.')]),
  ('R para Análise Geoespacial','R combina estatística e objetos espaciais, permitindo investigar padrões e produzir resultados documentados. O manejo de CRS e de dados ausentes precisa acompanhar o fluxo analítico.',
   'Usar sf para ler polígonos e resumir indicadores, registrando critérios de junção e unidades.',[
   ('Projeto e dependências','Organize scripts, dados e resultados; registre versões de R e pacotes. Trabalhe com fontes preservadas e configuração separada. Um projeto reproduzível precisa de caminhos relativos consistentes.'),
   ('Objetos sf e referência','Confira st_crs, geometria e schema ao importar. st_transform converte coordenadas; definir CRS não é reprojetar. Verifique comportamento geodésico e unidades das funções utilizadas.'),
   ('Manipulação e joins','Separe junção por chave e relação espacial. Revise múltiplas correspondências e ausências após st_join. Não some indicadores duplicados pela expansão da tabela.'),
   ('Estatística e mapas','Explore distribuições por região e período. Trate NA de acordo com a pergunta, não apenas removendo linhas. Mapas de taxas devem explicitar denominadores e limites da agregação.'),
   ('Relatório reproduzível','Inclua código, sessões, fontes e critérios em documento reexecutável. Teste uma sessão nova e registre diferenças. Separe interpretação de inferência confirmada por desenho adequado.')]),
  ('SQL para Consultas Espaciais','SQL espacial combina seleção relacional e predicados geográficos. O desempenho e a correção dependem de schema, referência espacial, cardinalidade e uso adequado dos índices.',
   'Consultar equipamentos em até um quilômetro de um ponto e resumir contagens por território.',[
   ('Modelo e seleção','Revise chaves e relações antes de escrever joins. Diferencie WHERE e HAVING e teste agregações em amostras pequenas. Nulos têm semântica própria e não devem ser comparados por igualdade comum.'),
   ('Tipos espaciais','Identifique geometry, geography, SRID e unidades. ST_Transform modifica coordenadas; ST_SetSRID apenas atribui referência. Não use predicados sobre CRSs incompatíveis.'),
   ('Predicados e agregações','Diferencie contém, cobre, intersecta e distância. Um ponto na borda pode receber tratamento diferente conforme o predicado. Avalie se a junção pode produzir múltiplas correspondências.'),
   ('Índices e plano','Use GiST e ST_DWithin com índice compatível. Examine EXPLAIN e estatísticas da tabela. Planeje filtros relacionais e espaciais sem presumir que todo índice será usado em tabelas pequenas.'),
   ('Parâmetros e operação','Passe valores por binding do cliente, sem concatenar entrada no SQL. Use transações para alterações e roles de menor privilégio. Registre schema e versão das consultas entregues.')]),
  ('APIs e Serviços Geoespaciais','APIs geográficas expõem dados e operações por contratos verificáveis. Paginação, referência espacial, autenticação e limites do serviço precisam ser tratados na integração.',
   'Consumir um serviço de feições paginado, preservar identificadores e validar a coleção recebida.',[
   ('Contrato e formatos','Diferencie mapa renderizado e dados vetoriais. WMS oferece imagens; WFS e APIs de feições entregam objetos. Consulte capabilities ou descrição do serviço antes de montar requisições.'),
   ('Requisições e limites','Defina timeout, paginação e política de repetição limitada. Repetir uma operação de escrita exige atenção à idempotência. Registre códigos HTTP e mensagens sem expor tokens.'),
   ('Geometria e referência','Confira formato, CRS e ordem de coordenadas. GeoJSON padrão usa longitude/latitude WGS84. Não transforme uma imagem WMS em dado vetorial sem método específico.'),
   ('Validação do retorno','Confirme schema, contagens, duplicatas e completude das páginas. Resposta HTTP 200 não demonstra que todos os dados foram obtidos. Verifique limites e filtros aplicados pelo servidor.'),
   ('Entrega e observabilidade','Preserve contratos e exemplos de uso. Controle credenciais fora do código e monitore mudanças de versão. Cache e reprocessamento devem respeitar licença e atualidade dos dados.')]),
  ('Automação de Pipelines Geográficos','Automação confiável reduz tarefas repetidas sem esconder decisões analíticas. Um pipeline precisa de entradas declaradas, validações, logs e resultados reexecutáveis.',
   'Automatizar leitura, revisão, reprojeção e exportação de várias camadas sem apagar fontes.',[
   ('Configuração e escopo','Defina arquivos, camadas, CRS de destino e critérios de seleção em configuração. Faça inventário inicial e diferencie ausência de arquivo de camada vazia. Valide caminhos antes de escrever.'),
   ('Funções de processamento','Separe leitura, validação, transformação e exportação. Preserve schema e identificadores, tratando uma camada por vez. Evite estado global oculto que torne o resultado dependente da ordem de execução.'),
   ('Controle de falhas','Registre camada, etapa e erro; não declare sucesso quando parte das saídas falhar. Arquivos temporários e gravação final controlada reduzem entregas parciais. Preserve as fontes para recuperação.'),
   ('Testes e repetição','Use dados pequenos com resultado conhecido e execute novamente para conferir idempotência. Teste nulos, CRS ausente e entrada inválida. Uma execução bem-sucedida não garante estabilidade em outros dados.'),
   ('Agendamento e operação','Registre versão, duração, contagens e localização dos produtos. Defina responsável por alertas e reexecução. Rotinas agendadas devem declarar ambiente e permissões, sem senha fixa no script.')]),
 ],
 [
  ('Modelagem Preditiva Geoespacial','Predição espacial estima resultados em locais ou períodos ainda não observados. A preparação e a avaliação devem reproduzir essa condição para produzir métricas úteis à decisão.',
   'Estimar uma variável ambiental em regiões novas usando atributos de relevo e cobertura do solo.',[
   ('Alvo e domínio','Defina variável, horizonte e unidade de observação. Diferencie interpolação dentro do suporte e extrapolação. Identifique atributos disponíveis na data real da previsão.'),
   ('Amostra e atributos','Mapeie distribuição e ausência das amostras. Combine fontes com escala e período consistentes. Evite incluir respostas futuras, proxies do alvo ou identificadores que permitam memorização.'),
   ('Baseline e ajuste','Compare média ou modelo simples com alternativas mais complexas. Aprenda imputação, escala e seleção de atributos somente no treino. Registre hiperparâmetros e procedimento de escolha.'),
   ('Validação coerente','Separe blocos espaciais ou períodos conforme o uso pretendido. Mantenha teste final fora do ajuste. Compare MAE, RMSE e resíduos por região, sem ocultar falhas locais na média.'),
   ('Mapa e incerteza','Mostre suporte dos dados e regiões fora do domínio de treinamento. Documente limitações e calibração quando houver intervalos. A previsão não elimina necessidade de observação e revisão.')]),
  ('Séries Temporais Ambientais','Séries ambientais combinam dinâmica, sazonalidade e processos de observação. Uma avaliação temporal precisa respeitar a ordem dos eventos e as informações disponíveis a cada previsão.',
   'Prever valores mensais de uma estação ambiental e comparar com um baseline sazonal.',[
   ('Calendário e observação','Uniformize datas, fuso e frequência. Diferencie lacuna, zero e período ainda não concluído. Reamostragem deve respeitar significado da variável, como soma de chuva ou média de temperatura.'),
   ('Exploração e baseline','Inspecione tendência, sazonalidade e mudanças de instrumento. Compare previsão ingênua e sazonal antes de modelos complexos. Registre período mínimo disponível para cada horizonte.'),
   ('Atributos temporais','Use defasagens e janelas calculadas apenas com passado conhecido. Não faça média centralizada como atributo de previsão futura. Preserve a separação entre preparação histórica e alvo.'),
   ('Avaliação em janelas','Adote origem móvel ou divisão cronológica e compare o mesmo horizonte. Evite embaralhar datas entre treino e teste. Métricas devem ser apresentadas por estação e período relevante.'),
   ('Operação e alertas','Registre previsão, data de emissão e observação posterior. Monitore mudança de padrão e atraso de dados. Diferencie previsão de limite operacional e explique a incerteza ao usuário.')]),
  ('Geoestatística e Interpolação','Interpolação produz estimativas entre amostras e depende do processo espacial, da vizinhança e do suporte. Superfícies suaves não demonstram precisão ou existência de dados suficientes.',
   'Comparar IDW e abordagem baseada em variograma para uma variável contínua amostrada em pontos.',[
   ('Amostragem e referência','Examine concentração, lacunas, duplicatas e suporte da medida. Use CRS e unidades adequados para distâncias. Valores coletados em profundidades ou períodos diferentes podem não ser comparáveis.'),
   ('Exploração e dependência','Observe distribuição, tendência e outliers antes do variograma. Registre pares, classes de distância e direção. Um variograma instável pode refletir falta de suporte, não ausência de estrutura.'),
   ('Métodos e parâmetros','IDW pondera inversamente a distância e depende de potência e vizinhança. Krigagem usa um modelo de dependência e hipóteses associadas. Justifique alcance, patamar e efeito pepita quando aplicáveis.'),
   ('Validação independente','Compare previsões com amostras reservadas e examine erros por localização. Escolha uma divisão que não favoreça apenas pontos muito próximos. Ajuste parâmetros sem usar o teste final.'),
   ('Grade e limites','Defina resolução de saída sem prometer detalhe inexistente. Mascare áreas sem suporte e documente extrapolação. Incerteza de krigagem é condicional ao modelo adotado, não inclui automaticamente todo erro de fonte.')]),
  ('Previsão de Riscos Ambientais','Modelos de risco combinam ameaça, exposição e vulnerabilidade sob hipóteses explícitas. Probabilidade, suscetibilidade e consequência não devem ser usadas como termos intercambiáveis.',
   'Comparar cenários de suscetibilidade a inundação e distribuição de infraestrutura exposta.',[
   ('Conceitos e objetivo','Defina evento, horizonte e decisão. Diferencie suscetibilidade espacial de probabilidade temporal. Um mapa de ameaça não equivale ao risco sem considerar exposição e vulnerabilidade.'),
   ('Fontes e escala','Inventarie relevo, drenagem, chuva, ocupação e registros de eventos. Confira precisão e cobertura. Ausência de registro não demonstra ausência do fenômeno em local pouco observado.'),
   ('Construção do modelo','Compare regra explícita, método estatístico e modelo preditivo conforme os dados. Documente pesos, variáveis e limites. Não trate saída de classificação como probabilidade calibrada sem avaliação.'),
   ('Cenários e avaliação','Reserve eventos ou regiões para avaliar generalização. Compare cenários de entrada e sensibilidade. Métricas devem considerar classes raras e consequências diferentes de falsos positivos e negativos.'),
   ('Comunicação e revisão','Apresente mapa, exposição, incerteza e condições de uso. Registre atualização e responsável pela revisão. Produtos de estudo não substituem laudos ou decisões de defesa civil sem validação especializada.')]),
  ('Validação de Modelos Espaciais e Temporais','A validação deve testar a capacidade pretendida de generalização. Separar amostras aleatoriamente pode oferecer uma avaliação otimista quando vizinhos ou datas próximas compartilham informação.',
   'Comparar divisão aleatória, blocos espaciais e divisão cronológica de um mesmo problema preditivo.',[
   ('Uso pretendido e separação','Defina se o modelo será aplicado a locais conhecidos, novas regiões ou datas futuras. Escolha separação coerente e registre grupos. O desenho da validação antecede a comparação de algoritmos.'),
   ('Vazamento de informação','Ajuste escala, imputação e seleção de atributos dentro do treino de cada fold. Preserve independência dos rótulos. Remova variáveis derivadas do alvo ou indisponíveis no momento de prever.'),
   ('Blocos e janelas','Use grupos espaciais ou janelas temporais conforme a tarefa. Considere distância entre treino e teste quando houver autocorrelação. O tamanho do bloco envolve a escala do processo e precisa de justificativa.'),
   ('Métricas e diagnóstico','Compare baseline, erro por grupo e distribuição de resíduos. Informe tamanho da amostra e variação entre folds. Evite escolher uma métrica apenas por oferecer número aparentemente melhor.'),
   ('Teste final e relatório','Use teste final após concluir escolhas de modelo e parâmetros. Registre limitações, domínio e repetibilidade. Uma mudança relevante de dados ou método exige nova avaliação antes da operação.')]),
 ],
]

REFERENCIAS = [
 ['https://scikit-learn.org/stable/modules/cross_validation.html'],
 ['https://docs.qgis.org/3.40/en/docs/user_manual/index.html','https://postgis.net/docs/manual-3.5/using_postgis_dbmanagement.html'],
 ['https://learn.microsoft.com/en-us/power-bi/guidance/star-schema'],
 ['https://geopandas.org/en/stable/docs/user_guide.html'],
 ['https://geopandas.org/en/stable/docs/user_guide.html','https://postgis.net/docs/manual-3.5/using_postgis_dbmanagement.html'],
 ['https://scikit-learn.org/stable/modules/cross_validation.html'],
]
