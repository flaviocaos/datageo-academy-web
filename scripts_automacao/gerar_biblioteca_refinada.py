"""Gera materiais independentes da Central Premium. Execute com Python 3.10+.

Os cálculos usam coordenadas planas em metros; não recebem latitude/longitude.
Os desafios são deliberadamente incompletos e incluem verificações executáveis.
"""
from pathlib import Path
import json
import textwrap

ROOT = Path(__file__).resolve().parents[1]

TOPO = [
('01_distancia_planimetrica', 'Distância planimétrica', 'Distância horizontal entre dois pontos em metros.', '''
def calcular(ponto_a, ponto_b):
    a, b = ponto(ponto_a), ponto(ponto_b)
    return math.hypot(b[0]-a[0], b[1]-a[1])
''', {'ponto_a': [0, 0], 'ponto_b': [3, 4]}),
('02_azimute', 'Azimute topográfico', 'Ângulo em graus, contado do norte no sentido horário.', '''
def calcular(ponto_a, ponto_b):
    a, b = ponto(ponto_a), ponto(ponto_b)
    de, dn = b[0]-a[0], b[1]-a[1]
    if de == 0 and dn == 0:
        raise ValueError('Pontos coincidentes não definem azimute.')
    return math.degrees(math.atan2(de, dn)) % 360
''', {'ponto_a': [0, 0], 'ponto_b': [10, 0]}),
('03_projecao_ponto', 'Projeção de ponto', 'Calcula a coordenada final a partir de distância e azimute.', '''
def calcular(origem, azimute, distancia):
    e, n = ponto(origem)
    d = numero(distancia)
    if d < 0:
        raise ValueError('Distância não pode ser negativa.')
    a = math.radians(numero(azimute) % 360)
    return [e+d*math.sin(a), n+d*math.cos(a)]
''', {'origem': [100, 200], 'azimute': 90, 'distancia': 50}),
('04_area_poligono', 'Área por coordenadas', 'Área de polígono simples pelo método de Gauss, em m² e hectares.', '''
def calcular(vertices):
    v = poligono(vertices)
    # Translação reduz perda de precisão em coordenadas UTM de grande magnitude.
    e0, n0 = v[0]
    q = [(e-e0, n-n0) for e,n in v]
    area = abs(math.fsum(a[0]*b[1]-b[0]*a[1]
                        for a,b in zip(q, q[1:]+q[:1]))) / 2
    return {'area_m2': area, 'area_ha': area/10000}
''', {'vertices': [[0, 0], [100, 0], [100, 100], [0, 100]]}),
('05_perimetro', 'Perímetro de polígono', 'Soma dos lados incluindo o fechamento do último vértice.', '''
def calcular(vertices):
    v = poligono(vertices)
    return math.fsum(math.hypot(b[0]-a[0], b[1]-a[1])
                     for a,b in zip(v, v[1:]+v[:1]))
''', {'vertices': [[0, 0], [3, 0], [3, 4]]}),
('06_fechamento_poligonal', 'Fechamento de poligonal', 'Erro linear e precisão relativa de um circuito fechado.', '''
def calcular(lados):
    # Cada lado: [azimute em graus, distância em metros].
    pares = [ponto(lado) for lado in lados]
    if not pares or any(d <= 0 for a,d in pares):
        raise ValueError('Informe lados com distâncias positivas.')
    de = math.fsum(d*math.sin(math.radians(a)) for a,d in pares)
    dn = math.fsum(d*math.cos(math.radians(a)) for a,d in pares)
    total = math.fsum(d for a,d in pares)
    erro = math.hypot(de, dn)
    return {'erro_e': de, 'erro_n': dn, 'erro_linear_m': erro,
            'perimetro_m': total,
            'precisao_1_para': None if erro <= total*1e-12 else total/erro}
''', {'lados': [[0, 100], [90, 100], [180, 100], [270, 100]]}),
('07_compensacao_bowditch', 'Compensação de Bowditch', 'Distribui o erro de fechamento proporcionalmente aos comprimentos.', '''
def calcular(origem, lados):
    # Aplicável a circuito fechado; não substitui ajustamento por mínimos quadrados.
    inicio = ponto(origem)
    pares = [ponto(lado) for lado in lados]
    if len(pares) < 3 or any(d <= 0 for a,d in pares):
        raise ValueError('Circuito precisa de pelo menos três lados positivos.')
    inc = [(d*math.sin(math.radians(a)), d*math.cos(math.radians(a)))
           for a,d in pares]
    erro_e, erro_n = math.fsum(x for x,y in inc), math.fsum(y for x,y in inc)
    total = math.fsum(d for a,d in pares)
    estacoes, correc = [list(inicio)], []
    for (de,dn), (_,d) in zip(inc, pares):
        ce, cn = -erro_e*d/total, -erro_n*d/total
        correc.append({'correcao_e': ce, 'correcao_n': cn})
        e,n = estacoes[-1]
        estacoes.append([e+de+ce, n+dn+cn])
    return {'estacoes': estacoes, 'correcoes': correc,
            'erro_original_m': math.hypot(erro_e, erro_n)}
''', {'origem': [0, 0], 'lados': [[0, 100], [90, 100], [180, 100], [270, 99.9]]}),
('08_nivelamento', 'Nivelamento geométrico', 'Calcula cotas e compensa fechamento por extensão nivelada.', '''
def calcular(cota_inicial, leituras, cota_final_conhecida=None):
    # Cada estação: [leitura de ré, leitura de vante, extensão nivelada em metros].
    cota = numero(cota_inicial)
    dados = [[numero(x) for x in linha] for linha in leituras]
    if not dados or any(len(linha)!=3 or linha[2]<=0 for linha in dados):
        raise ValueError('Informe estações [ré, vante, distância positiva].')
    if any(re < 0 or vante < 0 for re,vante,d in dados):
        raise ValueError('Leituras de mira devem ser não negativas.')
    cotas = [cota]
    for re,vante,d in dados:
        cotas.append(cotas[-1]+re-vante)
    erro = 0 if cota_final_conhecida is None else cotas[-1]-numero(cota_final_conhecida)
    total = math.fsum(d for re,vante,d in dados)
    acumulada, ajustadas = 0, [cota]
    for i, (re,vante,d) in enumerate(dados, 1):
        acumulada += d
        ajustadas.append(cotas[i]-erro*acumulada/total)
    return {'cotas_brutas': cotas, 'cotas_ajustadas': ajustadas,
            'erro_fechamento_m': erro, 'compensado': cota_final_conhecida is not None}
''', {'cota_inicial': 100, 'leituras': [[1.5, 1.0, 50], [1.2, 0.8, 50]], 'cota_final_conhecida': 100.8}),
('09_intersecao_direcoes', 'Interseção de direções', 'Encontra a interseção à frente de duas estações conhecidas.', '''
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
''', {'estacao_a': [0, 0], 'azimute_a': 45, 'estacao_b': [10, 0], 'azimute_b': 315}),
('10_memorial_descritivo', 'Memorial descritivo', 'Gera texto com vértices, azimutes, distâncias, área e perímetro.', '''
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
    return '\\n'.join(linhas)
''', {'vertices': [[500000, 6900000], [500100, 6900000], [500100, 6900100], [500000, 6900100]], 'identificacao': 'Parcela didática', 'referencia': 'SIRGAS 2000 / UTM 22S — EPSG:31982'}),
]

COMMON = '''
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
'''

EXERCISES = [
('01_filtrar_medicoes', 'Filtrar medições válidas', 'Retorne somente valores numéricos finitos e não negativos; ignore None, textos e booleanos.',
 'valores', [([1, None, -2, 0, 'x', True], [1, 0]), ([], [])]),
('02_azimute', 'Azimute do norte', 'Receba dois pontos [E,N]. Use atan2(delta E, delta N), converta para graus e normalize em [0,360). Rejeite pontos coincidentes.',
 'a, b', [(([0,0],[1,0]),90), (([0,0],[0,-1]),180)]),
('03_area_hectares', 'Área em hectares', 'Receba vértices de polígono simples plano em metros; use Gauss, módulo e divida por 10000. Inclua o último lado.',
 'vertices', [([[0,0],[100,0],[100,100],[0,100]],1), ([[0,0],[0,100],[100,0]],0.5)]),
('04_deduplicar_pontos', 'Deduplicação estável', 'Remova coordenadas repetidas preservando a ordem. Retorne uma lista de listas, sem modificar a entrada.',
 'pontos', [([[1,2],[1,2],[3,4]],[[1,2],[3,4]]), ([],[])]),
('05_mediana', 'Mediana sem dependências', 'Ordene uma cópia dos valores e calcule o centro; em tamanho par use a média dos dois centrais. Rejeite lista vazia.',
 'valores', [([3,1,2],2), ([10,2,4,8],6)]),
('06_normalizar_minmax', 'Normalização de atributos', 'Aplique (x-min)/(max-min). Se todos forem iguais retorne zeros; lista vazia resulta em lista vazia.',
 'valores', [([10,20,30],[0,0.5,1]), ([7,7],[0,0]), ([],[])]),
('07_interpolar_idw', 'Interpolação IDW', 'Receba pontos [E,N,valor] e alvo [E,N]. Use pesos 1/distância². Se o alvo coincidir com um ponto, retorne seu valor.',
 'pontos, alvo', [(([[0,0,10],[2,0,20]],[1,0]),15), (([[0,0,10],[2,0,20]],[0,0]),10)]),
('08_consulta_parametrizada', 'Consulta SQL segura', 'Retorne tupla (SQL, parâmetros). SQL fixo: SELECT id FROM academy.pontos WHERE categoria = %s; parâmetros devem ser tupla unitária. Nunca concatene a categoria.',
 'categoria', [('escola',('SELECT id FROM academy.pontos WHERE categoria = %s',('escola',))), ("x' OR 1=1 --",('SELECT id FROM academy.pontos WHERE categoria = %s',("x' OR 1=1 --",)))]),
('09_mae', 'Erro absoluto médio', 'Calcule média dos erros absolutos entre observado e previsto. Rejeite comprimentos diferentes ou vetores vazios.',
 'observado, previsto', [(([1,2,3],[2,2,5]),1), (([0,0],[0,0]),0)]),
('10_agrupar_categorias', 'Resumo por categoria', 'Receba lista de registros com categoria e area_ha. Some áreas por categoria e devolva um dicionário.',
 'registros', [([{'categoria':'A','area_ha':1},{'categoria':'A','area_ha':2},{'categoria':'B','area_ha':4}],{'A':3,'B':4}), ([],{})]),
]

def gerar():
    topo, desafios = ROOT/'scripts_topografia', ROOT/'desafios_python'
    topo.mkdir(exist_ok=True); desafios.mkdir(exist_ok=True)
    for nome,titulo,descricao,corpo,exemplo in TOPO:
        cab = f'''"""DataGeo Academy — {titulo}.
{descricao}

Uso: python {nome}.py --exemplo
     python {nome}.py entrada.json --saida resultado.json
Importação: calcular(**dados). JSON deve usar as chaves mostradas por --exemplo.
Coordenadas E/N em CRS projetado, distâncias em metros e ângulos em graus.
Não realiza transformação de datum nem correção de distâncias de terreno.
Saída é cálculo didático, sujeito à revisão para uso profissional.
"""\n'''
        cli = f'''
EXEMPLO = {exemplo!r}

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
                arquivo.write(texto+'\\n')
        else:
            print(texto)
    except (ValueError, TypeError, OSError) as erro:
        parser.exit(2, f'Erro: {{erro}}\\n')

if __name__ == '__main__':
    main()
'''
        (topo/f'{nome}.py').write_text(cab+COMMON+textwrap.dedent(corpo)+cli,encoding='utf-8')
    for nome,titulo,instrucao,args,casos in EXERCISES:
        multiplo = ', ' in args
        fonte = f'''"""DataGeo Academy — Desafio: {titulo}.
Objetivo: {instrucao}
1. Complete resolver() substituindo o raise abaixo.
2. Execute python {nome}.py e faça as verificações passarem.
3. Acrescente casos extremos, validação e documentação de unidades.
Somente biblioteca padrão; os testes fornecidos são exemplos, não avaliação exaustiva.
"""
import math

def resolver({args}):
    # TODO: implemente o algoritmo descrito; mantenha a assinatura da função.
    raise NotImplementedError('Complete resolver() para concluir este exercício.')

CASOS = {casos!r}

def verificar():
    for entrada, esperado in CASOS:
        resultado = resolver(*entrada) if {multiplo!r} else resolver(entrada)
        if isinstance(esperado, (int,float)):
            assert math.isclose(resultado, esperado, rel_tol=1e-9, abs_tol=1e-9), (resultado, esperado)
        else:
            assert resultado == esperado, (resultado, esperado)
    print('Casos fornecidos aprovados! Amplie os testes com entradas inválidas e limites.')

if __name__ == '__main__':
    try:
        verificar()
    except NotImplementedError as erro:
        print('Exercício pendente:', erro)
        raise SystemExit(1)
'''
        (desafios/f'{nome}.py').write_text(fonte,encoding='utf-8')
    print('10 scripts topográficos e 10 desafios gerados.')

if __name__ == '__main__':
    gerar()
