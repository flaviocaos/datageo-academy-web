"""Copia (--copiar) e cataloga PDFs das seis áreas; atualiza as abas do site."""
from pathlib import Path
from html import escape
from urllib.parse import quote
import argparse, hashlib, json, re, shutil
SITE=Path(__file__).resolve().parents[1]
LOCAL=SITE/'ENTREGA'/'Livros_Tecnicos'
ORIGENS=['AREA 1 - IA e Machine Learning','AREA 2 - Geotecnologias','AREA 3 - BI_ Business Inteligence','AREA 4 - Ciencia_de_Dados','AREA 5 - Programacao_para_Dados','AREA 6 - Analise_Preditiva']

def pdfs(pasta):
    if not pasta.is_dir(): raise FileNotFoundError(pasta)
    arquivos=sorted((p for p in pasta.rglob('*') if p.is_file() and p.suffix.lower()=='.pdf'),key=lambda p:p.as_posix().casefold())
    if not arquivos: raise ValueError(f'Sem PDFs: {pasta}')
    return arquivos

def hash_pdf(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def renderizar(dados):
    partes=['<section class="resources academic-books" id="livros-tecnicos" aria-labelledby="livros-tecnicos-titulo"><div class="container">',f'<div class="section-heading"><div><div class="eyebrow">Coleção acadêmica · {sum(len(a["livros"]) for a in dados["areas"])} livros</div><h2 id="livros-tecnicos-titulo">Livros Acadêmicos</h2></div><p>Seis áreas de conhecimento, capas originais e download direto em PDF.</p></div>','<div class="course-tabs academic-tabs" role="tablist" aria-label="Áreas dos livros acadêmicos">']
    for i,a in enumerate(dados['areas'],1):
        partes.append(f'<button type="button" class="course-tab academic-tab" id="book-tab-{i}" role="tab" aria-selected="{str(i==1).lower()}" aria-controls="book-panel-{i}" tabindex="{0 if i==1 else -1}">{escape(a["nome"])}</button>')
    partes.append('</div>')
    for i,a in enumerate(dados['areas'],1):
        partes.append(f'<div class="academic-panel" id="book-panel-{i}" role="tabpanel" aria-labelledby="book-tab-{i}" tabindex="0"'+(' hidden' if i!=1 else '')+f'><p class="academic-summary">{len(a["livros"])} livros · {escape(a["nome"])}</p><div class="academic-grid">')
        for l in a['livros']:
            t=escape(l['titulo'])
            partes.append(f'<article class="resource-card academic-card"><div class="academic-art"><img src="{escape(l["capa_url"])}" alt="Capa de {t}" loading="lazy" decoding="async" style="max-width:100%;max-height:100%;width:auto;height:auto;border-radius:5px;box-shadow:10px 14px 24px #08254642"></div><div class="resource-body"><span class="resource-type">Livro técnico · PDF</span><h3>{t}</h3><p>Material técnico de {escape(a["nome"])}.</p><a class="resource-button" href="{escape(l["url"])}" download="{escape(l["arquivo"])}">Baixar livro .pdf <span aria-hidden="true">↓</span></a></div></article>')
        partes.append('</div></div>')
    partes.append('</div></section>')
    p=SITE/'index.html';html=p.read_text(encoding='utf-8')
    html,n=re.subn(r'<section\b[^>]*\bid="livros-tecnicos"[^>]*>.*?</section>',lambda _: '\n'.join(partes),html,count=1,flags=re.S)
    if n!=1: raise ValueError('Seção não encontrada')
    p.write_text(html,encoding='utf-8')

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--copiar',action='store_true');args=parser.parse_args()
    if args.copiar:
        fontes=[(SITE.parent/'ENTREGA'/'Livros_Tecnicos'/n/'pdf') for n in ORIGENS]
        inventarios=[pdfs(p) for p in fontes]
        for i,(origem,arquivos) in enumerate(zip(fontes,inventarios),1):
            for p in arquivos:
                destino=LOCAL/f'AREA {i}'/p.relative_to(origem);destino.parent.mkdir(parents=True,exist_ok=True)
                if not destino.exists() or hash_pdf(destino)!=hash_pdf(p): shutil.copy2(p,destino)
                if hash_pdf(destino)!=hash_pdf(p): raise ValueError(f'Cópia divergente: {p}')
    cp=SITE/'livros_academicos/catalogo.json';dados=json.loads(cp.read_text(encoding='utf-8'))
    if len(dados['areas'])!=6: raise ValueError('Esperadas seis áreas')
    for i,a in enumerate(dados['areas'],1):
        anteriores={l.get('caminho'):l for l in a['livros']};livros=[]
        for p in pdfs(LOCAL/f'AREA {i}'):
            caminho=p.relative_to(SITE).as_posix();capa=p.with_name(p.stem+'_capa.png').relative_to(SITE).as_posix()
            nome=re.sub(r'^\d+[_\s-]*','',p.stem);nome=re.sub(r'_DataGeo$','',nome,flags=re.I).replace('_',' ')
            l=dict(anteriores.get(caminho,{}));l.update(titulo=nome,arquivo=p.name,caminho=caminho,url='./'+quote(caminho,safe='/'),capa=capa,capa_url='./'+quote(capa,safe='/'),sha256=hash_pdf(p));livros.append(l)
        a['livros']=livros;a['pasta']=(LOCAL/f'AREA {i}').relative_to(SITE).as_posix();print(f'AREA {i}: {len(livros)} PDFs')
    dados['edicao']='Acervo local sincronizado das seis áreas acadêmicas'
    cp.write_text(json.dumps(dados,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');renderizar(dados)

if __name__=='__main__': main()
