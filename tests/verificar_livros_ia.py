"""Verifica conteúdo independente, páginas, diagramação e 48 exemplos reais."""
from pathlib import Path
import hashlib
import json
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts_automacao'))
from gerar_livros_ia import LIVROS, ANTIGOS, HASH_OFICIAL, OFICIAL, PASTA, fitz, executar

def validar_documento(doc,livro):
    assert 40<=len(doc)<=60 and len(doc)==42
    assert doc.metadata['title']==livro.TITULO
    assert doc.metadata['author']=='DataGeo Academy'
    assert [t[1] for t in doc.get_toc()]==[f'{n:02d}. {c["titulo"]}' for n,c in enumerate(livro.CAPITULOS,1)]
    assert [t[2] for t in doc.get_toc()]==list(range(5,41,3))
    assert len(doc.embfile_names())==15
    fonte=json.loads(doc.embfile_get('fonte_editorial.json'))
    assert fonte['capitulos']==json.loads(json.dumps(livro.CAPITULOS,ensure_ascii=False))
    refs=json.loads(doc.embfile_get('resultados_laboratorios.json'))
    assert len(refs)==12
    counts=[]
    for i,c in enumerate(livro.CAPITULOS):
        teoria,lab,ex=[doc[p].get_text() for p in range(4+3*i,7+3*i)]
        assert 'Hipóteses e aprofundamento técnico' in teoria
        assert 'Resultado de referência calculado' in lab
        assert 'Leitura do código' in lab
        assert 'Comentário de solução' in ex and 'Aplicação ampliada' in ex
        assert doc.embfile_get(f'capitulo_{i+1:02d}.py').decode('utf-8')==c['codigo']
        for texto in [teoria,lab,ex]:
            assert '\ufffd' not in texto
            counts.append(len(texto.split()))
    assert min(counts)>=120
    assert sum(counts)>=9000, (livro.TITULO,sum(counts))
    for page in doc[1:]:
        for b in page.get_text('blocks'):
            assert b[0]>=0 and b[1]>=0 and b[2]<=page.rect.width+.2 and b[3]<=page.rect.height+.2
    return sum(counts)

def main():
    assert hashlib.sha256((PASTA/OFICIAL).read_bytes()).hexdigest()==HASH_OFICIAL
    total=0; textos=set(); codigos=set(); assinaturas=[]
    for livro in LIVROS:
        with fitz.open(PASTA/(livro.TITULO+'.pdf')) as doc:
            palavras=validar_documento(doc,livro);total+=palavras
        for c in livro.CAPITULOS:
            assert c['codigo'] not in codigos;codigos.add(c['codigo'])
            for p in c['teoria']+[c['aprofundamento'],c['leitura_codigo'],c['tarefa'],c['resposta'],c['ampliacao']]:
                assert p not in textos, 'Parágrafo editorial clonado';textos.add(p)
        # Similaridade lexical de sequências de cinco palavras, sem cabeçalhos comuns.
        tokens=re.findall(r'\w+',' '.join(' '.join(c['teoria'])+' '+c['aprofundamento'] for c in livro.CAPITULOS).lower())
        assinaturas.append(set(zip(tokens,tokens[1:],tokens[2:],tokens[3:],tokens[4:])))
        executar(livro)
        print(livro.TITULO+f': 42 páginas, {palavras} palavras técnicas, 12 códigos OK',flush=True)
    for i,a in enumerate(assinaturas):
        for b in assinaturas[i+1:]:
            assert len(a&b)/min(len(a),len(b))<.05,'Conteúdo excessivamente semelhante'
    if '--antes-integrar' not in sys.argv:
        assert all(not (PASTA/n).exists() for n in ANTIGOS)
    print(f'OK: quatro livros independentes, 168 páginas, {total} palavras técnicas, 48 laboratórios, oficial intacto.')

if __name__=='__main__':main()
