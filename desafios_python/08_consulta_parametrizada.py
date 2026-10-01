"""DataGeo Academy — Desafio: Consulta SQL segura.
Objetivo: Retorne tupla (SQL, parâmetros). SQL fixo: SELECT id FROM academy.pontos WHERE categoria = %s; parâmetros devem ser tupla unitária. Nunca concatene a categoria.
1. Complete resolver() substituindo o raise abaixo.
2. Execute python 08_consulta_parametrizada.py e faça as verificações passarem.
3. Acrescente casos extremos, validação e documentação de unidades.
Somente biblioteca padrão; os testes fornecidos são exemplos, não avaliação exaustiva.
"""
import math

def resolver(categoria):
    # TODO: implemente o algoritmo descrito; mantenha a assinatura da função.
    raise NotImplementedError('Complete resolver() para concluir este exercício.')

CASOS = [('escola', ('SELECT id FROM academy.pontos WHERE categoria = %s', ('escola',))), ("x' OR 1=1 --", ('SELECT id FROM academy.pontos WHERE categoria = %s', ("x' OR 1=1 --",)))]

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
