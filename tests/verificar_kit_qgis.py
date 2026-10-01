"""Teste integrado: execute com o Python do QGIS 3, com QT_QPA_PLATFORM=offscreen.

No Windows, use python-qgis.bat com o caminho absoluto deste arquivo.
Cria dados sintéticos e saídas temporárias dentro da pasta do projeto.
"""
import os
from pathlib import Path
import runpy
import sys
import tempfile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from qgis.core import QgsApplication, QgsProject, QgsVectorLayer, QgsFeature, QgsGeometry
from qgis.gui import QgsMapCanvas

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(os.environ["QGIS_PREFIX_PATH"]) / "python" / "plugins"))
from processing.core.Processing import Processing


def executar(pasta):
    kit = runpy.run_path(str(ROOT / "scripts_automacao" / "automacao_qgis_filtro.py"))
    projeto = QgsProject.instance()
    pontos = QgsVectorLayer("Point?crs=EPSG:4674&field=uf:string&field=valor:double&field=vazio:string&field=zero:integer", "pontos", "memory")
    for indice, (uf, valor) in enumerate([("SC", 10), ("PR", 20), ("SC", None)]):
        f = QgsFeature(pontos.fields())
        f.setGeometry(QgsGeometry.fromWkt(f"POINT({-48.5 + indice * .01} -27.5)"))
        f.setAttributes([uf, valor, "  ", 0])
        assert pontos.dataProvider().addFeatures([f])[0]
    pontos.updateExtents()
    projeto.addMapLayer(pontos)

    # 2: arquivos reais e recusa de sobrescrita.
    caminhos = kit["exportar_camadas_lote"]([pontos], pasta, projeto)
    assert len(caminhos) == 1 and Path(caminhos[0]).is_file()
    try:
        kit["exportar_camadas_lote"]([pontos], pasta, projeto)
    except FileExistsError:
        pass
    else:
        raise AssertionError("A exportação sobrescreveu um arquivo.")

    # 1: filtro real no provedor OGR, combinação e restauração.
    ogr = QgsVectorLayer(caminhos[0], "pontos_ogr", "ogr")
    assert ogr.isValid()
    projeto.addMapLayer(ogr)
    anterior = kit["aplicar_filtros"]({ogr.id(): '"uf" = \'SC\''}, projeto=projeto)
    assert ogr.featureCount() == 2
    kit["restaurar_filtros"](anterior, projeto)
    assert ogr.featureCount() == 3
    try:
        kit["aplicar_filtros"]({'camada_inexistente': 'x = 1'}, projeto=projeto)
    except ValueError:
        pass
    else:
        raise AssertionError("Camada inexistente n?o foi rejeitada.")
    assert ogr.subsetString() == "" and ogr.featureCount() == 3

    # 3: transformação de graus para UTM, com coordenadas alteradas.
    utm = kit["reprojetar_sirgas2000_lote"]([pontos], "EPSG:31983", projeto=projeto)[0]
    assert utm.crs().authid() == "EPSG:31983" and utm.featureCount() == 3
    assert next(utm.getFeatures()).geometry().asPoint().x() > 100000

    # 4: buffers e rejeição de metros usados em CRS geográfico.
    buffers = kit["criar_buffers"](utm, 100, projeto=projeto)
    assert buffers.featureCount() == 3
    try:
        kit["criar_buffers"](pontos, 100, projeto=projeto)
    except ValueError:
        pass
    else:
        raise AssertionError("Buffer em graus foi aceito.")

    # 5: polígono de aproximadamente um hectare; preservação da origem.
    poligonos = QgsVectorLayer("Polygon?crs=EPSG:31983&field=id:integer", "parcelas", "memory")
    f = QgsFeature(poligonos.fields())
    f.setGeometry(QgsGeometry.fromWkt("POLYGON((500000 7000000,500100 7000000,500100 7000100,500000 7000100,500000 7000000))"))
    f.setAttributes([1])
    assert poligonos.dataProvider().addFeatures([f])[0]
    poligonos.updateExtents()
    areas = kit["calcular_areas_hectares"](poligonos, projeto=projeto)
    assert .98 < next(areas.getFeatures())["area_ha"] < 1.02
    assert poligonos.fields().indexFromName("area_ha") == -1

    # 6: espaços vazios removidos; zero e origem preservados.
    limpa, removidos = kit["limpar_colunas_vazias"](pontos, projeto=projeto)
    assert removidos == ["vazio"] and limpa.fields().indexFromName("zero") >= 0
    assert pontos.fields().indexFromName("vazio") >= 0

    # 7: merge real e harmonização em CRS de destino.
    merged = kit["unificar_camadas"]([pontos, utm], "EPSG:31983", projeto=projeto)
    assert merged.featureCount() == 6 and merged.crs().authid() == "EPSG:31983"

    # 8: renderização offscreen para PNG; não abre janela.
    canvas = QgsMapCanvas()
    canvas.setDestinationCrs(utm.crs())
    canvas.setLayers([utm])
    canvas.setExtent(utm.extent())
    png = kit["exportar_mapa_png"](Path(pasta) / "mapa.png", 320, 180, canvas=canvas)
    from qgis.PyQt.QtGui import QImage
    imagem = QImage(png)
    assert not imagem.isNull() and imagem.width() == 320 and imagem.height() == 180

    # 9: malha real na extensão do polígono em metros.
    grade = kit["criar_grade_amostral"](poligonos, 50, tipo=2, projeto=projeto)
    assert grade.featureCount() == 4 and grade.crs().authid() == "EPSG:31983"

    # 10: estatísticas com nulo, desvio populacional e detecção de campo.
    resumo = kit["imprimir_estatisticas_atributos"](pontos, ["valor", "zero"], projeto=projeto)
    assert resumo["valor"]["contagem"] == 2 and resumo["valor"]["nulos"] == 1
    assert resumo["valor"]["media"] == 15 and resumo["valor"]["desvio_padrao"] == 5
    assert resumo["zero"]["contagem"] == 3 and resumo["zero"]["soma"] == 0
    print("PASS: todas as dez ferramentas executadas no QGIS real.", flush=True)
    canvas.setLayers([])
    projeto.clear()
    del canvas, ogr


def main():
    import gc
    import traceback
    erro = None
    with tempfile.TemporaryDirectory(prefix="teste_qgis_", dir=ROOT) as pasta:
        assert Path(pasta).resolve().parent == ROOT.resolve()
        app = QgsApplication([], False, str(Path(pasta) / "perfil"))
        app.initQgis()
        Processing.initialize()
        try:
            executar(pasta)
        except Exception as falha:
            traceback.print_exc()
            erro = str(falha)
        finally:
            QgsProject.instance().clear()
            gc.collect()
            app.exitQgis()
        if erro is not None:
            raise AssertionError(erro)


if __name__ == "__main__":
    main()
