"""Compila 28 volumes PDF de 42 páginas e copia os dois PDFs de referência.

Python 3.10+ e PyMuPDF. Execute: python scripts_automacao/gerar_livros_pdf.py
Não apaga fontes. --somente 'Título' permite revisar um volume antes do lote.
Cada capítulo inclui fundamentos, laboratório executável e exercícios comentados.
"""
from pathlib import Path
from html import escape as esc
import argparse
import hashlib
import json
import math
import shutil
import statistics
import sys
from catalogo_livros import AREAS, CATALOGO, REFERENCIAS
from conteudo_livros_pdf import CHAPTERS, PROFILES, LAB_EXPLANATIONS

ROOT=Path(__file__).resolve().parents[1]
try:import pymupdf as fitz
except ImportError:
    sys.path.insert(0,str(ROOT/'.capas-deps'));import pymupdf as fitz
DEST=ROOT/'livros_academicos'
NAVY=(11/255,47/255,91/255);GREEN=(107/255,214/255,106/255)
CSS='''body{font-family:sans-serif;font-size:10.5pt;line-height:1.36;color:#173651;margin:0}
h1{font-size:19pt;color:#0B2F5B;line-height:1.17;margin:0 0 12pt}
h2{font-size:12pt;color:#117983;line-height:1.3;margin:12pt 0 6pt}
h3{font-size:10.5pt;color:#0B2F5B;margin:10pt 0 5pt}
p{margin:0 0 8pt;text-align:justify}table{border-collapse:collapse;width:100%;font-size:9pt;margin:7pt 0 10pt}
th{background:#0B2F5B;color:white}td,th{border:0.5pt solid #bfd5e1;padding:5pt;text-align:left}
tr:nth-child(even){background:#eff5f9}pre{background:#eff5f9;border-left:3pt solid #16BFD0;padding:9pt;font-family:monospace;font-size:8.4pt;line-height:1.25;white-space:pre-wrap}
.note{background:#eef8ef;border-left:3pt solid #6BD66A;padding:9pt;font-size:9.5pt}.kicker{font-size:9pt;color:#14756d;letter-spacing:1pt}
li{margin-bottom:6pt}ul,ol{padding-left:17pt;margin:8pt 0 12pt}'''

def ps(*textos):return ''.join('<p>'+esc(t)+'</p>' for t in textos)
def lista(items,ordered=False):
    tag='ol' if ordered else 'ul'
    return '<'+tag+'>'+''.join('<li>'+esc(t)+'</li>' for t in items)+'</'+tag+'>'
def tabela(headers,rows):
    return '<table><tr>'+''.join('<th>'+esc(str(h))+'</th>' for h in headers)+'</tr>'+''.join('<tr>'+''.join('<td>'+esc(str(v))+'</td>' for v in row)+'</tr>' for row in rows)+'</table>'

def dados(i,j):
    seed=100+i*37+j*11
    observed=[round(seed/10+x*2.3+(x%2)*1.7,2) for x in range(6)]
    errors=[-1.2,.7,2.1,-.6,1.5,-1.1]
    return [{'id':f'P{k+1:02d}','grupo':'ABC'[k//2],'e':100+k*80,'n':200+(k%3)*60,
             'observado':o,'estimado':round(o+errors[k]*(1+j/10),2),'denominador':100+k*75+i*20}
            for k,o in enumerate(observed)]

def metricas(obs,pred):
    e=[b-a for a,b in zip(obs,pred)]
    return {'MAE':statistics.mean(abs(x) for x in e),'RMSE':math.sqrt(statistics.mean(x*x for x in e)),'viés':statistics.mean(e)}

def codigo_lab(ch,d,titulo):
    prefix='import math, statistics, json, hashlib\nDADOS = '+repr(d)+'\n'
    # Linha de dados compacta em múltiplas linhas: cabe na página sem reduzir fonte.
    prefix='import math, statistics, json, hashlib\nDADOS = [\n'+''.join('    '+repr(row)+',\n' for row in d)+']\n'
    bodies=[
'''# Contrato: coordenadas planas em metros; valores sintéticos.
ids = [p['id'] for p in DADOS]
assert len(ids) == len(set(ids))
for p in DADOS:
    assert p['grupo'] in ('A', 'B', 'C')
    for campo in ('e', 'n', 'observado', 'estimado'):
        assert math.isfinite(p[campo])
    assert p['denominador'] > 0
RESULTADO = {'registros': len(DADOS), 'ids_unicos': len(set(ids))}
print(RESULTADO)
''',
'''RESULTADO = {}
for grupo in ('A', 'B', 'C'):
    v = [p['observado'] for p in DADOS if p['grupo'] == grupo]
    RESULTADO[grupo] = {'n': len(v), 'min': min(v), 'max': max(v),
                       'media': statistics.mean(v)}
print(RESULTADO)
''',
'''a, b = DADOS[0], DADOS[-1]
de, dn = b['e'] - a['e'], b['n'] - a['n']
distancia = math.hypot(de, dn)
if distancia == 0:
    raise ValueError('Pontos coincidentes: azimute indefinido.')
azimute = math.degrees(math.atan2(de, dn)) % 360
RESULTADO = {'distancia_m': distancia, 'azimute_graus': azimute}
print(RESULTADO)
''',
'''v = [p['observado'] for p in DADOS]
v[2] = None  # Ausência didática, preservando o registro.
mediana = statistics.median(x for x in v if x is not None)
tratado = [mediana if x is None else x for x in v]
RESULTADO = {'mediana': mediana, 'original': v, 'tratado': tratado}
print(RESULTADO)
''',
'''raio = 150.0  # metros, sistema plano local didático
RESULTADO = {}
for a in DADOS:
    RESULTADO[a['id']] = [b['id'] for b in DADOS if b['id'] != a['id']
        and math.hypot(b['e']-a['e'], b['n']-a['n']) <= raio]
print(RESULTADO)
''',
'''obs = [p['observado'] for p in DADOS]
pred = [p['estimado'] for p in DADOS]
media = statistics.mean(obs)  # Apenas baseline descritivo do exemplo.
mae_media = statistics.mean(abs(media-x) for x in obs)
mae_estimativa = statistics.mean(abs(a-b) for a,b in zip(obs,pred))
RESULTADO = {'media': media, 'mae_media': mae_media,
             'mae_estimativa_sintetica': mae_estimativa}
print(RESULTADO)
''',
'''e = [p['estimado']-p['observado'] for p in DADOS]
RESULTADO = {'mae': statistics.mean(abs(x) for x in e),
 'rmse': math.sqrt(statistics.mean(x*x for x in e)),
 'vies': statistics.mean(e)}
print(RESULTADO)
''',
'''RESULTADO = {}
for fator in (0.9, 1.0, 1.1):
    e = [p['estimado']*fator-p['observado'] for p in DADOS]
    RESULTADO[fator] = {'mae': statistics.mean(abs(x) for x in e),
                        'vies': statistics.mean(e)}
print(RESULTADO)
''',
'''taxas = [100*p['observado']/p['denominador'] for p in DADOS]
total_n = sum(p['observado'] for p in DADOS)
total_d = sum(p['denominador'] for p in DADOS)
RESULTADO = {'media_taxas': statistics.mean(taxas),
             'taxa_total': 100*total_n/total_d}
print(RESULTADO)
''',
'''texto = json.dumps(DADOS, sort_keys=True, ensure_ascii=False)
RESULTADO = {'registros': len(DADOS),
 'sha256_dados': hashlib.sha256(texto.encode('utf-8')).hexdigest(),
 'referencia': 'plano local didatico, metros',
 'natureza': 'dados sinteticos'}
print(RESULTADO)
''',
'''treino = [p['observado'] for p in DADOS if p['grupo'] != 'C']
teste = [p['observado'] for p in DADOS if p['grupo'] == 'C']
media_treino = statistics.mean(treino)
RESULTADO = {'media_treino': media_treino,
 'n_treino': len(treino), 'n_teste': len(teste),
 'mae_teste': statistics.mean(abs(x-media_treino) for x in teste)}
print(RESULTADO)
''',
'''def mae(obs, pred):
    if not obs or len(obs) != len(pred):
        raise ValueError('Vetores vazios ou incompatíveis.')
    return statistics.mean(abs(a-b) for a,b in zip(obs,pred))
assert mae([1,2,3], [1,2,3]) == 0
assert mae([1,2,3], [3,4,5]) == 2
try:
    mae([], [])
except ValueError:
    RESULTADO = {'testes': 3, 'situacao': 'aprovados'}
else:
    raise AssertionError('Entrada vazia aceita indevidamente.')
print(RESULTADO)
''']
    return prefix+bodies[ch-1]

def resultado_lab(code):
    context={'print':lambda *args:None}
    exec(compile(code,'laboratorio','exec'),context)
    return context['RESULTADO']

def gabarito_numerico(ch,d):
    r=resultado_lab(codigo_lab(ch,d,''))
    if ch==1:return f'O contrato encontra {r["registros"]} registros e {r["ids_unicos"]} identificadores únicos. A validação deve falhar se uma chave for repetida, um denominador for não positivo ou uma medida não for finita. Alterar o valor observado não muda a contagem, mas ainda precisa respeitar o contrato.'
    if ch==2:return 'As médias por grupo são '+', '.join(f'{g}: {v["media"]:.4f}' for g,v in r.items())+'. Cada grupo contém duas observações. Alterar o primeiro observado afeta o resumo do grupo A, sem alterar B e C. O tamanho da amostra e sua cobertura ainda precisam ser avaliados no caso real.'
    if ch==3:return f'Distância entre primeiro e último ponto = {r["distancia_m"]:.4f} m; azimute = {r["azimute_graus"]:.4f} graus. O cálculo usa coordenadas planas locais. Mudar o observado não altera distância ou direção; mudar coordenadas altera ambos. Não aplique essa fórmula a graus para obter metros.'
    if ch==4:return f'A mediana dos valores disponíveis é {r["mediana"]:.4f}. O terceiro registro recebe esse valor e deve permanecer marcado como tratado. Mudar uma observação pode alterar a mediana e o valor imputado. Em uso preditivo, estime esse parâmetro somente com dados de treino.'
    if ch==5:return 'A quantidade de vizinhos por ponto é '+', '.join(f'{k}: {len(v)}' for k,v in r.items())+'. Alterar observado não muda vizinhança; raio ou coordenada pode mudar. A lista descreve relações, não novos eventos. Confira o tratamento de pontos coincidentes e de distância exatamente igual ao raio.'
    if ch==6:return f'Média de referência = {r["media"]:.4f}; MAE dessa média = {r["mae_media"]:.4f}; MAE da estimativa sintética = {r["mae_estimativa_sintetica"]:.4f}. A comparação usa o mesmo conjunto e serve ao cálculo. Não comprova superioridade de modelo treinado nem generalização a dados reais.'
    if ch==7:return f'MAE = {r["mae"]:.4f}; RMSE = {r["rmse"]:.4f}; viés = {r["vies"]:.4f}. Confira erro por registro e explique diferença entre magnitude e sinal. Esses números não são limites universais de aprovação; uma mudança em observado afeta erro e métricas.'
    if ch==8:return 'O MAE por fator de perturbação é '+', '.join(f'{k:.1f}: {v["mae"]:.4f}' for k,v in r.items())+'. A alteração demonstra sensibilidade aritmética e pode mudar a conclusão. A amplitude entre cenários não é intervalo de confiança: não há distribuição probabilística de erro definida.'
    if ch==9:return f'Média simples das taxas = {r["media_taxas"]:.4f}; taxa dos totais = {r["taxa_total"]:.4f}, ambas na base por cem unidades. A diferença vem dos pesos dos denominadores. Antes de interpretar, confira se a variável pode ser numerador de uma taxa e se população e período são compatíveis.'
    if ch==10:return f'O manifesto identifica {r["registros"]} registros e produz SHA-256 que começa por {r["sha256_dados"][:16]}. Mudar uma observação muda o hash. Isso detecta mudança binária da representação serializada, mas não demonstra qualidade temática, autorização de uso ou validade científica.'
    if ch==11:return f'O treino contém {r["n_treino"]} registros e o grupo reservado contém {r["n_teste"]}. Média de treino = {r["media_treino"]:.4f}; MAE no grupo C = {r["mae_teste"]:.4f}. Mudar um observado do treino pode mudar o baseline; mudar apenas o teste deve alterar avaliação, não o parâmetro aprendido.'
    return 'Os três testes passam: previsão igual à observação tem MAE zero; deslocamento uniforme de duas unidades tem MAE dois; vetor vazio é rejeitado. Acrescente caso incompatível, não finito e uma entrada específica do tema. Testes aritméticos não dispensam revisão da hipótese e da fonte.'

def pagina(doc,title,body,kind='conteudo'):
    p=doc.new_page(width=595.28,height=841.89);num=len(doc)
    p.draw_line((50,43),(545,43),color=GREEN,width=1.3)
    p.insert_text((50,32),'DataGeo Academy | '+title[:75],fontname='helv',fontsize=8,color=NAVY)
    p.insert_text((50,817),'DataGeo Academy | Colecao tecnica | 2026',fontsize=8,color=NAVY)
    p.insert_text((478,817),f'Pagina {num} / 42',fontsize=8,color=NAVY)
    spare,scale=p.insert_htmlbox(fitz.Rect(50,61,545,793),body,css=CSS,scale_low=1)
    if spare<0:raise ValueError(f'Conteúdo excedeu página {num}: {title}. Revise a composição; não reduzir fonte nem criar página vazia.')
    return p

def capa(doc,titulo,area):
    p=doc.new_page(width=595.28,height=841.89)
    p.draw_rect(p.rect,color=NAVY,fill=NAVY)
    for x in range(40,595,40):p.draw_line((x,300),(x,790),color=(.06,.26,.40),width=.4)
    for y in range(300,820,40):p.draw_line((35,y),(565,y),color=(.06,.26,.40),width=.4)
    p.insert_image(fitz.Rect(55,48,330,230),filename=str(ROOT/'LOGOMARCA_2.png'))
    css='body{font-family:sans-serif;color:white;font-size:13pt}h1{font-size:34pt;line-height:1.12}p{line-height:1.5}.tag{color:#6BD66A;font-size:12pt}'
    text=f'<p class="tag">COLEÇÃO ACADÊMICA · DATAGEO ACADEMY</p><h1>{esc(titulo)}</h1><p>{esc(area)}</p><p class="tag">12 capítulos · Laboratórios · Exercícios comentados</p>'
    spare,scale=p.insert_htmlbox(fitz.Rect(55,268,535,690),text,css=css,scale_low=1)
    if spare<0:raise ValueError('Título excedeu capa')
    p.draw_line((55,721),(535,721),color=GREEN,width=2)
    p.insert_text((55,755),'Autoria institucional: DataGeo Academy',fontsize=12,color=GREEN)
    p.insert_text((55,783),'Conhecimento que gera decisoes | Edicao 2.0 | 2026',fontsize=10,color=(.75,.88,.94))

def fundamento(ch,titulo,contexto,caso,etapas,profile,d):
    nome,textos,perguntas=CHAPTERS[ch-1]
    topical=etapas[ch-2][1] if 2<=ch<=6 else contexto if ch==1 else profile['tarefas'][ch-1]
    rows=[['Objeto do estudo',profile['objeto']],['Procedimento em foco',profile['tarefas'][ch-1]],['Risco a controlar',profile['risco']],['Evidência requerida',perguntas[0]]]
    body=f'<div class="kicker">CAPÍTULO {ch:02d} · FUNDAMENTOS E CRITÉRIOS</div><h1>{ch}. {esc(nome)}</h1><h2>{ch}.1 Base conceitual</h2>'+ps(*textos)
    body+=f'<h2>{ch}.2 Aplicação em {esc(titulo)}</h2>'+ps(topical)
    body+=tabela(['ELEMENTO','DECISÃO TÉCNICA'],rows)
    body+=ps('O caso integrador deste volume é: '+caso+' Aplique os critérios acima ao suporte e à finalidade desse caso, separando resultado calculado de interpretação temática.')
    return body

def laboratorio(ch,titulo,d,code,result,profile):
    nome,exp1,exp2=LAB_EXPLANATIONS[ch-1]
    # Cada laboratório tem entrada e saída próprias; valores são calculados, não inventados.
    body=f'<div class="kicker">CAPÍTULO {ch:02d} · LABORATÓRIO REPRODUZÍVEL</div><h1>{ch}.3 {esc(nome)}</h1>'+ps(exp1)
    body+='<h2>Python 3 · Biblioteca padrão</h2><pre>'+esc(code)+'</pre>'
    # Resultado compacto: conteúdo completo acompanha o arquivo-fonte embutido.
    res=json.dumps(result,ensure_ascii=False,sort_keys=True,default=str)
    body+=f'<h2>Resultado de referência</h2><pre>{esc(res)}</pre>'+ps(exp2)
    body+=f'<div class="note">Relação com o tema: {esc(profile["tarefas"][ch-1])} O exemplo é aritmético e sintético; dados e método específicos de {esc(titulo.lower())} devem respeitar as hipóteses discutidas neste capítulo.</div>'
    return body

def exercicios(ch,titulo,caso,profile,d):
    chapter,base,perguntas=CHAPTERS[ch-1]
    m=metricas([p['observado'] for p in d],[p['estimado'] for p in d])
    media=statistics.mean(p['observado'] for p in d)
    codigo=f'{ch:02d}'
    if ch==6:
        table=tabela(['ALTERNATIVA','CONTRIBUIÇÃO','LIMITAÇÃO'],profile['alternativas'])
    else:
        table=tabela(['ID / GRUPO','OBSERVADO','ESTIMADO','DENOM.'],[[p['id']+' / '+p['grupo'],f"{p['observado']:.2f}",f"{p['estimado']:.2f}",p['denominador']] for p in d])
    tasks=[
        f'Exercício {codigo}.A — Cálculo: reproduza o laboratório deste capítulo com os dados abaixo, registre a saída e confira um resultado manualmente. Preserve unidades e explique o significado da operação. Depois substitua o primeiro valor observado por observado + 2 e identifique quais saídas devem mudar.',
        f'Exercício {codigo}.B — Aplicação: no caso “{caso}”, {profile["tarefas"][ch-1][0].lower()+profile["tarefas"][ch-1][1:]} Registre fonte necessária, parâmetro, evidência de verificação e uma condição em que a etapa deve ser interrompida.',
        f'Exercício {codigo}.C — Diagnóstico: responda “{perguntas[1]}”. Construa um exemplo de erro relacionado a {profile["risco"]} e mostre como ele pode produzir saída numericamente plausível, mas incompatível com a decisão.'
    ]
    body=f'<div class="kicker">CAPÍTULO {ch:02d} · EXERCÍCIOS E REVISÃO</div><h1>{ch}.4 Caderno de aplicação</h1>'+table+lista(tasks,True)
    body+=f'<h2>{ch}.5 Comentário de solução</h2>'+ps(
        gabarito_numerico(ch,d),
        f'Conecte {profile["foco"]} ao objeto e período do caso. Critério: {perguntas[0]} A resposta deve identificar fonte, parâmetro e evidência. Diferencie medida, cálculo e hipótese; uma saída plausível não demonstra adequação temática.',
        f'Uma execução sem exceção não elimina {profile["risco"]}. Rastreie a etapa problemática, preserve a entrada original e compare parâmetros. Justifique a correção sem inventar observações ou eliminar registros apenas para melhorar uma métrica.')
    body+=f'<h2>{ch}.6 Critérios de aceite do exercício</h2>'+lista([perguntas[2],'Entrada, procedimento e saída conferidos; divergências justificadas.','Limites de aplicação e próxima verificação registrados.'])
    return body

def gerar(i,j,item):
    titulo,contexto,caso,etapas=item;profile=PROFILES[i];d=dados(i,j)
    doc=fitz.open();capa(doc,titulo,AREAS[i])
    pagina(doc,titulo,'<h1>Folha de rosto e controle documental</h1>'+ps(titulo,AREAS[i],'Autoria institucional e edição: DataGeo Academy.')+tabela(['CAMPO','REGISTRO'],[
        ['Código',f'DGA-LPDF-{i+1:02d}-{j+1:02d}'],['Edição / ano','2.0 / 2026'],['Formato / extensão','PDF pesquisável / 42 páginas'],['Estrutura','12 capítulos; fundamentos, laboratório e exercícios'],['Natureza dos dados','Sintéticos, identificados em todos os laboratórios'],['Objetivo do volume',contexto],['Caso integrador',caso],['Rastreabilidade','Fontes e códigos incorporados ao PDF; referências no final']])+ps(
        'A autoria é institucional. Os laboratórios usam Python 3 e biblioteca padrão para cálculos de referência. Métodos especializados são contextualizados no conteúdo; exemplos numéricos não equivalem a validação de dados reais nem a resultado de cliente.',
        'O controle documental identifica a edição e a finalidade. Ao adaptar os exercícios a um estudo profissional, registre fonte, versões, parâmetros e evidências. Preserve os dados de origem e documente a revisão técnica antes de usar resultados para decisão.')+tabela(['REVISÃO','ALTERAÇÃO'],[['2.0','Expansão em PDF com 12 capítulos e exercícios comentados.'],['Uso em projeto','Registrar data, responsável, fontes e alterações realizadas.']]))
    tocrows=[[f'{n:02d}',title,5+(n-1)*3] for n,(title,text,qs) in enumerate(CHAPTERS,1)]
    pagina(doc,titulo,'<h1>Sumário técnico progressivo</h1>'+tabela(['CAP.','TEMA','PÁGINA'],tocrows)+ps(
        'Cada capítulo ocupa três páginas: conceitos e critérios; laboratório reproduzível; exercícios e comentário de solução. A sequência avança da formulação do problema à revisão da entrega. Os marcadores laterais do PDF permitem navegar diretamente ao capítulo.',
        'O código de cada laboratório e os dados sintéticos acompanham o PDF como arquivos incorporados. Para extraí-los, use um leitor que suporte anexos ou o script de extração fornecido no repositório. A fonte editorial identifica título, área, entradas e respostas de referência.')+tabela(['SEÇÃO COMPLEMENTAR','PÁGINA'],[['Introdução e plano de estudo',4],['Referências e aprofundamento',41],['Projeto final e rubrica de avaliação',42]]))
    pagina(doc,titulo,'<h1>Introdução e plano de estudo</h1>'+ps(contexto,
        f'O objetivo deste livro é apoiar o estudo de {titulo.lower()} com uma sequência verificável. O caso integrador é: {caso} A leitura combina conceitos, procedimentos, cálculos e revisão, conectando a escolha de ferramentas ao problema e ao suporte dos dados.',
        f'Na área {AREAS[i]}, o trabalho exige atenção a {profile["foco"]}. O volume organiza essa atenção em doze capítulos, com exemplos pequenos que podem ser conferidos manualmente. O conjunto sintético permite distinguir falha aritmética, erro de preparação e hipótese de análise, sem apresentar números artificiais como observações de um território real.',
        'O leitor deve conhecer tabelas, códigos, coordenadas e leitura de gráficos. Ao usar uma ferramenta especializada, consulte a documentação da versão efetivamente instalada. Os exemplos Python são independentes e servem à compreensão dos cálculos. Rotinas operacionais precisam de dados autorizados, controle de ambiente e testes próprios.',
        'Recomenda-se ler os conceitos, executar o laboratório e responder às perguntas de diagnóstico nessa ordem. Compare a resposta numérica com a referência e redija uma justificativa temática. Uma divergência deve ser analisada, não apenas corrigida até coincidir com o número apresentado.',
        'O exercício final reúne método, evidências e limitações. A finalidade é aprender a produzir resultados rastreáveis e a reconhecer condições em que faltam dados ou o método é inadequado. A quantidade de páginas não substitui revisão: decisões, unidades, cobertura e avaliação precisam permanecer coerentes do início ao fim.')+tabela(['COMPETÊNCIA','EVIDÊNCIA ESPERADA'],[[str(k),t] for k,(t,text) in enumerate(etapas,1)])+ps('Plano sugerido: um capítulo por sessão de estudo, com execução e revisão do exercício. Reserve uma sessão adicional para comparar cenários e outra para organizar o relatório final. Registre dúvidas, fontes consultadas e decisões de adaptação.'))
    anexos={};toc=[]
    for ch in range(1,13):
        toc.append([1,f'{ch:02d}. {CHAPTERS[ch-1][0]}',len(doc)+1])
        code=codigo_lab(ch,d,titulo);result=resultado_lab(code)
        anexos[f'capitulo_{ch:02d}.py']=code.encode('utf-8')
        pagina(doc,titulo,fundamento(ch,titulo,contexto,caso,etapas,profile,d))
        pagina(doc,titulo,laboratorio(ch,titulo,d,code,result,profile))
        pagina(doc,titulo,exercicios(ch,titulo,caso,profile,d))
    refs=list(dict.fromkeys(REFERENCIAS[i]+['https://docs.python.org/3/library/statistics.html','https://docs.python.org/3/library/math.html']))
    pagina(doc,titulo,'<h1>Referências e aprofundamento</h1>'+ps(
        'As referências abaixo são documentação oficial para consulta dos conceitos operacionais e das ferramentas relacionadas à área. A organização didática e os exemplos sintéticos foram preparados para esta edição. A leitura técnica deve ser complementada com bibliografia especializada, desenho amostral e revisão do uso pretendido.')+lista(refs)+
        '<h2>Como verificar uma referência</h2>'+lista(['Confirme versão do software e seção correspondente ao procedimento utilizado.','Relacione a afirmação à documentação que realmente a sustenta.','Registre parâmetros, unidades, opções e comportamento em dados ausentes.','Teste o exemplo em conjunto conhecido antes de aplicar a uma base extensa.','Separe método documentado de hipótese específica do estudo.'])+ps(
        'As páginas de documentação podem evoluir. Registre a data de consulta e mantenha compatibilidade com seu ambiente. Não atribua à referência uma aprovação da aplicação, da amostra ou do resultado deste livro. A documentação explica funções e métodos; a adequação ao problema requer critérios e evidências.',
        f'Para aprofundar {titulo.lower()}, transforme o caso integrador em um plano de pesquisa ou projeto. Identifique dados adicionais, critérios de seleção, comparação de alternativas e validação independente. Aplique as perguntas dos capítulos como roteiro de revisão e registre o efeito de escolhas relevantes.',
        'Os anexos incorporados incluem os doze laboratórios e o conjunto de dados. A execução pode ser refeita em ambiente Python 3 sem acesso à rede. Eles são uma referência didática de cálculo; não instalam serviços, não publicam dados nem substituem ferramentas especializadas do tema.')+
        tabela(['ANEXO INCORPORADO','CONTEÚDO'],[['dados_sinteticos.json','Seis observações, grupos, coordenadas e valores.'],['capitulo_01.py a capitulo_12.py','Códigos independentes e executáveis.'],['fonte_editorial.json','Tema, área, contexto, caso e capítulos.']]))
    pagina(doc,titulo,'<h1>Projeto final e rubrica de avaliação</h1>'+ps('Projeto: '+caso,
        f'O trabalho deverá demonstrar {profile["foco"]} em um fluxo reproduzível. Escolha fonte autorizada ou mantenha o conjunto sintético identificado. Entregue inventário, critérios, procedimento e relatório. Não substitua falta de dado por resultado inventado.')+tabela(['DIMENSÃO','CRITÉRIO','PONTOS'],[
        ['Escopo','Pergunta, unidade, período e objetivo explícitos.',15],['Dados','Origem, referência, domínio e cobertura documentados.',20],['Método','Etapas e parâmetros justificados.',20],['Avaliação','Baseline, erros e casos inválidos conferidos.',20],['Comunicação','Resultado, limitações e reprodução claros.',15],['Revisão','Erros tratados e evidências preservadas.',10]])+
        '<h2>Sequência de entrega</h2>'+lista(['Descreva a decisão e prepare uma versão pequena da base com resultado verificável.','Registre fontes e aplique regras de preparação com relatório de rejeições.','Execute o método e compare com baseline pertinente à tarefa.','Avalie cenários, resíduos e limitações de suporte ou horizonte.','Produza mapa ou tabela com unidades e origem; organize o procedimento.','Peça a um revisor para reproduzir a execução e justificar divergências.'],True)+
        '<h2>Comentário orientador</h2>'+ps(
        'A melhor entrega não é a de maior complexidade, mas a que responde à pergunta com dados e hipóteses rastreáveis. Erros numéricos precisam de correção; falta de cobertura precisa de reconhecimento e eventualmente coleta; hipótese inadequada exige revisão do desenho. Explicite qual dessas situações foi encontrada.',
        f'No tema {titulo}, examine especialmente {profile["risco"]}. Demonstre uma conferência concreta que detecte esse problema. Uma conclusão válida deve identificar domínio de aplicação, evidência disponível e próxima ação, sem transformar previsão ou estimativa em certeza.',
        'A rubrica orienta estudo e revisão. A pontuação não constitui habilitação profissional ou certificação. Após concluir, registre uma revisão do trabalho, preservando o histórico das alterações e as razões que levaram a mudar dados, parâmetros ou interpretação.'))
    assert len(doc)==42
    doc.set_toc(toc);doc.set_metadata({'title':titulo,'author':'DataGeo Academy','subject':AREAS[i]+' | 12 capítulos técnicos e exercícios','creator':'DataGeo Academy | Compilador Python/PyMuPDF'})
    for name,data in anexos.items():doc.embfile_add(name,data,filename=name,desc='Laboratório didático executável')
    doc.embfile_add('dados_sinteticos.json',json.dumps(d,ensure_ascii=False,indent=2).encode('utf-8'))
    doc.embfile_add('fonte_editorial.json',json.dumps({'titulo':titulo,'area':AREAS[i],'contexto':contexto,'caso':caso,'etapas':etapas,'capitulos':[c[0] for c in CHAPTERS]},ensure_ascii=False,indent=2).encode('utf-8'))
    dest=DEST/(titulo+'.pdf');doc.save(dest,garbage=4,deflate=True);doc.close()
    with fitz.open(dest) as check:
        assert 40<=len(check)<=60
        assert len(check.get_toc())==12
        assert all(len(p.get_text().split())>=180 for p in list(check)[4:40])
    print(f'OK: {titulo} — 42 páginas, 12 capítulos',flush=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--somente');args=parser.parse_args()
    DEST.mkdir(exist_ok=True)
    originals=[('Cartografia Básica Aplicada às Geotecnologias','Cartografia_Basica_Aplicada_Geotecnologias.pdf',53),('Inteligência Artificial Aplicada','Inteligencia_Artificial_Aplicada.pdf',60)]
    for name,filename,pages in originals:
        source=ROOT/'ENTREGA/Livros_Tecnicos'/filename;dest=DEST/(name+'.pdf')
        with fitz.open(source) as d:assert len(d)==pages
        if dest.exists():assert dest.read_bytes()==source.read_bytes(),'Original divergente: não será sobrescrito.'
        else:shutil.copy2(source,dest)
    for i,items in enumerate(CATALOGO):
        for j,item in enumerate(items):
            if item[2] is not None and (not args.somente or args.somente==item[0]):gerar(i,j,item)
    if args.somente:return
    info={'formato':'PDF','edicao':'2.0','areas':[],'autoria_novos':'DataGeo Academy (institucional)'}
    for area,items in zip(AREAS,CATALOGO):
        books=[]
        for titulo,contexto,caso,etapas in items:
            p=DEST/(titulo+'.pdf')
            with fitz.open(p) as d:pages=len(d)
            books.append({'titulo':titulo,'arquivo':p.name,'original':caso is None,'paginas':pages,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
        info['areas'].append({'nome':area,'livros':books})
    (DEST/'catalogo.json').write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()
