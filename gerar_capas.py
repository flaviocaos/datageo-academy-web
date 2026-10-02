"""Renderiza as capas dos livros técnicos em PNG a 300 DPI.

Dependências: python -m pip install PyMuPDF Pillow
Uso: python gerar_capas.py
"""

from pathlib import Path
import json
import sys

# Usa a dependência instalada localmente, sem modificar o Python do sistema.
sys.path.insert(0, str(Path(__file__).resolve().parent / ".capas-deps"))

import pymupdf
from PIL import Image


SITE = Path(__file__).resolve().parent
PASTA_LOCAL = SITE / "ENTREGA" / "Livros_Tecnicos"
PASTA = PASTA_LOCAL if PASTA_LOCAL.is_dir() else SITE.parent / "ENTREGA" / "Livros_Tecnicos"
ARQUIVOS = (
    ("Cartografia_Basica_Aplicada_Geotecnologias.pdf", "capa_cartografia.png"),
    ("Inteligencia_Artificial_Aplicada.pdf", "capa_ia.png"),
)
DPI = 300


def main() -> None:
    catalogo_path = SITE / 'livros_academicos' / 'catalogo.json'
    catalogo = json.loads(catalogo_path.read_text(encoding='utf-8'))
    livros = [livro for area in catalogo['areas'] for livro in area['livros']]
    for livro in livros:
        origem = (SITE / livro['caminho']).resolve()
        saida = (SITE / livro['capa']).resolve()
        if not origem.is_relative_to(SITE) or not saida.is_relative_to(SITE):
            raise ValueError('Caminho fora do projeto')
        with pymupdf.open(origem) as documento:
            if documento.page_count == 0:
                raise ValueError(f"PDF sem páginas: {origem}")
            pagina = documento.load_page(0)
            imagem = pagina.get_pixmap(dpi=DPI, colorspace=pymupdf.csRGB, alpha=False)
            saida.parent.mkdir(parents=True, exist_ok=True)
            imagem.save(saida)
            livro['paginas'] = documento.page_count

        with Image.open(saida) as capa:
            capa.load()
            if capa.format != "PNG" or capa.size != (imagem.width, imagem.height):
                raise ValueError(f"Falha na validação da imagem: {saida}")
            print(f"{saida.name}: {capa.width} x {capa.height} px, {DPI} DPI, {saida.stat().st_size:,} bytes")
    catalogo_path.write_text(json.dumps(catalogo, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(f'{len(livros)} capas geradas e verificadas.')


if __name__ == "__main__":
    main()
