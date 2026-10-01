"""Verifica 30 DOCX, estrutura dos 28 novos e original preservado. Python padrão."""
from pathlib import Path
from zipfile import ZipFile
from urllib.parse import unquote
from html.parser import HTMLParser
import hashlib
import json
import re
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
W='http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS={'w':W}

class Parser(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a':self.links.append(a)

def main():
    info=json.loads((ROOT/'livros_academicos/catalogo.json').read_text(encoding='utf-8'))
    if info.get('formato')=='PDF':
        from verificar_livros_pdf import main as verificar_pdf
        return verificar_pdf()
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    sec=html[html.index('<section class="resources academic-books"'):html.index('<section class="resources" id="apresentacoes-tecnicas"')]
    books=re.findall(r'<button[^>]*class="course-tab academic-tab"[^>]*>(.*?)</button>',sec)
    courses=re.findall(r'<button[^>]*class="course-tab"[^>]*>(.*?)</button>',html)
    assert books==courses and len(books)==6
    panels=re.findall(r'<div class="academic-panel".*?(?=<div class="academic-panel"|<p class="academic-note")',sec,re.S)
    assert len(panels)==6 and all(p.count('class="resource-card academic-card"')==5 for p in panels)
    assert ' hidden' not in panels[0].split('>')[0] and all(' hidden' in p.split('>')[0] for p in panels[1:])
    parser=Parser();parser.feed(sec);assert len(parser.links)==30
    page=Parser();page.feed(html);assert len(page.ids)==len(set(page.ids))
    for a in parser.links:
        f=(ROOT/unquote(a['href'])).resolve()
        assert f.is_relative_to(ROOT) and f.is_file()
        assert a.get('download')==f.name and f.suffix=='.docx' and 'target' not in a
    meta=json.loads((ROOT/'livros_academicos/catalogo.json').read_text(encoding='utf-8'))
    assert len(list((ROOT/'livros_academicos').glob('*.docx')))==30
    carto=ROOT/'livros_academicos/Cartografia Básica Aplicada às Geotecnologias.docx'
    assert hashlib.sha256(carto.read_bytes()).hexdigest()==meta['cartografia_sha256']
    source=next((ROOT.parent/'PROJETOS_E_CURSOS/LIVROS_TECNICOS').rglob('Cartografia_Basica_Aplicada_Geotecnologias.docx'),None)
    if source:assert source.read_bytes()==carto.read_bytes()
    novos=0
    for area in meta['areas']:
        for book in area['livros']:
            f=ROOT/'livros_academicos'/book['arquivo']
            with ZipFile(f) as z:
                assert z.testzip() is None
                for name in z.namelist():
                    if name.endswith(('.xml','.rels')):ET.fromstring(z.read(name))
                if book['original']:continue
                novos+=1
                body=ET.fromstring(z.read('word/document.xml'))
                text=' '.join(n.text or '' for n in body.findall('.//w:t',NS))
                assert book['titulo'] in text and 'FOLHA DE ROSTO' in text
                assert 'Autoria institucional: DataGeo Academy' in text
                assert len(text.split())>800
                fonte=z.read('datageo/fonte.txt').decode('utf-8')
                intro=fonte.split('## 1. Introdução')[1].split('## 2.')[0]
                assert len(intro.split())>250
                assert 'DataGeo Academy' in z.read('word/header1.xml').decode('utf-8')
                assert ' TOC ' in z.read('word/document.xml').decode('utf-8')
                headings=[p for p in body.findall('.//w:p',NS) if p.find('w:pPr/w:pStyle',NS) is not None and p.find('w:pPr/w:pStyle',NS).get(f'{{{W}}}val')=='Heading1']
                assert len(headings)==8
                anchors={n.get(f'{{{W}}}name') for n in body.findall('.//w:bookmarkStart',NS)}
                assert all(n.get(f'{{{W}}}anchor') in anchors for n in body.findall('.//w:hyperlink',NS))
                assert body.findall('.//w:drawing',NS) and z.read('word/media/LOGOMARCA_2.png')==(ROOT/'LOGOMARCA_2.png').read_bytes()
    assert novos==28
    if 'conversao_ia' in meta:
        with ZipFile(ROOT/'livros_academicos/Inteligência Artificial Aplicada.docx') as z:
            pages=[n for n in z.namelist() if n.startswith('word/media/pagina_')]
            assert len(pages)==meta['conversao_ia']['paginas']
            assert 'Conversão visual' in z.read('datageo/fonte.txt').decode('utf-8')
    print('OK: 6 abas idênticas aos minicursos, 5 livros por aba, 30 downloads e 28 novos DOCX estruturados.')

if __name__=='__main__':main()
