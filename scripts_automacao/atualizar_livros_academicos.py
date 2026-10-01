"""Atualiza só a seção de livros, lendo o catálogo editorial validado.
Uso: python scripts_automacao/atualizar_livros_academicos.py
"""
from pathlib import Path
from html import escape
from urllib.parse import quote
import json
ROOT=Path(__file__).resolve().parents[1]

def main():
    path=ROOT/'index.html';s=path.read_text(encoding='utf-8')
    info=json.loads((ROOT/'livros_academicos/catalogo.json').read_text(encoding='utf-8'))
    areas=info['areas'];assert len(areas)==6
    tabs=[];panels=[]
    for i,area in enumerate(areas,1):
        assert len(area['livros'])==5
        tabs.append(f'<button type="button" class="course-tab academic-tab" id="book-tab-{i}" role="tab" aria-selected="{str(i==1).lower()}" aria-controls="book-panel-{i}" tabindex="{0 if i==1 else -1}">{escape(area["nome"])}</button>')
        cards=[]
        for j,livro in enumerate(area['livros'],1):
            titulo=livro['titulo'];arquivo=livro['arquivo']
            p=ROOT/'livros_academicos'/arquivo
            if not p.is_file():raise FileNotFoundError(p)
            tipo='DOCX · reprodução do PDF' if titulo=='Inteligência Artificial Aplicada' and 'conversao_ia' in info else 'Livro acadêmico · DOCX'
            numero=f'{i:02d}.{j:02d}'
            cards.append(f'''<article class="resource-card academic-card">
              <div class="academic-art" aria-hidden="true"><div class="academic-cover"><div class="academic-cover-brand"><img src="LOGOMARCA_2.png" alt="" loading="lazy" decoding="async"><span>DATAGEO<br>ACADEMY</span></div><span class="academic-cover-series">COLEÇÃO ACADÊMICA / {numero}</span><strong>{escape(titulo)}</strong><span class="academic-cover-orbit"></span><small>{escape(area['nome'])}</small><span class="academic-cover-footer">CONHECIMENTO QUE GERA DECISÕES</span></div></div>
              <div class="resource-body"><span class="resource-type">{escape(tipo)}</span><h3>{escape(titulo)}</h3><p>{'Material original da Academy nesta área de conhecimento.' if livro['original'] else 'Introdução, capítulos técnicos progressivos e exercício orientado em documento Word editável.'}</p><a class="resource-button" href="./livros_academicos/{quote(arquivo)}" download="{escape(arquivo)}" aria-label="Baixar livro em Word: {escape(titulo)}">Baixar livro .docx <span aria-hidden="true">↓</span></a></div>
            </article>''')
        panels.append(f'<div class="academic-panel" id="book-panel-{i}" role="tabpanel" aria-labelledby="book-tab-{i}" tabindex="0"{ " hidden" if i!=1 else ""}><p class="academic-summary">5 livros · {escape(area["nome"])} · Download direto em Word</p><div class="academic-grid">'+''.join(cards)+'</div></div>')
    section='''<section class="resources academic-books" id="livros-tecnicos" aria-labelledby="livros-tecnicos-titulo"><div class="container">
      <div class="section-heading"><div><div class="eyebrow">Coleção acadêmica · 30 livros</div><h2 id="livros-tecnicos-titulo">Livros Acadêmicos</h2></div><p>Seis áreas de conhecimento, cinco livros em cada uma. Escolha sua frente de estudo e baixe os materiais em Word.</p></div>
      <div class="course-tabs academic-tabs" role="tablist" aria-label="Áreas dos livros acadêmicos">'''+''.join(tabs)+'</div>'+''.join(panels)+'''
      <p class="academic-note">Os 28 novos volumes são introduções técnico-didáticas com autoria institucional DataGeo Academy. Cartografia mantém o DOCX encontrado no projeto. Inteligência Artificial Aplicada preserva as páginas do PDF disponível em um DOCX de reprodução visual, sem edição textual.</p>
    </div></section>
    '''
    a=s.index('<section class="resources" id="livros-tecnicos"') if '<section class="resources" id="livros-tecnicos"' in s else s.index('<section class="resources academic-books"')
    b=s.index('<section class="resources" id="apresentacoes-tecnicas"',a)
    s=s[:a]+section+s[b:]
    s=s.replace('<a href="#livros-tecnicos">Livros técnicos</a>','<a href="#livros-tecnicos">Livros acadêmicos</a>')
    path.write_text(s,encoding='utf-8');print('30 cards, 6 abas independentes e 30 links DOCX integrados.')

if __name__=='__main__':main()
