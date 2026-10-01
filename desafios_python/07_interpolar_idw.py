"""DataGeo Academy — Desafio: Interpolação IDW.
Objetivo: Receba pontos [E,N,valor] e alvo [E,N]. Use pesos 1/distância². Se o alvo coincidir com um ponto, retorne seu valor.
1. Complete resolver() substituindo o raise abaixo.
2. Execute python 07_interpolar_idw.py e faça as verificações passarem.
3. Acrescente casos extremos, validação e documentação de unidades.
Somente biblioteca padrão; os testes fornecidos são exemplos, não avaliação exaustiva.
"""
import math

def resolver(pontos, alvo):
    # TODO: implemente o algoritmo descrito; mantenha a assinatura da função.
    raise NotImplementedError('Complete resolver() para concluir este exercício.')

CASOS = [(([[0, 0, 10], [2, 0, 20]], [1, 0]), 15), (([[0, 0, 10], [2, 0, 20]], [0, 0]), 10)]

def verificar():
    for entrada, esperado in CASOS:
        resultado = resolver(*entrada) if True else resolver(entrada)
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
