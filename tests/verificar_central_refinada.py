"""Valida a Central refinada e cálculos sem dependências. Execute com Python."""
from pathlib import Path
from html.parser import HTMLParser
from zipfile import ZipFile
import importlib.util
import math
import re
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]

def carregar(p):
    spec=importlib.util.spec_from_file_location(p.stem,p)
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod

class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.tabs=[]
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='a':self.links.append(a)
        if tag=='button' and a.get('role')=='tab':self.tabs.append(a)

def main():
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    central=html[html.index('<section class="premium-central"'):html.index('<section class="resources" id="infograficos"')]
    parser=Links();parser.feed(central)
    assert len(parser.tabs)==3 and [a['aria-controls'] for a in parser.tabs]==[f'premium-panel-{i}' for i in range(1,4)]
    assert central.count('class="premium-card premium-featured"')==3
    assert central.count('class="refined-group')==6
    assert not any('./'+p+'/' in central for p in ['templates_gis','bancos_dados','portfolios_cases','roadmaps_aprendizado','exercicios_praticos','glossarios_tecnicos'])
    locais=[a for a in parser.links if a['href'].startswith('./')]
    externos=[a for a in parser.links if a['href'].startswith('https://')]
    assert len(locais)==len({a['href'] for a in locais})==41
    for a in locais:
        p=(ROOT/a['href']).resolve()
        assert p.is_relative_to(ROOT) and p.is_file(),p
        assert a.get('download')==p.name and 'target' not in a
    assert len(externos)==13 and all(a.get('target')=='_blank' and 'noopener' in a['rel'] for a in externos)
    assert central.count('data-portal')==15
    paths=sorted((ROOT/'scripts_topografia').glob('*.py'));assert len(paths)==10
    m=[carregar(p) for p in paths]
    assert all(mod.calcular(**mod.EXEMPLO) is not None for mod in m)
    assert m[0].calcular([0,0],[3,4])==5
    assert m[1].calcular([0,0],[-1,0])==270 and m[1].calcular([0,0],[0,1])==0
    assert math.dist(m[2].calcular([50,50],180,20),[50,30])<1e-10
    v=[[500000,6900000],[500100,6900000],[500100,6900100],[500000,6900100]]
    assert m[3].calcular(v)=={'area_m2':10000,'area_ha':1}
    assert m[3].calcular(list(reversed(v)))['area_m2']==10000 and m[4].calcular(v+[v[0]])==400
    lados=[[0,10],[90,10],[180,10],[270,9]]
    assert math.isclose(m[5].calcular(lados)['erro_linear_m'],1)
    assert math.isclose(m[5].calcular(lados)['precisao_1_para'],39)
    bow=m[6].calcular([100,200],lados)
    assert math.dist(bow['estacoes'][-1],[100,200])<1e-10
    assert math.isclose(math.fsum(c['correcao_e'] for c in bow['correcoes']),-1)
    assert m[7].calcular(100,[[1.5,1,50],[1.2,.8,50]],100.8)['cotas_ajustadas'][-1]==100.8
    assert math.dist(m[8].calcular([0,0],45,[10,0],315)['ponto'],[5,5])<1e-10
    texto=m[9].calcular(v,'Lote','EPSG:31982');assert '10000.000 m²' in texto and '400.000 m' in texto
    for fn,args in [(m[1].calcular,([0,0],[0,0])),(m[0].calcular,([float('nan'),0],[1,1])),
                    (m[2].calcular,([0,0],0,-1)),(m[3].calcular,([[0,0],[1,1],[0,1],[1,0]],)),
                    (m[8].calcular,([0,0],0,[1,0],0))]:
        try:fn(*args)
        except ValueError:pass
        else:raise AssertionError('Entrada inválida aceita.')
    desafios=sorted((ROOT/'desafios_python').glob('*.py'));assert len(desafios)==10
    for p in desafios:
        mod=carregar(p)
        try:mod.verificar()
        except NotImplementedError:pass
        else:raise AssertionError('Desafio deveria aguardar o aluno.')
    docs=list((ROOT/'roteiros_servidores').glob('*.docx'));assert len(docs)==2
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    for doc in docs:
        with ZipFile(doc) as z:
            assert z.testzip() is None
            for n in z.namelist():
                if n.endswith(('.xml','.rels')):ET.fromstring(z.read(n))
            assert len([n for n in z.namelist() if n.startswith('word/media/')])==2
            assert len(z.read('datageo/fonte.txt').decode('utf-8').split())>800
            assert 'DataGeo Academy' in z.read('word/header1.xml').decode('utf-8')
            assert ' TOC ' in z.read('word/document.xml').decode('utf-8')
            d=ET.fromstring(z.read('word/document.xml'));assert len(d.findall('.//w:drawing',ns))==2
            ids={x.get('{'+ns['w']+'}name') for x in d.findall('.//w:bookmarkStart',ns)}
            assert all(x.get('{'+ns['w']+'}anchor') in ids for x in d.findall('.//w:hyperlink',ns))
    print('OK: 3 abas, 41 downloads, 13 portais, 10 cálculos, 10 desafios e 2 DOCX ilustrados.')

if __name__=='__main__':main()
