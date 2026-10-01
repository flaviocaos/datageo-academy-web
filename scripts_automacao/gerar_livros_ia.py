"""Compila quatro manuscritos independentes; valida e integra com --integrar.

Execute com o Python do ambiente científico. Os PDFs têm 42 páginas com
12 capítulos próprios, código executado, tabelas e exercícios comentados.
Nenhum texto ou laboratório editorial do gerador legado é utilizado.
"""
from pathlib import Path
from html import escape as esc
from importlib.metadata import version
import argparse
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[1]
try:
    import pymupdf as fitz
except ImportError:
    sys.path.insert(0,str(ROOT/'.capas-deps'))
    import pymupdf as fitz
from livros_ia import geopandas, machine_learning, cnns, expansao_urbana
from livros_ia.aprofundamentos import GEO, ML, CNN, URB

LIVROS=[geopandas,machine_learning,cnns,expansao_urbana]
for livro,notas in zip(LIVROS,[GEO,ML,CNN,URB]):
    assert len(livro.CAPITULOS)==len(notas)==12
    for capitulo,(fundamento,leitura) in zip(livro.CAPITULOS,notas):
        capitulo['aprofundamento']=fundamento
        capitulo['leitura_codigo']=leitura
PASTA=ROOT/'livros_academicos'
AREA='Inteligência Artificial e Data Science'
OFICIAL='Inteligência Artificial Aplicada.pdf'
HASH_OFICIAL='e6bc62361f08021138294cd6ad60b12e1ef28f4489fb1debaa42b96615dbe046'
ANTIGOS={
 'Machine Learning Geoespacial.pdf':'a59cedde20427cc55e2fdbb16af5ab9f8c5c8792ba8d58642fd85c1f2ad5dc5f',
 'Deep Learning para Sensoriamento Remoto.pdf':'c2444ef4637e94f8e33b719ee5a50d592e3a9409eb01945e083e2d7c014f2de5',
 'IA Explicável para Análises Geográficas.pdf':'aa1362dda73d15508a5f125f5d962bc54f59338f32240478e6fcf84711881367',
 'IA Generativa na Inteligência Territorial.pdf':'166e131e79daf500b4d6dd0c5900b5bd35482a6014276335fc40a260e78509c4'}
NAVY=(11/255,47/255,91/255); GREEN=(107/255,214/255,106/255)
CSS='''body{font-family:sans-serif;font-size:11pt;line-height:1.45;color:#173651;margin:0}
h1{font-size:20pt;color:#0B2F5B;line-height:1.18;margin:0 0 13pt}
h2{font-size:12pt;color:#117983;margin:13pt 0 6pt;line-height:1.25}
p{margin:0 0 10pt;text-align:justify}
table{border-collapse:collapse;width:100%;font-size:9pt;margin:9pt 0 12pt}
td,th{border:.5pt solid #bfd5e1;padding:6pt;text-align:left}th{background:#0B2F5B;color:white}
tr:nth-child(even){background:#eff5f9}
pre{background:#eff5f9;border-left:3pt solid #16BFD0;padding:9pt;font-family:monospace;font-size:8.5pt;line-height:1.28;white-space:pre-wrap}
li{margin-bottom:7pt}ul,ol{padding-left:18pt}
.kicker{font-size:9pt;color:#14756d;letter-spacing:1pt}
.note{background:#eef8ef;border-left:3pt solid #6BD66A;padding:10pt;font-size:10pt}'''

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ps(*textos):return ''.join('<p>'+esc(t)+'</p>' for t in textos)
def tabela(headers,rows):
    return '<table><tr>'+''.join('<th>'+esc(str(x))+'</th>' for x in headers)+'</tr>'+''.join('<tr>'+''.join('<td>'+esc(str(x))+'</td>' for x in row)+'</tr>' for row in rows)+'</table>'
def lista(items):return '<ul>'+''.join('<li>'+esc(t)+'</li>' for t in items)+'</ul>'

def pagina(doc,titulo,body):
    p=doc.new_page(width=595.28,height=841.89)
    p.draw_line((50,43),(545,43),color=GREEN,width=1.4)
    p.insert_text((50,32),'DataGeo Academy | '+titulo[:74],fontsize=8,color=NAVY)
    p.insert_text((50,817),'DataGeo Academy | Programacao geoespacial | Edicao 3.0',fontsize=8,color=NAVY)
    p.insert_text((478,817),f'Pagina {len(doc)} / 42',fontsize=8,color=NAVY)
    spare,scale=p.insert_htmlbox(fitz.Rect(50,61,545,793),body,css=CSS,scale_low=1)
    if spare<0:raise ValueError(f'Conteúdo excedeu página {len(doc)} de {titulo}')
    return p

def capa(doc,titulo):
    p=doc.new_page(width=595.28,height=841.89)
    p.draw_rect(p.rect,color=NAVY,fill=NAVY)
    for x in range(40,596,40):p.draw_line((x,300),(x,790),color=(.06,.26,.4),width=.4)
    for y in range(300,820,40):p.draw_line((35,y),(565,y),color=(.06,.26,.4),width=.4)
    p.insert_image(fitz.Rect(55,48,330,230),filename=str(ROOT/'LOGOMARCA_2.png'))
    body='<p class="tag">COLEÇÃO ACADÊMICA · DATAGEO ACADEMY</p><h1>'+esc(titulo)+'</h1><p>'+AREA+'</p><p class="tag">12 capítulos próprios · Código executável<br>Tabelas · Exercícios comentados</p>'
    css='body{font-family:sans-serif;color:white;font-size:13pt}h1{font-size:34pt;line-height:1.12}p{line-height:1.5}.tag{color:#6BD66A;font-size:12pt}'
    spare,_=p.insert_htmlbox(fitz.Rect(55,268,535,690),body,css=css,scale_low=1)
    if spare<0:raise ValueError('Capa excedida: '+titulo)
    p.draw_line((55,721),(535,721),color=GREEN,width=2)
    p.insert_text((55,755),'Autoria institucional: DataGeo Academy',fontsize=12,color=GREEN)
    p.insert_text((55,783),'Conhecimento que gera decisoes | Edicao 3.0 | 2026',fontsize=10,color=(.75,.88,.94))

def executar(livro):
    respostas=[]
    for n,c in enumerate(livro.CAPITULOS,1):
        ctx={'__name__':'__laboratorio__','print':lambda *a,**k:None}
        exec(compile(c['codigo'],f'{livro.TITULO}/capitulo_{n:02d}.py','exec'),ctx)
        assert 'RESULTADO' in ctx
        # Não serializar arrays ou tipos de bibliotecas sem conversão explícita.
        json.dumps(ctx['RESULTADO'],ensure_ascii=False,allow_nan=False)
        respostas.append(ctx['RESULTADO'])
    return respostas

def gerar(livro,respostas,ambiente):
    titulo=livro.TITULO;doc=fitz.open();capa(doc,titulo)
    pagina(doc,titulo,'<h1>Folha de rosto e controle documental</h1>'+ps(titulo,'Autoria e edição institucional: DataGeo Academy.')+tabela(['CAMPO','REGISTRO'],[
      ['Edição','3.0 / 2026 / PDF pesquisável / 42 páginas'],
      ['Organização','12 capítulos exclusivos deste tema; teoria, programação e aplicação'],
      ['Dados','Sintéticos e identificados; não representam medições de um município'],
      ['Bibliotecas',', '.join(livro.DEPENDENCIAS)],
      ['Fontes editoriais','scripts_automacao/livros_ia; fonte completa anexada ao PDF'],
      ['Verificação','12 laboratórios executados; asserções e saídas incorporadas'],
      ['Caso integrador',livro.PROJETO]])+ps(
      'O conteúdo deste volume foi escrito para sua sequência temática. A autoria é institucional; não há atribuição a pesquisadores ou revisores externos. A composição usa a identidade visual da Academy, mas os capítulos, exemplos e exercícios são independentes dos outros três volumes desta edição.',
      'Os códigos são completos e executáveis em ambiente com as dependências indicadas. Os exercícios pedem alterações adicionais, e seus comentários orientam a solução. A validação automatizada verifica execução e propriedades declaradas; não constitui revisão científica externa nem certificação de resultados de campo.')+tabela(['REVISÃO','ESCOPO'],[['3.0','Substituição do volume provisório por conteúdo específico e APIs reais.'],['Adaptação','Registrar autor da mudança, fonte, período, parâmetros e evidências.']]))
    pagina(doc,titulo,'<h1>Sumário técnico progressivo</h1>'+tabela(['CAP.','TEMA','PÁGINA'],[[str(n),c['titulo'],5+3*(n-1)] for n,c in enumerate(livro.CAPITULOS,1)])+ps(
      'Cada capítulo possui três partes: fundamentos e uma tabela de decisões; laboratório integral com resultado calculado; exercícios autorais com comentários e uma aplicação ampliada. Os marcadores do PDF levam diretamente ao início de cada capítulo.',
      'Os anexos incluem doze scripts Python independentes, fonte editorial em JSON, saídas de referência e requisitos do ambiente. Use um leitor com suporte a anexos ou o extrator fornecido no projeto. Execute os exemplos após ler o contrato e conferir as dependências.')+tabela(['COMPLEMENTO','PÁGINA'],[['Introdução e percurso de estudo',4],['Referências e ambiente',41],['Projeto integrador e rubrica',42]]))
    pagina(doc,titulo,'<h1>Introdução e percurso de estudo</h1>'+ps(*livro.INTRO))
    toc=[]
    for n,(c,res) in enumerate(zip(livro.CAPITULOS,respostas),1):
        toc.append([1,f'{n:02d}. {c["titulo"]}',len(doc)+1])
        pagina(doc,titulo,f'<div class="kicker">CAPÍTULO {n:02d} · TEORIA E MÉTODO</div><h1>{n}. {esc(c["titulo"])}</h1><h2>{n}.1 Fundamentos</h2>'+ps(*c['teoria'])+'<h2>Hipóteses e aprofundamento técnico</h2>'+ps(c['aprofundamento'])+'<h2>Decisões e limites do procedimento</h2>'+tabela(['ELEMENTO','CONFIGURAÇÃO','INTERPRETAÇÃO'],c['tabela'])+f'<div class="note">{esc(c["revisao"])}</div>')
        texto_res=json.dumps(res,ensure_ascii=False,sort_keys=True)
        pagina(doc,titulo,f'<div class="kicker">CAPÍTULO {n:02d} · PROGRAMAÇÃO</div><h1>{n}.2 Laboratório executável</h1>'+ps('Arquivo incorporado: '+f'capitulo_{n:02d}.py. Execute em Python 3 com as dependências deste volume. O exemplo é independente: imports, entradas, processamento e verificação estão no bloco abaixo.')+'<pre>'+esc(c['codigo'])+'</pre><h2>Resultado de referência calculado</h2><pre>'+esc(texto_res)+'</pre><h2>Leitura do código</h2>'+ps(c['leitura_codigo'])+ps('As asserções verificam o contrato indicado no capítulo. O resultado acima foi produzido pela execução deste código. Valores em bytes e resultados de ponto flutuante podem variar conforme plataforma e versão; conserve as propriedades testadas e as tolerâncias explicitadas.'))
        pagina(doc,titulo,f'<div class="kicker">CAPÍTULO {n:02d} · EXERCÍCIOS AUTORAIS</div><h1>{n}.3 Caderno de aplicação</h1><h2>Exercício A · Modificação controlada</h2>'+ps(c['tarefa'])+'<h2>Comentário de solução</h2>'+ps(c['resposta'])+'<h2>Exercício B · Aplicação ampliada</h2>'+ps(c['ampliacao'])+'<h2>Critérios específicos de revisão</h2>'+ps(c['revisao'])+tabela(['EVIDÊNCIA','REGISTRO A ENTREGAR'],[['Experimento','Código original e modificação com sua hipótese.'],['Resultado','Saídas antes e depois; verificação numérica ou geométrica.'],['Interpretação','Explicação da diferença e limite de aplicação ao território.'],['Reprodução','Versões, parâmetros, seed e arquivo de entrada quando houver.']])+ps('Responda antes de consultar o comentário. A aplicação ampliada é aberta e não possui um único número oficial: sua avaliação depende de cumprir os critérios específicos, conservar o contrato e justificar a hipótese escolhida.'))
    pagina(doc,titulo,'<h1>Referências e ambiente reproduzível</h1>'+ps('Fontes técnicas primárias para consultar assinaturas de API, modelos de dados e hipóteses de uso. A organização didática, os exercícios e os dados sintéticos são próprios deste volume. Documentação de software não substitui avaliação do desenho do estudo.')+lista(livro.REFERENCIAS)+'<h2>Ambiente que executou os laboratórios</h2>'+ps('; '.join(k+': '+v for k,v in ambiente.items()))+'<h2>Instalação e extração</h2><pre>python -m venv .venv\n# Windows: .venv/Scripts/python.exe\npython -m pip install -r requirements.txt\npython capitulo_01.py</pre>'+ps('O requirements.txt está incorporado ao PDF e enumera as dependências do volume. A instalação deve ocorrer no ambiente virtual escolhido. Para PyTorch CPU, use o índice oficial de wheels CPU conforme a documentação da plataforma. Não é necessário baixar dados ou pesos para executar os laboratórios.',
      'Os scripts não dependem de execução prévia de capítulos e os arquivos de saída de demonstração usam diretórios temporários. Para adaptar a dados reais, substitua entradas com contrato equivalente e revise datas, suporte e critérios; não apenas os nomes dos arquivos. O anexo resultados_laboratorios.json permite conferir as saídas da edição.'))
    pagina(doc,titulo,'<h1>Projeto integrador e avaliação</h1>'+ps(livro.PROJETO)+'<h2>Entregáveis</h2>'+lista([
      'Relatório com pergunta, unidade de análise, período, fontes e hipótese do procedimento.',
      'Código organizado em etapas, com contrato de entrada e asserções coerentes com os capítulos.',
      'Tabela de verificação que confronte resultado principal com uma alternativa ou cálculo de referência.',
      'Artefatos reabertos em processo novo, acompanhados de manifesto de versões e parâmetros.',
      'Discussão das limitações específicas e dos dados adicionais necessários para aplicação real.'])+tabela(['DIMENSÃO','CRITÉRIO','PONTOS'],[['Escopo e suporte','Pergunta e unidades explícitas, dados identificados.',15],['Programação','APIs corretas, fluxo reproduzível e tratamento de casos inválidos.',25],['Avaliação','Controles específicos, baseline ou conservação verificável.',25],['Interpretação','Separar resultado numérico, hipótese e conclusão territorial.',20],['Entrega','Arquivos, documentação e reprodução por outro estudante.',15]])+'<h2>Revisão final</h2>'+ps('Escolha dois capítulos que tenham alterado uma decisão do projeto e explique como. Demonstre um caso em que o fluxo deve rejeitar a entrada e outro em que a saída é matematicamente válida, mas inadequada à pergunta. Essa distinção é necessária para concluir a entrega.',
      'O avaliador deve conseguir localizar cada fonte, executar o código e conferir uma saída sem reconstruir escolhas não documentadas. Registre erros encontrados e correções realizadas. Uma métrica elevada ou um mapa bem apresentado não compensa uma referência espacial, data, máscara ou divisão de dados incompatível.'))
    assert len(doc)==42
    doc.set_toc(toc)
    doc.set_metadata({'title':titulo,'author':'DataGeo Academy','subject':AREA+' | Conteúdo independente | Edição 3.0','creator':'DataGeo Academy / Python e PyMuPDF'})
    for n,c in enumerate(livro.CAPITULOS,1):
        doc.embfile_add(f'capitulo_{n:02d}.py',c['codigo'].encode('utf-8'))
    fonte={'titulo':titulo,'introducao':livro.INTRO,'projeto':livro.PROJETO,'referencias':livro.REFERENCIAS,'capitulos':livro.CAPITULOS}
    doc.embfile_add('fonte_editorial.json',json.dumps(fonte,ensure_ascii=False,indent=2).encode('utf-8'))
    doc.embfile_add('resultados_laboratorios.json',json.dumps(respostas,ensure_ascii=False,indent=2).encode('utf-8'))
    doc.embfile_add('requirements.txt',('\n'.join(livro.DEPENDENCIAS)+'\n').encode('utf-8'))
    dest=PASTA/(titulo+'.pdf'); temporario=dest.with_suffix('.novo.pdf')
    doc.save(temporario,garbage=4,deflate=True);doc.close()
    with fitz.open(temporario) as check:
        assert len(check)==42 and len(check.get_toc())==12
        assert len(check.embfile_names())==15
        for page in check[4:40]:
            assert len(page.get_text().split())>=120, 'Página técnica insuficiente'
    temporario.replace(dest)
    return {'titulo':titulo,'arquivo':dest.name,'original':False,'paginas':42,'sha256':sha(dest),
            'conteudo_unico':True,'edicao':'3.0','descricao':livro.DESCRICAO}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--integrar',action='store_true',help='Atualiza catálogo e remove somente os quatro provisórios conferidos.')
    args=parser.parse_args()
    assert sha(PASTA/OFICIAL)==HASH_OFICIAL,'PDF oficial divergente: interrompido.'
    info=json.loads((PASTA/'catalogo.json').read_text(encoding='utf-8'))
    preservados={b['arquivo']:sha(PASTA/b['arquivo']) for a in info['areas'][1:] for b in a['livros']}
    ambiente={'Python':sys.version.split()[0]}
    for nome in ['geopandas','shapely','scikit-learn','numpy','pandas','torch','rasterio','PyMuPDF']:
        ambiente[nome]=version(nome)
    livros=[]; titulos=set(); codigos=set()
    for livro in LIVROS:
        assert len(livro.CAPITULOS)==12
        for c in livro.CAPITULOS:
            assert c['titulo'] not in titulos; titulos.add(c['titulo'])
            assert c['codigo'] not in codigos; codigos.add(c['codigo'])
        respostas=executar(livro)
        livros.append(gerar(livro,respostas,ambiente))
        print(livro.TITULO+': 42 páginas, 12 laboratórios OK',flush=True)
    assert sha(PASTA/OFICIAL)==HASH_OFICIAL
    assert all(sha(PASTA/n)==h for n,h in preservados.items())
    if args.integrar:
        removidos=[]
        # Lista fechada, alvo resolvido dentro de livros_academicos e hash conferido.
        # Não há remoção recursiva e nenhum arquivo oficial entra nesta lista.
        for nome,h in ANTIGOS.items():
            p=(PASTA/nome).resolve()
            assert p.parent==PASTA.resolve() and p.name!=OFICIAL
            if p.exists():
                assert sha(p)==h,'Provisório alterado: remoção interrompida.'
        for nome,h in ANTIGOS.items():
            p=(PASTA/nome).resolve()
            if p.exists():p.unlink()
            removidos.append({'arquivo':nome,'sha256_anterior':h,'removido':not p.exists()})
        original=info['areas'][0]['livros'][0]
        assert original['arquivo']==OFICIAL and original['original']
        info['areas'][0]={'nome':AREA,'livros':[original]+livros}
        info['edicao']='3.0 (IA e Data Science); demais áreas preservadas'
        (PASTA/'catalogo.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        (PASTA/'substituicao_ia.json').write_text(json.dumps({'pdf_oficial_preservado':HASH_OFICIAL,'provisorios':removidos,'novos':livros,'ambiente':ambiente},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        print('Catálogo integrado; quatro provisórios removidos e demais PDFs preservados.')

if __name__=='__main__':main()
