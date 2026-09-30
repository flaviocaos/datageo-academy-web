"""Mapeia as seis áreas, registra os PDFs e atualiza o painel de mini-cursos.

Execute novamente para sincronizar novos cursos e materiais com o index.html.
Apenas cursos com subpasta direta 'pdf' são incluídos. Pastas 'ppt' são ignoradas.
"""
from pathlib import Path
from html import escape
from urllib.parse import quote
import json
import os
import re

SITE = Path(__file__).resolve().parent
RAIZ_LOCAL = SITE / "ENTREGA" / "Mini_Cursos" / "AREAS"
RAIZ = RAIZ_LOCAL if RAIZ_LOCAL.is_dir() else SITE.parent / "ENTREGA" / "Mini_Cursos" / "AREAS"
NOMES_AREAS = ["IA e Machine Learning", "Geotecnologias", "BI - Business Intelligence", "Ciência de Dados", "Programação para Dados", "Análise Preditiva"]
CORRECOES = {
    "Ciencia": "Ciência", "Programacao": "Programação", "Analise": "Análise",
    "Automacao": "Automação", "Agronegocio": "Agronegócio", "Etica": "Ética",
    "Estatistica": "Estatística", "Series": "Séries", "Temporais": "Temporais",
    "Funcoes": "Funções", "Integracao": "Integração", "Modulo": "Módulo",
    "Subareas": "Subáreas", "Geotecnoloigias": "Geotecnologias", "PostGress": "PostgreSQL",
    "MiniCurso": "Mini-curso", "Fundacoes": "Fundações", "Geo": "Geoespacial",
}


def amigavel(nome):
    nome = re.sub(r"_DataGeo$", "", nome)
    return " ".join(CORRECOES.get(p, p) for p in re.split(r"[_\s]+", nome) if p)


def mapear():
    areas = sorted((p for p in RAIZ.iterdir() if p.is_dir() and re.match(r"AREA\s+\d+", p.name, re.I)), key=lambda p: int(re.search(r"\d+", p.name).group()))
    if len(areas) != 6:
        raise ValueError(f"Esperadas seis áreas, encontradas {len(areas)}")
    resultado = []
    for indice, area in enumerate(areas):
        cursos = []
        for curso in sorted((p for p in area.iterdir() if p.is_dir()), key=lambda p: p.name.casefold()):
            pasta_pdf = next((p for p in curso.iterdir() if p.is_dir() and p.name.casefold() == "pdf"), None)
            if pasta_pdf is None:
                continue
            arquivos = sorted((p for p in pasta_pdf.rglob("*") if p.is_file() and p.suffix.casefold() == ".pdf" and not any(s.casefold() == "ppt" for s in p.relative_to(pasta_pdf).parts[:-1])), key=lambda p: p.as_posix().casefold())
            materiais = [{"nome": p.name, "titulo": amigavel(p.stem), "caminho": str(p.resolve()), "url": quote(Path(os.path.relpath(p, SITE)).as_posix(), safe="/")} for p in arquivos]
            cursos.append({"nome_pasta": curso.name, "titulo": amigavel(curso.name), "caminho": str(curso.resolve()), "pdfs": materiais})
        resultado.append({"nome_pasta": area.name, "titulo": NOMES_AREAS[indice], "caminho": str(area.resolve()), "cursos": cursos})
    return resultado


CSS = '''  <style id="mini-course-tabs-style">
    .course-tabs{display:flex;gap:10px;flex-wrap:wrap;margin:0 0 32px}
    .course-tab{padding:12px 16px;border:1px solid var(--line);border-radius:9px;background:transparent;color:var(--muted);font:inherit;font-size:13px;font-weight:600;cursor:pointer;transition:background .2s,border-color .2s}
    .course-tab:hover{border-color:var(--cyan);color:var(--white)}
    .course-tab[aria-selected="true"]{background:var(--green);border-color:var(--green);color:var(--navy)}
    .course-tab:focus-visible,.course-material-button:focus-visible,.course-panel:focus-visible{outline:3px solid var(--cyan);outline-offset:4px}
    .course-panel[hidden],.course-materials[hidden]{display:none!important}
    .course-panel-summary{color:var(--muted);font-size:13px;margin:0 0 22px}
    .course-area-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:24px;align-items:start}
    .course-area-card{background:var(--white);color:var(--navy);border:1px solid #dce7ee;border-radius:16px;padding:26px;box-shadow:0 14px 32px #031a3026;min-width:0}
    .course-card-top{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:22px}
    .course-area-card .icon{background:#16bfd012;border-color:#16bfd044;color:#078b99}
    .course-file-count{font-size:11px;font-weight:600;color:#436879;background:#e6eff4;padding:5px 10px;border-radius:20px}
    .course-area-card h3{font-size:20px;line-height:1.35;letter-spacing:-.4px;margin:10px 0 24px;min-height:54px;overflow-wrap:anywhere}
    .course-material-button{font:inherit;font-size:13px;font-weight:700;cursor:pointer;background:var(--green);color:var(--navy);border:0;border-radius:8px;padding:13px 16px;display:flex;align-items:center;justify-content:space-between;gap:12px;width:100%}
    .course-material-button:hover{background:#87e586}
    .course-material-button:disabled{opacity:.6;cursor:default}
    .course-material-button[aria-expanded="true"] .course-chevron{transform:rotate(180deg)}
    .course-chevron{transition:transform .2s}
    .course-materials{margin-top:18px;padding-top:16px;border-top:1px solid #dce7ee}
    .course-materials ul{list-style:none;padding:0;margin:0;display:grid;gap:10px;max-height:360px;overflow-y:auto;overscroll-behavior:contain}
    .course-materials a{display:flex;align-items:start;gap:10px;padding:12px;background:#eaf1f6;border:1px solid #dce7ee;border-radius:8px;color:var(--navy);font-size:12px;line-height:1.5}
    .course-materials a:hover{background:#dff1f2;border-color:var(--cyan)}
    .course-materials a:focus-visible{outline:2px solid #078b99;outline-offset:-2px}
    .course-materials a>span:first-child{flex:1;overflow-wrap:anywhere}
    .course-materials small{display:block;color:#50657b;font-size:10px;margin-top:5px;overflow-wrap:anywhere}
    .course-empty{font-size:13px;color:#50657b}
    @media(max-width:960px){.course-area-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
    @media(max-width:600px){.course-area-grid{grid-template-columns:1fr}.course-tabs{gap:8px}.course-tab{font-size:12px;padding:10px 12px}.course-area-card{padding:24px}.course-area-card h3{min-height:0}}
  </style>
'''

JS = '''  <script id="mini-course-tabs-script">
    (() => {
      const root = document.getElementById('mini-cursos');
      const tabs = [...root.querySelectorAll('[role="tab"]')];
      function activate(tab, focus) {
        tabs.forEach(item => {
          const selected = item === tab;
          item.setAttribute('aria-selected', String(selected));
          item.tabIndex = selected ? 0 : -1;
          document.getElementById(item.getAttribute('aria-controls')).hidden = !selected;
        });
        if (focus) tab.focus();
      }
      tabs.forEach((tab, index) => {
        tab.addEventListener('click', () => activate(tab, false));
        tab.addEventListener('keydown', event => {
          let next;
          if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
          else if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
          else if (event.key === 'Home') next = 0;
          else if (event.key === 'End') next = tabs.length - 1;
          else return;
          event.preventDefault();
          activate(tabs[next], true);
        });
      });
      root.querySelectorAll('.course-material-button').forEach(button => {
        button.addEventListener('click', () => {
          const expanded = button.getAttribute('aria-expanded') !== 'true';
          button.setAttribute('aria-expanded', String(expanded));
          document.getElementById(button.getAttribute('aria-controls')).hidden = !expanded;
        });
      });
    })();
  </script>
'''


def main():
    areas = mapear()
    total_cursos = sum(len(a["cursos"]) for a in areas)
    total_pdfs = sum(len(c["pdfs"]) for a in areas for c in a["cursos"])
    parts = ['''<section class="resources" id="mini-cursos" aria-labelledby="mini-cursos-titulo"><div class="container">
      <div class="section-heading"><div><div class="eyebrow">Aprendizado em foco</div><h2 id="mini-cursos-titulo">Mini-cursos</h2></div><p>Explore seis áreas de conhecimento. Escolha um curso e acesse seus materiais em PDF.</p></div>
      <div class="course-tabs" role="tablist" aria-label="Áreas dos mini-cursos">''']
    for i, area in enumerate(areas, 1):
        parts.append(f'<button type="button" class="course-tab" id="course-tab-{i}" role="tab" aria-selected="{str(i == 1).lower()}" aria-controls="course-area-{i}" tabindex="{0 if i == 1 else -1}">{escape(area["titulo"])}</button>')
    parts.append('</div>')
    for i, area in enumerate(areas, 1):
        quantidade = sum(len(c["pdfs"]) for c in area["cursos"])
        parts.append(f'<div class="course-panel" id="course-area-{i}" role="tabpanel" aria-labelledby="course-tab-{i}" tabindex="0"{ " hidden" if i != 1 else ""}><p class="course-panel-summary">{len(area["cursos"])} cursos · {quantidade} materiais PDF · Os arquivos abrem em uma nova aba.</p><div class="course-area-grid">')
        for j, curso in enumerate(area["cursos"], 1):
            title = escape(curso["titulo"], quote=True)
            materials_id = f"course-materials-{i}-{j}"
            count = len(curso["pdfs"])
            parts.append(f'''<article class="course-area-card"><div class="course-card-top"><div class="icon" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M4 4h7a3 3 0 0 1 3 3v13a4 4 0 0 0-4-3H4V4Zm10 3a3 3 0 0 1 3-3h3v13h-2a4 4 0 0 0-4 3"/></svg></div><span class="course-file-count">{count} PDF{ "s" if count != 1 else ""}</span></div><span class="resource-type">{escape(area["titulo"])}</span><h3>{title}</h3><button type="button" class="course-material-button" aria-expanded="false" aria-controls="{materials_id}" aria-label="Acessar Material: {title}"{ " disabled" if count == 0 else ""}>Acessar Material <span class="course-chevron" aria-hidden="true">⌄</span></button><div class="course-materials" id="{materials_id}" hidden><ul>''')
            for pdf in curso["pdfs"]:
                parts.append(f'<li><a href="{escape(pdf["url"], quote=True)}" target="_blank" rel="noopener noreferrer"><span>{escape(pdf["titulo"])}<small>{escape(pdf["nome"])}</small></span><span aria-hidden="true">↗</span><span class="visually-hidden"> (abre em nova aba)</span></a></li>')
            parts.append('</ul></div></article>')
        parts.append('</div></div>')
    parts.append('</div></section>')
    section = "\n      ".join(parts)
    path = SITE / "index.html"
    original = path.read_text(encoding="utf-8")
    pattern = r'<section class="resources" id="mini-cursos"[\s\S]*?</section>'
    match = re.search(pattern, original)
    if not match:
        raise ValueError("Seção de mini-cursos não encontrada")
    updated = original[:match.start()] + section + original[match.end():]
    base_original = original.replace(CSS, "").replace(JS, "")
    updated = updated.replace(CSS, "").replace(JS, "")
    assert re.sub(pattern, "", base_original) == re.sub(pattern, "", updated), "Alteração inesperada fora da seção"
    updated = updated.replace('</head>', CSS + '</head>').replace('</body>', JS + '</body>')
    path.write_text(updated, encoding="utf-8")
    (SITE / "mini_cursos_acervo.json").write_text(json.dumps(areas, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Mapeamento e HTML salvos: {len(areas)} áreas, {total_cursos} cursos, {total_pdfs} PDFs.")
    for area in areas:
        print(f'{area["titulo"]}: {len(area["cursos"])} cursos, {sum(len(c["pdfs"]) for c in area["cursos"])} PDFs')


if __name__ == "__main__":
    main()
