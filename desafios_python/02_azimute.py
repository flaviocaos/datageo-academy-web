"""DataGeo Academy — Desafio: Azimute do norte.
Objetivo: Receba dois pontos [E,N]. Use atan2(delta E, delta N), converta para graus e normalize em [0,360). Rejeite pontos coincidentes.
1. Complete resolver() substituindo o raise abaixo.
2. Execute python 02_azimute.py e faça as verificações passarem.
3. Acrescente casos extremos, validação e documentação de unidades.
Somente biblioteca padrão; os testes fornecidos são exemplos, não avaliação exaustiva.
"""
import math

def resolver(a, b):
    # TODO: implemente o algoritmo descrito; mantenha a assinatura da função.
    raise NotImplementedError('Complete resolver() para concluir este exercício.')

CASOS = [(([0, 0], [1, 0]), 90), (([0, 0], [0, -1]), 180)]

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
