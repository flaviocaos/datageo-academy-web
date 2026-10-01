"""DataGeo Academy — Desafio: Normalização de atributos.
Objetivo: Aplique (x-min)/(max-min). Se todos forem iguais retorne zeros; lista vazia resulta em lista vazia.
1. Complete resolver() substituindo o raise abaixo.
2. Execute python 06_normalizar_minmax.py e faça as verificações passarem.
3. Acrescente casos extremos, validação e documentação de unidades.
Somente biblioteca padrão; os testes fornecidos são exemplos, não avaliação exaustiva.
"""
import math

def resolver(valores):
    # TODO: implemente o algoritmo descrito; mantenha a assinatura da função.
    raise NotImplementedError('Complete resolver() para concluir este exercício.')

CASOS = [([10, 20, 30], [0, 0.5, 1]), ([7, 7], [0, 0]), ([], [])]

def verificar():
    for entrada, esperado in CASOS:
        resultado = resolver(*entrada) if False else resolver(entrada)
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
