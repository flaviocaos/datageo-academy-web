"""Valida 30 PDFs, originais intactos, conteúdo, exercícios e links reais."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote
import hashlib
import json
import math
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
try:import pymupdf as fitz
except ImportError:
    sys.path.insert(0,str(ROOT/'.capas-deps'));import pymupdf as fitz

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.ids=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a':self.links.append(a)

def main():
    folder=ROOT/'livros_academicos'
    info=json.loads((folder/'catalogo.json').read_text(encoding='utf-8'))
    assert info['formato']=='PDF' and len(info['areas'])==6
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    sec=html[html.index('<section class="resources academic-books"'):html.index('<section class="resources" id="apresentacoes-tecnicas"')]
    tabs=re.findall(r'<button[^>]*class="course-tab academic-tab"[^>]*>(.*?)</button>',sec)
    courses=re.findall(r'<button[^>]*class="course-tab"[^>]*>(.*?)</button>',html)
    assert tabs==courses and len(tabs)==6
    panels=re.findall(r'<div class="academic-panel".*?(?=<div class="academic-panel"|<p class="academic-note")',sec,re.S)
    assert len(panels)==6 and all(p.count('class="resource-card academic-card"')==5 for p in panels)
    assert '.docx' not in sec and sec.count('download=')==30
    links=Links();links.feed(sec);assert len(links.links)==30
    page=Links();page.feed(html);assert len(page.ids)==len(set(page.ids))
    for a in links.links:
        p=(ROOT/unquote(a['href'])).resolve()
        assert p.is_relative_to(folder) and p.is_file() and p.suffix=='.pdf'
        assert a.get('download')==p.name and 'target' not in a
    files=list(folder.glob('*.pdf'));assert len(files)==30
    originals={
       'Cartografia Básica Aplicada às Geotecnologias.pdf':('Cartografia_Basica_Aplicada_Geotecnologias.pdf',53),
       'Inteligência Artificial Aplicada.pdf':('Inteligencia_Artificial_Aplicada.pdf',60)}
    total,labs,words=0,0,0
    for area in info['areas']:
        assert len(area['livros'])==5
        for book in area['livros']:
            p=folder/book['arquivo']
            assert hashlib.sha256(p.read_bytes()).hexdigest()==book['sha256']
            with fitz.open(p) as d:
                assert 40<=len(d)<=60 and len(d)==book['paginas']
                total+=len(d)
                if p.name in originals:
                    name,n=originals[p.name]
                    assert len(d)==n and p.read_bytes()==(ROOT/'ENTREGA/Livros_Tecnicos'/name).read_bytes()
                    continue
                assert len(d)==42 and len(d.get_toc())==12
                assert [t[2] for t in d.get_toc()]==list(range(5,41,3))
                assert 'DataGeo Academy' in d.metadata['author']
                assert 'controle documental' in d[1].get_text().lower()
                assert 'Sumário técnico progressivo' in d[2].get_text()
                assert len(d.embfile_names())==14
                contents=[p.get_text() for p in d]
                counts=[len(t.split()) for t in contents]
                assert min(counts[4:40])>=180 and sum(counts)>10000
                words+=sum(counts)
                for ch in range(12):
                    concept,lab,ex=contents[4+ch*3:7+ch*3]
                    assert 'Base conceitual' in concept and 'DECISÃO TÉCNICA' in concept
                    assert 'Python 3' in lab and 'Resultado de referência' in lab
                    assert 'Exercício' in ex and 'Comentário de solução' in ex
                    code=d.embfile_get(f'capitulo_{ch+1:02d}.py').decode('utf-8')
                    context={'print':lambda *args:None}
                    exec(compile(code,'laboratorio','exec'),context)
                    assert 'RESULTADO' in context
                    if ch==6:
                        dados=context['DADOS'];errors=[abs(x['estimado']-x['observado']) for x in dados]
                        assert math.isclose(context['RESULTADO']['mae'],sum(errors)/len(errors))
                    labs+=1
                # Nenhuma página técnica vazia ou texto fora dos limites físicos.
                for page in d[4:40]:
                    for block in page.get_text('blocks'):
                        assert block[0]>=0 and block[1]>=0 and block[2]<=page.rect.width+.2 and block[3]<=page.rect.height+.2
    audit=json.loads((folder/'limpeza_documental.json').read_text(encoding='utf-8'))
    for a in audit['arquivos']:
        if a['remover']:assert a['paginas']<40 and not (folder/a['arquivo']).exists()
    print(f'OK: 30 PDFs, {total} páginas, 28 volumes de 42 páginas, {labs} laboratórios e {words} palavras nos novos livros.')

if __name__=='__main__':main()
