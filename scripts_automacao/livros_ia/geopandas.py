"""Manuscrito e doze laboratórios originais de GeoPandas."""
from .estrutura import cap

TITULO = 'Ciência de Dados Espaciais com GeoPandas'
DESCRICAO = 'Operações vetoriais com GeoPandas: projeções, joins, overlays, interpolação areal e entrega em GeoPackage.'
DEPENDENCIAS = ['geopandas>=1.0,<2', 'shapely>=2,<3', 'pyogrio>=0.10,<1', 'pandas>=2.2,<4']
INTRO = [
    'Uma tabela espacial não é apenas uma tabela com coordenadas. A geometria estabelece relações de vizinhança, contenção e interseção; o sistema de referência estabelece a interpretação de distâncias e áreas. Este livro desenvolve um fluxo vetorial completo, da leitura de atributos até a entrega de um GeoPackage auditável. A biblioteca GeoPandas é usada diretamente em todos os laboratórios: nenhuma operação espacial é substituída por uma soma genérica.',
    'O caso de estudo é a distribuição de infraestrutura entre setores de planejamento. Os dados são pequenos e sintéticos para que áreas, contagens e interseções possam ser conferidas manualmente. A partir dessa base, o leitor aprende a distinguir atribuição cadastral, proximidade e interpolação areal. Essas perguntas têm suportes diferentes e não devem receber a mesma solução apenas porque todas envolvem um mapa.',
    'A sequência começa pelo contrato tabular e pela geometria ativa; avança por projeções, validação, joins e overlays; termina em agregação, ponderação e persistência. Cada laboratório é independente e contém uma asserção ligada ao resultado esperado. Execute os anexos em um ambiente virtual, compare a saída com o PDF e altere uma hipótese por vez. O comportamento nas bordas recebe atenção especial porque produz erros silenciosos em projetos reais.',
    'Os exemplos em metros usam EPSG:31982, SIRGAS 2000 / UTM 22S. Coordenadas retangulares simplificadas não representam um município real. No capítulo de transformação, longitude e latitude são plausíveis para a região de Florianópolis. Um CRS numericamente válido não prova a origem da coordenada: metadados de levantamento e precisão precisam acompanhar a base utilizada em produção.',
    'Ao concluir, o leitor deverá entregar código reproduzível, inventário dos dados, critérios de validação e um arquivo espacial reaberto com sucesso. O objetivo não é memorizar chamadas de API, mas compreender qual relação espacial cada chamada calcula, quais registros podem desaparecer e quais totais precisam ser conservados.'
]
REFERENCIAS = [
 'https://geopandas.org/en/stable/docs/user_guide/data_structures.html',
 'https://geopandas.org/en/stable/docs/user_guide/projections.html',
 'https://geopandas.org/en/stable/docs/user_guide/mergingdata.html',
 'https://geopandas.org/en/stable/docs/user_guide/set_operations.html',
 'https://geopandas.org/en/stable/docs/user_guide/spatial_indexing.html',
 'https://shapely.readthedocs.io/en/stable/reference/shapely.make_valid.html'
]
PROJETO = 'Construir um inventário de equipamentos por setor, medir cobertura de atendimento de 100 metros, distribuir população por interseção areal e entregar um GeoPackage com setores, equipamentos e indicadores. Compare contagem por contenção com contagem por interseção; declare explicitamente o tratamento de equipamentos na divisa.'
CAPITULOS = [
cap('Contrato tabular e geometria ativa', '''Um GeoDataFrame combina índices, atributos e uma coluna de geometria ativa. A existência de uma coluna chamada geometry não garante que todos os elementos sejam válidos ou do mesmo tipo. O contrato de entrada deve identificar chave primária, unidade de observação, campos obrigatórios, CRS e domínios. Um equipamento duplicado na tabela pode ser contado duas vezes mesmo que as geometrias sejam perfeitas.

A validação de atributos precede a análise espacial. Chaves únicas permitem rastrear o resultado de joins; domínios restringem categorias; valores ausentes precisam ser distinguidos de zero. A geometria ativa determina qual coluna participa de area, buffer e sjoin. É possível manter uma segunda geometria, como centroide, mas alterná-la sem registro modifica o significado do cálculo.

O índice do pandas não substitui automaticamente o identificador de negócio. Depois de concatenar ou explodir feições, índices podem repetir. Preserve uma chave estável e use validações explícitas. No exemplo, duas escolas sintéticas recebem identificadores próprios e um campo capacidade inteiro. A asserção protege contra duplicação; a coluna de geometria fica vinculada a um CRS métrico antes de qualquer distância.''', '''
import geopandas as gpd
from shapely.geometry import Point
g = gpd.GeoDataFrame(
    {'id': [1, 2], 'tipo': ['escola', 'escola'],
     'capacidade': [120, 180]},
    geometry=[Point(500000, 6900000),
              Point(500100, 6900000)], crs=31982)
assert g['id'].is_unique and not g.geometry.isna().any()
assert (g['capacidade'] > 0).all()
assert g.geometry.name == 'geometry'
RESULTADO = {'n': len(g), 'capacidade': int(g.capacidade.sum()),
             'epsg': g.crs.to_epsg()}
print(RESULTADO)
''', [('Chave', 'id único', 'Duplicação altera a contagem'), ('Domínio', 'capacidade positiva', 'Ausência não equivale a zero'), ('Geometria', 'Point não nulo', 'Tipo incompatível interrompe o fluxo'), ('CRS', 'EPSG:31982', 'Unidade da coordenada é metro')],
'Insira uma terceira linha com id=2 e capacidade=-10. Escreva um validador que acumule os dois problemas em uma lista, em vez de interromper na primeira asserção. Depois adicione uma geometria alternativa de buffer e comprove qual coluna está ativa antes e depois de set_geometry.',
'O conjunto original soma 300 vagas e contém dois registros. A nova linha viola unicidade e positividade; são falhas independentes. Use duplicated(keep=False) para localizar todos os IDs envolvidos e uma máscara capacidade<=0 para os valores inválidos. A troca da geometria ativa não altera os atributos, mas modifica operações geométricas subsequentes; registre o nome antigo e o novo.',
'Defina um esquema de entrada com tipo de cada campo, domínio e regra de ausência. Teste uma tabela vazia e um id nulo: is_unique sozinho não impede uma chave ausente. Rejeite a base antes de produzir indicadores e preserve um arquivo de diagnóstico com os registros recusados.',
'Verifique unicidade, nulidade, geometria ativa e CRS separadamente; o resultado esperado do laboratório é n=2, capacidade=300 e epsg=31982.'),
cap('Referência espacial, transformação e escala', '''set_crs e to_crs resolvem problemas diferentes. O primeiro atribui a interpretação de coordenadas existentes; o segundo transforma números a partir de uma referência conhecida. Atribuir UTM a números em graus não reprojeta a base: apenas produz coordenadas falsas com aparência métrica. O erro pode atravessar toda a cadeia sem lançar uma exceção.

EPSG:4674 descreve SIRGAS 2000 geográfico, com coordenadas angulares. EPSG:31982 descreve SIRGAS 2000 / UTM zona 22 sul, apropriado para cálculos locais dentro de sua zona. Não existe uma única projeção ideal para qualquer extensão. Para bases continentais, a distorção e as zonas exigem uma decisão cartográfica explícita. Área e distância em GeoPandas são operações planas na unidade do CRS.

O laboratório transforma dois pontos próximos de Florianópolis e calcula sua distância projetada. A verificação de ida e volta permite detectar troca de longitude com latitude e perda grosseira de precisão, mas não demonstra acurácia de levantamento. O intervalo plausível de distância é uma segunda defesa. Em dados reais, confronte pontos de controle e documente datum, época, origem e tolerância.''', '''
import geopandas as gpd
from shapely.geometry import Point
g = gpd.GeoDataFrame({'id': [1, 2]},
    geometry=[Point(-48.55, -27.60), Point(-48.549, -27.60)],
    crs=4674)
utm = g.to_crs(31982)
dist = utm.geometry.iloc[0].distance(utm.geometry.iloc[1])
volta = utm.to_crs(4674)
assert volta.geometry.iloc[0].distance(g.geometry.iloc[0]) < 1e-8
assert 90 < dist < 110
RESULTADO = {'distancia_m': round(dist, 3),
             'crs_destino': utm.crs.to_epsg()}
print(RESULTADO)
''', [('set_crs', 'Atribuir metadado conhecido', 'Não modifica números'), ('to_crs', 'Transformar coordenadas', 'Exige referência de origem'), ('EPSG:4674', 'Longitude e latitude', 'Não usar area como hectares'), ('EPSG:31982', 'UTM 22S em metros', 'Aplicação regional')],
'Calcule a distância depois de atribuir erroneamente EPSG:31982 aos números originais. Compare essa medida com a transformação correta. Em seguida, repita o ensaio com latitude=-10 e explique por que a comparação em metros continua exigindo análise da zona e da distorção.',
'A atribuição incorreta fornece 0,001 como se fosse metro, quando a diferença original representa um milésimo de grau. A reprojeção correta produz uma distância próxima de 99 metros na latitude usada. A ida e volta confirma consistência matemática, não a veracidade do datum informado. Distâncias em regiões diferentes não devem ser comparadas sem avaliar a adequação da projeção.',
'Implemente uma regra de plausibilidade para bounds: longitude entre -180 e 180, latitude entre -90 e 90 e coordenadas UTM em faixa coerente. Essas regras detectam alguns erros, mas não autorizam inferir um CRS desconhecido. Mantenha a entrada sem análise quando a referência não puder ser comprovada.',
'Confirme que nenhum aviso de cálculo em CRS geográfico aparece e que a reprojeção usa to_crs; não utilize allow_override para disfarçar metadados incompatíveis.'),
cap('Qualidade geométrica e reparo controlado', '''Geometrias ausentes, vazias e inválidas constituem três estados distintos. Uma geometria ausente não foi fornecida; uma vazia existe sem coordenadas; uma inválida viola regras do modelo geométrico. Um polígono que cruza a si mesmo pode gerar área inesperada ou falhar no overlay. Filtrar todos esses estados como se fossem a mesma coisa perde informação útil para a revisão.

make_valid tenta produzir uma geometria válida, mas não adivinha a intenção do levantamento. Um polígono em laço pode virar MultiPolygon ou GeometryCollection. O resultado exige revisão de tipo, número de partes e área. Aplicar buffer(0) indiscriminadamente como cura universal é inadequado quando a posição e a topologia têm relevância cadastral.

O exemplo usa um polígono autointersectante de dois triângulos. A forma reparada é válida e sua área é mensurável, porém a decisão de manter as duas partes depende da finalidade. Antes de substituir a geometria original, guarde seu WKT, o diagnóstico e a alteração de área. A ordem das operações também importa: simplificar antes de validar pode esconder uma falha em vez de explicá-la.''', '''
import geopandas as gpd
from shapely.geometry import Polygon
from shapely import make_valid
ruim = Polygon([(0,0), (100,100), (0,100),
                (100,0), (0,0)])
g = gpd.GeoDataFrame({'id': [1]}, geometry=[ruim], crs=31982)
assert not g.geometry.is_valid.iloc[0]
reparada = make_valid(ruim)
assert reparada.is_valid and not reparada.is_empty
assert abs(reparada.area - 5000) < 1e-8
RESULTADO = {'tipo': reparada.geom_type,
             'area_reparada_m2': reparada.area,
             'partes': len(reparada.geoms)}
print(RESULTADO)
''', [('Ausente', 'isna', 'Solicitar ou excluir com justificativa'), ('Vazia', 'is_empty', 'Não confundir com atributo ausente'), ('Inválida', 'is_valid=False', 'Diagnosticar antes de reparar'), ('Reparada', 'make_valid', 'Revisar tipo e área resultantes')],
'Crie uma tabela com um polígono válido, o laço do exemplo, None e Polygon(). Classifique cada linha antes do reparo. Extraia as partes poligonais da geometria reparada sem descartar silenciosamente componentes de outra dimensão.',
'O laço reparado tem dois triângulos que totalizam 5.000 m². A área original calculada como zero não é um denominador confiável para uma taxa percentual de mudança: registre diferença absoluta e estado inválido. None e Polygon() precisam de diagnósticos distintos. Uma GeometryCollection demanda uma política de seleção de componentes que preserve o registro de tudo o que foi retirado.',
'Construa um relatório com id, motivo, tipo antes, tipo depois, área depois e decisão de revisão. Teste o fluxo com uma coleção de linhas e polígonos. O reparo só deve entrar na base operacional quando o tipo final cumprir o contrato e a alteração tiver sido aceita.',
'Confirme validade, área de 5.000 m² e duas partes. Não trate sucesso do algoritmo como confirmação de consistência territorial.'),
cap('Exploração espacial sem confundir suporte', '''Estatísticas de atributos e estatísticas espaciais respondem a perguntas diferentes. A média simples da densidade entre setores atribui peso igual a cada setor; a densidade da região corresponde à soma da população dividida pela soma da área. Em territórios com áreas desiguais, os dois números divergem de maneira legítima. A escolha deve acompanhar a unidade de análise.

Um centroide resume a geometria, mas pode cair fora de um polígono côncavo. representative_point retorna um ponto interno e é útil para rótulos, sem representar o centro de massa. Bounds descrevem a extensão retangular e ajudam a detectar coordenadas anômalas. Nenhuma dessas medidas substitui um teste de associação espacial, como autocorrelação, ou uma hipótese sobre distribuição populacional.

O laboratório contrasta média simples e densidade regional em dois setores retangulares. O segundo setor tem o dobro da área e quatro vezes a população. O cálculo deixa visível o efeito dos pesos. Antes de gerar um dashboard, apresente numerador e denominador ao lado do indicador; arredondamento de densidades intermediárias não deve contaminar o total.''', '''
import geopandas as gpd
from shapely.geometry import box
g = gpd.GeoDataFrame({'id':[1,2], 'pop':[100,400]},
    geometry=[box(0,0,100,100), box(100,0,300,100)], crs=31982)
g['ha'] = g.area / 10000
g['densidade'] = g['pop'] / g['ha']
regional = g['pop'].sum() / g['ha'].sum()
simples = g['densidade'].mean()
assert abs(regional - 500/3) < 1e-8
assert simples == 150
RESULTADO = {'media_setores': simples,
             'densidade_regional': round(regional, 3),
             'bounds': g.total_bounds.tolist()}
print(RESULTADO)
''', [('Média simples', '(100+200)/2', '150 hab/ha'), ('Densidade regional', '500/3', '166,667 hab/ha'), ('Área', '1 ha e 2 ha', 'Peso espacial desigual'), ('Ponto interno', 'representative_point', 'Apoio à rotulagem')],
'Divida o setor de 2 hectares em duas partes iguais, cada uma com 200 habitantes. Recalcule a média simples e a densidade regional. Explique por que a média simples mudou mesmo sem mudança territorial ou populacional.',
'A média das três densidades passa para (100+200+200)/3=166,667, enquanto a densidade regional permanece 500/3. O indicador não ponderado depende da partição. Esse exemplo materializa o problema do suporte e da unidade espacial modificável: subdividir feições muda a contribuição de cada unidade à média. Não atribua a mudança a um fenômeno demográfico.',
'Adicione um setor com população desconhecida. Calcule cobertura populacional e espacial dos registros conhecidos antes de divulgar a densidade agregada. O valor zero só representa ausência de moradores quando a fonte o afirma; não deve servir como preenchimento automático de missing.',
'Conserve população total de 500 e área total de 3 hectares durante a subdivisão. Declare claramente se o indicador representa setores ou a população regional.'),
cap('Junção espacial e regras de fronteira', '''sjoin combina atributos segundo um predicado geométrico. within exige interior estrito do polígono para um ponto; intersects inclui a fronteira. Um ponto na divisa de dois setores pode ser associado a ambos por intersects. Esse resultado não é duplicação acidental do algoritmo: é consequência da relação escolhida e precisa de uma regra de negócio.

O tipo de join controla quais linhas sobrevivem. Em um left join, pontos sem correspondência permanecem com atributos nulos do setor. Em um inner join, desaparecem. Contar linhas após um join sem verificar a multiplicidade das chaves pode superestimar equipamentos. A relação um-para-muitos é válida em algumas análises, mas incompatível com atribuição exclusiva sem desempate.

Neste laboratório, três pontos representam interior, fronteira compartilhada e exterior. A comparação entre within e intersects revela o caso ambíguo. Uma política cadastral poderia usar setor oficial de origem; um desempate técnico poderia usar menor identificador com justificativa. Não mova a coordenada alguns centímetros apenas para evitar a discussão sobre bordas.''', '''
import geopandas as gpd
from shapely.geometry import box, Point
setores = gpd.GeoDataFrame({'setor':['A','B']},
    geometry=[box(0,0,100,100), box(100,0,200,100)], crs=31982)
pontos = gpd.GeoDataFrame({'id':[1,2,3]},
    geometry=[Point(50,50), Point(100,50), Point(250,50)],
    crs=31982)
inter = gpd.sjoin(pontos, setores, how='left', predicate='intersects')
interno = gpd.sjoin(pontos, setores, how='left', predicate='within')
assert len(inter[inter.id==2]) == 2
assert interno.loc[interno.id==2, 'setor'].isna().all()
RESULTADO = {'linhas_intersects':len(inter),
             'sem_setor_within':int(interno.setor.isna().sum())}
print(RESULTADO)
''', [('within', 'Interior estrito', 'Fronteira fica sem correspondência'), ('intersects', 'Contato ou interior', 'Pode associar dois setores'), ('left', 'Preservar equipamentos', 'Mantém os não associados'), ('inner', 'Só correspondências', 'Pode esconder ausência de cobertura')],
'Implemente uma atribuição exclusiva: mantenha todos os IDs, marque pontos ambíguos e escolha o menor código de setor apenas para os ambíguos. Informe contagem por setor antes e depois do desempate, além do número de pontos externos.',
'intersects produz quatro linhas porque o ponto 2 aparece duas vezes e o ponto 3 continua sem setor. within deixa dois pontos sem setor, o da fronteira e o externo. Ordenar por id e setor e remover duplicatas oferece um desempate determinístico, mas a coluna de ambiguidade deve ser calculada antes da remoção. O ponto externo continua nulo; inventar um setor alteraria o contrato.',
'Teste uma linha que toca três polígonos e uma base de setores sobrepostos. Diferencie ambiguidade por fronteira de ambiguidade por erro topológico. Para contagens exclusivas, use a chave do equipamento e verifique que a soma dos atribuídos mais os não atribuídos retorna o total original.',
'Mantenha três IDs na saída exclusiva e registre uma ambiguidade. A escolha do predicado deve aparecer no relatório.'),
cap('Overlay e conservação de áreas', '''Enquanto sjoin transfere atributos mantendo a geometria da esquerda, overlay cria geometrias resultantes das operações de conjunto. intersection recorta a porção comum; difference retira uma região; union conserva partes de ambos os conjuntos. Essa distinção é essencial quando a análise pede hectares de cobertura, em vez de uma simples associação entre atributos.

A conservação de área funciona como teste de coerência: para um polígono A e uma máscara B, área de A intersectado com B somada à área de A menos B deve recuperar a área de A, dentro da tolerância numérica. A identidade pode falhar no fluxo se partes forem descartadas, CRS forem diferentes ou geometrias inválidas forem reparadas sem revisão.

O exemplo divide um setor de 20.000 m² por uma máscara que cobre metade dele. O laboratório usa keep_geom_type=True para conservar apenas partes poligonais. Em interseções que geram linhas de fronteira, essa opção pode remover resultados de dimensão inferior; isso é adequado para medir área, mas precisa ser explícito. Tolerâncias devem depender da unidade e precisão, não de um número mágico universal.''', '''
import geopandas as gpd
from shapely.geometry import box
a = gpd.GeoDataFrame({'id':[1]},
    geometry=[box(0,0,200,100)], crs=31982)
b = gpd.GeoDataFrame({'zona':['Z']},
    geometry=[box(100,-20,250,120)], crs=31982)
dentro = gpd.overlay(a,b,how='intersection',keep_geom_type=True)
fora = gpd.overlay(a,b,how='difference',keep_geom_type=True)
ai, af = dentro.area.sum(), fora.area.sum()
assert abs(ai + af - a.area.sum()) < 1e-6
RESULTADO = {'intersecao_m2':float(ai),
             'restante_m2':float(af), 'fracao':float(ai/a.area.sum())}
print(RESULTADO)
''', [('sjoin', 'Mantém geometria da esquerda', 'Associação de atributos'), ('intersection', 'Parte comum', 'Cobertura mensurada'), ('difference', 'Parte fora da máscara', 'Área remanescente'), ('Conservação', 'Dentro + fora = origem', 'Teste numérico')],
'Acrescente uma segunda máscara parcialmente sobreposta à primeira. Compare a soma das áreas das interseções individuais com a interseção da união das máscaras. Explique como evitar contar a região sobreposta duas vezes.',
'No exemplo original, dentro e fora têm 10.000 m² cada e a fração é 0,5. Com duas máscaras sobrepostas, somar interseções individuais pode contar a mesma parcela duas vezes. Unifique as geometrias das máscaras antes da interseção quando o objetivo for cobertura total sem dupla contagem. Mantenha as interseções separadas quando a pergunta pedir presença de cada categoria.',
'Calcule área de cobertura por categoria e área exclusiva entre categorias. Produza uma tabela com total bruto, sobreposição e total único. Use geometrias válidas e um mesmo CRS, depois teste conservação também no limite onde a máscara apenas toca a borda do setor.',
'Verifique 20.000 m² na origem e 50% de cobertura. Não utilize número de linhas resultantes como aproximação de área.'),
cap('Buffers, união e cobertura de atendimento', '''Um buffer é uma região definida pela distância euclidiana em um CRS plano. Ao redor de pontos, aproxima um círculo por segmentos; ao redor de linhas, cria um corredor cujas extremidades e junções dependem das opções. Essa região não equivale automaticamente a tempo de viagem, acessibilidade em rede ou área de serviço de uma escola.

Buffers de equipamentos próximos se sobrepõem. Somar suas áreas responde à soma da capacidade geométrica individual, enquanto medir a área da união responde à cobertura territorial única. Para percentuais por setor, a sequência adequada é gerar buffers, unir quando a pergunta exigir cobertura única, intersectar com setores e dividir pela área de cada setor.

O laboratório usa dois pontos separados por 100 metros e raio de 100 metros. A área da união deve ser inferior à soma dos círculos e superior à área de um círculo. quad_segs controla a discretização; aumentar o valor reduz erro geométrico e eleva o custo. Uma análise operacional deve acrescentar restrições de circulação, barreiras e capacidade, em vez de comunicar o buffer como acesso efetivo.''', '''
import geopandas as gpd
from shapely.geometry import Point
g = gpd.GeoDataFrame({'id':[1,2]},
    geometry=[Point(0,0), Point(100,0)], crs=31982)
buffers = g.geometry.buffer(100, quad_segs=32)
uniao = buffers.union_all()
bruta = buffers.area.sum()
unica = uniao.area
assert buffers.area.iloc[0] < unica < bruta
RESULTADO = {'area_bruta_m2':round(bruta,2),
             'area_unica_m2':round(unica,2),
             'sobreposicao_m2':round(bruta-unica,2)}
print(RESULTADO)
''', [('Raio', '100 metros', 'Proximidade plana'), ('quad_segs', '32 por quadrante', 'Aproximação do arco'), ('Soma', 'Áreas individuais', 'Inclui repetição na sobreposição'), ('União', 'Cobertura única', 'Remove dupla contagem')],
'Repita o cálculo com quad_segs=4, 16 e 64. Compare a área de um buffer com pi*100² e quantifique o erro relativo. Depois afaste o segundo ponto para 250 metros e teste se a sobreposição desaparece.',
'A área poligonal fica abaixo da área ideal do círculo, convergindo com maior discretização. A 250 metros de separação, os círculos de raio 100 não se sobrepõem; a união recupera a soma das áreas dentro da precisão numérica. O parâmetro melhora a aproximação geométrica, mas não transforma distância euclidiana em distância de rede.',
'Recorte a união em três setores e verifique que a soma das áreas recortadas coincide com a cobertura dentro da região, quando os setores formam uma partição sem sobreposição. Mantenha separadas cobertura geométrica e número de pessoas atendidas.',
'Confronte soma e união, documente a discretização e evite percentuais acima de 100% quando a finalidade for cobertura territorial única.'),
cap('Dissolve, agregação e pesos territoriais', '''dissolve realiza uma união de geometrias por grupo e agrega atributos com regras explícitas. A operação espacial e a tabular precisam ser planejadas em conjunto. Somar população normalmente faz sentido; somar densidade normalmente não. Para calcular densidade agregada, transporte numerador e denominador e derive o indicador após a agregação.

O comportamento default de agregação não conhece a semântica de cada coluna. Uma categoria textual pode usar first, mas isso é incorreto se o grupo contém valores conflitantes. Registre cardinalidade e regras por atributo. O índice resultante pode conter o código de grupo; as_index=False preserva esse identificador como coluna e facilita a exportação.

No laboratório, dois setores da região A são unidos e um setor da região B permanece separado. A soma da população deve continuar 600; a área da região A passa a 20.000 m². Se os setores se sobrepuserem, a união reduz a área total enquanto a população continua sendo somada; a densidade resultante ficaria artificialmente elevada. Testes topológicos, portanto, antecedem agregações demográficas.''', '''
import geopandas as gpd
from shapely.geometry import box
g = gpd.GeoDataFrame({'regiao':['A','A','B'],
    'pop':[100,200,300]}, geometry=[box(0,0,100,100),
    box(100,0,200,100),box(200,0,300,100)], crs=31982)
r = g.dissolve(by='regiao', aggfunc={'pop':'sum'}, as_index=False)
r['ha'] = r.area/10000
r['densidade'] = r['pop']/r['ha']
assert r['pop'].sum() == 600 and len(r)==2
assert r.loc[r.regiao=='A','ha'].iloc[0] == 2
RESULTADO = r[['regiao','pop','ha','densidade']].to_dict('records')
print(RESULTADO)
''', [('População', 'sum', 'Grandeza extensiva'), ('Densidade', 'Recalcular após dissolve', 'Grandeza intensiva'), ('Categoria', 'Verificar conflitos', 'first pode ocultar divergência'), ('Geometria', 'União por grupo', 'Sobreposição altera área')],
'Inclua um campo renda_media com valores 1.000, 2.000 e 3.000. Calcule renda média regional ponderada por população e compare com a média simples para a região A. Não some rendas médias.',
'Para A, a renda ponderada é (100*1000+200*2000)/300=1.666,667, enquanto a média simples é 1.500. Crie previamente o produto renda_media*pop, agregue esse total e divida pela população agregada. Se houver população zero ou renda ausente, a política de denominador precisa ser revista. As densidades regionais originais são 150 hab/ha em A e 300 hab/ha em B.',
'Adicione um atributo de fonte e teste se cada região contém uma única fonte. Caso haja mais de uma, produza uma lista de proveniências ou uma tabela relacionada. Não descarte metadados apenas porque não cabem no esquema de agregação inicial.',
'Confirme conservação de população, grupos esperados e regra de agregação por atributo. Recalcule intensivos a partir de seus componentes.'),
cap('Índice espacial e seleção de candidatos', '''O índice espacial reduz o número de pares candidatos; ele não altera a definição geométrica da pergunta. A busca por envelopes retangulares pode retornar candidatos que não satisfazem uma relação exata. GeoPandas permite informar um predicado para refinar o resultado. Essa distinção ajuda a compreender por que uma consulta pode retornar muitos candidatos em geometrias extensas e sinuosas.

O ganho depende da distribuição espacial, do formato das feições e da seletividade da consulta. Um índice em pontos compactos costuma eliminar muitos pares; envelopes de polígonos que cobrem quase toda a região podem oferecer pouca redução. Avaliar desempenho apenas com uma pequena amostra densa produz uma expectativa enganosa para bases reais.

O laboratório constrói cem pontos em uma grade e busca os que intersectam uma janela. Compara a seleção indexada com o predicado vetorizado aplicado a toda a série. A igualdade dos IDs é a verificação de correção; quantidade de candidatos é uma evidência de seletividade. Não compare tempos de uma única execução como prova de eficiência, porque aquecimento, alocação e tamanho da amostra influenciam o resultado.''', '''
import geopandas as gpd
from shapely.geometry import Point, box
g = gpd.GeoDataFrame({'id':range(100)},
    geometry=[Point(x,y) for x in range(10) for y in range(10)],
    crs=31982)
janela = box(2.5,2.5,5.5,5.5)
indices = g.sindex.query(janela, predicate='intersects')
selecionados = set(g.iloc[indices]['id'])
referencia = set(g.loc[g.intersects(janela),'id'])
assert selecionados == referencia and len(selecionados)==9
RESULTADO = {'total':len(g), 'selecionados':len(indices),
             'ids':sorted(selecionados)}
print(RESULTADO)
''', [('Envelope', 'Busca de candidatos', 'Pode conter falso positivo'), ('Predicado', 'Refinamento geométrico', 'Garante relação exata'), ('Índice posicional', 'Usar iloc', 'Não confundir com rótulo'), ('Referência', 'Consulta sem índice', 'Teste de equivalência')],
'Troque a janela retangular por um polígono triangular e compare consultas com e sem predicate. Conte candidatos descartados pelo refinamento. Mude o índice tabular para IDs entre 1.000 e 1.099 e mostre por que loc não substitui iloc na seleção dos resultados.',
'O índice espacial retorna posições da série, não necessariamente seus rótulos. Com índice tabular alterado, iloc continua correto e loc pode falhar ou selecionar outras linhas. A consulta sem predicado trabalha com envelopes e pode incluir pontos fora do triângulo; a consulta com intersects deve coincidir com o teste vetorizado exato. O laboratório retangular seleciona nove pontos.',
'Meça mediana de tempos em cinco execuções para 10 mil e 100 mil pontos, separando construção do índice e consulta. Registre distribuição, tamanho da janela e quantidade de candidatos. Mantenha asserções de equivalência enquanto otimiza.',
'Use iloc para posições, refine relações geométricas e confronte IDs com uma implementação de referência.'),
cap('Proximidade, empates e limite de distância', '''sjoin_nearest associa cada feição à mais próxima segundo a distância plana. O resultado não equivale a within: um equipamento fora de um setor pode ser ligado a ele por proximidade. max_distance define até onde a associação é admissível. Sem esse limite, uma observação isolada pode receber uma referência absurdamente distante.

Empates são possíveis e podem gerar mais de uma linha por feição da esquerda. Uma atribuição exclusiva demanda política de desempate documentada, como prioridade operacional ou código estável. A distância zero também não significa identidade: um ponto dentro de vários polígonos pode estar a distância zero de todos. A dimensionalidade das geometrias modifica a interpretação da medida.

O exemplo associa duas demandas a postos de atendimento, preservando uma demanda além de 30 metros como não atendida. O campo de distância permite conferir a regra. Não interprete essa distância como trajeto rodoviário. A busca é útil para triagem de proximidade, mas serviços de roteamento precisam de rede, restrições e tempos próprios.''', '''
import geopandas as gpd
from shapely.geometry import Point
d = gpd.GeoDataFrame({'demanda':[1,2]},
    geometry=[Point(10,0),Point(200,0)],crs=31982)
p = gpd.GeoDataFrame({'posto':['A','B']},
    geometry=[Point(0,0),Point(100,0)],crs=31982)
r = gpd.sjoin_nearest(d,p,how='left',max_distance=30,
                     distance_col='dist_m')
assert r.loc[r.demanda==1,'posto'].iloc[0]=='A'
assert r.loc[r.demanda==2,'posto'].isna().all()
RESULTADO = {'atendidas':int(r.posto.notna().sum()),
             'distancia_primeira':float(r.dist_m.iloc[0])}
print(RESULTADO)
''', [('nearest', 'Menor distância plana', 'Pode associar feição externa'), ('max_distance', '30 metros', 'Bloqueia associação distante'), ('distance_col', 'Distância auditável', 'Permite conferir o limite'), ('Empate', 'Múltiplas referências', 'Exige desempate quando exclusivo')],
'Adicione uma demanda em (50,0), equidistante dos dois postos. Aumente max_distance para 60 e conte correspondências. Produza uma saída exclusiva e uma coluna numero_candidatos para preservar o empate.',
'A nova demanda aparece duas vezes com distância de 50 metros. A primeira continua ligada a A e a demanda em 200 permanece sem posto porque está a 100 metros de B. A contagem de linhas atribuídas não é a contagem de demandas atendidas: use nunique na chave antes do desempate. Uma ordenação estável por posto resolve a exclusividade, mas não torna A operacionalmente melhor.',
'Repita a busca com polígonos de área de serviço e explique a diferença entre distância ao limite e distância ao centroide. Use a geometria que representa a pergunta, mantendo a referência projetada e um limite compatível com a finalidade.',
'Confirme uma demanda atendida e distância de 10 metros no conjunto original. Conte chaves distintas, não apenas linhas do join.'),
cap('Interpolação areal e hipótese de uniformidade', '''Interpolação areal transfere uma grandeza extensiva de zonas de origem para zonas de destino usando frações de área. A regra população_destino=sum(população_origem*área_interseção/área_origem) presume distribuição uniforme dentro de cada origem. Essa hipótese não é descoberta pelos dados geométricos e pode ser ruim onde há água, áreas industriais ou concentração residencial.

A conservação do total depende da cobertura dos destinos e da ausência de sobreposição entre eles. Se os destinos não cobrem toda a origem, parte da população fica sem alocação. Se se sobrepõem, a soma pode exceder a população original. Antes de confiar no resultado, calcule cobertura, duplicação e resíduos por zona de origem.

O laboratório reparte cem pessoas de um retângulo entre duas zonas com 25% e 75% da área. O resultado não representa contagem observada: é estimativa sob uma hipótese explícita. A ponderação dasimétrica poderia usar máscara residencial ou outro dado auxiliar, mas também exigiria validar o significado desse suporte. O uso de área zero como denominador deve ser bloqueado.''', '''
import geopandas as gpd
from shapely.geometry import box
o = gpd.GeoDataFrame({'origem':['O'],'pop':[100]},
    geometry=[box(0,0,200,100)],crs=31982)
o['area_origem'] = o.area
d = gpd.GeoDataFrame({'destino':['D1','D2']},
    geometry=[box(0,0,50,100),box(50,0,200,100)],crs=31982)
r = gpd.overlay(o,d,how='intersection')
r['estimada'] = r['pop']*r.area/r['area_origem']
assert abs(r['estimada'].sum()-100)<1e-8
RESULTADO = r[['destino','estimada']].to_dict('records')
print(RESULTADO)
''', [('Extensivo', 'População total', 'Pode ser repartido por pesos'), ('Peso', 'Interseção / origem', 'Hipótese de uniformidade'), ('Intensivo', 'Densidade', 'Derivar após alocar numerador'), ('Conservação', 'Soma dos pesos = 1', 'Exige partição completa')],
'Reduza o segundo destino até x=150 e calcule a população não alocada. Depois sobreponha D1 e D2 em 20 metros e calcule a soma de pesos. Implemente uma verificação que rejeite pesos acima de 1 por origem.',
'Com cobertura até x=150, as áreas cobrem 75% da origem e apenas 75 pessoas são alocadas; o resíduo é 25. Uma sobreposição de 20 metros de largura acrescenta 2.000 m² contados novamente, equivalentes a 10% da origem. A soma estimada sobe para 110. Normalizar os pesos sem explicar o problema ocultaria a sobreposição ou a lacuna.',
'Crie uma máscara de ocupação residencial que exclua metade da origem. Recalcule os pesos somente no suporte elegível e compare com a uniformidade simples. Apresente ambos como cenários, pois a máscara não prova por si só onde cada morador reside.',
'Confira resultados de 25 e 75 pessoas e conserve o total apenas sob cobertura completa, sem dupla contagem e com área de origem positiva.'),
cap('GeoPackage, reabertura e entrega reproduzível', '''Persistir a saída não é o último teste; reabri-la é. Um arquivo espacial pode existir e ainda perder CRS, tipos de atributo ou identificadores. GeoPackage combina geometria e atributos em um contêiner SQLite, suporta múltiplas camadas e evita várias limitações de nomes de campos do shapefile. Essa escolha não elimina a necessidade de um esquema de entrega.

O laboratório usa um diretório temporário, grava uma camada e a reabre com pyogrio. Confere quantidade, CRS, chave e área. O uso de diretório temporário impede sobrescrever material de estudo ou dados de projeto. Em produção, escreva para um nome novo, valide e somente depois promova a saída ao destino final.

Um manifesto deve registrar origem, versões, data, CRS, camadas, regras de transformação e checksums. Hash do arquivo identifica exatamente o artefato entregue, mas não garante equivalência semântica entre duas gravações: metadados internos podem mudar. Por isso combine integridade binária com testes de conteúdo, tolerâncias geométricas e evidências de reabertura. Um relatório curto de validação vale mais que a simples mensagem arquivo salvo.''', '''
from pathlib import Path
from tempfile import TemporaryDirectory
import geopandas as gpd
from shapely.geometry import box
g = gpd.GeoDataFrame({'id':[1],'classe':['teste']},
    geometry=[box(0,0,100,100)],crs=31982)
with TemporaryDirectory() as pasta:
    arq = Path(pasta)/'entrega.gpkg'
    g.to_file(arq,layer='setores',driver='GPKG',engine='pyogrio')
    l = gpd.read_file(arq,layer='setores',engine='pyogrio')
    assert len(l)==1 and l.crs.to_epsg()==31982
    assert l['id'].tolist()==[1] and l.area.iloc[0]==10000
    RESULTADO = {'camada':'setores','n':len(l),
                 'area_m2':float(l.area.sum()),'bytes':arq.stat().st_size}
print(RESULTADO)
''', [('Integridade', 'Arquivo reaberto', 'Existência isolada é insuficiente'), ('CRS', 'EPSG preservado', 'Verificar após persistência'), ('Esquema', 'Campos e tipos', 'Preservar chaves e domínios'), ('Geometria', 'Área e validade', 'Usar tolerância documentada')],
'Grave duas camadas, setores e equipamentos, no mesmo GeoPackage. Reabra ambas pelo nome e crie um manifesto JSON contendo número de registros, CRS, campos e hash SHA-256 do arquivo final. Faça o hash depois de terminar todas as gravações.',
'O exemplo conserva um polígono de 10.000 m² e EPSG:31982. O tamanho em bytes varia com versões e metadados e não deve ser usado como resultado geométrico fixo. O manifesto deve distinguir nome de arquivo e nome de camada. Ao incluir uma segunda camada, confirme as duas explicitamente para não validar apenas a primeira camada encontrada pelo leitor.',
'Organize o projeto integrador com funções de leitura, validação, processamento e entrega. Teste um diretório sem permissão e uma camada inexistente. A falha deve produzir diagnóstico e conservar a entrada, sem substituir um resultado anterior por um arquivo incompleto.',
'Reabra com o mesmo nome de camada, confira esquema e CRS, e mantenha os totais de população e cobertura calculados ao longo do fluxo.')
]
