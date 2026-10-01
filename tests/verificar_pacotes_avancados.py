"""Teste integrado das 40 funções com dados sintéticos, sem arquivos do usuário.

Execute: python tests/verificar_pacotes_avancados.py
Requer as dependências documentadas nos quatro pacotes.
"""
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts_automacao'))
import numpy as np
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import box, Polygon
import canivete_ia_geospatial as ia
import canivete_analise_preditiva as pr
import canivete_ciencia_dados as cd
import canivete_programacao_dados as geo


def verificar():
    rng = np.random.default_rng(42)
    X = rng.normal(size=(60, 3))
    y = X[:, 0] * 3 + X[:, 1]
    classes = (X[:, 0] > 0).astype(int)
    xy = np.column_stack((np.arange(60) * 100, np.zeros(60)))
    grupos = ia.criar_blocos_espaciais(xy, 1000)
    assert len(np.unique(grupos)) == 6
    matriz, preparo = ia.preparar_atributos([[1, np.nan], [2, 3], [3, 4]])
    assert np.isfinite(matriz).all() and preparo.transform([[4, 5]]).shape == (1, 2)
    clf = ia.treinar_classificador(X, classes, 10)
    assert (clf.predict(X) == classes).mean() > .9
    assert ia.treinar_regressor(X, y, 10).predict(X).shape == (60,)
    assert len(ia.agrupar_kmeans(X, 3)[0]) == 60
    assert set(ia.detectar_aglomerados([[0, 0], [1, 1], [100, 100]], 3, 2)) == {0, -1}
    assert len(ia.detectar_anomalias(X)[0]) == 60
    assert ia.reduzir_dimensionalidade(X, 2)[0].shape == (60, 2)
    assert len(ia.validar_espacialmente(clf, X, classes, grupos, 3)['test_score']) == 3
    df = pd.DataFrame({'data': pd.date_range('2020-01-01', periods=24, freq='MS'), 'valor': np.arange(24.)})
    serie = pr.regularizar_serie(df, 'data', 'valor')
    lags = pr.criar_defasagens(serie, 3)
    treino, teste = pr.dividir_temporalmente(lags)
    assert treino.index.max() < teste.index.min()
    nomes = ['lag_1', 'lag_2', 'lag_3']
    ridge = pr.treinar_ridge(treino[nomes], treino.alvo)
    assert len(pr.treinar_floresta(X, y, 10).predict(X)) == 60
    assert len(pr.prever_recursivamente(ridge, serie, 3, 4)) == 4
    assert np.allclose(pr.prever_tendencia([1, 2, 3], 2)[0], [4, 5])
    assert np.allclose(pr.interpolar_idw([[0, 0], [0, 0], [2, 0]], [1, 3, 4], [[0, 0], [1, 0]], 3), [2, 3])
    assert np.allclose(pr.interpolar_rbf([[0, 0], [1, 0], [0, 1]], [0, 1, 1], [[.5, .5]]), [1])
    metricas = pr.avaliar_previsoes(y, y, ridge, X, grupos, 3)
    assert metricas['rmse'] == 0 and len(metricas['rmse_blocos']) == 3
    tabela = pd.DataFrame({'grupo': ['a', 'a', 'b', 'b', 'b'], 'valor': [1., 2., 3., np.nan, 100.]})
    assert cd.diagnosticar_qualidade(tabela).loc['valor', 'nulos'] == 1
    assert cd.padronizar_colunas(pd.DataFrame(columns=['Área', 'Area', 'area_2'])).columns.is_unique
    assert cd.converter_numericos(pd.DataFrame({'v': ['1.234,5']}), ['v'], ',', '.').v[0] == 1234.5
    assert not cd.preencher_ausentes(tabela, ['valor']).valor.isna().any()
    assert tabela.valor.isna().sum() == 1  # A fonte permanece intacta.
    assert len(cd.remover_duplicatas(pd.concat([tabela, tabela]))) == 5
    assert cd.marcar_outliers(tabela, ['valor']).valor_outlier.iloc[-1]
    assert len(cd.resumir_por_grupo(tabela, ['grupo'], ['valor'])) == 2
    assert cd.calcular_correlacoes(tabela).shape == (1, 1)
    limite = gpd.GeoDataFrame({'zona': ['a']}, geometry=[box(0, 0, 100, 100)], crs=31982)
    pontos = geo.criar_pontos(pd.DataFrame({'x': [25, 75], 'y': [25, 75]}), 'x', 'y', 31982)
    assert geo.reprojetar_sirgas(pontos).crs.to_epsg() == 4674
    invalido = gpd.GeoDataFrame(geometry=[Polygon([(0, 0), (1, 1), (1, 0), (0, 1), (0, 0)])], crs=31982)
    assert geo.reparar_geometrias(invalido).geometry.is_valid.all()
    buffers = geo.criar_buffers(pontos, 5, 31982)
    assert np.allclose(buffers.area, np.pi * 25, rtol=.01)
    assert geo.juntar_espacialmente(pontos, limite, 'within').zona.tolist() == ['a', 'a']
    assert len(geo.dissolver_por_atributo(pd.concat([limite, limite]), 'zona')) == 1
    assert len(geo.recortar_vetor(pontos, limite)) == 2
    grade = geo.criar_grade(limite, 50, 31982)
    assert len(grade) == 4 and np.isclose(grade.area.sum(), limite.area.sum())
    try:
        geo.criar_buffers(pontos, 5, 4326)
        raise AssertionError('CRS angular aceito em operação métrica')
    except ValueError:
        pass
    with tempfile.TemporaryDirectory() as temp:
        pasta = Path(temp)
        tabela.to_csv(pasta / 'dados.csv', index=False)
        assert len(cd.ler_csv(pasta / 'dados.csv', obrigatorias=['valor'])) == 5
        cd.exportar_relatorio(tabela, pasta / 'qualidade.json')
        try:
            cd.exportar_relatorio(tabela, pasta / 'qualidade.json')
            raise AssertionError('Relatorio existente foi sobrescrito')
        except FileExistsError:
            pass
        import json
        assert json.loads((pasta / 'qualidade.json').read_text(encoding='utf-8'))['linhas'] == 5
        limite.to_file(pasta / 'limite.gpkg', driver='GPKG')
        assert len(geo.ler_vetor(pasta / 'limite.gpkg')) == 1
        perfil = dict(driver='GTiff', height=10, width=10, count=3, dtype='float32',
                      crs='EPSG:31982', transform=from_origin(0, 100, 10, 10), nodata=-9999)
        raster = rng.normal(size=(3, 10, 10)).astype('float32')
        raster[:, 0, 0] = -9999
        with rasterio.open(pasta / 'entrada.tif', 'w', **perfil) as dst:
            dst.write(raster)
        ia.classificar_raster(clf, pasta / 'entrada.tif', pasta / 'classes.tif')
        with rasterio.open(pasta / 'classes.tif') as src:
            assert src.count == 1 and src.crs.to_epsg() == 31982
            assert src.read(1)[0, 0] == -1 and set(np.unique(src.read(1))) <= {-1, 0, 1}
            esperado = clf.predict(raster[:, 1:, :].reshape(3, -1).T).reshape(9, 10)
            assert np.array_equal(src.read(1)[1:, :], esperado)
        mascara = gpd.GeoDataFrame(geometry=[box(0, 50, 50, 100)], crs=31982)
        geo.recortar_raster(pasta / 'entrada.tif', mascara, pasta / 'recorte.tif')
        with rasterio.open(pasta / 'recorte.tif') as src:
            assert src.width == 5 and src.height == 5 and src.nodata == -9999
    from html.parser import HTMLParser
    class Links(HTMLParser):
        downloads = {}
        def handle_starttag(self, tag, attrs):
            dados = dict(attrs)
            if tag == 'a' and 'download' in dados:
                self.downloads[dados['href']] = dados['download']
    site = Path(__file__).resolve().parents[1]
    parser = Links()
    parser.feed((site / 'index.html').read_text(encoding='utf-8'))
    import ast
    for nome in ['ia_geospatial', 'analise_preditiva', 'ciencia_dados', 'programacao_dados']:
        caminho = f'./scripts_automacao/canivete_{nome}.py'
        assert parser.downloads[caminho] == f'canivete_{nome}.py'
        arvore = ast.parse((site / caminho).read_text(encoding='utf-8'))
        assert sum(isinstance(no, ast.FunctionDef) for no in arvore.body) == 10
    print('OK: 40 funcoes, dados vetoriais/raster, validacao espacial e 4 downloads.')


if __name__ == '__main__':
    verificar()
