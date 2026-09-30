"""Extrai a primeira página das apresentações técnicas em PNG, a 300 DPI."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / ".capas-deps"))
import pymupdf

PASTA = Path(__file__).resolve().parent.parent / "ENTREGA" / "Apresentacoes_Tecnicas"


def main():
    arquivos = sorted(
        (p for p in PASTA.iterdir() if p.is_file() and p.suffix.lower() == ".pdf"),
        key=lambda p: p.name.casefold(),
    )
    if not arquivos:
        raise FileNotFoundError(f"Nenhum PDF encontrado em {PASTA}")
    erros = []
    for indice, arquivo in enumerate(arquivos, 1):
        try:
            with pymupdf.open(arquivo) as documento:
                if not documento.page_count:
                    raise ValueError("PDF sem páginas")
                imagem = documento[0].get_pixmap(dpi=300, colorspace=pymupdf.csRGB, alpha=False)
                destino = arquivo.with_name(arquivo.stem + "_capa.png")
                imagem.save(destino)
                verificada = pymupdf.Pixmap(destino)
                if (verificada.width, verificada.height) != (imagem.width, imagem.height):
                    raise ValueError("Dimensões da capa inválidas")
                print(f"[{indice}/{len(arquivos)}] {destino.name}: {imagem.width} x {imagem.height} px", flush=True)
        except Exception as erro:
            erros.append(f"{arquivo.name}: {erro}")
            print(f"ERRO: {erros[-1]}", file=sys.stderr, flush=True)
    if erros:
        raise RuntimeError("Falha ao gerar capas:\n" + "\n".join(erros))
    print(f"Concluído: {len(arquivos)} capas PNG a 300 DPI.", flush=True)


if __name__ == "__main__":
    main()
