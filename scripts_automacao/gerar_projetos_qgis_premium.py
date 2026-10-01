"""Gera dez projetos QGIS autossuficientes e estilos QML usando PyQGIS 3.28+.

Execute com o Python do QGIS. Cada QGZ incorpora bases sintéticas e instruções.
Os QML externos são estilos independentes para a camada principal indicada.
"""
import gc
import math
from pathlib import Path
import shutil
import tempfile
from qgis.core import (
    Qgis, QgsApplication, QgsProject, QgsVectorLayer, QgsField,
    QgsCoordinateReferenceSystem, QgsFillSymbol, QgsLineSymbol, QgsMarkerSymbol,
    QgsRendererCategory, QgsCategorizedSymbolRenderer, QgsGraduatedSymbolRenderer,
    QgsRendererRange, QgsSingleSymbolRenderer, QgsPalLayerSettings, QgsTextFormat,
    QgsVectorLayerSimpleLabeling, QgsPrintLayout, QgsLayoutItemMap,
    QgsLayoutItemLabel, QgsLayoutItemLegend, QgsLayoutItemScaleBar,
    QgsLayoutPoint, QgsLayoutSize, QgsUnitTypes, QgsRectangle,
    QgsVectorLayerTemporalProperties, QgsLayoutExporter,
)
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor, QFont

ROOT=Path(__file__).resolve().parents[1]
PLANOS=[
    [(1,'unidades')],
    [(8,'inventario'),(8,'limite'),(2,'cobertura')],
    [(2,'cobertura')],
    [(9,'setores'),(4,'equipamentos')],
    [(3,'drenagem'),(3,'bacias')],
    [(9,'setores')],
    [(7,'pontos_interesse'),(4,'rede'),(1,'unidades')],
    [(4,'equipamentos'),(4,'rede'),(1,'unidades')],
    [(10,'observacoes'),(10,'estacoes')],
    [(1,'unidades'),(7,'pontos_interesse')],
]
CORES=['#6BD66A','#16BFD0','#F2C14E','#A7BED3']


def simbolo(layer, cor):
    if layer.geometryType()==0:
        return QgsMarkerSymbol.createSimple({'name':'circle','color':cor,'outline_color':'#0B2F5B','outline_width':'0.3','size':'3'})
    if layer.geometryType()==1:
        return QgsLineSymbol.createSimple({'line_color':cor,'line_width':'0.8'})
    return QgsFillSymbol.createSimple({'color':cor,'outline_color':'#0B2F5B','outline_width':'0.25'})


def estilizar(layer, indice):
    campo=next((c for c in ['classe','categoria','tipo','grupo','estacao','nome'] if layer.fields().indexFromName(c)>=0),None)
    if indice==5 and layer.name()=='setores':
        layer.addExpressionField('0.5*("renda_media"-1500.0)/1300.0 + 0.5*"equipamentos"/3.0', QgsField('indice_demo',QVariant.Double))
        campo='indice_demo'
        ranges=[QgsRendererRange(a,b,simbolo(layer,c),t) for a,b,c,t in
                [(0,.4,'#A7BED3','0 a 0,4'),(.4,.7,'#16BFD0','0,4 a 0,7'),(.7,1,'#6BD66A','0,7 a 1')]]
        layer.setRenderer(QgsGraduatedSymbolRenderer(campo,ranges))
    elif campo:
        values=sorted(layer.uniqueValues(layer.fields().indexFromName(campo)),key=str)
        layer.setRenderer(QgsCategorizedSymbolRenderer(campo,[QgsRendererCategory(v,simbolo(layer,CORES[n%len(CORES)]),str(v)) for n,v in enumerate(values)]))
    else:
        layer.setRenderer(QgsSingleSymbolRenderer(simbolo(layer,CORES[indice%len(CORES)])))
    label=QgsPalLayerSettings()
    label.fieldName='nome' if layer.fields().indexFromName('nome')>=0 else 'id'
    fmt=QgsTextFormat(); fmt.setFont(QFont('Arial',9));fmt.setSize(9);fmt.setColor(QColor('#0B2F5B'))
    label.setFormat(fmt)
    layer.setLabeling(QgsVectorLayerSimpleLabeling(label))
    layer.setLabelsEnabled(True)
    metadata=layer.metadata();metadata.setTitle(layer.name());metadata.setAbstract('Dados sintéticos DataGeo Academy, somente para exercícios; EPSG:31982.');layer.setMetadata(metadata)


def texto_layout(layout,texto,x,y,w,h,tamanho=10):
    item=QgsLayoutItemLabel(layout);item.setText(texto);item.setFont(QFont('Arial',tamanho));item.setFontColor(QColor('#0B2F5B'))
    layout.addLayoutItem(item);item.attemptMove(QgsLayoutPoint(x,y));item.attemptResize(QgsLayoutSize(w,h))
    return item


def criar_layout(project,layers,title,indice):
    layout=QgsPrintLayout(project);layout.initializeDefaults();layout.setName('DataGeo - Entrega tecnica')
    largura,altura=(420,297) if indice==9 else (297,210)
    layout.pageCollection().page(0).setPageSize(QgsLayoutSize(largura,altura))
    texto_layout(layout,'DataGeo Academy | '+title,10,7,largura-20,10,14)
    texto_layout(layout,'BASE SINTETICA - exemplo tecnico, sem valor cadastral ou levantamento de campo',10,20,largura-20,7,8)
    mapa=QgsLayoutItemMap(layout);layout.addLayoutItem(mapa)
    mapa.attemptMove(QgsLayoutPoint(10,35));mapa.attemptResize(QgsLayoutSize(largura-95,altura-65));mapa.setCrs(project.crs());mapa.setLayers(layers);mapa.setKeepLayerSet(True)
    extent=QgsRectangle(layers[0].extent())
    for layer in layers[1:]:extent.combineExtentWith(layer.extent())
    extent.scale(1.15);mapa.setExtent(extent)
    mapa.attemptResize(QgsLayoutSize(largura-95,altura-65));mapa.zoomToExtent(extent);mapa.setFrameEnabled(True)
    assert all(math.isfinite(v) for v in [mapa.extent().xMinimum(),mapa.extent().xMaximum(),mapa.extent().yMinimum(),mapa.extent().yMaximum()])
    legenda=QgsLayoutItemLegend(layout);legenda.setTitle('Legenda');legenda.setLinkedMap(mapa);legenda.setAutoUpdateModel(False)
    legenda.model().rootGroup().clear()
    for layer in layers:legenda.model().rootGroup().addLayer(layer)
    from qgis.core import QgsLegendStyle
    for style in [QgsLegendStyle.Title,QgsLegendStyle.Subgroup,QgsLegendStyle.SymbolLabel]:legenda.setStyleFont(style,QFont('Arial',9))
    layout.addLayoutItem(legenda);legenda.attemptMove(QgsLayoutPoint(largura-78,35));legenda.attemptResize(QgsLayoutSize(65,100))
    barra=QgsLayoutItemScaleBar(layout);barra.setStyle('Single Box');barra.setLinkedMap(mapa);barra.setUnits(QgsUnitTypes.DistanceMeters);barra.setUnitsPerSegment(500);barra.setNumberOfSegments(2);barra.setNumberOfSegmentsLeft(0);barra.setUnitLabel('m');barra.setFont(QFont('Arial',8));barra.setHeight(2)
    layout.addLayoutItem(barra);barra.attemptMove(QgsLayoutPoint(12,altura-25))
    texto_layout(layout,'N (grade) ↑',largura-74,altura-42,60,10,10)
    texto_layout(layout,'SIRGAS 2000 / UTM 22S - EPSG:31982 | Fonte: simulacao DataGeo | GRS80',10,altura-12,largura-20,7,8)
    if indice==0:
        atlas=layout.atlas();atlas.setCoverageLayer(layers[0]);atlas.setEnabled(True);atlas.setPageNameExpression('"nome"');atlas.setFilenameExpression("concat('atlas_',\"id\")");mapa.setAtlasDriven(True)
    project.layoutManager().addLayout(layout)
    return layout


def gerar():
    pasta=ROOT/'templates_gis'
    fontes=sorted(pasta.glob('*.txt'))
    assert len(fontes)==10
    previews=ROOT/'.preview-corporativa';previews.mkdir(exist_ok=True)
    for indice,fonte in enumerate(fontes):
        project=QgsProject.instance();project.clear();project.setFileName(str(fonte.with_suffix('.qgz')))
        project.setCrs(QgsCoordinateReferenceSystem('EPSG:31982'));project.setEllipsoid('GRS80')
        project.setFilePathStorage(Qgis.FilePathType.Relative)
        title=fonte.read_text(encoding='utf-8').splitlines()[0].lstrip('# ')
        project.setTitle('DataGeo Academy - '+title)
        meta=project.metadata();meta.setTitle(title);meta.setAuthor('DataGeo Academy');meta.setAbstract('Modelo demonstrativo com dados incorporados. '+fonte.read_text(encoding='utf-8'));project.setMetadata(meta)
        shutil.copyfile(fonte,project.createAttachedFile('instrucoes.txt'))
        attached={};layers=[]
        group=project.layerTreeRoot().addGroup('Dados demonstrativos - '+title)
        for number,name in PLANOS[indice]:
            if number not in attached:
                source=next((ROOT/'bancos_dados').glob(f'{number:02d}_*.gpkg'))
                target=project.createAttachedFile(source.name);shutil.copyfile(source,target);attached[number]=target
            layer=QgsVectorLayer(attached[number]+'|layername='+name,name,'ogr')
            assert layer.isValid(),name
            estilizar(layer,indice)
            if indice==8 and name=='observacoes':
                layer.addExpressionField('to_date("data_ref")',QgsField('data_observacao',QVariant.Date))
                prop=layer.temporalProperties();prop.setMode(QgsVectorLayerTemporalProperties.ModeFeatureDateTimeInstantFromField);prop.setStartField('data_observacao');prop.setIsActive(True)
            project.addMapLayer(layer,False);group.addLayer(layer);layers.append(layer)
        # Pontos e linhas à frente dos polígonos, inclusive na composição impressa.
        ordem=sorted(layers,key=lambda l:l.geometryType())
        project.layerTreeRoot().setHasCustomLayerOrder(True);project.layerTreeRoot().setCustomLayerOrder(ordem)
        from qgis.core import QgsReferencedRectangle
        extent=QgsRectangle(layers[0].extent())
        for layer in layers[1:]:extent.combineExtentWith(layer.extent())
        extent.scale(1.1);project.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(extent,project.crs()))
        # O estilo externo corresponde à primeira camada do tema, identificada aqui.
        msg,ok=layers[0].saveNamedStyle(str(fonte.with_suffix('.qml')))
        assert ok,msg
        qml_dest=project.createAttachedFile(fonte.with_suffix('.qml').name);shutil.copyfile(fonte.with_suffix('.qml'),qml_dest)
        layout=criar_layout(project,ordem,title,indice)
        assert project.write(),fonte
        settings=QgsLayoutExporter.ImageExportSettings();settings.dpi=110;settings.exportMetadata=False
        assert QgsLayoutExporter(layout).exportToImage(str(previews/(fonte.stem+'.png')),settings)==QgsLayoutExporter.Success
        # Teste de transporte: apenas o QGZ é copiado, sem bases externas.
        with tempfile.TemporaryDirectory(prefix='qgz_portavel_',dir=previews) as teste:
            copiado=Path(teste)/fonte.with_suffix('.qgz').name;shutil.copyfile(fonte.with_suffix('.qgz'),copiado)
            reopened=QgsProject();assert reopened.read(str(copiado))
            assert len(reopened.mapLayers())==len(layers)
            assert all(l.isValid() and l.featureCount()>0 for l in reopened.mapLayers().values())
            reopened.clear()
        print('QGZ e QML validados:',fonte.stem)
        project.clear();del project,layout,layers,ordem;gc.collect()


if __name__=='__main__':
    with tempfile.TemporaryDirectory(prefix='perfil_qgis_',dir=ROOT/'.preview-corporativa') as perfil:
        app=QgsApplication([],False,perfil);app.initQgis()
        try:gerar()
        finally:QgsProject.instance().clear();gc.collect();app.exitQgis()
