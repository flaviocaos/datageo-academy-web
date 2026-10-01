"""Dinâmica urbana: transições temporais, demanda, alocação e cenários."""
from .estrutura import cap

TITULO='Análise Preditiva de Expansão Urbana'
DESCRICAO='Simulação temporal de expansão urbana: propensão, demanda, autômatos celulares, cenários e validação da mudança.'
DEPENDENCIAS=['numpy>=2,<3','scikit-learn>=1.7,<2','rasterio>=1.4,<2']
INTRO=[
 'Modelar expansão urbana exige separar três componentes: quanto crescimento se espera, onde ele pode ocorrer e quais restrições impedem a conversão. Um mapa de probabilidade não define por si só a demanda, e uma quantidade de novos pixels não explica sua localização. Este livro constrói explicitamente esses componentes para que hipóteses, parâmetros e resultados possam ser auditados.',
 'O caso integrador usa grades sintéticas em datas sucessivas. A classe urbana é representada por zero e um, acompanhada de uma máscara de elegibilidade e de covariáveis disponíveis na data inicial. O conjunto não descreve Florianópolis nem outra cidade. A finalidade é exercitar transições, vizinhança, validação temporal e incerteza sem confundir simulação didática com previsão oficial de ocupação.',
 'A primeira parte harmoniza mapas e calcula transições e indicadores de mudança. A segunda transforma distância a infraestrutura e contexto local em covariáveis para um modelo de conversão. A terceira separa demanda e alocação, introduz atualização celular e comparação de cenários. Os últimos capítulos medem acerto da mudança, simulam múltiplas realizações e exportam uma entrega espacial reproduzível.',
 'O leitor deve conhecer arrays, classificação binária e noções de georreferenciamento. Os códigos usam NumPy, Scikit-Learn e Rasterio de forma efetiva. Exemplos pequenos permitem calcular quantidades manualmente, mas mostram controles que permanecem relevantes em mosaicos extensos: datas consistentes, máscaras, unidades, alinhamento e conservação da quantidade alocada.',
 'O produto final deve ser apresentado como cenário condicionado às hipóteses. Uma simulação com maior ocupação perto de vias não demonstra efeito causal de uma nova estrada. Decisões de planejamento precisam de dados observados, análise institucional e revisão técnica. O estudante aprenderá a registrar essa diferença junto ao código, em vez de escondê-la em uma nota desvinculada dos resultados.'
]
REFERENCIAS=[
 'https://scikit-learn.org/stable/modules/linear_model.html#logistic-regression',
 'https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html',
 'https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.choice.html',
 'https://rasterio.readthedocs.io/en/stable/topics/georeferencing.html',
 'https://rasterio.readthedocs.io/en/stable/topics/writing.html'
]
PROJETO='Simular conversão urbana em uma grade com mapas de três datas, infraestrutura e áreas proibidas. Ajustar propensão com o primeiro intervalo, validar no segundo, estimar demanda em três cenários, alocar mudanças com vizinhança e executar vinte realizações. Entregar mapas, área em hectares, Figure of Merit e manifesto de hipóteses.'
CAPITULOS=[
cap('Mapas temporais, alinhamento e unidade de mudança', '''Comparar duas datas exige que os pixels representem o mesmo suporte espacial. CRS igual não basta: resolução, origem, extensão e grade devem coincidir. Um deslocamento de um pixel transforma bordas estáveis em falsas conversões e perdas. Para classes categóricas, a reamostragem deve preservar categorias, normalmente por vizinho mais próximo; interpolação bilinear cria valores sem significado de classe.

A definição de urbano precisa permanecer consistente entre datas. Se uma fonte inclui área pavimentada e outra apenas edifícios, uma diferença de legenda pode parecer expansão. Nodata não representa não urbano: deve ser excluído do conjunto comparável. A máscara de análise comum identifica onde as duas datas têm observação válida.

O laboratório compara duas grades 4×4 alinhadas e calcula conversão, persistência e retração. A soma dessas quantidades com a persistência não urbana recupera o total comparável. Expansão líquida é novas células menos células perdidas, enquanto expansão bruta é somente conversão para urbano. Essa distinção evita atribuir o mesmo significado a estudos que medem mudança de maneira diferente.''', '''
import numpy as np
a=np.array([[1,1,0,0],[1,0,0,0],[0,0,0,0],[0,0,0,0]])
b=np.array([[1,1,1,0],[1,1,0,0],[0,0,0,0],[0,0,0,0]])
valido=np.ones_like(a,dtype=bool)
novo=(a==0)&(b==1)&valido
perda=(a==1)&(b==0)&valido
persist=(a==1)&(b==1)&valido
assert int(novo.sum())==2 and int(perda.sum())==0
assert int(b.sum()-a.sum())==int(novo.sum()-perda.sum())
RESULTADO={'nova_urbanizacao':int(novo.sum()),
 'persistencia_urbana':int(persist.sum()),'mudanca_liquida':int(b.sum()-a.sum())}
print(RESULTADO)
''', [('Origem e resolução', 'Mesma grade', 'Evita mudança artificial'), ('Nodata', 'Máscara comum', 'Não tratar como não urbano'), ('Expansão bruta', '0 → 1', 'Conta novas células'), ('Mudança líquida', 'Novas menos perdas', 'Pode ocultar troca de localização')],
'Desloque b uma coluna com preenchimento nodata e compare conversões calculadas antes e depois de excluir a faixa sem observação. Escreva um contrato contendo CRS, transformada, resolução, datas e legenda, e rejeite grades incompatíveis.',
'A base original possui três células urbanas persistentes e duas conversões, totalizando cinco células urbanas na segunda data. O deslocamento altera correspondência pixel a pixel e produz mudanças falsas. Remover apenas nodata evita interpretar a faixa descoberta como perda, mas não corrige o deslocamento interno; o alinhamento deve ser restaurado antes da comparação.',
'Confronte duas legendas em que urbano tem definições diferentes. Crie uma tabela de correspondência e identifique classes que não podem ser harmonizadas sem revisar os dados de origem. Mantenha uma máscara de cobertura comparável e divulgue sua área.',
'Confirme mesma grade e definição de classe. Distinga expansão bruta, líquida e cobertura observável.'),
cap('Matriz de transição e hipótese de estabilidade', '''Uma matriz de transição conta mudanças entre classes de uma data para outra. Na versão binária, as quatro células representam não urbano persistente, conversão, perda urbana e persistência urbana. Dividir cada linha por seu total estima probabilidades condicionais à classe inicial durante o intervalo observado.

Aplicar essas probabilidades ao futuro assume estabilidade do mecanismo e compatibilidade do intervalo. Uma taxa de cinco anos não é automaticamente uma taxa anual. Além disso, a matriz descreve quantidades agregadas e não informa onde a mudança ocorre. Infraestrutura, política urbana e disponibilidade de terra podem alterar o processo, tornando a extrapolação inadequada.

O laboratório usa bincount para construir a matriz sem loops por pixel. A codificação 2*origem+destino produz quatro posições. Verifica que soma das contagens corresponde ao total de pixels e que linhas normalizadas somam um. Uma classe inicial ausente tem denominador zero e deve ser marcada como não estimável, em vez de receber uma probabilidade inventada.''', '''
import numpy as np
a=np.array([0,0,0,0,0,0,1,1,1,1])
b=np.array([0,0,0,0,1,1,1,1,1,1])
cont=np.bincount(2*a+b,minlength=4).reshape(2,2)
tot=cont.sum(axis=1,keepdims=True)
p=np.divide(cont,tot,out=np.zeros_like(cont,dtype=float),where=tot>0)
assert cont.sum()==10 and np.allclose(p.sum(axis=1),1)
RESULTADO={'contagens':cont.tolist(),
 'probabilidades':p.round(4).tolist(),'taxa_conversao':float(p[0,1])}
print(RESULTADO)
''', [('0 → 0', 'Não urbano persistente', '4 células'), ('0 → 1', 'Conversão', '2 células'), ('1 → 0', 'Perda urbana', '0 células'), ('1 → 1', 'Persistência urbana', '4 células')],
'Aplique a taxa 2/6 a uma região com 900 células inicialmente não urbanas. Calcule a demanda esperada e explique por que o resultado não identifica quais células mudarão. Em seguida, acrescente perdas urbanas e compare crescimento bruto com líquido.',
'A extrapolação produz 300 conversões esperadas no mesmo intervalo sob estabilidade da taxa. É uma expectativa agregada, não uma localização. Se a quantidade de terra elegível for menor que 300, a extrapolação é inviável e deve ser revisada; não basta forçar alocação em áreas proibidas. Perdas precisam de um componente separado quando a aplicação admite retração.',
'Calcule matrizes para dois intervalos de mesma duração e confronte as taxas. Estime incerteza amostral com reamostragem por blocos, mantendo dependência local, em vez de tratar todos os pixels como observações independentes.',
'Registre intervalo, legenda, cobertura e classe ausente. Não confunda matriz de transição com modelo espacial de alocação.'),
cap('Covariáveis disponíveis e vizinhança urbana', '''Covariáveis para prever conversão precisam ser observadas na data inicial. Distância à via futura, urbanização da data final ou cadastro atualizado depois da mudança podem revelar o alvo. A matriz de atributos deve conservar essa restrição temporal mesmo quando as camadas mais recentes são as mais fáceis de obter.

A fração urbana na vizinhança resume contexto local e pode representar contiguidade, mas não prova causalidade. A escolha de raio modifica a escala do processo. Na borda da grade, uma vizinhança incompleta requer denominador baseado nos vizinhos disponíveis; preencher fora da imagem com não urbano reduz artificialmente a fração se o denominador continuar fixo.

O laboratório calcula oito vizinhos por deslocamentos e uma contagem de vizinhos existentes. O centro é excluído, evitando que a própria classe inicial domine o atributo. Em seguida, calcula distância plana a um eixo viário vertical na unidade de metros. A resolução de 30 metros converte diferenças de coluna em distância física. Para uma rede real, distância euclidiana e acessibilidade de viagem são indicadores diferentes.''', '''
import numpy as np
u=np.zeros((5,5),dtype=int); u[2,2]=1
pad=np.pad(u,1); limite=np.pad(np.ones_like(u),1)
soma=np.zeros_like(u,dtype=float); n=np.zeros_like(u,dtype=float)
for dr in [-1,0,1]:
    for dc in [-1,0,1]:
        if dr==0 and dc==0: continue
        soma+=pad[1+dr:6+dr,1+dc:6+dc]
        n+=limite[1+dr:6+dr,1+dc:6+dc]
frac=soma/n
r,c=np.indices(u.shape); dist_via=np.abs(c-1)*30.0
assert frac[2,2]==0 and frac[2,1]==1/8
assert n[0,0]==3 and dist_via[2,4]==90
RESULTADO={'fracao_vizinha':float(frac[2,1]),
 'vizinhos_canto':int(n[0,0]),'distancia_m':float(dist_via[2,4])}
print(RESULTADO)
''', [('Temporal', 'Camadas da data inicial', 'Evita informação posterior'), ('Vizinhança', 'Oito células, sem centro', 'Escala de 30 m por pixel'), ('Borda', 'Denominador variável', 'Evita viés de preenchimento'), ('Via', 'Distância plana', 'Não equivale a tempo de acesso')],
'Amplie o raio da vizinhança para dois pixels e compare valores perto do núcleo urbano. Crie uma grade 3×3 e confira os denominadores manualmente. Troque a resolução para 10 metros e recalcule a distância à via sem mudar os índices.',
'O raio maior suaviza e amplia contexto, alterando a variável mesmo com a mesma ocupação. Com resolução de 10 metros, a posição da coluna 4 fica a 30 metros da coluna 1, em vez de 90. A fração urbana não depende diretamente da unidade, mas sua janela corresponde a uma extensão física diferente. O denominador de canto considera apenas vizinhos dentro da grade.',
'Inclua máscara de observação válida no cálculo e não conte nodata como vizinho não urbano. Guarde nome, data e resolução de cada covariável em um manifesto para impedir que a data final entre no ajuste por engano.',
'Confira datas, distância em metros e denominador das bordas. Exclua o centro quando o contrato for fração de vizinhos.'),
cap('Propensão à conversão com regressão logística', '''A propensão é estimada apenas nas células elegíveis e inicialmente não urbanas. Incluir células já urbanas mistura persistência com conversão e pode tornar o alvo trivial. O rótulo positivo identifica células que eram não urbanas no início e urbanas no fim do intervalo; as covariáveis pertencem ao início.

Uma regressão logística fornece um modelo simples de probabilidade condicional. Padronização deve ser ajustada no treino. O sinal dos coeficientes descreve associação na amostra, não efeito causal de uma obra. Dados de conversão rara exigem avaliação apropriada e podem demandar ponderação, mas ponderar classes altera a interpretação das probabilidades.

O laboratório gera distância à via e fração urbana, cria conversões por um mecanismo probabilístico declarado e ajusta um pipeline. A comparação entre duas condições exemplifica efeito aprendido: perto da via com vizinhança urbana versus distante com pouca vizinhança. A direção esperada é conferida por asserção. O exemplo ensina ajuste, mas a probabilidade numérica só vale dentro do experimento sintético.''', '''
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
rng=np.random.default_rng(44)
dist=rng.uniform(0,1000,500); viz=rng.uniform(0,1,500)
X=np.column_stack([dist,viz])
p=1/(1+np.exp(-(-2-.003*dist+4*viz)))
y=rng.binomial(1,p)
m=make_pipeline(StandardScaler(),LogisticRegression(max_iter=300)).fit(X,y)
casos=np.array([[100,.8],[900,.1]])
saida=m.predict_proba(casos)[:,1]
assert saida[0]>saida[1]
RESULTADO={'perto_contiguo':round(float(saida[0]),4),
 'longe_isolado':round(float(saida[1]),4),'conversoes':int(y.sum())}
print(RESULTADO)
''', [('Universo', 'Não urbano elegível no início', 'Não misturar persistência'), ('Alvo', 'Conversão no intervalo', 'Definir datas'), ('Covariáveis', 'Distância e vizinhança inicial', 'Sem futuro'), ('Probabilidade', 'Condicionada ao modelo', 'Avaliar calibração fora do treino')],
'Adicione células já urbanas ao conjunto como se fossem conversões e observe a mudança dos coeficientes. Depois remova-as e escreva uma função que construa a máscara de treinamento a partir de urbano_inicial, observação válida e restrição legal.',
'Células já urbanas não sofreram a transição 0→1 no intervalo e não pertencem ao universo do modelo de conversão. Misturá-las muda a pergunta e pode introduzir uma forte relação artificial com vizinhança. A máscara correta é (~urbano_inicial)&valido&permitido. A direção de associação no simulador é maior probabilidade para menor distância e maior fração urbana.',
'Compare logística linear com uma transformação log1p da distância, escolhendo o procedimento em validação temporal. Registre desempenho e calibração em blocos. Não interprete coeficiente de distância como benefício causal de uma estrada.',
'Treine somente no universo de conversão e confira disponibilidade temporal. Não use probabilidades ajustadas como demanda total sem uma decisão explícita.'),
cap('Backtesting temporal e baseline de persistência', '''Um backtest ajusta o procedimento em um intervalo passado e avalia um intervalo posterior. As camadas de entrada do segundo intervalo devem ser reconstruídas na sua data inicial, incluindo vizinhança atualizada. Reutilizar atributos da primeira data com rótulos do segundo intervalo pode testar uma hipótese diferente da previsão operacional.

Separar tempo não elimina dependência espacial. Blocos retidos ou avaliação por região ajudam a diagnosticar transferência. A baseline de persistência mantém o mapa sem novas conversões: costuma obter acurácia alta quando a mudança é rara, mas recall de expansão igual a zero. Avalie a mudança explicitamente e apresente quantidade prevista junto às métricas.

O laboratório usa dois intervalos sintéticos para ajustar e testar logística, calcula AP no período posterior e mostra que persistência não encontra conversões. A base futura não participa de fit. O exemplo não usa TimeSeriesSplit porque dados de pixels em intervalos não são uma sequência simples de linhas intercambiáveis; a divisão é feita pelo significado das datas.''', '''
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
rng=np.random.default_rng(45)
def intervalo(n):
    x=rng.uniform(0,1,(n,2))
    p=1/(1+np.exp(-(-3+4*x[:,0]-2*x[:,1])))
    return x,rng.binomial(1,p)
X1,y1=intervalo(350); X2,y2=intervalo(200)
m=LogisticRegression(max_iter=300).fit(X1,y1)
p=m.predict_proba(X2)[:,1]
assert y2.sum()>0 and len(p)==200
RESULTADO={'AP_futuro':round(average_precision_score(y2,p),4),
 'conversoes_observadas':int(y2.sum()),'recall_persistencia':0.0}
print(RESULTADO)
''', [('Treino', 'Intervalo anterior', 'Ajusta modelo'), ('Teste', 'Intervalo posterior', 'Não participa de seleção'), ('Persistência', 'Sem conversões', 'Alta acurácia pode enganar'), ('Diagnóstico espacial', 'Métricas por bloco', 'Complementa separação temporal')],
'Altere o intercepto do segundo intervalo para aumentar a demanda sem mudar as relações de localização. Compare AP, probabilidade média e quantidade esperada. Depois inverta o sinal de uma covariável e examine mudança de ranking.',
'Mudar o intercepto altera prevalência e pode exigir reavaliar calibração ou demanda; o ranking estrutural pode permanecer semelhante. Inverter uma relação altera o mecanismo e tende a comprometer ordenação. AP também depende da prevalência, portanto não interprete qualquer aumento como melhoria do modelo. Persistência continua com zero conversões e recall zero quando existem mudanças observadas.',
'Monte três datas de mapas, reconstrua covariáveis para cada data inicial e registre uma tabela de intervalos com duração e amostra elegível. Reserve o último intervalo para um teste único depois de decidir método e hiperparâmetros.',
'Reconstrua entradas por data e compare mudança com persistência. Não use o intervalo futuro para selecionar a configuração.'),
cap('Demanda, ranking e restrições de alocação', '''Demanda define a quantidade de células a converter; propensão define uma ordem ou distribuição de preferência. Uma alocação por ranking seleciona as células elegíveis com maiores escores até atingir a demanda. Essa regra separa quantidade de localização e facilita cenários com a mesma propensão e demandas diferentes.

Máscaras devem excluir células já urbanas, nodata e áreas proibidas antes da seleção. Se a demanda excede a capacidade elegível, a rotina deve falhar ou reportar déficit conforme o contrato; não pode remover restrições silenciosamente. Empates precisam de regra estável para que a execução seja reproduzível. Um desempate por índice é técnico e não representa preferência substantiva.

O laboratório usa seis células com duas proibições e seleciona duas elegíveis. lexsort ordena por escore descendente e depois por índice. A asserção protege quantidade e restrição. O procedimento é determinístico, mas a certeza do algoritmo não representa certeza da previsão. Escores semelhantes perto do corte podem produzir grande sensibilidade à demanda ou a pequenas alterações de entrada.''', '''
import numpy as np
p=np.array([.8,.7,.9,.4,.6,.3])
permitido=np.array([True,True,False,True,True,False])
demanda=2; candidatos=np.flatnonzero(permitido)
if demanda>len(candidatos): raise ValueError('Demanda acima da capacidade')
ordem=np.lexsort((candidatos,-p[candidatos]))
escolhidos=candidatos[ordem[:demanda]]
novo=np.zeros(len(p),dtype=bool); novo[escolhidos]=True
assert novo.sum()==2 and not novo[~permitido].any()
RESULTADO={'indices':escolhidos.tolist(),'demanda':demanda,
 'capacidade':len(candidatos)}
print(RESULTADO)
''', [('Demanda', 'Duas conversões', 'Quantidade externa ao ranking'), ('Propensão', 'Escores p', 'Preferência relativa'), ('Restrição', 'Máscara anterior à seleção', 'Nunca relaxar silenciosamente'), ('Empate', 'Índice crescente', 'Desempate reproduzível')],
'Aumente a demanda para cinco e teste a mensagem de erro. Iguale p das células 0 e 1 e selecione somente uma. Depois compare a alocação por ranking com limiar 0,5, mantendo restrições, e conte a diferença de quantidade.',
'A capacidade é quatro, então demanda cinco é inviável. No empate entre índices 0 e 1, lexsort seleciona 0 primeiro conforme a regra registrada. O limiar 0,5 seleciona três células permitidas, enquanto a demanda de duas seleciona apenas 0 e 1. Um limiar traduz probabilidade em decisão, mas não garante cumprir uma quantidade de expansão definida externamente.',
'Converta quantidade em hectares com a área do pixel e compare três demandas. Produza um relatório com capacidade total, demanda solicitada, demanda atendida e células no limite de corte. Examine sensibilidade quando a maioria dos escores está próxima.',
'Confirme exatamente a quantidade solicitada e nenhuma conversão proibida. Mantenha demanda e regra de localização como componentes separados.'),
cap('Atualização celular e crescimento contíguo', '''Um autômato celular atualiza o estado de uma grade com base em regras de vizinhança e condições locais. Na expansão urbana, uma preferência por células próximas ao tecido existente pode representar contiguidade, mas precisa ser tratada como hipótese de cenário. A intensidade desse componente controla quão disperso ou compacto o crescimento simulado se torna.

Atualização síncrona calcula todas as mudanças a partir do mesmo estado anterior. Atualização assíncrona modifica o contexto a cada célula convertida e depende da ordem de processamento. Misturar essas estratégias sem registro torna os resultados difíceis de comparar. Quando há passos temporais, recalcular a vizinhança após cada passo permite realimentação explícita.

O laboratório executa um passo síncrono: soma vizinhos, combina propensão base com preferência local e escolhe três células não urbanas. A máscara exclui o estado urbano atual e uma faixa proibida. O aumento de quantidade é exatamente três. A regra não incorpora calibração temporal, rede viária real ou legislação; é um componente didático que deve ser validado com padrões observados antes de uso aplicado.''', '''
import numpy as np
u=np.zeros((5,5),dtype=bool); u[2,2]=True
pad=np.pad(u.astype(float),1); viz=np.zeros_like(u,dtype=float)
for dr in [-1,0,1]:
    for dc in [-1,0,1]:
        if dr or dc: viz+=pad[1+dr:6+dr,1+dc:6+dc]
base=np.full((5,5),.2); score=base+.5*viz/8
elegivel=~u; elegivel[:,0]=False
ids=np.flatnonzero(elegivel)
ordem=np.lexsort((ids,-score.ravel()[ids]))
novo=u.copy(); novo.ravel()[ids[ordem[:3]]]=True
assert novo.sum()-u.sum()==3 and not novo[:,0].any()
RESULTADO={'urbanas_antes':int(u.sum()),'depois':int(novo.sum()),
 'novas_posicoes':np.argwhere(novo&~u).tolist()}
print(RESULTADO)
''', [('Síncrono', 'Mesmo estado para o passo', 'Não depende de ordem interna'), ('Assíncrono', 'Atualiza contexto a cada conversão', 'Ordem pode mudar resultado'), ('Vizinhança', 'Componente de score', 'Hipótese de contiguidade'), ('Restrição', 'Excluída em cada passo', 'Preservar durante realimentação')],
'Execute dois passos de três conversões, recalculando vizinhança entre eles. Compare com uma única seleção de seis a partir do estado inicial. Calcule distância média das novas células ao núcleo original para discutir diferença de padrão.',
'Dois passos permitem que células convertidas no primeiro influenciem a seleção do segundo. Uma única seleção de seis não contém essa realimentação. A quantidade final pode ser igual, mas a localização divergir. Essa diferença não identifica qual cenário é correto; revela uma hipótese de dinâmica que precisa de comparação com observações e análise de sensibilidade.',
'Teste pesos de vizinhança 0, 0,5 e 2 mantendo a demanda. Compare número de componentes urbanos e proporção de novas células adjacentes. Não selecione o peso somente por aparência visual: defina métricas de padrão e um intervalo de validação.',
'Declare atualização, passo temporal e peso de vizinhança. Preserve quantidade e restrições em cada iteração.'),
cap('Cenários de demanda e capacidade territorial', '''Cenários não são sinônimos de intervalos probabilísticos. Um cenário baixo, central e alto pode representar hipóteses econômicas, institucionais ou demográficas diferentes, sem probabilidade associada. A demanda deve estar vinculada a uma justificativa e a uma unidade: hectares, população ou células não são intercambiáveis sem parâmetros adicionais.

Se a demanda parte de população, uma hipótese de densidade transforma pessoas em área. Densidade constante não representa automaticamente expansão vertical ou vazios internos. Se a demanda parte de taxa de crescimento da área urbana, composição temporal e base de cálculo precisam ser explícitas. Capacidade elegível limita a área possível e pode tornar uma hipótese inviável.

O laboratório converte taxas de cinco anos em novas células usando a área urbana inicial e arredonda para uma demanda inteira. Compara com capacidade de cem células. O cenário alto é sinalizado quando excede capacidade. Não reduza o número silenciosamente: a divergência é informação para discutir hipóteses, restrições e unidades.''', '''
import math
urbanas=500; capacidade=100; area_pixel_m2=900
cenarios={'baixo':.05,'central':.15,'alto':.30}
res=[]
for nome,taxa in cenarios.items():
    demanda=math.ceil(urbanas*taxa)
    res.append({'cenario':nome,'novas_celulas':demanda,
      'hectares':demanda*area_pixel_m2/10000,
      'viavel':demanda<=capacidade})
assert [r['novas_celulas'] for r in res]==[25,75,150]
assert not res[2]['viavel']
RESULTADO=res
print(RESULTADO)
''', [('Baixo', '5% em cinco anos', '25 células; 2,25 ha'), ('Central', '15% em cinco anos', '75 células; 6,75 ha'), ('Alto', '30% em cinco anos', '150 células; 13,5 ha'), ('Capacidade', '100 células', '9 ha disponíveis')],
'Troque área do pixel para 10×10 metros mantendo o número de células urbanas. Compare área física inicial e demanda em hectares. Depois calcule demanda por população adicional de 2.000 habitantes com densidades de 100 e 200 habitantes por hectare.',
'Mantendo quinhentas células, a área inicial muda de 45 hectares para 5 hectares ao trocar pixels de 30 por 10 metros. Portanto, repetir o mesmo número de células não conserva o território. Para 2.000 habitantes adicionais, densidades de 100 e 200 hab/ha implicam 20 e 10 hectares, respectivamente. Essa conversão incorpora uma hipótese de densidade, não uma observação de área.',
'Redija fichas de cenário com fonte da hipótese, horizonte, taxa, densidade, capacidade e critérios de inviabilidade. Compare adensamento interno e expansão horizontal sem tratar os dois processos como a mesma conversão raster.',
'Declare unidades e horizonte, sinalize cenários inviáveis e não apresente cenários sem probabilidade como intervalos de confiança.'),
cap('Figure of Merit e avaliação da mudança', '''Avaliar o mapa urbano final pode ser dominado pela persistência. Figure of Merit compara mudanças previstas e observadas: acertos de mudança divididos pela união das mudanças, incluindo omissões e falsas conversões. Na situação binária sem categorias de destino múltiplas, equivale à IoU dos conjuntos de conversão.

A avaliação deve distinguir erro de quantidade e erro de alocação. Um modelo pode prever a quantidade correta em lugares errados, ou localizar parte da mudança e errar a demanda. Confrontar só total de área esconde o primeiro problema; confrontar só acurácia do mapa final esconde a raridade da mudança. Relate ambos e compare com baseline de persistência e alocação simples.

O laboratório usa conjuntos de índices para tornar contagens auditáveis. Três mudanças previstas e três observadas compartilham duas posições. O FoM é 0,5, embora o erro de quantidade seja zero. A avaliação de bordas e tolerância espacial pode ser acrescentada como análise separada, sem substituir silenciosamente o critério pixel a pixel.''', '''
observado={2,5,8}
previsto={2,5,9}
acertos=len(observado&previsto)
omissoes=len(observado-previsto)
falsas=len(previsto-observado)
fom=acertos/(acertos+omissoes+falsas)
erro_quantidade=abs(len(previsto)-len(observado))
assert fom==.5 and erro_quantidade==0
RESULTADO={'acertos':acertos,'omissoes':omissoes,
 'falsas_conversoes':falsas,'FoM':fom,'erro_quantidade':erro_quantidade}
print(RESULTADO)
''', [('Acerto', 'Mudança no mesmo local', '2 células'), ('Omissão', 'Observada e não prevista', '1 célula'), ('Falsa conversão', 'Prevista e não observada', '1 célula'), ('Quantidade', 'Três versus três', 'Erro zero não garante localização')],
'Crie uma previsão com cinco células contendo todas as três observadas. Calcule FoM, recall e erro de quantidade. Compare com uma previsão de somente duas células corretas e discuta qual atende melhor a uma decisão de planejamento.',
'Cinco previstas com três corretas produzem FoM=3/5=0,6, recall=1 e erro de quantidade=2. Duas previstas corretas produzem FoM=2/3, recall=2/3 e erro de quantidade=1. A segunda tem FoM maior, mas perde uma ocorrência. A preferência depende de custo e finalidade; nenhuma métrica isolada define a melhor decisão em todos os contextos.',
'Avalie resultados por blocos e por distância à via. Faça uma análise de tolerância de um pixel separada da avaliação exata. Declare que a tolerância relaxa a localização e registre a resolução para traduzir esse relaxamento em metros.',
'Apresente quantidade, acertos e omissões de mudança. Não reporte apenas acurácia do estado urbano final.'),
cap('Ensembles de alocação e frequência de conversão', '''Uma alocação estocástica pode gerar várias realizações com a mesma demanda. O mapa de frequência registra quantas vezes cada célula foi selecionada. Isso descreve variabilidade sob o algoritmo e as hipóteses escolhidas; não é automaticamente a probabilidade real de urbanização. Diferentes mecanismos de amostragem produzem frequências distintas.

Amostragem ponderada sem reposição seleciona quantidade fixa e impede escolher a mesma célula duas vezes na mesma realização. Os pesos precisam ser não negativos e ter soma positiva. Escores logísticos podem servir como pesos, mas essa decisão não conserva necessariamente a interpretação original das probabilidades. Registre demanda, máscara, seed e número de realizações.

O laboratório usa seis células elegíveis, demanda dois e duzentas realizações. A soma das frequências deve ser dois, pois cada realização seleciona exatamente duas células. A célula de maior peso tende a ter frequência maior, mas o valor calculado é específico da amostragem. Expandir a análise para incerteza de parâmetros, demanda e classificação de entrada requer variar esses componentes explicitamente.''', '''
import numpy as np
rng=np.random.default_rng(51)
w=np.array([.4,.25,.15,.1,.06,.04]); w=w/w.sum()
cont=np.zeros(6,dtype=int); realizacoes=200; demanda=2
for _ in range(realizacoes):
    ids=rng.choice(6,size=demanda,replace=False,p=w)
    assert len(set(ids))==demanda
    cont[ids]+=1
freq=cont/realizacoes
assert abs(freq.sum()-demanda)<1e-8
RESULTADO={'frequencias':freq.tolist(),'soma':float(freq.sum()),
 'realizacoes':realizacoes}
print(RESULTADO)
''', [('Demanda fixa', 'Duas por realização', 'Soma das frequências = 2'), ('Sem reposição', 'ID único por realização', 'Conserva quantidade'), ('Pesos', 'Normalizados e positivos', 'Regra de alocação declarada'), ('Frequência', 'Proporção de seleções', 'Condicionada à simulação')],
'Compare duzentas com duas mil realizações usando seed fixa. Depois mantenha pesos e altere demanda de dois para quatro. Explique por que frequência de seleção não é igual ao peso normalizado e por que aumenta com a demanda.',
'Pesos são probabilidades de escolha usadas pelo mecanismo, enquanto inclusão sem reposição depende de todas as escolhas e da demanda. Com quatro vagas, mais células entram em cada realização e a soma das frequências passa a quatro. Mais realizações reduz erro Monte Carlo do mecanismo escolhido, mas não elimina incerteza sobre dados, parâmetros ou adequação do modelo.',
'Varie intercepto do modelo e demanda em um ensemble externo, mantendo vinte realizações por combinação. Separe variação dentro de um cenário e variação entre cenários. Apresente o mapa de frequência com sua hipótese, sem chamar a legenda de probabilidade observada.',
'Confira demanda em toda realização, pesos válidos e soma das frequências. Diferencie incerteza de simulação e incerteza do mundo real.'),
cap('Taxas compostas, horizontes e sensibilidade', '''Uma taxa acumulada em cinco anos não pode ser dividida por cinco sem considerar o modelo temporal. Sob crescimento composto, taxa anual equivalente é (1+taxa_intervalo)^(1/anos)-1. Sob conversão de células elegíveis com hazard constante, a relação usa sobrevivência: hazard anual=1-(1-prob_intervalo)^(1/anos). Esses dois mecanismos usam bases diferentes.

Crescimento da área urbana incide sobre a área já urbana; hazard de conversão incide sobre células ainda não urbanas. Confundir as bases altera a demanda. Além disso, disponibilidade de terra diminui à medida que ocorre conversão e pode impor saturação. Extrapolar um regime linear indefinidamente ignora esse limite.

O laboratório calcula taxa composta equivalente para crescimento de 20% em cinco anos e hazard anual para probabilidade de conversão de 20%. As verificações recompõem o intervalo original. Uma análise de sensibilidade deve variar horizonte, taxa e capacidade separadamente, registrando onde cada cenário deixa de ser viável. Não atribua precisão à segunda casa decimal quando a hipótese de taxa é incerta.''', '''
taxa_5anos=.20; anos=5
crescimento_anual=(1+taxa_5anos)**(1/anos)-1
hazard_anual=1-(1-taxa_5anos)**(1/anos)
recomposto=(1+crescimento_anual)**anos-1
prob_recomposta=1-(1-hazard_anual)**anos
assert abs(recomposto-.2)<1e-10
assert abs(prob_recomposta-.2)<1e-10
RESULTADO={'crescimento_anual':round(crescimento_anual,6),
 'hazard_anual':round(hazard_anual,6),
 'divisao_simples':taxa_5anos/anos}
print(RESULTADO)
''', [('Composto', 'Base urbana cresce', '(1+r)^t'), ('Hazard', 'Base não convertida diminui', '1-(1-h)^t'), ('Linear', 'Incremento fixo', 'Hipótese diferente'), ('Capacidade', 'Limite territorial', 'Pode restringir extrapolação')],
'Calcule os dois mecanismos para 10 anos. Use 500 células urbanas e 1.000 não urbanas e estime quantidades adicionais em cada base. Explique por que os resultados não precisam coincidir apesar de partir de 20% em cinco anos.',
'Com crescimento composto equivalente, dez anos implicam 44% de crescimento sobre 500 células, ou 220 novas. Com hazard equivalente, dez anos implicam 36% de conversão de 1.000 não urbanas, ou 360 novas. As bases e os processos são distintos. Dividir 20% por cinco fornece 4% ao ano, diferente das taxas equivalentes calculadas.',
'Monte uma grade de sensibilidade com taxas de 10%, 20% e 30% em cinco anos e horizontes de cinco e dez anos. Sinalize resultados acima da capacidade e compare mecanismo composto com incremento linear.',
'Declare base de cálculo e mecanismo temporal. Recomponha o intervalo original para conferir a conversão de taxas.'),
cap('GeoTIFF, manifesto e entrega de cenários', '''A entrega espacial precisa conservar valores, referência e interpretação. Um GeoTIFF de cenário pode armazenar classes, escores ou frequências, mas sua legenda e nodata devem ser inequívocos. Para classe binária, uint8 é suficiente; para probabilidades, use float32 e uma máscara de validade ou valor nodata fora do domínio.

A transformada afim relaciona índices de linha e coluna a coordenadas. from_origin recebe canto superior esquerdo e resolução positiva; a orientação vertical é codificada na transformada. Área do pixel em um CRS projetado métrico pode ser derivada do determinante da parte linear. Copiar uma transformada de outro recorte sem ajustar origem desloca a saída.

O laboratório grava uma grade sintética em diretório temporário, reabre e confere CRS, valores, resolução e área. O manifesto JSON identifica o cenário, horizonte e seed. Em um projeto completo, inclua hashes, versões, fontes e critérios de validação temporal. A imagem final deve ser acompanhada de quantidades, FoM e limites, para que um mapa visualmente convincente não substitua a evidência.''', '''
from pathlib import Path
from tempfile import TemporaryDirectory
import numpy as np
import rasterio
from rasterio.transform import from_origin
u=np.zeros((4,4),dtype='uint8'); u[1:3,1:3]=1
t=from_origin(500000,6900000,30,30)
with TemporaryDirectory() as pasta:
    arq=Path(pasta)/'cenario.tif'
    with rasterio.open(arq,'w',driver='GTiff',height=4,width=4,
        count=1,dtype='uint8',crs='EPSG:31982',transform=t,nodata=255) as dst:
        dst.write(u,1); dst.update_tags(cenario='didatico',horizonte='5 anos')
    with rasterio.open(arq) as src:
        l=src.read(1); assert np.array_equal(l,u)
        assert src.crs.to_epsg()==31982 and src.res==(30,30)
        RESULTADO={'urbanas':int(l.sum()),'hectares':float(l.sum()*900/10000),
                   'cenario':src.tags()['cenario']}
print(RESULTADO)
''', [('Classe', 'uint8; nodata=255', 'Zero é não urbano observado'), ('CRS', 'EPSG:31982', 'Unidade métrica'), ('Resolução', '30 × 30 metros', '0,09 ha por pixel'), ('Manifesto', 'Hipóteses e validação', 'Não substituir por legenda visual')],
'Exporte uma frequência float32 e preserve nodata=-1. Reabra e confira domínio [0,1] somente nos pixels válidos. Crie um manifesto com demanda, restrições, horizonte, parâmetros, seed, fontes, métricas e hash calculado depois da gravação.',
'A grade original tem quatro células urbanas de 900 m², totalizando 0,36 hectare. O valor nodata=255 não entra na soma de classe: a leitura com máscara ou uma condição explícita deve excluí-lo. Frequências usam domínio distinto de classe e precisam de legenda própria. O hash final identifica exatamente o arquivo já fechado, depois de todas as alterações de tags.',
'Entregue três cenários com mapas e uma tabela de comparação. Para cada um, informe demanda, quantidade atendida, área, capacidade remanescente e avaliação histórica. Peça a outro estudante para reproduzir uma saída em processo novo usando apenas o manifesto e as fontes.',
'Reabra o arquivo, confira transformada e domínio e acompanhe cada mapa com hipóteses e evidências de avaliação.')
]
