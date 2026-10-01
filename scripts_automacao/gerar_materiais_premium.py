"""Gera 60 materiais técnicos e conecta os cards do site a arquivos reais.

Uso: python scripts_automacao/gerar_materiais_premium.py [--substituir]
Dependências: geopandas, shapely, pyogrio (somente para os GeoPackages).
As bases são sintéticas; nenhum dado de clientes ou órgão público é copiado.
"""
import argparse
from datetime import date
from html import escape, unescape
from pathlib import Path
import re
import sqlite3
import unicodedata
import geopandas as gpd
from shapely.geometry import Point, LineString, box

ROOT = Path(__file__).resolve().parents[1]
FOLDERS = {'templates': 'templates_gis', 'bases': 'bancos_dados',
           'portfolio': 'portfolios_cases', 'roadmaps': 'roadmaps_aprendizado',
           'exercicios': 'exercicios_praticos', 'glossarios': 'glossarios_tecnicos'}
CRS = 31982  # SIRGAS 2000 / UTM 22S; adequado apenas à zona correspondente.
X, Y = 500000, 6900000

# Conteúdo específico: objetivo operacional, sequência, exemplo e aceite.
TEMPLATES = [
('atlas executivo', 'Selecione uma camada de cobertura com ID único e um nome por unidade.|Crie um layout A4 paisagem e reserve espaços para mapa, legenda, fontes e síntese.|Ative a geração de atlas/map series usando a camada de cobertura, com extensão dinâmica.|Padronize escala e margens; teste unidades pequenas, grandes e multipartes.|Exporte uma página por unidade e confira sequência, nomes e referências.',
 "QGIS, título por feição: concat('Unidade: ', attribute(@atlas_feature, 'nome'))\nNome de saída: concat('atlas_', attribute(@atlas_feature, 'id'))",
 'Cada unidade deve gerar exatamente uma página; não pode haver rótulo cortado, legenda sem classe ou escala incompatível.'),
('projeto ambiental', 'Crie grupos: referência, meio físico, uso do solo, restrições, resultados e campo.|Mantenha fontes brutas em modo de leitura e resultados em um GeoPackage separado.|Defina nomes estáveis, IDs persistentes, unidades e dicionário de atributos.|Documente CRS original, transformações e data de aquisição de cada fonte.|Salve caminhos relativos e reabra o projeto a partir de uma cópia em outra pasta.',
 'Estrutura sugerida:\n01_fontes/\n02_trabalho/base.gpkg\n03_resultados/\n04_mapas/\n05_documentacao/\nCampos mínimos: id, fonte, data_ref, classe, observacao.',
 'A cópia do projeto deve abrir sem fontes ausentes; camadas devem manter IDs, CRS e metadados.'),
('uso e cobertura', 'Defina uma classificação mutuamente exclusiva compatível com as fontes.|Crie um campo classe e aplique domínio de valores válidos.|Use cores com contraste e revise a legenda em tamanho de impressão.|Calcule hectares em projeção adequada e agregue por classe.|Diferencie áreas não classificadas de lacunas e de regiões fora do estudo.',
 'QGIS, área plana em camada métrica: round(area($geometry) / 10000, 2)\nClasses didáticas: vegetacao, urbanizado, agua, nao_classificado.\nNão confundir valor zero com ausência de informação.',
 'A soma das áreas por classe deve coincidir com a área classificada; lacunas e sobreposições precisam de justificativa.'),
('indicadores urbanos', 'Escolha indicadores com unidade, período e denominador explícitos.|Relacione dados à camada territorial por chave única, não por ordem das linhas.|Calcule taxas antes de mapear e documente denominadores nulos.|Use classificação coerente entre períodos e escreva a pergunta de negócio.|Inclua uma tabela com valores e ressalvas para apoiar a leitura do mapa.',
 'Taxa por 1.000 habitantes = equipamentos * 1000 / populacao.\nQGIS: CASE WHEN "populacao" > 0 THEN 1000.0 * "equipamentos" / "populacao" ELSE NULL END',
 'A junção não pode multiplicar unidades; taxas devem usar o mesmo período e denominador válido.'),
('diagnóstico hídrico', 'Selecione bacias e drenagem com origem e escala documentadas.|Defina sentido dos trechos e trate cruzamentos sem conexão conforme a realidade.|Use espessura e cor para hierarquia da rede, evitando ocultar canais menores.|Inclua localização, escala, unidades e pontos de monitoramento no layout.|Compare a extensão da rede com o limite da bacia e registre exceções.',
 'Esquema da camada trechos: id, de_no, para_no, ordem, fonte, data_ref.\nQGIS, comprimento plano em metros: length($geometry).\nO sentido geométrico de uma linha não demonstra sozinho o sentido de fluxo.',
 'Trechos conectados devem compartilhar nós quando exigido; bacias, rede e pontos devem ter CRS compatíveis.'),
('análise multicritério', 'Defina critérios, direção de preferência, escala e fonte.|Normalize variáveis para intervalos comparáveis e trate dados ausentes.|Separe restrições impeditivas de critérios ponderados.|Calcule a combinação e compare cenários de pesos.|Registre sensibilidade e evite apresentar o ranking como verdade absoluta.',
 'Normalização benefício: (x - minimo) / (maximo - minimo).\nNormalização custo: 1 - valor_normalizado.\nÍndice = 0.5 * acesso + 0.3 * infraestrutura + 0.2 * adequacao.\nSe maximo=minimo, defina tratamento explícito; não divida por zero.',
 'Pesos devem somar 1; critérios devem ter a mesma orientação; teste se pequenas mudanças alteram decisões.'),
('simbologia corporativa', 'Defina famílias de cor para referências, temas e alertas.|Reserve destaque para informação prioritária, sem depender apenas da cor.|Escolha símbolos legíveis nas escalas finais e revise contraste.|Crie convenções de rótulos e tamanhos para diferentes níveis de mapa.|Salve estilos QGIS/ArcGIS separadamente e teste sua aplicação à camada correta.',
 'Paleta de identidade: azul #0B2F5B; verde #6BD66A; ciano #16BFD0.\nUse contorno e forma além da cor.\nConvenção: limite=linha tracejada; ponto de coleta=círculo; alerta=triângulo.\nEstilos QML e LYRX não são intercambiáveis.',
 'O mapa deve continuar compreensível em impressão reduzida e para leitores com dificuldade de distinguir cores.'),
('processamento em lote', 'Liste entradas com caminho, CRS e formato esperado.|Separe saída e fonte; planeje nomes únicos por camada.|Defina parâmetros uma única vez e registre-os por execução.|Interrompa entradas inválidas sem anunciar sucesso do lote completo.|Reabra as saídas e compare contagem, extensão e atributos.',
 'Exemplo com o kit real da Academy, após importar como kit:\n# QGIS: kit.exportar_camadas_lote(camadas, pasta_saida)\nConsulte a assinatura no script antes de executar.\nManifesto: entrada, saida, parametros, inicio, fim, status, mensagem.',
 'Cada entrada precisa de status verificável; fontes não devem ser sobrescritas e falhas devem ficar registradas.'),
('monitoramento temporal', 'Crie campos de data de aquisição e período de referência.|Mantenha mesma área de estudo e método entre observações.|Harmonize resolução e classes sem esconder mudanças de fonte.|Apresente mapas lado a lado com legenda e escala consistentes.|Diferencie mudança observada de efeitos de nuvens, sensores ou processamento.',
 'Tabela de acompanhamento: id_unidade, data_ref, indicador, unidade, fonte, metodo.\nVariação absoluta = valor_final - valor_inicial.\nVariação percentual = 100*(final-inicial)/inicial, apenas quando inicial!=0.',
 'As comparações precisam ser temporal e metodologicamente compatíveis; lacunas devem estar visíveis.'),
('mapa para impressão', 'Escolha A4 ou A3 conforme a densidade da informação e o uso final.|Defina título, mapa principal, localização, legenda e referência espacial.|Inclua autoria, data, fontes, escala gráfica e unidade de medida.|Revise fontes incorporadas, contraste e espessura de linhas no PDF.|Imprima uma amostra ou visualize no tamanho final antes da entrega.',
 'Checklist do layout: título; legenda; escala gráfica; norte quando pertinente; SRC; fontes; autoria; data.\nPara imagens, 300 DPI é uma referência de exportação, não uma garantia de precisão cartográfica.',
 'Todos os elementos devem ser legíveis no tamanho de uso; a escala informada deve corresponder à composição final.'),
]

PORTFOLIOS = [
('Inventário ambiental demonstrativo', 'Cruzar observações de campo com unidades do estudo e classificar evidências.', 'inventario.gpkg: pontos com id, grupo, data_ref e observacao; limite com polígonos.', 'Validar CRS e registros.|Associar cada ponto à unidade territorial.|Resumir quantidade por grupo sem extrapolar representatividade.|Produzir mapa, tabela e limitações.', 'Se oito registros se distribuem entre três grupos, a soma das contagens deve ser oito; isso não estima abundância no território.'),
('Automação de exportação', 'Comparar uma tarefa manual documentada com uma rotina reproduzível.', 'Três camadas de teste; parâmetros e registro de execução; saídas novas.', 'Medir execução manual com o mesmo escopo.|Executar rotina com logs e tratamento de falhas.|Comparar conteúdo das saídas, não apenas tempo.|Descrever a função do autor e as decisões.', 'Exemplo fictício: 12 minutos contra 3 minutos representa 75% de redução; substitua pelos tempos medidos antes de divulgar.'),
('Inteligência urbana', 'Comparar oferta de serviços por população e localização.', 'Setores sintéticos com populacao e equipamentos; pontos de serviço.', 'Verificar chaves e períodos.|Calcular equipamentos por 1.000 habitantes.|Mapear distribuição e distinguir disponibilidade de acessibilidade.|Redigir síntese sem classificar causalidade.', 'Setor com 2 equipamentos e 4.000 habitantes tem 0,5 equipamento por 1.000; o valor não mede qualidade do atendimento.'),
('Classificação de cobertura', 'Apresentar um processo de classificação com avaliação independente.', 'Cena e amostras com origem registrada; divisão geográfica de treino e teste.', 'Descrever sensor, bandas e datas.|Separar treino e teste sem pixels vizinhos vazarem.|Treinar e guardar parâmetros.|Apresentar matriz de confusão e limitações.', 'Matriz didática [[8,2],[1,9]] tem acurácia 17/20=0,85; não é resultado obtido em campo.'),
('Predição espacial', 'Avaliar generalização geográfica de uma variável contínua.', 'Amostras sintéticas, atributos numéricos, coordenadas métricas e IDs de blocos.', 'Definir alvo e data de disponibilidade das variáveis.|Separar blocos geográficos.|Ajustar pré-processamento dentro do treino.|Comparar modelo com referência simples e mapear resíduos.', 'MAE e RMSE devem usar observações fora do ajuste; explicar unidades e distribuição espacial do erro.'),
('Dashboard territorial', 'Organizar indicadores para uma pergunta executiva específica.', 'Dimensão territorial, calendário e fatos com unidade e fonte.', 'Definir granularidade e chaves.|Modelar relações evitando duplicação de totais.|Criar mapa, filtros e indicadores.|Verificar atualização e explicar contexto.', 'Um total filtrado deve coincidir com a soma da tabela na mesma seleção; não somar taxas sem denominadores.'),
('Acessibilidade a serviços', 'Explorar distância e cobertura sem confundir proximidade com acesso real.', 'Pontos de demanda, serviços e rede com restrições explicitadas.', 'Definir distância euclidiana ou de rede.|Usar CRS métrico adequado.|Calcular relação de demanda e serviços.|Apresentar hipóteses de viagem e grupos não atendidos.', 'Um buffer de 500 m não garante caminhada de 500 m; barreiras e rede viária podem mudar o acesso.'),
('Monitoramento hídrico', 'Comparar séries e locais mantendo unidade e qualidade de observação.', 'Estações, datas, valores e indicadores de qualidade sintéticos.', 'Conferir duplicatas e unidade.|Organizar séries por estação.|Identificar lacunas sem preencher com informação futura.|Apresentar tendências e limites de interpretação.', 'Média entre 10, 12 e 14 é 12; a tendência temporal não demonstra causa hidrológica por si só.'),
('Arquitetura de banco espacial', 'Demonstrar modelagem, integridade e consultas orientadas ao uso.', 'Esquema de unidades, ativos e observações; diagrama e consultas SQL.', 'Definir chaves primárias e estrangeiras.|Escolher SRID e índices.|Validar inserções e consultas de relacionamento.|Documentar desempenho e decisões de modelagem.', 'Uma junção 1:N pode duplicar unidades; agregue ativos antes de contar unidades territoriais.'),
('Apresentação de portfólio', 'Selecionar entregas verificáveis e comunicar a contribuição profissional.', 'Um projeto real autorizado ou caso didático claramente identificado.', 'Resumir problema e destinatário.|Apresentar método e papel do autor.|Mostrar evidências de resultado e limitações.|Fechar com próximos passos e links permitidos.', 'Não declarar clientes, ganhos, autoria exclusiva ou métricas sem evidência e autorização.'),
]

TRILHAS = [
('QGIS', ['Carregar vetores e identificar CRS', 'Editar atributos e organizar GeoPackage', 'Filtrar, selecionar e relacionar tabelas', 'Aplicar buffers e recortes em CRS métrico', 'Validar geometrias e relações topológicas', 'Construir simbologia e layout', 'Automatizar um fluxo no modelador', 'Entregar atlas e relatório de qualidade']),
('ArcGIS Pro', ['Organizar projeto e geodatabase', 'Conferir projeções e domínios', 'Consultar tabelas e seleções', 'Executar operações vetoriais documentadas', 'Revisar integridade e relacionamentos', 'Compor mapas e layouts', 'Planejar automação com ArcPy', 'Entregar projeto reproduzível']),
('Python', ['Criar ambiente e usar arquivos', 'Dominar funções e tratamento de erros', 'Manipular tabelas com pandas', 'Ler e transformar vetores com GeoPandas', 'Cruzar camadas e medir em CRS métrico', 'Ler raster por janelas e máscaras', 'Organizar módulos, testes e logs', 'Publicar um kit documentado']),
('R', ['Organizar projeto e dependências', 'Ler tabelas e tipos de dados', 'Manipular grupos e valores ausentes', 'Ler vetores com sf e verificar CRS', 'Produzir mapas e gráficos', 'Aplicar estatística com pressupostos', 'Registrar scripts e ambiente', 'Entregar relatório analítico reproduzível']),
('SQL e PostGIS', ['Modelar tabelas e chaves', 'Consultar e agregar atributos', 'Relacionar tabelas com joins', 'Carregar geometrias e conferir SRID', 'Aplicar predicados espaciais', 'Planejar índices e verificar consultas', 'Controlar transações e integridade', 'Documentar banco e consultas de negócio']),
('IA geoespacial', ['Definir problema e alvo', 'Examinar atributos e lacunas', 'Separar blocos de treino e teste', 'Construir pipeline sem vazamento', 'Treinar referência e Random Forest', 'Avaliar erro e sensibilidade', 'Classificar raster e tratar nodata', 'Comunicar limites e reprodutibilidade']),
('Sensoriamento remoto', ['Identificar sensores e resoluções', 'Escolher cenas e datas', 'Entender reflectância e pré-processamento', 'Calcular índices com máscaras', 'Organizar amostras e classes', 'Classificar com avaliação independente', 'Comparar períodos compatíveis', 'Entregar mapas e relatório de precisão']),
('BI geográfico', ['Definir pergunta e indicadores', 'Modelar granularidade e calendário', 'Preparar dados e chaves territoriais', 'Calcular medidas e denominadores', 'Criar mapa e gráficos adequados', 'Aplicar filtros e verificar totais', 'Organizar narrativa e acessibilidade', 'Documentar atualização e apresentar painel']),
('Drones', ['Entender produtos e finalidade', 'Planejar aquisição e qualidade', 'Distinguir apoio e verificação', 'Entender orientação e processamento', 'Interpretar ortofoto e nuvem de pontos', 'Diferenciar modelos de superfície e terreno', 'Avaliar precisão e metadados', 'Documentar produto e limites de uso']),
('Carreira', ['Mapear competências e objetivo', 'Escolher domínio e problema aplicado', 'Construir projeto demonstrativo', 'Registrar evidências e decisões', 'Escrever narrativa de portfólio', 'Preparar apresentação e revisão técnica', 'Planejar estudo e busca de oportunidades', 'Revisar metas com entregas verificáveis']),
]

EXERCICIOS = [
('Consistência topológica', 'Dois quadrados em CRS métrico: A=(0,0)-(1000,1000), B=(900,0)-(1900,1000). Os números são locais para cálculo didático, não localização real.', 'Crie os dois polígonos e declare um CRS métrico apenas para o ensaio.|Verifique validade geométrica e sobreposição.|Calcule áreas individuais, interseção e união.|Proponha uma correção somente após definir a regra da cobertura.|Documente atribuir CRS versus reprojetar em dados reais.', 'Cada polígono tem 100 ha; sobreposição=10 ha; união=190 ha. Ambos podem ser geometricamente válidos apesar da sobreposição.', 'ST_Area(ST_Intersection(a.geom,b.geom))/10000.0; no QGIS use interseção seguida de área plana.'),
('Mapa de indicadores', 'Tabela: setor A, população 2000, serviços 2; setor B, população 4000, serviços 2; setor C, população 0, serviços 1.', 'Relacione a tabela por código estável.|Calcule serviços por 1.000 habitantes.|Represente valores com legenda e unidade.|Trate o setor C como sem taxa calculável.|Revise dados fonte e denominador.', 'A=1,0; B=0,5; C=NULL. Não registrar infinito nem zero para a taxa de C.', 'CASE WHEN "populacao">0 THEN 1000.0*"servicos"/"populacao" ELSE NULL END'),
('Automação com Python', 'CSV: id,classe,valor\n1,A,10\n2,B,20\n3,A,30\n4,B,40', 'Leia o CSV sem perder IDs.|Selecione classe A.|Exporte resultado para arquivo novo.|Registre contagem inicial e final.|Teste uma classe ausente e uma coluna obrigatória ausente.', 'Entrada=4 linhas; filtro A=2 linhas; soma de valor=40. Classe ausente deve produzir tabela vazia com esquema mantido.', "import pandas as pd\ndf=pd.read_csv('entrada.csv')\nsaida=df.loc[df['classe'].eq('A')].copy()\nsaida.to_csv('resultado.csv',index=False)"),
('Consulta espacial', 'Dois polígonos adjacentes: A=(0,0)-(100,100), B=(100,0)-(200,100); pontos P1=(25,25), P2=(150,50), P3=(100,50).', 'Crie geometrias no mesmo CRS.|Compare ST_Within e ST_Covers.|Relacione pontos a polígonos.|Identifique ambiguidade na borda.|Defina regra de associação para não duplicar contagem.', 'P1 está dentro de A; P2 dentro de B; P3 está na borda de ambos: Within é falso e Covers é verdadeiro para os dois.', 'SELECT p.id,u.id FROM pontos p JOIN unidades u ON ST_Covers(u.geom,p.geom);'),
('Classificação sintética', 'Atributos de treino: (0,0)->0; (0,1)->0; (1,0)->1; (1,1)->1. Matriz de avaliação independente didática: [[8,2],[1,9]].', 'Separe atributos e classe.|Treine um classificador com os quatro exemplos para entender a API.|Explique por que o conjunto pequeno não valida uso real.|Calcule métricas usando a matriz independente fornecida.|Discuta classes e amostragem necessárias numa cena real.', 'Acurácia=0,85. Precisão da classe 1=9/11; revocação da classe 1=9/10. O treino minúsculo não constitui avaliação independente.', "from sklearn.tree import DecisionTreeClassifier\nmodelo=DecisionTreeClassifier(random_state=42).fit([[0,0],[0,1],[1,0],[1,1]],[0,0,1,1])\nprint(modelo.predict([[1,.5]]))  # [1]"),
('Dashboard', 'Fatos: A/2025=10, B/2025=20, A/2026=15, B/2026=25. Dimensão de setores com uma linha por código.', 'Modele relação entre dimensão e fatos.|Crie total por ano e variação por setor.|Aplique filtros de ano e setor.|Verifique se relações duplicam linhas.|Escreva um resumo sem somar anos como se fossem o mesmo instante.', 'Total 2025=30; total 2026=40; variação total=33,333...%. Setor A=50%; B=25%.', 'Variação percentual=100*(valor_atual-valor_anterior)/valor_anterior, para denominador diferente de zero.'),
('Proximidade', 'Dois pontos em metros: P=(0,0), Q=(300,400); raio de cobertura=500 m.', 'Calcule distância euclidiana.|Construa buffer circular em CRS métrico.|Compare predicados estrito e inclusivo.|Repita com ponto a 501 m.|Explique diferença entre proximidade em linha reta e rede.', 'Distância P-Q=500 m. Em cálculo analítico Q está no limite; aproximação poligonal do buffer pode alterar relação. Use distância<=500 para o teste inclusivo.', 'distancia=((x2-x1)**2+(y2-y1)**2)**0.5\nEm PostGIS, ST_DWithin(geom_p,geom_q,500) usa distância inclusiva em unidades do CRS.'),
('Interpolação IDW', 'Amostras: (0,0)=10, (1000,0)=20. Destino=(500,0); potência=2.', 'Calcule distâncias e pesos.|Normalize os pesos.|Estime o ponto central.|Teste coincidência exata com uma amostra.|Discuta ausência de extrapolação confiável com apenas duas amostras.', 'No centro, pesos iguais e estimativa=15. Na coordenada (0,0), retorne 10 diretamente para evitar divisão por zero.', 'peso_i=1/(distancia_i**potencia)\nestimativa=sum(peso_i*valor_i)/sum(peso_i)\nDistância zero exige tratamento específico.'),
('Previsão temporal', 'Observado=[10,12,14]; previsto=[9,12,16]. Série de treino regular=[2,4,6,8,10].', 'Separe treino passado e teste futuro.|Calcule MAE, RMSE e R² da previsão fornecida.|Ajuste uma tendência linear à série de treino.|Compare com referência do último valor.|Explique limites da extrapolação.', 'MAE=1; RMSE=sqrt(5/3)=1,290994...; R²=1-5/8=0,375. Tendência linear prevê 12 no próximo passo.', 'MAE=mean(abs(y-p)); RMSE=sqrt(mean((y-p)**2)); R²=1-sum((y-p)**2)/sum((y-mean(y))**2).'),
('Entrega integrada', 'Use os dados sintéticos de bancos_dados e escolha uma pergunta territorial com unidade e critério de qualidade.', 'Inventarie fontes e declare que são sintéticas.|Produza uma análise com operações documentadas.|Gere mapa, tabela e relatório.|Reabra dados exportados e repita verificações.|Apresente conclusões proporcionais à demonstração.', 'Entrega mínima: GeoPackage verificável, mapa com referências, tabela de resultados, relatório de método e limitações, manifesto e checklist.', 'Manifesto: caminho, tipo, versão, data, responsável, CRS, contagem e checksum opcional.'),
]

# Definições específicas; cada linha é um termo e sua explicação operacional.
GLOSSARIOS = [
[
('Datum','Referência geodésica que estabelece como coordenadas se relacionam à Terra; não é sinônimo de projeção.'),
('CRS/SRC','Sistema que combina referência e eixos/unidades; registre a definição completa e não apenas um nome informal.'),
('SIRGAS2000','Referencial adotado oficialmente no Brasil; sua realização e época devem ser consideradas em trabalhos de precisão.'),
('EPSG:4674','SIRGAS2000 em coordenadas geográficas; longitude e latitude são angulares, não distâncias em metros.'),
('Projeção','Transformação da superfície para um plano, com distorções que devem ser adequadas ao objetivo.'),
('UTM','Família de projeções por fusos; exige fuso e hemisfério compatíveis com a região.'),
('Atribuir CRS','Rotular a interpretação das coordenadas existentes; não altera seus números.'),
('Reprojetar','Calcular coordenadas em outro CRS mediante operação definida; difere de trocar metadados.'),
('Escala','Relação entre representação e terreno; ampliar visualização não aumenta a precisão da fonte.'),
('Época','Instante ao qual coordenadas ou realização se referem, relevante para movimentos e alta precisão.'),
('Altitude elipsoidal','Distância referida ao elipsoide, diferente de altitudes físicas associadas ao campo de gravidade.'),
('Precisão','Dispersão ou qualidade especificada de medida; não equivale automaticamente à exatidão em relação à referência.')],
[
('Validade geométrica','Conformidade interna de uma geometria com regras do modelo; não garante relações corretas entre feições.'),
('Topologia','Relações como conexão, adjacência e contenção; regras dependem da finalidade da base.'),
('Sobreposição','Área compartilhada entre feições; pode ser erro de uma partição ou relação legítima entre temas.'),
('Lacuna','Região sem cobertura; só é erro onde o modelo exige continuidade e não autoriza vazios.'),
('Sliver','Fragmento estreito frequentemente produzido por desalinhamento; não deve ser removido sem avaliação de escala e origem.'),
('Snapping','Ajuste de vértices segundo uma tolerância; valores excessivos podem alterar relações legítimas.'),
('Dangle','Extremidade sem conexão de uma linha; pode representar erro ou terminal legítimo de rede.'),
('Multipartes','Feição com vários componentes geométricos; sua existência não representa erro por definição.'),
('Autointerseção','Cruzamento da própria geometria; pode invalidar polígonos conforme o modelo adotado.'),
('Tolerância','Limite de comparação ou edição com unidade e justificativa; não use um número universal.'),
('Integridade referencial','Consistência dos vínculos entre registros, geralmente mantida por chaves e restrições.'),
('Exceção aprovada','Ocorrência permitida com justificativa e aprovação rastreáveis; não é erro simplesmente ocultado.')],
[
('Resolução espacial','Dimensão do elemento amostrado; tamanho de pixel não garante precisão da posição.'),
('Resolução espectral','Detalhe de discriminação de faixas do espectro captadas pelo sensor.'),
('Resolução temporal','Frequência de observação; revisita nominal não assegura cenas sem nuvens.'),
('Resolução radiométrica','Capacidade de quantizar sinal; número de bits não determina sozinho qualidade da informação.'),
('Reflectância','Razão relacionada à energia refletida; compare produtos calibrados e processamento compatível.'),
('Radiância','Energia radiativa medida por unidade de área, ângulo sólido e faixa; difere de reflectância.'),
('NDVI','Índice (NIR-vermelho)/(NIR+vermelho); exige bandas corretas e tratamento de nodata e denominador zero.'),
('Máscara de nuvem','Identificação de pixels não utilizáveis por cobertura atmosférica; revise critérios e sombras.'),
('Classificação supervisionada','Atribuição de classes com exemplos rotulados; qualidade depende das amostras e avaliação independente.'),
('Matriz de confusão','Contagem de referências versus previsões por classe, usada para calcular métricas.'),
('Nodata','Código ou máscara de ausência de observação; não deve ser interpretado como zero físico.'),
('Composição de bandas','Representação conjunta de bandas em canais de cor; cores falsas não indicam valores naturais.')],
[
('Ortofoto','Imagem corrigida geometricamente para reduzir efeitos de perspectiva e relevo, segundo o processo empregado.'),
('GSD','Distância amostrada no terreno por pixel; não equivale a erro posicional validado.'),
('Nuvem de pontos','Conjunto de coordenadas 3D e atributos derivados de levantamento ou processamento.'),
('MDS','Modelo digital de superfície que pode incluir vegetação, edificações e outros objetos.'),
('MDT','Modelo digital do terreno, cujo objetivo é representar a superfície do solo após classificação adequada.'),
('Ponto de apoio','Ponto usado no ajuste; não é independente para medir a qualidade desse mesmo ajuste.'),
('Ponto de verificação','Ponto excluído do ajuste e reservado à avaliação independente de posição.'),
('Sobreposição de imagens','Cobertura comum entre imagens para reconstrução e alinhamento; exigência depende do projeto.'),
('Aerotriangulação','Estimativa da geometria de aquisição e correspondências entre imagens.'),
('RTK','Posicionamento relativo com correções em tempo real; requer condições e rastreabilidade adequadas.'),
('PPK','Processamento posterior de observações de posicionamento; não dispensa verificação do produto.'),
('RMSE posicional','Raiz da média dos quadrados dos erros em relação a referência independente; declare eixos e unidades.')],
[
('Chave primária','Identificador único não nulo de um registro; não confundir com posição atual na tabela.'),
('Chave estrangeira','Vínculo que referencia uma chave de outra tabela e ajuda a manter integridade.'),
('JOIN','Combinação de registros por condição; relações 1:N podem multiplicar linhas.'),
('SRID','Identificador de referência espacial associado à geometria; atribuir não transforma coordenadas.'),
('Índice GiST','Estrutura usada por PostGIS para acelerar consultas espaciais compatíveis; confirme benefício no plano.'),
('ST_Within','Testa interior/contenção segundo relações topológicas; pontos apenas na borda não estão within.'),
('ST_Covers','Relação inclusiva de cobertura que pode incluir a borda; pode gerar múltiplas correspondências.'),
('ST_Intersects','Testa se geometrias compartilham pelo menos um ponto, incluindo contato na borda.'),
('ST_Transform','Transforma coordenadas para outro SRID; exige CRS de origem correto.'),
('ST_SetSRID','Atribui referência à geometria sem transformar valores de coordenadas.'),
('Transação','Unidade de operações com confirmação ou reversão; use para evitar estados parcialmente atualizados.'),
('GeoPackage','Contêiner SQLite para dados geoespaciais com estruturas padronizadas; não é um servidor PostGIS.')],
[
('Ambiente virtual','Conjunto isolado de dependências para reproduzir execução; registre versões e Python.'),
('Função','Bloco reutilizável com parâmetros e retorno; documente pressupostos e efeitos sobre arquivos.'),
('Módulo','Arquivo importável que organiza código; evite executar processos destrutivos durante importação.'),
('DataFrame','Tabela tipada com índice; IDs de negócio não devem depender do índice temporário.'),
('GeoDataFrame','Tabela com geometria ativa e CRS; a informação espacial exige operações coerentes.'),
('Array raster','Matriz ou conjunto de bandas; valores precisam de transformação espacial e CRS para localização.'),
('Pipeline','Sequência organizada de transformação e processamento; em ML ajuste etapas somente no treino.'),
('Exceção','Sinalização de erro tratável; não suprima falhas sem registro e critério de recuperação.'),
('Log','Registro de etapas e resultados da execução; mantenha parâmetros, status e identificação da fonte.'),
('Idempotência','Propriedade de repetir operação sem efeitos adicionais indevidos; defina política de saídas.'),
('Teste','Verificação com entrada e resultado esperado; testes sintéticos não validam precisão de dados reais.'),
('Serialização','Representação de objetos em arquivo; escolha formato que preserve tipos, unidades e metadados.')],
[
('População','Conjunto alvo do estudo; diferencie população estatística de habitantes.'),
('Amostra','Subconjunto observado; desenho amostral influencia representatividade e incerteza.'),
('Média','Soma dividida pelo número de observações válidas; sensível a valores extremos.'),
('Mediana','Valor central ordenado; não é necessariamente igual à média de uma distribuição assimétrica.'),
('Desvio padrão','Medida de dispersão em torno da média; indique convenção amostral ou populacional.'),
('Outlier','Observação atípica segundo critério; não é automaticamente erro a excluir.'),
('Dado ausente','Informação não observada; zero e ausência têm significados diferentes.'),
('Imputação','Preenchimento com regra estimada; em modelos aprenda regras apenas no treino.'),
('Correlação','Associação entre variáveis sob uma medida; não estabelece causalidade.'),
('Viés','Desvio sistemático associado à coleta, modelo ou procedimento; mais dados não o eliminam necessariamente.'),
('Intervalo de confiança','Procedimento com cobertura associada a pressupostos; difere de intervalo de previsão individual.'),
('Autocorrelação espacial','Dependência relacionada à proximidade ou estrutura espacial; altera interpretação de testes e validação.')],
[
('Atributo/feature','Variável usada pelo modelo; deve estar disponível no instante e local da previsão.'),
('Alvo','Variável que se deseja estimar; defina unidade, classe e modo de obtenção.'),
('Treino','Dados usados para ajustar parâmetros do modelo e pré-processamento.'),
('Validação','Dados ou procedimento para escolher e avaliar configurações sem contaminar o teste final.'),
('Teste','Conjunto reservado para estimar generalização após decisões de modelagem.'),
('Vazamento','Uso indevido de informação futura, do teste ou de vizinhos dependentes durante o ajuste.'),
('Hiperparâmetro','Configuração escolhida fora do ajuste interno; seleção deve respeitar a divisão dos dados.'),
('Overfitting','Ajuste excessivo a padrões do treino com generalização insuficiente.'),
('Classificação','Predição de categorias; avaliação por classe pode ser mais informativa que acurácia global.'),
('Regressão','Predição de valores contínuos; métricas devem informar a unidade e a distribuição dos erros.'),
('Agrupamento','Organização não supervisionada por similaridade; grupos não têm significado causal automático.'),
('Validação espacial','Separação por blocos ou regiões para reduzir dependência entre treino e teste.')],
[
('KPI','Indicador vinculado a objetivo e decisão; declare fórmula, unidade, período e responsável.'),
('Granularidade','Nível de detalhe de cada registro; determina agregações e relações válidas.'),
('Dimensão','Entidade descritiva usada para filtrar ou agrupar fatos, como território e tempo.'),
('Fato','Registro de ocorrência ou medida no nível definido; evite misturar granularidades.'),
('Medida','Cálculo de resultado sob contexto de filtros; diferencie valor armazenado de expressão calculada.'),
('Denominador','Base de uma taxa; zero ou períodos incompatíveis exigem tratamento explícito.'),
('Filtro','Restrição de contexto; verifique sua propagação no modelo e nas visualizações.'),
('Drill-down','Navegação para níveis mais detalhados; exige hierarquia e dados disponíveis coerentes.'),
('Dashboard','Conjunto de visualizações orientado a perguntas e ações, não apenas coleção de gráficos.'),
('Narrativa analítica','Sequência de explicação de contexto, evidência e implicação com limites declarados.'),
('Atualização','Reprocessamento dos dados; registre origem, falhas e data da informação exibida.'),
('Acessibilidade','Condições para compreender e operar o painel, incluindo contraste, rótulos e alternativas à cor.')],
[
('Defasagem/lag','Valor de período anterior usado como atributo; não deve incorporar informação futura.'),
('Horizonte','Quantidade de passos futuros previstos; erros e incerteza podem crescer com a distância temporal.'),
('Tendência','Componente de evolução ao longo do tempo; extrapolação não garante continuidade futura.'),
('Sazonalidade','Padrão associado a ciclos regulares, distinto de tendência e eventos isolados.'),
('Interpolação','Estimativa entre observações segundo um modelo espacial ou temporal.'),
('Extrapolação','Estimativa além do domínio observado, frequentemente com maior risco de erro.'),
('IDW','Média ponderada por distância inversa; exige escolhas de potência, vizinhança e tratamento de coincidências.'),
('RBF','Interpolação por funções de base radial; pressupostos e suavização influenciam a superfície.'),
('MAE','Média do erro absoluto; mantém unidade do alvo e reduz ênfase em grandes erros frente ao RMSE.'),
('RMSE','Raiz da média do erro quadrático; destaca erros grandes e mantém unidade do alvo.'),
('R²','Comparação do erro com variabilidade observada; pode ser negativo fora do treino e não mede causalidade.'),
('Backtesting','Avaliação em períodos posteriores ao treino por janelas; respeita a ordem temporal e disponibilidade dos atributos.')],
]


def limpar(texto):
    return unescape(re.sub('<[^>]+>', '', texto)).strip()


def slug(texto):
    normal = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode().lower()
    return re.sub('[^a-z0-9]+', '_', normal).strip('_')


def cabecalho(titulo, descricao):
    return f'# {titulo}\n\n**DataGeo Academy — material técnico | edição 1.0 | {date.today().isoformat()}**\n\n{descricao}\n\n'


def lista_etapas(texto):
    return '\n'.join(f'{i}. {s}' for i, s in enumerate(texto.split('|'), 1))


def template(titulo, descricao, i):
    tema, etapas, exemplo, aceite = TEMPLATES[i]
    return cabecalho(titulo, descricao) + f'''## Natureza e aplicação

Este arquivo é um modelo textual de planejamento, parâmetros e revisão para
{tema}. Não é um projeto .qgs/.qgz/.aprx nem um estilo já instalado. Use-o para
montar a configuração no QGIS ou ArcGIS Pro, adaptando fontes, escala e formato.

## Preparação das entradas

- Preserve as fontes; trabalhe em cópia e identifique o responsável pela revisão.
- Registre nome, versão, data, licença, extensão, contagem e CRS de cada camada.
- Defina identificadores estáveis, campos obrigatórios e unidades dos indicadores.
- Escolha uma projeção adequada à região para operações planas; SIRGAS2000
  geográfico EPSG:4674 usa graus, enquanto uma zona UTM apropriada usa metros.

## Montagem do modelo

{lista_etapas(etapas)}

## Exemplo de configuração

```text
{exemplo}
```

## Critério específico de aceite

{aceite}

## Quadro para execução

| Registro | Preenchimento |
| --- | --- |
| Projeto / área / finalidade | [definir] |
| Dados e referências | [identificar arquivos e datas] |
| Parâmetros e tolerâncias | [valor, unidade e justificativa] |
| Produto esperado | [mapa, camada, relatório ou rotina] |
| Teste de conferência | [procedimento e resultado esperado] |
| Revisor / data / versão | [registrar] |

## Revisão antes de distribuir

- [ ] Reabrir o resultado exportado e verificar geometria, atributos e CRS.
- [ ] Conferir escala, legenda e fontes quando houver composição cartográfica.
- [ ] Registrar limitações e diferenças entre as fontes e a saída.
- [ ] Guardar o projeto e parâmetros usados, não apenas a imagem final.
- [ ] Confirmar que caminhos relativos funcionam numa cópia da pasta de entrega.

Não interprete aparência profissional como garantia de precisão. Compare valores
e relações com critérios mensuráveis e comunique o que não foi validado.

Referências: https://docs.qgis.org/3.44/en/docs/user_manual/ e
https://pro.arcgis.com/en/pro-app/latest/help/main/welcome-to-the-arcgis-pro-app-help.htm
'''


def portfolio(titulo, descricao, i):
    nome, objetivo, entradas, etapas, resultado = PORTFOLIOS[i]
    return cabecalho(titulo, descricao) + f'''## Caso demonstrativo: {nome}

Este é um roteiro técnico para construir um estudo de caso, não um relato de
cliente atendido nem uma promessa de desempenho. Dados e números de exemplo são
didáticos. Para divulgar um trabalho real, substitua-os por evidências autorizadas.

## Problema e proposta

**Objetivo:** {objetivo}

**Entradas:** {entradas}

Defina o destinatário, a pergunta analítica, o período e o uso esperado. Identifique
qual decisão o resultado pode apoiar e qual decisão exige informação adicional.

## Desenvolvimento documentado

{lista_etapas(etapas)}

## Resultado de referência e discussão

{resultado}

## Estrutura da apresentação

1. Contexto: área, período, pergunta e relevância do problema.
2. Dados: origem, limitações, unidades, CRS e permissão de divulgação.
3. Método: sequência de operações, parâmetros, versões e escolhas do autor.
4. Evidências: mapa, tabela, consulta, métrica ou execução com referência verificável.
5. Discussão: o que foi demonstrado, o que permanece incerto e alternativas.
6. Próximo passo: validação necessária ou evolução do projeto, sem garantia de ganho.

## Pacote mínimo para portfólio

| Entrega | O que comprovar |
| --- | --- |
| Resumo executivo | Problema e contribuição claramente identificados |
| Dados demonstrativos / links permitidos | Origem, data e condições de acesso |
| Método reproduzível | Entradas, etapas e parâmetros registrados |
| Evidências de resultado | Referência aos produtos e critérios de conferência |
| Limitações | Escala, precisão, amostragem e restrições de uso |

## Revisão profissional

- [ ] Distinguir trabalho próprio, colaboração e fontes externas.
- [ ] Remover identificadores pessoais ou dados confidenciais não autorizados.
- [ ] Explicar métricas, denominadores e comparação usada.
- [ ] Não converter observação ou correlação em prova de causalidade.
- [ ] Permitir que outra pessoa confira pelo menos uma conclusão pelos dados.

## Perguntas para entrevista ou reunião

Qual decisão técnica foi mais importante? Qual alternativa foi descartada e por
quê? Que evidência suporta a conclusão? O que mudaria com uma fonte de maior
precisão? Responda com fatos do projeto, evitando atribuir ganhos não medidos.
'''


def roadmap(titulo, descricao, i):
    area, marcos = TRILHAS[i]
    semanas = '\n\n'.join(f'''### Etapa {n}: {marco}

- **Estudo:** identifique conceitos, entradas e pressupostos desta competência.
- **Prática:** aplique o tema a uma cópia de dados demonstrativos e registre cada operação.
- **Entrega:** produza uma evidência de {marco.lower()}, com fonte e parâmetros.
- **Aceite:** explique o resultado e reproduza a etapa sem seguir uma sequência memorizada.
''' for n, marco in enumerate(marcos, 1))
    return cabecalho(titulo, descricao) + f'''## Trilha de {area}

Plano sugerido de oito etapas, adaptável à experiência e disponibilidade. Uma
etapa pode ocupar mais de uma semana; não avance apenas porque o prazo terminou.
A trilha é um roteiro de estudo, não certificação ou garantia de contratação.

## Pré-requisitos e organização

Identifique seu nível inicial e escolha um problema simples com dados autorizados.
Separe ambiente de trabalho, fontes, resultados e diário de aprendizagem. Reserve
tempo para revisão e registre dúvidas com exemplos reproduzíveis. Para operações
espaciais, confira CRS e unidades; para modelos, reserve dados de avaliação.

## Sequência de desenvolvimento

{semanas}

## Projeto integrador

Escolha uma pergunta coerente com {area} e conecte pelo menos quatro competências
da trilha. Entregue fontes identificadas, método, resultado verificável e limitações.
Apresente seu papel no trabalho e peça revisão de uma pessoa que possa conferir
uma operação ou conclusão. Não utilize dados sintéticos como evidência do mundo real.

## Rubrica de autoavaliação

| Dimensão | 0 — insuficiente | 1 — em progresso | 2 — demonstrado |
| --- | --- | --- | --- |
| Método | Não explicado | Parcialmente registrado | Reproduzível |
| Qualidade | Não conferida | Conferência parcial | Critérios e evidências |
| Comunicação | Resultado isolado | Contexto incompleto | Contexto, conclusão e limites |
| Autonomia | Apenas reproduz tutorial | Adapta com apoio | Resolve e justifica escolhas |

Revise lacunas por dimensão; a soma não equivale a certificado de competência.
Guarde versões e repita a atividade com outro conjunto pequeno para distinguir
compreensão de memorização. Atualize o plano conforme dificuldades observadas.
'''


def exercicio(titulo, descricao, i):
    tema, dados, etapas, resposta, exemplo = EXERCICIOS[i]
    return cabecalho(titulo, descricao) + f'''## Desafio: {tema}

Os dados e resultados de referência são sintéticos para treinamento. O objetivo é
verificar operações e raciocínio, não representar uma área ou fenômeno real.

## Dados de entrada

```text
{dados}
```

## Procedimento

{lista_etapas(etapas)}

## Apoio técnico

```text
{exemplo}
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

{resposta}

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
'''


def glossario(titulo, descricao, i):
    termos = '\n\n'.join(f'### {nome}\n\n{definicao}' for nome, definicao in GLOSSARIOS[i])
    return cabecalho(titulo, descricao) + f'''## Como consultar

Este glossário reúne doze conceitos e seus cuidados operacionais. As definições
são referências introdutórias para leitura e comunicação; consulte a documentação
da ferramenta e a metodologia do projeto para uma implementação específica.

## Conceitos e aplicação

{termos}

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
'''


def camada(geometrias, **campos):
    n = len(geometrias)
    return gpd.GeoDataFrame({'id': list(range(1,n+1)), 'fonte': ['simulacao_datageo']*n,
                            'sintetico': [1]*n, **campos}, geometry=geometrias, crs=CRS)


def gerar_base(path, titulo, descricao, i):
    quadrados = [box(X+a*1000,Y+b*1000,X+(a+1)*1000,Y+(b+1)*1000) for a in range(3) for b in range(3)]
    pontos = [Point(X+150+j*250, Y+150+(j%3)*300) for j in range(8)]
    textos = []
    if i == 0:
        dados = {'unidades': camada([box(X+k*1000,Y,X+(k+1)*1000,Y+3000) for k in range(3)], codigo=['D001','D002','D003'], nome=['Unidade A','Unidade B','Unidade C'], nivel=['demonstrativo']*3)}
        textos = ['Três unidades adjacentes de 300 ha cada; área total 900 ha.', 'Chave codigo é única. Use-a para junções, não fid ou ordem da tabela.']
    elif i == 1:
        dados = {'cobertura': camada(quadrados, classe=['vegetacao','urbanizado','agua']*3, area_ha=[100.0]*9, data_ref=['2025-01-01']*9)}
        textos = ['Nove células, três classes, 300 ha por classe e 900 ha ao todo.', 'A área_ha foi derivada da geometria métrica; recalcule após editar.']
    elif i == 2:
        dados = {'bacias': camada([box(X+k*1000,Y,X+(k+1)*1000,Y+3000) for k in range(3)], nome=['Bacia A','Bacia B','Bacia C']),
                 'drenagem': camada([LineString([(X+500,Y+2500),(X+1500,Y+1500)]),LineString([(X+2500,Y+2500),(X+1500,Y+1500)]),LineString([(X+1500,Y+1500),(X+1500,Y+100)])], de_no=[1,2,3], para_no=[3,3,4], ordem=[1,1,2])}
        textos = ['Dois trechos convergem no nó 3 e um segue até o nó 4.', 'Limites das bacias são esquemáticos, não derivados de terreno; não usar para modelagem hidrológica real.']
    elif i == 3:
        dados = {'equipamentos': camada(pontos, tipo=['saude','educacao','servico','agua']*2, capacidade=[10,20,30,40,15,25,35,45]),
                 'rede': camada([LineString([pontos[j],pontos[j+1]]) for j in range(7)], de_id=list(range(1,8)), para_id=list(range(2,9)), restricao=['nao_modelada']*7)}
        textos = ['Oito equipamentos e sete ligações entre IDs consecutivos.', 'Ligações não representam ruas ou tubulações reais; capacidade é uma unidade fictícia de exercício.']
    elif i == 4:
        dados = {'unidades': camada([box(X,Y,X+3000,Y+3000)], codigo=['D001'], nome=['Unidade demonstrativa']),
                 'ativos': camada(pontos, unidade_id=[1]*8, nome=[f'Ativo {k}' for k in range(1,9)])}
        textos = ['Protótipo portátil para planejar um banco PostGIS. GeoPackage não executa SQL PostGIS.', '''SQL para PostgreSQL com PostGIS instalado, em esquema de exercício novo:
CREATE TABLE unidades (id bigint PRIMARY KEY, codigo text UNIQUE NOT NULL, geom geometry(Polygon,31982));
CREATE TABLE ativos (id bigint PRIMARY KEY, unidade_id bigint REFERENCES unidades(id), nome text, geom geometry(Point,31982));
CREATE INDEX ativos_geom_gist ON ativos USING gist(geom);
SELECT u.id, count(a.id) FROM unidades u LEFT JOIN ativos a ON a.unidade_id=u.id GROUP BY u.id;
Não aplicar sem avaliar permissões, esquema de destino e CRS real.''']
    elif i == 5:
        dados = {'coletas': camada(pontos, data_ref=['2025-01-15']*8, classe=['solo','agua','vegetacao','infraestrutura']*2, observacao=['Registro didatico, sem vistoria real']*8, responsavel=['equipe_demo']*8)}
        textos = ['Oito observações com classes e datas fictícias.', 'Para campo, configure domínios, obrigatoriedade, formulário e regras de sincronização no aplicativo escolhido; este arquivo não configura aplicativo automaticamente.']
    elif i == 6:
        dados = {'pontos_interesse': camada(pontos, categoria=['saude','educacao','comercio','lazer']*2, nome=[f'POI demonstrativo {k}' for k in range(1,9)], data_ref=['2025-01-01']*8)}
        textos = ['Oito POIs: dois por categoria. Os nomes não representam estabelecimentos reais.', 'Analise proximidade em metros, mas não interprete distância euclidiana como tempo de viagem.']
    elif i == 7:
        dados = {'inventario': camada(pontos, grupo=['vegetacao','solo','agua','vegetacao','solo','agua','vegetacao','solo'], observacao=['Evidencia sintetica para pratica']*8, data_ref=['2025-02-01']*8),
                 'limite': camada([box(X,Y,X+3000,Y+3000)], nome=['Limite de exercício'])}
        textos = ['Oito registros: vegetação=3, solo=3, água=2; todos dentro do limite.', 'Sem amostragem de campo ou identificação de espécie; não inferir abundância, qualidade ambiental ou conformidade.']
    elif i == 8:
        dados = {'setores': camada(quadrados[:4], codigo=['S001','S002','S003','S004'], populacao=[2000,4000,3000,1000], equipamentos=[2,2,3,1], renda_media=[1800.0,2200.0,1500.0,2800.0], data_ref=['2025-01-01']*4)}
        textos = ['Quatro setores, população total fictícia 10.000, oito equipamentos.', 'Taxas por mil: 1, 0,5, 1 e 1. Renda em unidade monetária fictícia; não representa estatística oficial.']
    else:
        geoms = [Point(X+500+est*1000,Y+500) for est in range(2) for mes in range(1,13)]
        dados = {'observacoes': camada(geoms, estacao=[f'E{est+1}' for est in range(2) for _ in range(12)], data_ref=[f'2025-{mes:02d}-01' for _ in range(2) for mes in range(1,13)], valor=[10.0+est*2+mes for est in range(2) for mes in range(1,13)], unidade=['unidade_demo']*24),
                 'estacoes': camada([Point(X+500,Y+500),Point(X+1500,Y+500)], codigo=['E1','E2'])}
        textos = ['Duas estações, doze meses cada, 24 observações. Chave lógica: estação + data.', 'Repetição de coordenadas é legítima na série. E1 varia de 11 a 22 e E2 de 13 a 24; não é medição ambiental real.']
    documentacao = cabecalho(titulo, descricao) + '''## Natureza dos dados

DADOS SINTÉTICOS PARA EXERCÍCIOS. Geometrias e atributos foram gerados por código,
sem levantamento, fonte cadastral, cliente, inventário de campo ou base oficial.
As coordenadas usam SIRGAS 2000 / UTM 22S (EPSG:31982), unidade metro, apenas para
uma demonstração consistente. A localização numérica não atribui realidade ao conteúdo.
Não usar para licenciamento, cadastro, decisão operacional ou laudo sobre local real.

## Conteúdo específico e resultados de referência

''' + '\n\n'.join(textos) + '\n\n## Camadas e dicionário de atributos\n\n'
    for nome, df in dados.items():
        df.to_file(path, layer=nome, driver='GPKG', engine='pyogrio', index=False)
        documentacao += f'### {nome}\n\nFeições: {len(df)}. Geometria: {df.geom_type.iloc[0]}.\n\n'
        documentacao += '| Campo | Tipo / significado |\n| --- | --- |\n'
        for coluna in df.columns:
            if coluna != 'geometry':
                documentacao += f'| {coluna} | {df[coluna].dtype}; ' + ('1 = dado sintético' if coluna == 'sintetico' else 'origem artificial' if coluna == 'fonte' else 'identificador estável da camada' if coluna == 'id' else f'exemplo: {df[coluna].iloc[0]}') + ' |\n'
    documentacao += '''
## Abrir e praticar

1. Abra as camadas do GeoPackage no QGIS ou ArcGIS Pro; confirme EPSG:31982.
2. Consulte material_leia_me com o gerenciador de banco ou leitor SQLite.
3. Trabalhe numa cópia; preserve a fonte e confira os resultados de referência.
4. Registre parâmetros, predicados espaciais e unidades de área/distância.
5. Reabra a saída exportada e compare contagem, geometria e atributos.

## Validação e limitações

Verifique IDs únicos por camada, geometrias válidas e ausência de coordenadas
vazias. Campo sintetico=1 e fonte=simulacao_datageo identificam cada feição.
Tabelas relacionadas não têm necessariamente restrições SQL implementadas;
confira vínculos antes de inserir dados. Não substitua CRS por metadados sem
transformação quando integrar novas fontes. Indicadores armazenados precisam
ser recalculados após mudanças de geometria ou atributos.

Referências: https://www.geopackage.org/spec140/ e
https://geopandas.org/en/stable/docs/user_guide/io.html
'''
    with sqlite3.connect(path) as con:
        con.execute('CREATE TABLE material_leia_me (id INTEGER PRIMARY KEY, titulo TEXT NOT NULL, conteudo TEXT NOT NULL)')
        con.execute('INSERT INTO material_leia_me VALUES (1,?,?)', (titulo, documentacao))
        con.execute("INSERT INTO gpkg_contents (table_name,data_type,identifier,description,last_change) VALUES ('material_leia_me','attributes','Documentação do material','Guia em português; dados sintéticos',strftime('%Y-%m-%dT%H:%M:%fZ','now'))")
        con.execute('CREATE TABLE material_dicionario (id INTEGER PRIMARY KEY, camada TEXT, campo TEXT, tipo TEXT, exemplo TEXT)')
        n=0
        for nome, df in dados.items():
            for coluna in df.columns:
                if coluna != 'geometry':
                    n+=1
                    con.execute('INSERT INTO material_dicionario VALUES (?,?,?,?,?)',(n,nome,coluna,str(df[coluna].dtype),str(df[coluna].iloc[0])))
        con.execute("INSERT INTO gpkg_contents (table_name,data_type,identifier,description,last_change) VALUES ('material_dicionario','attributes','Dicionário de campos','Esquema e exemplos por camada',strftime('%Y-%m-%dT%H:%M:%fZ','now'))")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--substituir', action='store_true', help='Recriar explicitamente os arquivos conhecidos do catálogo.')
    args = parser.parse_args()
    html_path = ROOT / 'index.html'
    html = html_path.read_text(encoding='utf-8')
    pattern = r'<details class="premium-collection" id="premium-([^"]+)".*?</details>'
    grupos = list(re.finditer(pattern, html, re.S))
    assert len(grupos) == 6
    plano=[]
    for grupo in grupos:
        chave=grupo.group(1)
        cards=list(re.finditer(r'<article class="premium-card premium-library-card">.*?</article>', grupo.group(), re.S))
        assert len(cards)==10
        for i, card in enumerate(cards):
            titulo=limpar(re.search(r'<h4>(.*?)</h4>',card.group(),re.S).group(1))
            descricao=limpar(re.search(r'<p>(.*?)</p>',card.group(),re.S).group(1))
            ext='.gpkg' if chave=='bases' else '.txt' if chave=='templates' else '.md'
            path=ROOT/FOLDERS[chave]/f'{i+1:02d}_{slug(titulo)}{ext}'
            if path.exists() and not args.substituir:
                raise FileExistsError(f'{path}: use --substituir se deseja recriar.')
            plano.append((chave,i,titulo,descricao,path,card.group()))
    for chave,i,titulo,descricao,path,card in plano:
        path.parent.mkdir(exist_ok=True)
        if chave=='bases':
            if path.exists():
                path.unlink()  # Caminho explícito dentro de bancos_dados, já validado no plano.
            gerar_base(path,titulo,descricao,i)
        else:
            func={'templates':template,'portfolio':portfolio,'roadmaps':roadmap,'exercicios':exercicio,'glossarios':glossario}[chave]
            path.write_text(func(titulo,descricao,i),encoding='utf-8')
        href='./'+path.relative_to(ROOT).as_posix()
        tipo='GeoPackage · dados sintéticos' if chave=='bases' else 'Modelo técnico · TXT' if chave=='templates' else 'Guia técnico · Markdown'
        novo=re.sub(r'<span class="premium-availability">.*?</span>',f'<span class="premium-availability">{tipo}</span>',card,flags=re.S)
        novo=re.sub(r'<a class="button primary premium-download".*?</a>',
            f'<a class="button primary premium-download" href="{escape(href,quote=True)}" download="{escape(path.name,quote=True)}" aria-label="Baixar Material Now: {escape(titulo,quote=True)}">Baixar Material Now <span aria-hidden="true">↓</span></a>',novo,flags=re.S)
        html=html.replace(card,novo,1)
    html=html.replace('60 propostas de materiais em seis coleções.','60 materiais para download em seis coleções.')
    html=html.replace('<strong>60</strong> temas para explorar','<strong>60</strong> materiais para baixar')
    html=html.replace('<strong>8</strong> downloads disponíveis','<strong>68</strong> downloads disponíveis')
    html=html.replace('Explore os temas e consulte a disponibilidade de cada material pelo WhatsApp.',
        'Escolha um material e baixe o arquivo diretamente. Modelos e guias têm instruções em português; as bases usam dados sintéticos para exercícios.')
    html=html.replace('Os seis kits Python, o template Word e o checklist têm arquivos para download imediato. As coleções apresentam temas de materiais; consulte a disponibilidade pelo WhatsApp antes de contratar. <a href="#contato">Fale com a DataGeo Academy</a>.',
        'Download direto: 60 materiais nas coleções, seis kits Python, um template Word e um checklist. Os modelos TXT são guias de configuração; os GeoPackages contêm dados sintéticos e documentação interna para exercícios. Guarde uma cópia antes de editar.')
    html_path.write_text(html,encoding='utf-8')
    print('Criados 60 arquivos e conectados 60 downloads diretos.')


if __name__=='__main__':
    main()
