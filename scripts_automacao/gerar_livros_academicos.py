"""Gera 28 livros introdutórios Word e preserva os dois materiais anteriores.
Uso: python scripts_automacao/gerar_livros_academicos.py
O DOCX de IA deve existir. Se só houver PDF, --converter-ia cria reprodução
visual das páginas (requer PyMuPDF); essa conversão não é uma edição textual.
Nunca sobrescreve os dois materiais anteriores. Novos livros: autoria institucional.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import argparse
import hashlib
import importlib.util
import io
import json
import shutil
import sys
import xml.etree.ElementTree as ET
from catalogo_livros import AREAS, CATALOGO, REFERENCIAS

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'livros_academicos'
spec=importlib.util.spec_from_file_location('word',ROOT/'scripts_automacao/gerar_documentos_corporativos.py')
corp=importlib.util.module_from_spec(spec);spec.loader.exec_module(corp)
b=corp.base;W,R=b.W,b.R
IA=DEST/'Inteligência Artificial Aplicada.docx'
CARTO=DEST/'Cartografia Básica Aplicada às Geotecnologias.docx'
WP='http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
PIC='http://schemas.openxmlformats.org/drawingml/2006/picture'

def imagem(body,rid,numero,cx,cy,alt):
    # DrawingML inline: proporção preservada, imagem embutida no pacote.
    p=b.element(body,'p');props=b.element(p,'pPr');b.element(props,'jc',{'val':'center'})
    run=b.element(p,'r');drawing=b.element(run,'drawing')
    inline=ET.SubElement(drawing,f'{{{WP}}}inline',{'distT':'0','distB':'0','distL':'0','distR':'0'})
    ET.SubElement(inline,f'{{{WP}}}extent',{'cx':str(cx),'cy':str(cy)})
    ET.SubElement(inline,f'{{{WP}}}docPr',{'id':str(numero),'name':f'Imagem {numero}','descr':alt})
    graphic=ET.SubElement(inline,f'{{{A}}}graphic')
    data=ET.SubElement(graphic,f'{{{A}}}graphicData',{'uri':PIC})
    pic=ET.SubElement(data,f'{{{PIC}}}pic')
    nv=ET.SubElement(pic,f'{{{PIC}}}nvPicPr')
    ET.SubElement(nv,f'{{{PIC}}}cNvPr',{'id':str(numero),'name':f'imagem{numero}.png'})
    ET.SubElement(nv,f'{{{PIC}}}cNvPicPr')
    fill=ET.SubElement(pic,f'{{{PIC}}}blipFill');ET.SubElement(fill,f'{{{A}}}blip',{f'{{{R}}}embed':rid})
    ET.SubElement(ET.SubElement(fill,f'{{{A}}}stretch'),f'{{{A}}}fillRect')
    sp=ET.SubElement(pic,f'{{{PIC}}}spPr');xf=ET.SubElement(sp,f'{{{A}}}xfrm')
    ET.SubElement(xf,f'{{{A}}}off',{'x':'0','y':'0'});ET.SubElement(xf,f'{{{A}}}ext',{'cx':str(cx),'cy':str(cy)})
    ET.SubElement(ET.SubElement(sp,f'{{{A}}}prstGeom',{'prst':'rect'}),f'{{{A}}}avLst')

def pacote(doc,body,dest,media,fonte,autor):
    sect=b.element(body,'sectPr')
    for tag,rel in [('headerReference','rId2'),('footerReference','rId3')]:
        node=b.element(sect,tag,{'type':'default'});node.set(f'{{{R}}}id',rel)
    b.element(sect,'pgSz',{'w':11906,'h':16838})
    b.element(sect,'pgMar',{'top':1134,'right':1134,'bottom':1134,'left':1134,'header':567,'footer':567,'gutter':0})
    with ZipFile(ROOT/'templates_carreira/modelo_relatorio_tecnico.docx') as z:
        parts={n:z.read(n) for n in z.namelist()}
    header=ET.Element(f'{{{W}}}hdr');b.paragraph(header,'DataGeo Academy | Livros acadêmicos · 2026','Caption')
    footer=ET.Element(f'{{{W}}}ftr');p=b.paragraph(footer,'DataGeo Academy · Página ','Caption');b.field(p,'PAGE')
    b.element(b.element(p,'r'),'t',text=' de ');b.field(p,'NUMPAGES')
    parts.update({'word/document.xml':b.xml(doc),'word/header1.xml':b.xml(header),'word/footer1.xml':b.xml(footer),'datageo/fonte.txt':fonte.encode('utf-8')})
    relationships=''
    for i,(nome,conteudo) in enumerate(media,1):
        parts['word/media/'+nome]=conteudo
        relationships+=f'<Relationship Id="rIdLivro{i}" Type="{R}/image" Target="media/{nome}"/>'
    parts['word/_rels/document.xml.rels']=parts['word/_rels/document.xml.rels'].replace(b'</Relationships>',(relationships+'</Relationships>').encode('utf-8'))
    parts['[Content_Types].xml']=parts['[Content_Types].xml'].replace(b'</Types>',b'<Default Extension="png" ContentType="image/png"/><Default Extension="txt" ContentType="text/plain"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/></Types>')
    core=ET.Element('{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}coreProperties')
    ET.SubElement(core,'{http://purl.org/dc/elements/1.1/}title').text=dest.stem
    ET.SubElement(core,'{http://purl.org/dc/elements/1.1/}creator').text=autor
    parts['docProps/core.xml']=ET.tostring(core,encoding='utf-8',xml_declaration=True)
    parts['_rels/.rels']=parts['_rels/.rels'].replace(b'</Relationships>',b'<Relationship Id="rIdMetadata" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/></Relationships>')
    with ZipFile(dest,'w',ZIP_DEFLATED) as z:
        for n,value in parts.items():z.writestr(n,value)

def fonte_livro(titulo,contexto,caso,etapas,area,refs):
    caminho=' → '.join(t for t,texto in etapas)
    intro=[contexto,
        f'Este volume integra a área {area} e organiza o estudo de {titulo.lower()} a partir de uma pergunta concreta: {caso[0].lower()+caso[1:]} A proposta é explicitar dados, hipóteses, procedimentos e critérios de avaliação antes de interpretar produtos ou automatizar decisões.',
        'O território reúne observações produzidas em escalas, datas e condições diferentes. Por isso, um resultado só pode ser compreendido quando sua unidade de análise, referência espacial, cobertura e origem estão declaradas. A compatibilidade de formatos não garante compatibilidade de significado. O leitor deve reconhecer essas diferenças, documentar transformações e distinguir evidência observada, estimativa e hipótese de trabalho.',
        f'A sequência técnica avança por cinco etapas: {caminho}. A ordem foi escolhida para conectar definição do problema, preparação, execução, avaliação e comunicação. Cada capítulo apresenta o conceito central e uma orientação de aplicação ao caso de estudo; o exercício final reúne as evidências necessárias para revisar o processo.',
        'O público inclui estudantes e profissionais que buscam uma introdução organizada ao tema. Recomenda-se conhecer tabelas, coordenadas, indicadores e leitura de mapas. Quando houver uso de ferramentas, confirme versões e documentação do ambiente escolhido. Os exemplos são propostas didáticas: não representam resultado de cliente, validação de instalação ou certificação de produto cartográfico.',
        'Ao concluir a leitura, o estudante deverá elaborar um fluxo justificável, identificar limitações de dados e métodos e comunicar resultados proporcionais às evidências. O material pode ser usado para leitura individual, discussão orientada ou preparação de um projeto. A aplicação profissional exige aprofundamento, revisão e responsabilidade compatíveis com a finalidade.'
    ]
    return intro

def gerar_novo(area,titulo,contexto,caso,etapas,refs):
    doc=ET.Element(f'{{{W}}}document');body=b.element(doc,'body')
    b.paragraph(body,'DATAGEO ACADEMY','Brand')
    b.paragraph(body,'COLEÇÃO ACADÊMICA · INTELIGÊNCIA GEOGRÁFICA','Subtitle')
    b.paragraph(body,titulo,'Title');b.paragraph(body,area,'Subtitle')
    from PIL import Image
    logo=ROOT/'LOGOMARCA_2.png'
    with Image.open(logo) as im:width,height=im.size
    imagem(body,'rIdLivro1',1,3600000,round(3600000*height/width),'Logotipo DataGeo Academy')
    b.paragraph(body,'Autoria institucional: DataGeo Academy','Subtitle')
    b.paragraph(body,'Edição 1.0 · 2026','Caption')
    b.paragraph(body,'Conhecimento que gera decisões','Subtitle')
    corp.pagebreak(body)
    b.paragraph(body,'FOLHA DE ROSTO','Subtitle');b.paragraph(body,titulo,'Title')
    b.table(body,['RESPONSABILIDADE EDITORIAL','IDENTIFICAÇÃO'],[
        ['Autoria institucional','DataGeo Academy'],['Organização e edição','DataGeo Academy'],
        ['Coleção / área',area],['Ano / edição','2026 / 1.0'],['Natureza','Livro introdutório técnico-didático'],
        ['Identificador',f'DGA-LA-{AREAS.index(area)+1:02d}-{CATALOGO[AREAS.index(area)].index((titulo,contexto,caso,etapas))+1:02d}']])
    b.paragraph(body,'Esta edição institucional apresenta introdução detalhada, capítulos técnicos progressivos e exercício orientado. A organização conecta conceitos, procedimentos, aplicação e critérios de revisão.','Note')
    corp.pagebreak(body)
    entradas=[('1. Introdução',1)]+[(f'{i+2}. {t}',i+2) for i,(t,txt) in enumerate(etapas)]+[('7. Exercício integrador',7),('8. Referências e aprofundamento',8)]
    corp.sumario(body,entradas);corp.pagebreak(body)
    corp.heading(body,'1. Introdução',1)
    intro=fonte_livro(titulo,contexto,caso,etapas,area,refs)
    for text in intro:b.paragraph(body,text)
    fonte=[f'# {titulo}','Autoria institucional: DataGeo Academy','## 1. Introdução',*intro]
    for i,(heading,text) in enumerate(etapas,2):
        corp.heading(body,f'{i}. {heading}',i)
        b.paragraph(body,f'{i}.1 Conceitos e critérios','Heading2');b.paragraph(body,text)
        b.paragraph(body,f'{i}.2 Aplicação ao estudo','Heading2')
        app=f'No estudo proposto — {caso[0].lower()+caso[1:]} — esta etapa deve produzir um registro de método e uma evidência verificável. Relacione as decisões de {heading.lower()} às fontes utilizadas, descreva os parâmetros escolhidos e compare o resultado com o critério definido antes da execução.'
        b.paragraph(body,app)
        b.paragraph(body,f'{i}.3 Pergunta de revisão','Heading2')
        pergunta=f'Quais dados, hipóteses e critérios permitem justificar {heading.lower()} neste caso? Identifique uma situação em que o procedimento seria inadequado e explique como detectá-la ou corrigir o fluxo.'
        b.paragraph(body,pergunta)
        fonte += [f'## {i}. {heading}',text,app,pergunta]
    corp.heading(body,'7. Exercício integrador',7)
    b.paragraph(body,'Objetivo: '+caso)
    b.table(body,['ENTREGA','CRITÉRIO DE REVISÃO'],[
        ['Plano de trabalho','Pergunta, área, período e unidade de análise explícitos.'],
        ['Inventário e dicionário','Fontes, versões, tipos, unidades e referência espacial documentados.'],
        ['Procedimento','Cinco etapas aplicadas com parâmetros e justificativa.'],
        ['Evidências','Resultados intermediários e finais conferidos por exemplos conhecidos.'],
        ['Conclusão','Limitações, interpretação e recomendações proporcionais às evidências.']])
    b.paragraph(body,'Reproduza uma execução em ambiente separado e confira os resultados. Discuta uma hipótese alternativa e um possível erro de interpretação. Entregue fontes autorizadas, procedimento e relatório de revisão; não invente medidas, resultados ou validações não executadas.')
    corp.heading(body,'8. Referências e aprofundamento',8)
    for ref in refs:b.paragraph(body,ref)
    b.paragraph(body,'Fontes oficiais consultadas em outubro de 2026. A documentação descreve ferramentas e métodos; exemplos e organização desta edição são conteúdo didático da DataGeo Academy. Consulte também bibliografia especializada e orientação profissional para aprofundamento.','Note')
    fonte+=['## 7. Exercício integrador',caso,'## 8. Referências',*refs]
    pacote(doc,body,DEST/(titulo+'.docx'),[(logo.name,logo.read_bytes())],'\n\n'.join(fonte),'DataGeo Academy')

def converter_ia():
    # Mantém conteúdo e paginação do PDF: páginas completas como imagens de 144 DPI.
    # Não reescreve, resume ou atribui novos autores ao material original.
    if IA.exists():return
    try:import pymupdf
    except ImportError:
        sys.path.insert(0,str(ROOT/'.capas-deps'));import pymupdf
    pdf=ROOT/'ENTREGA/Livros_Tecnicos/Inteligencia_Artificial_Aplicada.pdf'
    source=pymupdf.open(pdf)
    doc=ET.Element(f'{{{W}}}document');body=b.element(doc,'body');media=[]
    for i,page in enumerate(source,1):
        if i>1:corp.pagebreak(body)
        pix=page.get_pixmap(dpi=144,alpha=False)
        img=pix.tobytes('png');media.append((f'pagina_{i:03d}.png',img))
        cx=5800000;cy=round(cx*page.rect.height/page.rect.width)
        # Cabe na área útil A4 com espaço para cabeçalho/rodapé.
        if cy>8700000:cx=round(cx*8700000/cy);cy=8700000
        imagem(body,f'rIdLivro{i}',i,cx,cy,f'Página {i} do PDF original de Inteligência Artificial Aplicada')
        b.paragraph(body,f'Página original {i} · Reprodução visual do PDF','Caption')
    fonte='Conversão visual do PDF original. Conteúdo integral preservado em imagens, sem edição textual.\n'+''.join(page.get_text() for page in source)
    pacote(doc,body,IA,media,fonte,'Conforme autoria do PDF original')
    return {'pdf':str(pdf.relative_to(ROOT)),'sha256_pdf':hashlib.sha256(pdf.read_bytes()).hexdigest(),'paginas':len(source),'tipo':'DOCX com reprodução visual integral do PDF; não é o DOCX original editável.'}

def main():
    manifest=DEST/'catalogo.json'
    if manifest.exists() and json.loads(manifest.read_text(encoding='utf-8')).get('formato')=='PDF':
        raise SystemExit('Acervo migrado definitivamente para PDF. Execute gerar_livros_pdf.py; não recriar os DOCX curtos.')
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--converter-ia',action='store_true');args=parser.parse_args()
    DEST.mkdir(exist_ok=True)
    if not CARTO.exists():
        sources=list((ROOT.parent/'PROJETOS_E_CURSOS/LIVROS_TECNICOS').rglob('Cartografia_Basica_Aplicada_Geotecnologias.docx'))
        if len(sources)!=1:raise FileNotFoundError('Informe e copie o original de Cartografia para livros_academicos.')
        shutil.copy2(sources[0],CARTO)
    conversao=converter_ia() if args.converter_ia else None
    total=0
    for area,itens,refs in zip(AREAS,CATALOGO,REFERENCIAS):
        assert len(itens)==5
        for titulo,contexto,caso,etapas in itens:
            if caso is None:continue
            gerar_novo(area,titulo,contexto,caso,etapas,refs);total+=1
    assert total==28
    manifest=DEST/'catalogo.json'
    info={'areas':[{ 'nome':a,'livros':[{'titulo':t,'arquivo':t+'.docx','original':c is None} for t,d,c,e in it]} for a,it in zip(AREAS,CATALOGO)],'autoria_novos':'DataGeo Academy (institucional)','cartografia_sha256':hashlib.sha256(CARTO.read_bytes()).hexdigest()}
    if conversao:info['conversao_ia']=conversao
    elif manifest.exists():
        antigo=json.loads(manifest.read_text(encoding='utf-8'))
        if 'conversao_ia' in antigo:info['conversao_ia']=antigo['conversao_ia']
    manifest.write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'{total} novos documentos com capa, folha de rosto, autoria, sumário e introdução gerados.')
    if not IA.exists():print('Pendente: original DOCX de IA ou conversão explicitamente selecionada com --converter-ia.')

if __name__=='__main__':main()
