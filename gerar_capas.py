"""Renderiza as capas dos livros técnicos em PNG a 300 DPI.

Dependências: python -m pip install PyMuPDF Pillow
Uso: python gerar_capas.py
"""

from pathlib import Path
import sys

# Usa a dependência instalada localmente, sem modificar o Python do sistema.
sys.path.insert(0, str(Path(__file__).resolve().parent / ".capas-deps"))

import pymupdf
from PIL import Image


PASTA = Path(__file__).resolve().parent.parent / "ENTREGA" / "Livros_Tecnicos"
ARQUIVOS = (
    ("Cartografia_Basica_Aplicada_Geotecnologias.pdf", "capa_cartografia.png"),
    ("Inteligencia_Artificial_Aplicada.pdf", "capa_ia.png"),
)
DPI = 300


def main() -> None:
    for origem, _ in ARQUIVOS:
        if not (PASTA / origem).is_file():
            raise FileNotFoundError(PASTA / origem)

    for origem, destino in ARQUIVOS:
        with pymupdf.open(PASTA / origem) as documento:
            if documento.page_count == 0:
                raise ValueError(f"PDF sem páginas: {origem}")
            pagina = documento.load_page(0)
            imagem = pagina.get_pixmap(dpi=DPI, colorspace=pymupdf.csRGB, alpha=False)
            saida = PASTA / destino
            imagem.save(saida)

        with Image.open(saida) as capa:
            capa.load()
            if capa.format != "PNG" or capa.size != (imagem.width, imagem.height):
                raise ValueError(f"Falha na validação da imagem: {saida}")
            print(f"{saida.name}: {capa.width} x {capa.height} px, {DPI} DPI, {saida.stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
