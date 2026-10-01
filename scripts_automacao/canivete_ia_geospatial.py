"""Dez ferramentas de IA geoespacial. Python 3.10+.

Instale: pip install numpy scikit-learn rasterio
Importe este arquivo como módulo; nada é executado ao importar.
X deve conter atributos numéricos, uma linha por amostra. Use coordenadas
projetadas em metros nas operações espaciais. Na validação, separe blocos
geográficos para reduzir o vazamento entre pontos vizinhos.
"""
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor, IsolationForest
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.model_selection import GroupKFold, cross_validate


def preparar_atributos(X):
    """1. Ajusta imputação pela mediana e escala. Retorna (matriz, pipeline).

    Exemplo: atributos, preparo = preparar_atributos([[1, 2], [3, np.nan]]).
    Em produção use preparo.transform(novos); não reajuste sobre o teste.
    """
    preparo = make_pipeline(SimpleImputer(strategy='median'), StandardScaler())
    return preparo.fit_transform(X), preparo


def criar_blocos_espaciais(coordenadas, tamanho=1000):
    """2. Cria IDs de blocos quadrados para validação geográfica.

    Exemplo: grupos = criar_blocos_espaciais([[500000, 7000000]], 1000).
    Coordenadas devem ter duas colunas (x, y), no mesmo CRS métrico.
    """
    pontos = np.asarray(coordenadas, dtype=float)
    if pontos.ndim != 2 or pontos.shape[1] != 2 or not np.isfinite(pontos).all() or tamanho <= 0:
        raise ValueError('Informe coordenadas Nx2 finitas e tamanho positivo.')
    _, grupos = np.unique(np.floor(pontos / tamanho), axis=0, return_inverse=True)
    return grupos


def treinar_classificador(X, classes, arvores=200, semente=42):
    """3. Treina Random Forest para classes de uso do solo ou outras categorias.

    Exemplo: modelo = treinar_classificador(X_treino, classes_treino).
    A imputação é ajustada somente ao conjunto informado; use treino separado.
    """
    modelo = make_pipeline(SimpleImputer(strategy='median'), RandomForestClassifier(
        n_estimators=arvores, class_weight='balanced', random_state=semente, n_jobs=-1))
    return modelo.fit(X, classes)


def treinar_regressor(X, valores, arvores=200, semente=42):
    """4. Estima variáveis contínuas, como biomassa ou temperatura.

    Exemplo: modelo = treinar_regressor(X_treino, biomassa_treino).
    Retorna pipeline pronto para modelo.predict(X_novo).
    """
    modelo = make_pipeline(SimpleImputer(strategy='median'), RandomForestRegressor(
        n_estimators=arvores, random_state=semente, n_jobs=-1))
    return modelo.fit(X, valores)


def agrupar_kmeans(X, grupos=3, semente=42):
    """5. Agrupa territórios por semelhança dos atributos padronizados.

    Exemplo: rotulos, modelo = agrupar_kmeans(indicadores, grupos=4).
    IDs de grupos não representam categorias previamente conhecidas.
    """
    modelo = make_pipeline(SimpleImputer(strategy='median'), StandardScaler(),
                           KMeans(n_clusters=grupos, random_state=semente, n_init=10))
    return modelo.fit_predict(X), modelo


def detectar_aglomerados(coordenadas, raio=100, minimo=5):
    """6. Aplica DBSCAN aos pontos projetados em metros.

    Exemplo: rotulos = detectar_aglomerados(xy, raio=500, minimo=4).
    Rótulo -1 identifica ruído. Não use longitude/latitude como metros.
    """
    xy = np.asarray(coordenadas, dtype=float)
    if xy.ndim != 2 or xy.shape[1] != 2 or not np.isfinite(xy).all():
        raise ValueError('As coordenadas devem ser uma matriz Nx2 finita.')
    return DBSCAN(eps=raio, min_samples=minimo).fit_predict(xy)


def detectar_anomalias(X, contaminacao='auto', semente=42):
    """7. Detecta observações atípicas com Isolation Forest.

    Exemplo: rotulos, modelo = detectar_anomalias(indicadores).
    Retorna -1 para candidatos a anomalias e 1 para observações usuais.
    """
    modelo = make_pipeline(SimpleImputer(strategy='median'),
                           IsolationForest(contamination=contaminacao, random_state=semente))
    return modelo.fit_predict(X), modelo


def reduzir_dimensionalidade(X, componentes=2):
    """8. Reduz atributos correlacionados usando PCA após padronização.

    Exemplo: componentes, modelo = reduzir_dimensionalidade(bandas, 2).
    Consulte modelo[-1].explained_variance_ratio_ para variância explicada.
    """
    modelo = make_pipeline(SimpleImputer(strategy='median'), StandardScaler(),
                           PCA(n_components=componentes))
    return modelo.fit_transform(X), modelo


def validar_espacialmente(modelo, X, y, blocos, divisões=5, metrica='accuracy'):
    """9. Avalia um estimador completo com blocos sem sobreposição.

    Exemplo: resultado = validar_espacialmente(modelo, X, y, blocos, 3).
    Passe pipeline com todo o pré-processamento, evitando ajustar X antes.
    """
    if len(np.unique(blocos)) < divisões:
        raise ValueError('O número de blocos deve ser pelo menos o de divisões.')
    return cross_validate(modelo, X, y, groups=blocos,
                          cv=GroupKFold(n_splits=divisões), scoring=metrica,
                          error_score='raise')


def classificar_raster(modelo, entrada, saida, bandas=None):
    """10. Classifica GeoTIFF por janelas, preservando CRS e pixels sem dados.

    Exemplo: classificar_raster(modelo, 'bandas.tif', 'classes.tif', [1, 2, 3]).
    Bandas devem seguir a ordem dos atributos de treino. Classes precisam ser
    inteiros não negativos até 2147483647. A saída usa -1 como nodata.
    """
    from pathlib import Path
    import rasterio
    if Path(entrada).resolve() == Path(saida).resolve() or Path(saida).exists():
        raise FileExistsError('Escolha uma saída nova, diferente da entrada.')
    with rasterio.open(entrada) as src:
        indices = bandas if bandas is not None else list(range(1, src.count + 1))
        perfil = src.profile.copy()
        perfil.update(count=1, dtype='int32', nodata=-1)
        with rasterio.open(saida, 'w', **perfil) as dst:
            for _, janela in src.block_windows(1):
                dados = src.read(indices, window=janela, masked=True)
                valido = ~np.ma.getmaskarray(dados).any(axis=0)
                valido &= np.isfinite(dados.data).all(axis=0)
                resultado = np.full(valido.shape, -1, dtype='int32')
                if valido.any():
                    previsao = np.asarray(modelo.predict(dados.data[:, valido].T), dtype=float)
                    if not np.isfinite(previsao).all() or (previsao < 0).any() or (previsao > 2147483647).any() or (previsao != np.floor(previsao)).any():
                        raise ValueError('Classes precisam ser inteiros não negativos int32.')
                    resultado[valido] = previsao.astype('int32')
                dst.write(resultado, 1, window=janela)
    return str(saida)
