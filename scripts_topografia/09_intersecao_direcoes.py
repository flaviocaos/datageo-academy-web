"""DataGeo Academy — Interseção de direções.
Encontra a interseção à frente de duas estações conhecidas.

Uso: python 09_intersecao_direcoes.py --exemplo
     python 09_intersecao_direcoes.py entrada.json --saida resultado.json
Importação: calcular(**dados). JSON deve usar as chaves mostradas por --exemplo.
Coordenadas E/N em CRS projetado, distâncias em metros e ângulos em graus.
Não realiza transformação de datum nem correção de distâncias de terreno.
Saída é cálculo didático, sujeito à revisão para uso profissional.
"""

import argparse
import json
import math
from pathlib import Path

def numero(valor):
    resultado = float(valor)
    if not math.isfinite(resultado):
        raise ValueError('Valores devem ser finitos.')
    return resultado

def ponto(valor):
    if len(valor) != 2:
        raise ValueError('Ponto deve conter [E, N], em metros.')
    return tuple(numero(x) for x in valor)

def poligono(vertices):
    v = [ponto(p) for p in vertices]
    if len(v)>1 and v[0]==v[-1]:
        v.pop()
    if len(v)<3 or len(set(v))!=len(v):
        raise ValueError('Polígono precisa de três vértices distintos, sem repetição.')
    def orient(a,b,c):
        return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    def on(a,b,p):
        return orient(a,b,p)==0 and min(a[0],b[0])<=p[0]<=max(a[0],b[0]) and min(a[1],b[1])<=p[1]<=max(a[1],b[1])
    lados = list(zip(v, v[1:]+v[:1]))
    for i,(a,b) in enumerate(lados):
        for j,(c,d) in enumerate(lados):
            if j<=i or j==i+1 or (i==0 and j==len(v)-1):
                continue
            o1,o2,o3,o4 = orient(a,b,c),orient(a,b,d),orient(c,d,a),orient(c,d,b)
            if (o1*o2<0 and o3*o4<0) or on(a,b,c) or on(a,b,d) or on(c,d,a) or on(c,d,b):
                raise ValueError('Polígono possui cruzamento ou contato entre lados não adjacentes.')
    a = v[0]
    if math.fsum((b[0]-a[0])*(c[1]-a[1])-(c[0]-a[0])*(b[1]-a[1]) for b,c in lados)==0:
        raise ValueError('Polígono degenerado, com área zero.')
    return v

def calcular(estacao_a, azimute_a, estacao_b, azimute_b):
    a, b = ponto(estacao_a), ponto(estacao_b)
    aa, ab = math.radians(numero(azimute_a)), math.radians(numero(azimute_b))
    u, v = (math.sin(aa), math.cos(aa)), (math.sin(ab), math.cos(ab))
    cruz = lambda x,y: x[0]*y[1]-x[1]*y[0]
    det = cruz(u,v)
    if abs(det) < 1e-10:
        raise ValueError('Direções paralelas ou numericamente instáveis.')
    delta = (b[0]-a[0], b[1]-a[1])
    t, s = cruz(delta,v)/det, cruz(delta,u)/det
    if t < -1e-9 or s < -1e-9:
        raise ValueError('Interseção está atrás de uma das estações.')
    return {'ponto': [a[0]+t*u[0], a[1]+t*u[1]], 'distancia_a': t, 'distancia_b': s}

EXEMPLO = {'estacao_a': [0, 0], 'azimute_a': 45, 'estacao_b': [10, 0], 'azimute_b': 315}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('entrada', nargs='?', type=Path)
    parser.add_argument('--exemplo', action='store_true')
    parser.add_argument('--saida', type=Path)
    args = parser.parse_args()
    if args.exemplo:
        print(json.dumps(EXEMPLO, ensure_ascii=False, indent=2))
        return
    if args.entrada is None:
        parser.error('Informe entrada.json ou --exemplo.')
    try:
        dados = json.loads(args.entrada.read_text(encoding='utf-8-sig'))
        resultado = calcular(**dados)
        texto = resultado if isinstance(resultado,str) else json.dumps(resultado, ensure_ascii=False, indent=2, allow_nan=False)
        if args.saida:
            # Não sobrescreve uma entrega já existente.
            with args.saida.open('x', encoding='utf-8') as arquivo:
                arquivo.write(texto+'\n')
        else:
            print(texto)
    except (ValueError, TypeError, OSError) as erro:
        parser.exit(2, f'Erro: {erro}\n')

if __name__ == '__main__':
    main()
