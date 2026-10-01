"""Extrai anexos do livro em uma pasta nova, sem sobrescrever arquivos.
Uso: python scripts_automacao/extrair_laboratorios_pdf.py livro.pdf pasta_saida
Requer PyMuPDF. Os livros novos incorporam dados e 12 laboratórios Python.
"""
from pathlib import Path
import argparse
import sys
ROOT=Path(__file__).resolve().parents[1]
try:import pymupdf
except ImportError:
    sys.path.insert(0,str(ROOT/'.capas-deps'));import pymupdf

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('pdf',type=Path);p.add_argument('saida',type=Path);args=p.parse_args()
    with pymupdf.open(args.pdf) as doc:
        names=doc.embfile_names()
        if not names:raise SystemExit('Este PDF não contém laboratórios incorporados.')
        if any(Path(n).name!=n or '\\' in n or ':' in n for n in names):
            raise SystemExit('Nome de anexo inválido; extração interrompida.')
        args.saida.mkdir(parents=True,exist_ok=False)
        for name in names:
            with (args.saida/name).open('xb') as f:f.write(doc.embfile_get(name))
    print(f'{len(names)} arquivos extraídos. Consulte o conteúdo antes de executar.')

if __name__=='__main__':main()
