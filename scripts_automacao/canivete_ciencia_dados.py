"""Dez ferramentas de ciência de dados. Python 3.10+.

Instale: pip install pandas numpy
As funções retornam cópias e não modificam o DataFrame original.
Importe como módulo e utilize as funções sobre suas tabelas.
"""
import json
import re
import unicodedata
from pathlib import Path
import numpy as np
import pandas as pd


def ler_csv(caminho, separador=',', codificacao='utf-8', obrigatorias=()):
    """1. Lê CSV e verifica colunas obrigatórias.

    Exemplo: df = ler_csv('dados.csv', ';', obrigatorias=['municipio']).
    Erros de codificação ou linhas inválidas são reportados, não descartados.
    """
    df = pd.read_csv(caminho, sep=separador, encoding=codificacao)
    faltantes = set(obrigatorias) - set(df.columns)
    if faltantes:
        raise ValueError(f'Colunas ausentes: {sorted(faltantes)}')
    return df


def diagnosticar_qualidade(df):
    """2. Gera uma tabela de tipo, nulos, percentual nulo e valores distintos.

    Exemplo: diagnosticar_qualidade(df).to_csv('qualidade.csv').
    O percentual é zero para uma tabela vazia, sem divisão por zero.
    """
    return pd.DataFrame({'tipo': df.dtypes.astype(str), 'nulos': df.isna().sum(),
        'percentual_nulo': df.isna().sum() * 100 / max(len(df), 1),
        'distintos': df.nunique(dropna=True)})


def padronizar_colunas(df):
    """3. Remove acentos e símbolos, usando nomes minúsculos com underscores.

    Exemplo: limpo = padronizar_colunas(df).
    Evita nomes duplicados com sufixos, inclusive colisões com nomes existentes.
    """
    copia = df.copy()
    usados, nomes = set(), []
    for coluna in df.columns:
        texto = unicodedata.normalize('NFKD', str(coluna)).encode('ascii', 'ignore').decode()
        base = re.sub(r'[^a-z0-9]+', '_', texto.lower()).strip('_') or 'coluna'
        nome, numero = base, 2
        while nome in usados:
            nome, numero = f'{base}_{numero}', numero + 1
        usados.add(nome)
        nomes.append(nome)
    copia.columns = nomes
    return copia


def converter_numericos(df, colunas, decimal='.', milhar=None, erros='raise'):
    """4. Converte números textuais, incluindo formato brasileiro.

    Exemplo: convertido = converter_numericos(df, ['area'], ',', '.').
    erros='coerce' transforma valores inválidos em NaN; padrão reporta erro.
    """
    if decimal == milhar:
        raise ValueError('Separadores decimal e de milhar devem ser diferentes.')
    copia = df.copy()
    for coluna in colunas:
        texto = copia[coluna].astype('string').str.strip()
        if milhar:
            texto = texto.str.replace(milhar, '', regex=False)
        texto = texto.str.replace(decimal, '.', regex=False)
        copia[coluna] = pd.to_numeric(texto, errors=erros)
    return copia


def preencher_ausentes(df, colunas, estrategia='mediana', valor=None):
    """5. Preenche lacunas por mediana, moda ou constante.

    Exemplo: preenchido = preencher_ausentes(df, ['renda'], 'mediana').
    Para modelos, calcule valores no treino e aplique constantes ao teste.
    Colunas inteiramente vazias exigem estrategia='constante' e valor válido.
    """
    copia = df.copy()
    for coluna in colunas:
        if estrategia == 'mediana':
            preenchimento = copia[coluna].median()
        elif estrategia == 'moda':
            moda = copia[coluna].mode(dropna=True)
            preenchimento = moda.iloc[0] if len(moda) else None
        elif estrategia == 'constante':
            preenchimento = valor
        else:
            raise ValueError('Use mediana, moda ou constante.')
        if preenchimento is None or pd.isna(preenchimento):
            raise ValueError(f'Não foi possível preencher {coluna}.')
        copia[coluna] = copia[coluna].fillna(preenchimento)
    return copia


def remover_duplicatas(df, chaves=None, manter='first'):
    """6. Elimina registros repetidos por todas as colunas ou por chaves.

    Exemplo: unicos = remover_duplicatas(df, ['codigo_ibge']).
    manter='last' conserva o último; manter=False elimina todas as ocorrências.
    """
    return df.drop_duplicates(subset=chaves, keep=manter).copy()


def marcar_outliers(df, colunas, fator=1.5):
    """7. Marca candidatos a outliers pela regra do intervalo interquartil.

    Exemplo: marcado = marcar_outliers(df, ['area', 'renda']).
    Cria colunas <nome>_outlier sem apagar dados. Revise casos com especialistas.
    """
    if fator <= 0:
        raise ValueError('O fator deve ser positivo.')
    copia = df.copy()
    for coluna in colunas:
        destino = f'{coluna}_outlier'
        if destino in copia.columns:
            raise ValueError(f'Coluna de saída já existe: {destino}')
        q1, q3 = copia[coluna].quantile([.25, .75])
        iqr = q3 - q1
        copia[destino] = (copia[coluna] < q1 - fator * iqr) | (copia[coluna] > q3 + fator * iqr)
    return copia


def resumir_por_grupo(df, grupos, valores):
    """8. Produz contagem, média, mediana, soma, mínimo e máximo por grupo.

    Exemplo: resumo = resumir_por_grupo(df, ['municipio'], ['area']).
    Valores precisam ser numéricos; grupos nulos são mantidos no resultado.
    """
    return df.groupby(grupos, dropna=False)[valores].agg(['count', 'mean', 'median', 'sum', 'min', 'max'])


def calcular_correlacoes(df, colunas=None, metodo='pearson'):
    """9. Calcula correlações numéricas com pares de observações disponíveis.

    Exemplo: matriz = calcular_correlacoes(df, ['area', 'populacao'], 'spearman').
    Correlação não estabelece causalidade; colunas constantes resultam em NaN.
    """
    numericos = df[colunas] if colunas is not None else df.select_dtypes(include='number')
    return numericos.corr(method=metodo, min_periods=2)


def exportar_relatorio(df, caminho):
    """10. Salva diagnóstico de qualidade e estatísticas numéricas em JSON.

    Exemplo: exportar_relatorio(df, 'relatorio.json').
    Não sobrescreve arquivos. Valores ausentes são serializados como null.
    """
    numericos = df.select_dtypes(include='number')
    resumo = numericos.describe().to_dict() if len(numericos.columns) else {}
    relatorio = {'linhas': len(df), 'colunas': len(df.columns),
        'duplicatas': int(df.duplicated().sum()),
        'qualidade': diagnosticar_qualidade(df).to_dict(orient='index'), 'estatisticas': resumo}
    def normalizar(obj):
        if isinstance(obj, dict):
            return {str(k): normalizar(v) for k, v in obj.items()}
        if isinstance(obj, (float, np.floating)) and not np.isfinite(obj):
            return None
        if isinstance(obj, np.generic):
            return obj.item()
        return obj
    with Path(caminho).open('x', encoding='utf-8') as arquivo:
        json.dump(normalizar(relatorio), arquivo, ensure_ascii=False, indent=2, allow_nan=False)
    return str(caminho)
