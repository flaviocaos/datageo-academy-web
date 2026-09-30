"""Atualiza somente o acervo de apresentações no index.html."""
from pathlib import Path
from html import escape
from urllib.parse import quote
import re

ROOT = Path(__file__).resolve().parent
PASTA = ROOT.parent / "ENTREGA" / "Apresentacoes_Tecnicas"
PALAVRAS = {
    "Analise": "Análise", "Automacao": "Automação", "Inteligencia": "Inteligência",
    "Estatistica": "Estatística", "Etica": "Ética", "Agronegocio": "Agronegócio",
    "Logistica": "Logística", "Mineracao": "Mineração", "Educacao": "Educação",
    "Saude": "Saúde", "Seguranca": "Segurança", "Publica": "Pública",
    "Energetico": "Energético", "Imobiliario": "Imobiliário", "Publico": "Público",
    "Telecomunicacoes": "Telecomunicações", "Modulo": "Módulo", "Visao": "Visão",
    "Explicavel": "Explicável", "Series": "Séries", "a": "à", "Moedas": "Moedas",
    "para": "para", "PowerBI": "Power BI", "NLP": "NLP:", "XAI": "(XAI)",
}


def titulo(stem):
    stem = re.sub(r"_DataGeo$", "", stem).replace("Agricultura_4_0", "Agricultura_4.0")
    stem = re.sub(r"^IA_0\d_", "IA: ", stem)
    resultado = " ".join(PALAVRAS.get(p, p) for p in stem.split("_"))
    return resultado.replace("IA:  ", "IA: ")


def main():
    arquivos = sorted((p for p in PASTA.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"), key=lambda p: p.name.casefold())
    if len(arquivos) < 3:
        raise ValueError("O acervo precisa de pelo menos três apresentações")
    cards = []
    for pdf in arquivos:
        capa = pdf.with_name(pdf.stem + "_capa.png")
        if not capa.is_file():
            raise FileNotFoundError(capa)
        nome = escape(titulo(pdf.stem), quote=True)
        caminho = "../ENTREGA/Apresentacoes_Tecnicas/"
        cards.append(f'''          <article class="resource-card presentation-card"><div class="presentation-preview"><img src="{caminho}{quote(capa.name)}" alt="Capa da apresentação: {nome}" loading="lazy" decoding="async"></div><div class="resource-body"><span class="resource-type">Apresentação técnica · PDF</span><h3>{nome}</h3><a class="resource-button" href="{caminho}{quote(pdf.name)}" target="_blank" rel="noopener noreferrer" aria-label="Ver apresentação: {nome} (abre em nova aba)">Ver apresentação <span aria-hidden="true">↗</span></a></div></article>''')
    section = '''<section class="resources" id="apresentacoes-tecnicas" aria-labelledby="apresentacoes-tecnicas-titulo">
      <div class="container">
        <div class="section-heading"><div><div class="eyebrow">Ideias para compartilhar</div><h2 id="apresentacoes-tecnicas-titulo">Apresentações Técnicas</h2></div><p>Explore ''' + str(len(arquivos)) + ''' apresentações sobre dados, inteligência artificial e aplicações das geotecnologias.</p></div>
        <div class="resource-grid catalog-grid">
''' + "\n".join(cards[:3]) + '''
        </div>
        <div class="catalog-action"><button type="button" class="catalog-toggle" aria-expanded="false" aria-controls="apresentacoes-tecnicas-acervo"><span class="catalog-toggle-label">Ver acervo completo</span> <span class="catalog-toggle-arrow" aria-hidden="true">➔</span></button></div>
        <div class="catalog-expansion" id="apresentacoes-tecnicas-acervo" inert><div class="catalog-expansion-inner"><div class="resource-grid catalog-grid">
''' + "\n".join(cards[3:]) + '''
        </div></div></div>
      </div>
    </section>'''
    css = '''  <style>
    #apresentacoes-tecnicas .presentation-card{border-radius:16px;box-shadow:0 14px 32px #031a3030;transition:box-shadow .25s,border-color .25s}
    #apresentacoes-tecnicas .presentation-card:hover{border-color:var(--cyan);box-shadow:0 18px 42px #031a3040}
    #apresentacoes-tecnicas .presentation-preview{aspect-ratio:16/9;width:100%;overflow:hidden;background:#e6eef4;border-bottom:1px solid #dce7ee;padding:8px}
    #apresentacoes-tecnicas .presentation-preview img{display:block;width:100%;height:100%;object-fit:contain;border-radius:8px}
    #apresentacoes-tecnicas .resource-body{padding:24px}
    #apresentacoes-tecnicas .resource-body h3{font-size:19px;line-height:1.35;flex:1;margin:10px 0 24px;overflow-wrap:anywhere}
    @media(max-width:600px){#apresentacoes-tecnicas .resource-body{padding:22px}}
  </style>
'''
    path = ROOT / "index.html"
    original = path.read_text(encoding="utf-8")
    pattern = r'<section class="resources" id="apresentacoes-tecnicas"[\s\S]*?</section>'
    match = re.search(pattern, original)
    if not match:
        raise ValueError("Seção de apresentações não encontrada")
    updated = original[:match.start()] + section + original[match.end():]
    # Remova o CSS anterior deste script caso o acervo seja atualizado novamente.
    updated = updated.replace(css, "").replace("</head>", css + "</head>")
    before_without_section = re.sub(pattern, "", original.replace(css, ""))
    after_without_section = re.sub(pattern, "", updated.replace(css, ""))
    assert before_without_section == after_without_section, "Alteração inesperada fora do acervo"
    assert section.count('target="_blank"') == len(arquivos)
    path.write_text(updated, encoding="utf-8")
    print(f"HTML salvo: 3 apresentações visíveis e {len(arquivos) - 3} expansíveis. Restante do site preservado.")


if __name__ == "__main__":
    main()
