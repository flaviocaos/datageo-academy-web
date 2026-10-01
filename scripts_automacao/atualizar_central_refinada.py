"""Reconstrói somente a Central Premium, preservando os três cards principais.
Uso: python scripts_automacao/atualizar_central_refinada.py
"""
from pathlib import Path
from html import escape
import re
from gerar_biblioteca_refinada import TOPO, EXERCISES

ROOT=Path(__file__).resolve().parents[1]
BR=[
 ('LinkedIn Brasil','Networking, alertas e busca por GIS, geoprocessamento e sensoriamento remoto.','https://br.linkedin.com/jobs/geoprocessamento-vagas'),
 ('Indeed Brasil','Buscas por cargo, cidade e modalidade de trabalho.','https://br.indeed.com/q-geoprocessamento-vagas.html'),
 ('Vagas.com','Oportunidades e processos seletivos de empresas brasileiras.','https://www.vagas.com.br/vagas-de-geoprocessamento'),
 ('InfoJobs','Pesquise geoprocessamento, topografia, cartografia e analista GIS.','https://www.infojobs.com.br/empregos.aspx?palabra=geoprocessamento'),
 ('Catho','Use a busca do portal com termos de SIG e análise territorial.','https://www.catho.com.br/'),
 ('Empregos.com.br','Busca por analista de geoprocessamento e cargos relacionados.','https://www.empregos.com.br/vagas/analista-de-geoprocessamento'),
 ('Gupy','Portal de vagas e seleção de empresas; filtre pelas competências geoespaciais.','https://portal.gupy.io/vagas'),
 ('Glassdoor Brasil','Buscas por analista de geoprocessamento e informações de empresas.','https://www.glassdoor.com.br/Vaga/brasil-analista-de-geoprocessamento-vagas-SRCH_IL.0%2C6_IN36_KO7%2C35.htm'),
]
GLOBAL=[
 ('GISjobs.com','Portal especializado em funções GIS e geoespaciais, principalmente nos Estados Unidos.','https://www.gisjobs.com/'),
 ('GEO CAREERS','Vagas de GIS, sensoriamento remoto e engenharia geoespacial; explore o filtro remoto.','https://www.geo-careers.com/'),
 ('GeoSearch','Recrutamento especializado em tecnologia geoespacial e geomática.','https://geosearch.com/candidates/'),
 ('Esri Careers','Oportunidades no ecossistema GIS da Esri; confira país e modalidade de cada vaga.','https://www.esri.com/en-us/about/careers/overview'),
 ('LinkedIn Global · GIS remoto','Busca internacional por GIS com filtro de modalidade remota.','https://www.linkedin.com/jobs/search/?keywords=GIS&f_WT=2'),
]
DB=[
 ('instalar_postgis.ps1','Instalar PostgreSQL / PostGIS','Laboratório Docker persistente, porta local e senha por ambiente.'),
 ('postgis_schema.sql','Schema e índice PostGIS','Pontos sintéticos, constraints, referência espacial e índices GiST.'),
 ('postgis_queries.sql','Queries espaciais PostGIS','Raio, distância, buffers, hectares, KNN e parâmetros SQL.'),
 ('instalar_oracle.ps1','Instalar Oracle Database Free','Instalador Docker com tag oficial escolhida pelo usuário.'),
 ('oracle_preparar_usuario.sql','Preparar usuário Oracle','Conta de laboratório, permissões e verificação do componente Spatial.'),
 ('oracle_schema.sql','Schema Oracle Spatial','Geometria SDO, metadata e índice espacial para pontos.'),
 ('oracle_queries.sql','Queries Oracle Spatial','Busca por distância, validação, WKT e variáveis de binding.'),
 ('instalar_mongodb.ps1','Instalar MongoDB','Laboratório Docker autenticado e volume persistente.'),
 ('mongodb_schema.js','Coleção e índice MongoDB','Validador GeoJSON, dados sintéticos e índice 2dsphere.'),
 ('mongodb_queries.js','Queries geográficas MongoDB','geoNear, geoWithin e agregação por categoria no mongosh.'),
 ('README.md','Guia de execução dos bancos','Ordem de instalação, pré-requisitos, comandos e referências oficiais.'),
]
ICON='<span class="refined-symbol" aria-hidden="true">↗</span>'

def arquivo(pasta,nome,titulo,descricao):
    href=f'./{pasta}/{nome}'
    if not (ROOT/pasta/nome).is_file():raise FileNotFoundError(href)
    return f'<article class="refined-item">{ICON}<div><h4>{escape(titulo)}</h4><p>{escape(descricao)}</p><span class="refined-format">{escape(Path(nome).suffix[1:].upper())}</span></div><a class="button primary premium-download" href="{escape(href)}" download="{escape(nome)}" aria-label="Baixar {escape(titulo)}">Baixar material <span aria-hidden="true">↓</span></a></article>'

def grupo(titulo,descricao,items,numero):
    return f'<details class="refined-group"><summary><span class="refined-number" aria-hidden="true">{numero}</span><span><strong>{escape(titulo)}</strong><small>{escape(descricao)}</small></span><span class="refined-count">{len(items)} itens</span><span class="refined-chevron" aria-hidden="true">+</span></summary><div class="refined-list">'+''.join(items)+'</div></details>'

def empregos(titulo,descricao,items,ident):
    lista=''.join(f'<li data-portal><span class="refined-symbol" aria-hidden="true">◎</span><div><h4>{escape(nome)}</h4><p>{escape(desc)}</p></div><a class="button primary" href="{escape(url)}" target="_blank" rel="noopener noreferrer" aria-label="Abrir {escape(nome)} em nova aba">Ver vagas ↗</a></li>' for nome,desc,url in items)
    return f'<details class="refined-group job-portals"><summary><span class="refined-number" aria-hidden="true">◎</span><span><strong>{escape(titulo)}</strong><small>{escape(descricao)}</small></span><span class="refined-count">{len(items)} portais</span><span class="refined-chevron" aria-hidden="true">+</span></summary><div class="refined-jobs"><label for="{ident}">Filtrar portais por nome ou assunto</label><input type="search" id="{ident}" placeholder="Ex.: GIS, remoto, topografia…" autocomplete="off" data-portal-filter aria-controls="{ident}-lista"><p class="portal-status" role="status" aria-live="polite">{len(items)} portais disponíveis</p><ul id="{ident}-lista" class="portal-list">{lista}</ul><p class="portal-empty" hidden>Nenhum portal encontrado. Tente outro termo.</p></div></details>'

def main():
    path=ROOT/'index.html'; html=path.read_text(encoding='utf-8')
    start=html.index('<section class="premium-central"');end=html.index('<section class="resources" id="infograficos"',start)
    antigo=html[start:end]
    principais=re.findall(r'<article class="premium-card premium-featured">.*?</article>',antigo,re.S)
    if len(principais)!=3:raise ValueError('Esperados os três cards originais de scripts, template e checklist.')
    groups=[
        [grupo('Scripts de Topografia','Cálculos planos, azimutes, nivelamento e memorial descritivo.',[arquivo('scripts_topografia',n+'.py',t,d) for n,t,d,_,_ in TOPO],'01'),
         grupo('Bancos de Dados Geográficos','Instalação, schemas e consultas em PostgreSQL/PostGIS, Oracle e MongoDB.',[arquivo('scripts_bancos_geo',n,t,d) for n,t,d in DB],'02')],
        [empregos('Portais Nacionais de Emprego','Oito canais para buscar oportunidades no Brasil.',BR,'portais-br'),
         empregos('Vagas Internacionais e Remotas de SIG','Canais especializados e busca global por GIS.',GLOBAL,'portais-global')],
        [grupo('Desafios Python','Dez exercícios com TODOs e verificações para praticar programação geográfica.',[arquivo('desafios_python',n+'.py',t,i) for n,t,i,_,_ in EXERCISES],'01'),
         grupo('Roteiros de Servidores','Manuais Word editáveis com sumário e diagramas de instalação.',[
             arquivo('roteiros_servidores','manual_geoserver.docx','GeoServer: instalação e publicação','Catálogo persistente, conexão PostGIS, workspace, WMS/WFS e backup.'),
             arquivo('roteiros_servidores','manual_postgis.docx','PostGIS: instalação e configuração','Extensão, schema, índices, conexão QGIS, permissões e restauração.')],'02')],
    ]
    nomes=['Materiais Práticos','Guias de Carreira','Desafios e Gamificação']
    tabs=''.join(f'<button type="button" class="premium-tab" id="premium-tab-{i}" role="tab" aria-selected="{str(i==1).lower()}" aria-controls="premium-panel-{i}" tabindex="{0 if i==1 else -1}">{nome}</button>' for i,nome in enumerate(nomes,1))
    panels=''.join(f'<div class="premium-panel" id="premium-panel-{i}" role="tabpanel" aria-labelledby="premium-tab-{i}" tabindex="0"{ " hidden" if i!=1 else ""}>{principais[i-1]}<div class="refined-grid">'+''.join(groups[i-1])+'</div>'+('<p class="premium-note">Pesquise também por cartografia, geomática, sensoriamento remoto, GIS e geospatial. Confirme país elegível, fuso e autorização de trabalho em cada anúncio; uma vaga remota pode ter restrições de localização. Links conferidos em outubro de 2026.</p>' if i==2 else '')+'</div>' for i in range(1,4))
    central=f'''<section class="premium-central" id="materiais-premium" aria-labelledby="premium-title"><div class="container">
      <div class="section-heading"><div><div class="eyebrow">Ferramentas reais · Desenvolvimento profissional</div><h2 id="premium-title">Central de Materiais Premium &amp; Carreira</h2></div><p>Programe, estruture dados e avance na carreira com downloads diretos, desafios e roteiros de implantação.</p></div>
      <div class="premium-tabs" role="tablist" aria-label="Categorias da Central Premium">{tabs}</div>
      {panels}
      <p class="premium-note">Abra as coleções para acessar os arquivos. Scripts topográficos usam coordenadas planas em metros; desafios devem ser completados pelo aluno. Consulte pré-requisitos dos kits e dos bancos antes de executar. Os documentos Word são editáveis e incluem orientações de validação.</p>
    </div></section>
    '''
    html=html[:start]+central+html[end:]
    path.write_text(html,encoding='utf-8')
    print('Central atualizada: 3 abas, 41 downloads e 13 portais de emprego.')

if __name__=='__main__':main()
