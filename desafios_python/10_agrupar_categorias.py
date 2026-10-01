"""DataGeo Academy — Desafio: Resumo por categoria.
Objetivo: Receba lista de registros com categoria e area_ha. Some áreas por categoria e devolva um dicionário.
1. Complete resolver() substituindo o raise abaixo.
2. Execute python 10_agrupar_categorias.py e faça as verificações passarem.
3. Acrescente casos extremos, validação e documentação de unidades.
Somente biblioteca padrão; os testes fornecidos são exemplos, não avaliação exaustiva.
"""
import math

def resolver(registros):
    # TODO: implemente o algoritmo descrito; mantenha a assinatura da função.
    raise NotImplementedError('Complete resolver() para concluir este exercício.')

CASOS = [([{'categoria': 'A', 'area_ha': 1}, {'categoria': 'A', 'area_ha': 2}, {'categoria': 'B', 'area_ha': 4}], {'A': 3, 'B': 4}), ([], {})]

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
