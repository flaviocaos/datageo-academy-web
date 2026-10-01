"""Dez ferramentas de programação geográfica. Python 3.10+.

Instale: pip install geopandas shapely pyproj rasterio numpy pandas
Importe como módulo. As funções vetoriais retornam novas GeoDataFrames.
Informe CRS corretos; atribuir CRS não equivale a reprojetar coordenadas.
"""
from pathlib import Path
import numpy as np
import geopandas as gpd
from shapely import make_valid
from shapely.geometry import box


def ler_vetor(caminho, camada=None):
    """1. Lê GeoPackage, GeoJSON ou Shapefile e exige CRS identificado.

    Exemplo: municipios = ler_vetor('base.gpkg', 'municipios').
    Se o arquivo não tem CRS, corrija seus metadados com conhecimento da origem.
    """
    dados = gpd.read_file(caminho, **({'layer': camada} if camada else {}))
    if dados.crs is None:
        raise ValueError('A camada não possui CRS definido.')
    return dados


def criar_pontos(tabela, coluna_x='longitude', coluna_y='latitude', crs='EPSG:4326'):
    """2. Converte uma tabela em pontos preservando todos os atributos.

    Exemplo: pontos = criar_pontos(df, 'lon', 'lat').
    Informe x/y no CRS declarado; as coordenadas precisam ser numéricas finitas.
    """
    xy = tabela[[coluna_x, coluna_y]].to_numpy(dtype=float)
    if not np.isfinite(xy).all():
        raise ValueError('As coordenadas precisam ser finitas.')
    return gpd.GeoDataFrame(tabela.copy(), geometry=gpd.points_from_xy(xy[:, 0], xy[:, 1]), crs=crs)


def reprojetar_sirgas(dados, epsg=4674):
    """3. Reprojeta para SIRGAS 2000 geográfico ou zona UTM explícita.

    Exemplo: utm = reprojetar_sirgas(pontos, 31982) para UTM 22S.
    EPSG 4674 usa graus; para áreas e buffers selecione a zona UTM adequada.
    """
    from pyproj import CRS
    alvo = CRS.from_user_input(epsg)
    if 'SIRGAS 2000' not in alvo.name or dados.crs is None:
        raise ValueError('Defina o CRS de origem e um destino SIRGAS 2000.')
    return dados.to_crs(alvo)


def reparar_geometrias(dados):
    """4. Corrige geometrias inválidas com make_valid, preservando vazias/nulas.

    Exemplo: corrigido = reparar_geometrias(poligonos).
    O reparo pode produzir GeometryCollection; revise os tipos antes de exportar.
    """
    copia = dados.copy()
    copia.geometry = copia.geometry.map(lambda geom: make_valid(geom) if geom is not None else None)
    return copia


def criar_buffers(dados, distancia, crs_metrico):
    """5. Reprojeta e cria buffers em metros num CRS projetado apropriado.

    Exemplo: zonas = criar_buffers(pontos, 100, 31982).
    A saída permanece no CRS métrico. Distância deve ser positiva.
    """
    from pyproj import CRS
    crs = CRS.from_user_input(crs_metrico)
    if distancia <= 0 or not crs.is_projected or not all(abs(a.unit_conversion_factor - 1) < 1e-9 for a in crs.axis_info[:2]):
        raise ValueError('Use distância positiva e CRS projetado em metros.')
    copia = dados.to_crs(crs)
    copia.geometry = copia.geometry.buffer(distancia)
    return copia


def juntar_espacialmente(esquerda, direita, predicado='intersects', como='left'):
    """6. Cruza atributos por relação espacial, alinhando os CRS.

    Exemplo: resultado = juntar_espacialmente(pontos, municipios, 'within').
    Múltiplas correspondências geram várias linhas; revise antes de agregar.
    """
    if esquerda.crs is None or direita.crs is None:
        raise ValueError('Ambas as camadas precisam de CRS.')
    return gpd.sjoin(esquerda, direita.to_crs(esquerda.crs), how=como, predicate=predicado)


def dissolver_por_atributo(dados, coluna, agregacao='first'):
    """7. Unifica geometrias por categoria e agrega atributos.

    Exemplo: regioes = dissolver_por_atributo(municipios, 'regiao', {'pop': 'sum'}).
    Use regras de agregação explícitas para evitar perder informação numérica.
    """
    return dados.dissolve(by=coluna, aggfunc=agregacao, as_index=False, dropna=False)


def recortar_vetor(dados, mascara):
    """8. Recorta uma camada pela geometria da máscara no CRS da entrada.

    Exemplo: recorte = recortar_vetor(rios, limite_municipal).
    As duas camadas precisam ter CRS; a máscara pode ter vários polígonos.
    """
    if dados.crs is None or mascara.crs is None:
        raise ValueError('Ambas as camadas precisam de CRS.')
    return gpd.clip(dados, mascara.to_crs(dados.crs))


def recortar_raster(entrada, mascara, saida, nodata=None):
    """9. Recorta GeoTIFF por polígonos e mantém transformação/CRS corretos.

    Exemplo: recortar_raster('imagem.tif', municipio, 'recorte.tif', nodata=-9999).
    Escolha nodata representável no tipo do raster e fora dos valores válidos.
    A função exige saída nova e máscara não vazia com CRS conhecido.
    """
    import rasterio
    from rasterio.mask import mask
    if Path(saida).exists() or Path(entrada).resolve() == Path(saida).resolve():
        raise FileExistsError('A saída deve ser nova e diferente da entrada.')
    with rasterio.open(entrada) as src:
        if src.crs is None or mascara.crs is None:
            raise ValueError('Raster e máscara precisam ter CRS.')
        limite = mascara.to_crs(src.crs)
        geometrias = [g.__geo_interface__ for g in limite.geometry if g is not None and not g.is_empty]
        if not geometrias:
            raise ValueError('A máscara não contém geometrias utilizáveis.')
        valor = nodata if nodata is not None else src.nodata
        if valor is None:
            raise ValueError('Informe nodata: o raster de origem não define esse valor.')
        dados, transformacao = mask(src, geometrias, crop=True, nodata=valor)
        perfil = src.profile.copy()
        perfil.update(height=dados.shape[1], width=dados.shape[2], transform=transformacao, nodata=valor)
        with rasterio.open(saida, 'w', **perfil) as dst:
            dst.write(dados)
    return str(saida)


def criar_grade(limite, tamanho, crs_metrico, maximo_celulas=100000):
    """10. Cria grade quadrada e recorta as células ao limite informado.

    Exemplo: grade = criar_grade(municipio, 1000, 31982).
    A célula usa metros. O limite de células evita alocações acidentais enormes.
    Células da borda são recortadas e recebem um ID único.
    """
    from pyproj import CRS
    crs = CRS.from_user_input(crs_metrico)
    if tamanho <= 0 or not crs.is_projected or not all(abs(a.unit_conversion_factor - 1) < 1e-9 for a in crs.axis_info[:2]):
        raise ValueError('Use tamanho positivo e CRS projetado em metros.')
    dados = limite.to_crs(crs)
    xmin, ymin, xmax, ymax = dados.total_bounds
    if not np.isfinite([xmin, ymin, xmax, ymax]).all() or xmax <= xmin or ymax <= ymin:
        raise ValueError('O limite deve ter extensão não vazia.')
    nx, ny = int(np.ceil((xmax-xmin)/tamanho)), int(np.ceil((ymax-ymin)/tamanho))
    if nx * ny > maximo_celulas:
        raise ValueError('A grade excede o máximo permitido de células.')
    celulas = [box(xmin+i*tamanho, ymin+j*tamanho, xmin+(i+1)*tamanho, ymin+(j+1)*tamanho)
               for i in range(nx) for j in range(ny)]
    grade = gpd.GeoDataFrame({'id': range(1, len(celulas)+1)}, geometry=celulas, crs=crs)
    recorte = gpd.clip(grade, dados)
    return recorte[recorte.geometry.area > 0].reset_index(drop=True)
