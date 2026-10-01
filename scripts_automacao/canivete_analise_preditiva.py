"""Dez ferramentas de predição espacial/temporal. Python 3.10+.

Instale: pip install numpy pandas scipy scikit-learn
Importe como módulo. Nenhuma previsão é executada automaticamente.
Valide modelos em períodos futuros ou blocos espaciais separados do treino.
"""
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from scipy.interpolate import RBFInterpolator
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import GroupKFold, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def regularizar_serie(dados, coluna_data, coluna_valor, frequencia='MS'):
    """1. Ordena datas e agrega valores pela média na frequência escolhida.

    Exemplo: serie = regularizar_serie(df, 'data', 'chuva', 'MS').
    Lacunas permanecem NaN; não interpole usando dados futuros antes do teste.
    """
    copia = dados[[coluna_data, coluna_valor]].copy()
    copia[coluna_data] = pd.to_datetime(copia[coluna_data], errors='raise')
    copia[coluna_valor] = pd.to_numeric(copia[coluna_valor], errors='raise')
    return copia.set_index(coluna_data)[coluna_valor].sort_index().resample(frequencia).mean()


def criar_defasagens(serie, atrasos=3):
    """2. Cria atributos com valores passados e alvo do período atual.

    Exemplo: tabela = criar_defasagens(serie, 12).
    Linhas incompletas são removidas; lag_1 é o período imediatamente anterior.
    """
    if not isinstance(atrasos, int) or atrasos < 1:
        raise ValueError('Atrasos deve ser inteiro positivo.')
    tabela = pd.DataFrame({'alvo': serie})
    for atraso in range(1, atrasos + 1):
        tabela[f'lag_{atraso}'] = serie.shift(atraso)
    return tabela.dropna()


def dividir_temporalmente(tabela, fracao_treino=0.8):
    """3. Separa treino passado e teste futuro, sem embaralhar.

    Exemplo: treino, teste = dividir_temporalmente(tabela, .8).
    Exige índice crescente e pelo menos uma linha em cada conjunto.
    """
    if not tabela.index.is_monotonic_increasing or not 0 < fracao_treino < 1:
        raise ValueError('Ordene o índice e use uma fração entre zero e um.')
    corte = int(len(tabela) * fracao_treino)
    if corte < 1 or corte >= len(tabela):
        raise ValueError('Dados insuficientes para separar treino e teste.')
    return tabela.iloc[:corte].copy(), tabela.iloc[corte:].copy()


def treinar_ridge(X, y, penalizacao=1.0):
    """4. Ajusta regressão regularizada com imputação e escala internas.

    Exemplo: modelo = treinar_ridge(X_treino, y_treino, 2).
    Retorna pipeline; os dados de teste não participam do ajuste.
    """
    return make_pipeline(SimpleImputer(strategy='median'), StandardScaler(),
                         Ridge(alpha=penalizacao)).fit(X, y)


def treinar_floresta(X, y, arvores=200, semente=42):
    """5. Ajusta predição não linear com Random Forest.

    Exemplo: modelo = treinar_floresta(indicadores_treino, alvo_treino).
    Avalie fora do treino para comparar com uma previsão simples de referência.
    """
    return make_pipeline(SimpleImputer(strategy='median'), RandomForestRegressor(
        n_estimators=arvores, random_state=semente, n_jobs=-1)).fit(X, y)


def prever_recursivamente(modelo, historico, atrasos=3, passos=6):
    """6. Prevê vários períodos alimentando novas previsões nas defasagens.

    Exemplo: futuro = prever_recursivamente(modelo, serie, 3, 6).
    Treine apenas com colunas lag_1..lag_N nessa ordem. A incerteza cresce
    com o horizonte; o retorno contém valores, sem inventar datas futuras.
    """
    valores = list(np.asarray(historico, dtype=float))
    if atrasos < 1 or passos < 1 or len(valores) < atrasos or not np.isfinite(valores[-atrasos:]).all():
        raise ValueError('Informe histórico finito suficiente e contagens positivas.')
    resultado = []
    nomes = [f'lag_{i}' for i in range(1, atrasos + 1)]
    for _ in range(passos):
        linha = [[valores[-i] for i in range(1, atrasos + 1)]]
        X = pd.DataFrame(linha, columns=nomes) if hasattr(modelo, 'feature_names_in_') else np.array(linha)
        valor = float(modelo.predict(X)[0])
        valores.append(valor)
        resultado.append(valor)
    return np.array(resultado)


def prever_tendencia(valores, passos=6):
    """7. Extrapola tendência linear em uma série de intervalos regulares.

    Exemplo: futuro, modelo = prever_tendencia([10, 12, 14], 2).
    Não modela sazonalidade; serve como referência simples para comparação.
    """
    y = np.asarray(valores, dtype=float)
    if y.ndim != 1 or len(y) < 2 or not np.isfinite(y).all() or passos < 1:
        raise ValueError('Informe pelo menos dois valores finitos e passos positivos.')
    modelo = LinearRegression().fit(np.arange(len(y)).reshape(-1, 1), y)
    return modelo.predict(np.arange(len(y), len(y) + passos).reshape(-1, 1)), modelo


def interpolar_idw(coordenadas, valores, destinos, vizinhos=8, potencia=2):
    """8. Interpola por distância inversa em coordenadas métricas.

    Exemplo: superficie = interpolar_idw(xy_amostras, valores, xy_grade).
    Pontos coincidentes são agregados pela média; distância zero retorna essa
    média diretamente, evitando divisão por zero. Não extrapole sem validar.
    """
    xy = np.asarray(coordenadas, dtype=float)
    y = np.asarray(valores, dtype=float)
    alvo = np.asarray(destinos, dtype=float)
    if xy.ndim != 2 or xy.shape[1] != 2 or y.shape != (len(xy),) or len(xy) == 0 or alvo.ndim != 2 or alvo.shape[1] != 2 or potencia <= 0 or vizinhos < 1:
        raise ValueError('Verifique coordenadas Nx2, valores e parâmetros positivos.')
    if not all(np.isfinite(a).all() for a in (xy, y, alvo)):
        raise ValueError('Todos os valores devem ser finitos.')
    unicos, inversos = np.unique(xy, axis=0, return_inverse=True)
    medias = np.bincount(inversos, weights=y) / np.bincount(inversos)
    dist, ids = cKDTree(unicos).query(alvo, k=min(vizinhos, len(unicos)))
    if dist.ndim == 1:
        dist, ids = dist[:, None], ids[:, None]
    exatos = dist[:, 0] == 0
    pesos = (np.maximum(dist[:, :1], np.finfo(float).tiny) / np.maximum(dist, np.finfo(float).tiny)) ** potencia
    resultado = (pesos * medias[ids]).sum(axis=1) / pesos.sum(axis=1)
    resultado[exatos] = medias[ids[exatos, 0]]
    return resultado


def interpolar_rbf(coordenadas, valores, destinos, suavizacao=0.0):
    """9. Interpola superfície com funções de base radial thin-plate spline.

    Exemplo: superficie = interpolar_rbf(xy, z, grade, suavizacao=1).
    Use pontos únicos e não colineares no mesmo CRS projetado. Para dados
    grandes, forneça amostras representativas: o ajuste exige memória.
    """
    modelo = RBFInterpolator(np.asarray(coordenadas, dtype=float),
                             np.asarray(valores, dtype=float), smoothing=suavizacao)
    return modelo(np.asarray(destinos, dtype=float))


def avaliar_previsoes(observado, previsto, modelo=None, X=None, blocos=None, divisões=5):
    """10. Calcula MAE, RMSE e R²; opcionalmente avalia em blocos espaciais.

    Exemplo: metricas = avaliar_previsoes(y_teste, modelo.predict(X_teste)).
    Se fornecer modelo, X e blocos, inclui RMSE por bloco via re-treinamento
    independente. O modelo deve encapsular seu pré-processamento.
    """
    resultado = {'mae': float(mean_absolute_error(observado, previsto)),
                 'rmse': float(np.sqrt(mean_squared_error(observado, previsto))),
                 'r2': float(r2_score(observado, previsto))}
    if any(v is not None for v in (modelo, X, blocos)):
        if any(v is None for v in (modelo, X, blocos)):
            raise ValueError('Forneça modelo, X e blocos juntos.')
        resultado['rmse_blocos'] = -cross_val_score(modelo, X, observado, groups=blocos,
            cv=GroupKFold(divisões), scoring='neg_root_mean_squared_error', error_score='raise')
    return resultado
