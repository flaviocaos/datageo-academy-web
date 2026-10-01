"""DataGeo Academy — Memorial descritivo.
Gera texto com vértices, azimutes, distâncias, área e perímetro.

Uso: python 10_memorial_descritivo.py --exemplo
     python 10_memorial_descritivo.py entrada.json --saida resultado.json
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

def calcular(vertices, identificacao, referencia):
    v = poligono(vertices)
    if not str(identificacao).strip() or not str(referencia).strip():
        raise ValueError('Informe identificação e CRS projetado, incluindo zona UTM.')
    e0,n0 = v[0]
    area = abs(math.fsum((a[0]-e0)*(b[1]-n0)-(b[0]-e0)*(a[1]-n0)
                        for a,b in zip(v,v[1:]+v[:1])))/2
    linhas = ['MEMORIAL DESCRITIVO — DataGeo Academy', str(identificacao),
              'Referência: '+str(referencia), 'Coordenadas E/N e distâncias em metros.']
    perimetro = 0
    for i,(a,b) in enumerate(zip(v,v[1:]+v[:1])):
        de,dn = b[0]-a[0], b[1]-a[1]
        d = math.hypot(de,dn); perimetro += d
        az = math.degrees(math.atan2(de,dn)) % 360
        linhas.append(f'V{i+1:02d}: E={a[0]:.3f}; N={a[1]:.3f}; '
                      f'segue para V{(i+1)%len(v)+1:02d}, azimute={az:.6f}°, distância={d:.3f} m.')
    linhas += [f'Área: {area:.3f} m² ({area/10000:.6f} ha).', f'Perímetro: {perimetro:.3f} m.',
               'Minuta de cálculo: revisar dados, confrontantes, responsabilidade técnica e requisitos da finalidade.']
    return '\n'.join(linhas)

EXEMPLO = {'vertices': [[500000, 6900000], [500100, 6900000], [500100, 6900100], [500000, 6900100]], 'identificacao': 'Parcela didática', 'referencia': 'SIRGAS 2000 / UTM 22S — EPSG:31982'}

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
