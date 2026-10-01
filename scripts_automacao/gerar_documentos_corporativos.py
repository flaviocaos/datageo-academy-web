"""Converte os quarenta guias em DOCX com cabeçalho, sumário e revisão técnica.

Uso: python scripts_automacao/gerar_documentos_corporativos.py
Na primeira execução lê os Markdown. Após sua remoção, reutiliza o conteúdo
incorporado ao DOCX, permitindo regenerar sem depender de fontes apagadas.
Não remove os Markdown; exclua-os somente após validar os documentos gerados.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import importlib.util
import re
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('word_base',ROOT/'templates_carreira/gerar_modelo_relatorio.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
W,R=base.W,base.R
FOLDERS=['portfolios_cases','roadmaps_aprendizado','exercicios_praticos','glossarios_tecnicos']
TYPES=['Estudo de caso demonstrativo','Plano de desenvolvimento profissional','Caderno técnico de exercícios','Referência técnica de conceitos']


def inline(parent,texto,style='Normal'):
    p=base.element(parent,'p');base.element(base.element(p,'pPr'),'pStyle',{'val':style})
    for parte in re.split(r'(\*\*.*?\*\*)',texto):
        if not parte:continue
        run=base.element(p,'r')
        if parte.startswith('**') and parte.endswith('**'):
            base.element(base.element(run,'rPr'),'b');parte=parte[2:-2]
        base.element(run,'t',text=parte)
    return p


def heading(body,title,number,level=1):
    p=base.paragraph(body,title,'Heading1' if level==1 else 'Heading2')
    start=base.element(p,'bookmarkStart',{'id':number,'name':f'Sec_{number:03d}'})
    p.insert(1,start)
    base.element(p,'bookmarkEnd',{'id':number})
    return p


def sumario(body,entries):
    base.paragraph(body,'SUMÁRIO','Subtitle')
    base.paragraph(body,'Navegue pelos títulos abaixo. No Word, atualize o sumário após editar o conteúdo para incluir a paginação atual.', 'Note')
    p=base.element(body,'p')
    base.element(base.element(p,'r'),'fldChar',{'fldCharType':'begin','dirty':'true'})
    base.element(base.element(p,'r'),'instrText',text=' TOC \\o "1-1" \\h \\z \\u ')
    base.element(base.element(p,'r'),'fldChar',{'fldCharType':'separate'})
    for text,anchor in entries:
        p=base.element(body,'p');base.element(base.element(p,'pPr'),'pStyle',{'val':'TOC1'})
        link=base.element(p,'hyperlink',{'anchor':f'Sec_{anchor:03d}'})
        run=base.element(link,'r');props=base.element(run,'rPr');base.element(props,'color',{'val':'167380'})
        base.element(run,'t',text=text)
    base.element(base.element(base.element(body,'p'),'r'),'fldChar',{'fldCharType':'end'})


def pagebreak(body):
    base.element(base.element(base.element(body,'p'),'r'),'br',{'type':'page'})


def gerar(fonte,destino,tipo):
    lines=fonte.splitlines();title=lines[0].lstrip('# ')
    document=ET.Element(f'{{{W}}}document');body=base.element(document,'body')
    base.paragraph(body,'DataGeo Academy','Brand')
    base.paragraph(body,'BIBLIOTECA CORPORATIVA · INTELIGÊNCIA GEOGRÁFICA','Subtitle')
    base.paragraph(body,title,'Title')
    base.paragraph(body,tipo,'Subtitle')
    base.table(body,['CONTROLE DOCUMENTAL','REGISTRO'],[
        ['Identificação',destino.stem],['Edição','1.0 · Material demonstrativo / formativo'],
        ['Elaboração','DataGeo Academy'],['Classificação','Uso educacional e desenvolvimento profissional'],
        ['Revisão do usuário','[Responsável / data / versão de aplicação]']])
    base.paragraph(body,'FINALIDADE E USO','Heading2')
    base.paragraph(body,'Documento técnico editável para orientação e prática. Os exemplos são didáticos e não constituem laudo assinado, avaliação de local real ou resultado de cliente. Adapte dados, escopo e critérios antes de usar em um serviço.', 'Note')
    base.paragraph(body,'Este material reúne orientação de método, desenvolvimento, revisão e evidências para apoiar entregas rastreáveis.', 'Normal')
    # Sumário é preenchido com âncoras existentes e contém um campo TOC atualizável.
    titulos=[s[3:].strip() for s in lines if s.startswith('## ')]
    entries=[('1. Identificação e aplicação',1)]
    entries += [(f'{n+2}. {t}',n+2) for n,t in enumerate(titulos)]
    entries.append((f'{len(entries)+1}. Conclusão, revisão e emissão',len(entries)+1))
    pagebreak(body);sumario(body,entries);pagebreak(body)
    heading(body,'1. Identificação e aplicação',1)
    base.table(body,['CAMPO','PREENCHIMENTO'],[
        ['Projeto / atividade','[Definir contexto e objetivo]'],['Dados / origem / período','[Identificar fontes, versões e autorização de uso]'],
        ['Ferramentas / parâmetros','[Registrar ambiente, versões e escolhas]'],['Critérios de qualidade','[Definir resultados esperados e tolerâncias]'],
        ['Limitações','[Distinguir dados sintéticos e evidências reais]']])
    base.paragraph(body,'Aplique o conteúdo ao problema definido, preserve fontes e registre o método. Referência espacial, unidades, seleção de dados e critérios de avaliação devem ser conhecidos antes da interpretação dos resultados.', 'Normal')
    sec=1;bookmark=1000;code=False;paragraphs=[];i=1
    def flush():
        if paragraphs:inline(body,' '.join(paragraphs));paragraphs.clear()
    while i<len(lines):
        line=lines[i].strip()
        if line.startswith('```'):
            flush();code=not code;i+=1;continue
        if code:
            base.paragraph(body,lines[i],'Code');i+=1;continue
        if line.startswith('## '):
            flush();sec+=1;heading(body,f'{sec}. {line[3:]}',sec);i+=1;continue
        if line.startswith('### '):
            flush();bookmark+=1;heading(body,line[4:],bookmark,2);i+=1;continue
        if line.startswith('|'):
            flush();rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                cells=[c.strip().replace('**','') for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?',c.replace(' ','')) for c in cells):rows.append(cells)
                i+=1
            if rows:base.table(body,rows[0],rows[1:])
            continue
        if not line:
            flush();i+=1;continue
        if line.startswith('**DataGeo Academy'):
            i+=1;continue
        if line.startswith('- '):
            flush();inline(body,'• '+line[2:],'ListText');i+=1;continue
        if re.match(r'^\d+\. ',line):
            flush();inline(body,line,'ListText');i+=1;continue
        paragraphs.append(line);i+=1
    flush();sec+=1;heading(body,f'{sec}. Conclusão, revisão e emissão',sec)
    base.paragraph(body,'Documente o que foi executado, o resultado observado e as limitações. Emita conclusão apenas proporcional às evidências disponíveis. O conteúdo deste guia não comprova por si só precisão cartográfica, conformidade ambiental ou competência profissional.', 'Normal')
    base.table(body,['ITEM DE REVISÃO','REGISTRO / DECISÃO'],[
        ['Escopo e dados','[Verificados / pendências]'],['Método e resultados','[Evidências / limitações]'],
        ['Exceções e ajustes','[Justificativa / aprovação]'],['Elaboração / revisão','[Nomes / função / data]'],
        ['Situação da emissão','[Rascunho / revisado / aprovado para a finalidade definida]']])
    base.paragraph(body,'Quando houver utilização profissional, a revisão, assinatura e responsabilidade são dos profissionais habilitados para o serviço. Não atribua assinatura ou aprovação a esta edição de referência.', 'Note')
    sect=base.element(body,'sectPr')
    for tag,rel in [('headerReference','rId2'),('footerReference','rId3')]:
        n=base.element(sect,tag,{'type':'default'});n.set(f'{{{R}}}id',rel)
    base.element(sect,'pgSz',{'w':11906,'h':16838})
    base.element(sect,'pgMar',{'top':1134,'right':1134,'bottom':1134,'left':1134,'header':567,'footer':567,'gutter':0})
    with ZipFile(ROOT/'templates_carreira/modelo_relatorio_tecnico.docx') as z:
        parts={n:z.read(n) for n in z.namelist()}
    styles=ET.fromstring(parts['word/styles.xml'])
    for st in styles.findall(f'{{{W}}}style'):
        name=st.get(f'{{{W}}}styleId')
        size={'Title':48,'Heading1':28,'Heading2':24}.get(name)
        if size:st.find(f'{{{W}}}rPr/{{{W}}}sz').set(f'{{{W}}}val',str(size))
    for name,font,size in [('Code','Consolas',17),('ListText','Calibri',20),('TOC1','Calibri',21)]:
        st=base.element(styles,'style',{'type':'paragraph','styleId':name});base.element(st,'name',{'val':name});base.element(st,'basedOn',{'val':'Normal'})
        pp=base.element(st,'pPr');base.element(pp,'spacing',{'after':90})
        rp=base.element(st,'rPr');base.element(rp,'rFonts',{'ascii':font,'hAnsi':font});base.element(rp,'sz',{'val':size})
        if name=='Code':base.element(pp,'shd',{'fill':'EFF4F8'})
    header=ET.Element(f'{{{W}}}hdr');base.paragraph(header,'DataGeo Academy  |  Biblioteca corporativa · Edição 1.0','Caption')
    footer=ET.Element(f'{{{W}}}ftr');p=base.paragraph(footer,'Material técnico / demonstrativo  •  Página ','Caption')
    base.field(p,'PAGE');base.element(base.element(p,'r'),'t',text=' de ');base.field(p,'NUMPAGES')
    parts.update({'word/document.xml':base.xml(document),'word/styles.xml':base.xml(styles),
                  'word/header1.xml':base.xml(header),'word/footer1.xml':base.xml(footer)})
    # Fonte textual incorporada e registrada no contêiner; permite regeneração.
    parts['datageo/fonte.txt']=fonte.encode('utf-8')
    # Mantém o namespace padrão exigido por leitores que detectam DOCX pelo manifesto.
    parts['[Content_Types].xml']=parts['[Content_Types].xml'].replace(
        b'</Types>',b'<Default Extension="txt" ContentType="text/plain"/></Types>')
    with ZipFile(destino,'w',ZIP_DEFLATED) as z:
        for n,data in parts.items():z.writestr(n,data)


def main():
    total=0
    for pasta,tipo in zip(FOLDERS,TYPES):
        dir=ROOT/pasta
        fontes=sorted(dir.glob('*.md'))
        if fontes:
            assert len(fontes)==10
            itens=[(p.read_text(encoding='utf-8'),p.with_suffix('.docx')) for p in fontes]
        else:
            docs=sorted(dir.glob('*.docx'));assert len(docs)==10
            itens=[]
            for p in docs:
                with ZipFile(p) as z:itens.append((z.read('datageo/fonte.txt').decode('utf-8'),p))
        for source,dest in itens:gerar(source,dest,tipo);total+=1
    print(f'{total} documentos DOCX gerados com cabeçalho, sumário navegável e conteúdo técnico.')


if __name__=='__main__':main()
