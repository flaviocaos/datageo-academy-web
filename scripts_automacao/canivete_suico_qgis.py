"""Canivete Suíço de Automação — dez ferramentas para QGIS 3.22 ou superior.

Ferramentas: 1) aplicar_filtros, 2) exportar_camadas_lote,
3) reprojetar_sirgas2000_lote, 4) criar_buffers, 5) calcular_areas_hectares,
6) limpar_colunas_vazias, 7) unificar_camadas, 8) exportar_mapa_png,
9) criar_grade_amostral, 10) imprimir_estatisticas_atributos.

Use no Console Python do QGIS, com o complemento Processing habilitado.
As novas operações vetoriais geram cópias em memória, sem editar as fontes.
Os arquivos exportados nunca substituem arquivos existentes. Operações em
lote podem deixar saídas anteriores se uma etapa posterior falhar.
Filtros e seleções: operações vetoriais usam todas as feições acessíveis sob
o filtro atual, ignorando a seleção. Para trabalhar com a base inteira,
remova o filtro antes. A limpeza de colunas exige uma camada sem filtro.

Filtros por atributos em camadas vetoriais carregadas no QGIS:

Execute no editor do Console Python do QGIS ou carregue o arquivo assim:

    from pathlib import Path
    exec(Path('/caminho/canivete_suico_qgis.py').read_text(encoding='utf-8'))
    historico = aplicar_filtros({'municipios': '"uf" = \'SC\''})
    # Outro exemplo: aplicar_filtros({'lotes': '"area_m2" >= 1000'})
    restaurar_filtros(historico)

O seletor pode ser o ID da camada ou seu nome exato, desde que seja único.
Por padrão, combina o novo filtro com o filtro existente usando AND.
Use combinar=False para substituir; use uma string vazia com combinar=False
para remover o filtro. A função retorna os filtros anteriores para restauração.

As condições usam a sintaxe do provedor de dados (normalmente cláusula SQL
WHERE sem a palavra WHERE), não necessariamente a linguagem de expressões
do QGIS. Use campos da fonte, e adapte a sintaxe para OGR, PostGIS etc.
O provedor precisa oferecer suporte a subset strings; algumas fontes, como
camadas temporárias em memória, podem não oferecer esse recurso.

As funções de filtro não alteram atributos ou geometrias nem exportam dados.
O filtro será persistido no projeto apenas se você decidir salvá-lo no QGIS.
Nenhum filtro é aplicado automaticamente ao executar este arquivo.

Referência: https://api.qgis.org/api/classQgsVectorLayer.html
Outras referências:
https://docs.qgis.org/3.40/en/docs/pyqgis_developer_cookbook/composer.html
https://docs.qgis.org/3.40/en/docs/user_manual/processing_algs/qgis/vectorcreation.html
https://api.qgis.org/api/3.40/classQgsDistanceArea.html
"""

from qgis.core import QgsProject, QgsVectorLayer


def _resolver_camada(projeto, seletor):
    if not isinstance(seletor, str) or not seletor.strip():
        raise ValueError("Informe o ID ou nome exato da camada.")
    camada = projeto.mapLayer(seletor)
    if camada is None:
        candidatas = projeto.mapLayersByName(seletor)
        if len(candidatas) != 1:
            raise ValueError(
                f"'{seletor}': encontradas {len(candidatas)} camadas. "
                "Use o ID para distinguir nomes repetidos."
            )
        camada = candidatas[0]
    if not isinstance(camada, QgsVectorLayer) or not camada.isValid():
        raise ValueError(f"'{seletor}' não é uma camada vetorial válida.")
    if camada.isEditable():
        raise ValueError(f"Finalize ou cancele a edição de '{camada.name()}' antes de filtrar.")
    provedor = camada.dataProvider()
    if provedor is None or not provedor.supportsSubsetString():
        raise ValueError(f"O provedor de '{camada.name()}' não suporta filtros de subconjunto.")
    return camada


def aplicar_filtros(filtros, combinar=True, projeto=None):
    """Aplica um lote de filtros; reverte os anteriores se houver falha.

    filtros: dict {ID ou nome da camada: condição SQL do provedor}.
    Retorno: dict {ID da camada: filtro anterior}, para restaurar_filtros().
    Uma camada só pode aparecer uma vez no lote, inclusive por nome e ID.
    """
    if not isinstance(filtros, dict) or not filtros:
        raise ValueError("Informe um dicionário não vazio de camadas e condições.")
    projeto = projeto if projeto is not None else QgsProject.instance()
    plano = []
    historico = {}
    for seletor, condicao in filtros.items():
        if not isinstance(condicao, str):
            raise TypeError(f"O filtro de '{seletor}' deve ser uma string.")
        camada = _resolver_camada(projeto, seletor)
        if camada.id() in historico:
            raise ValueError(f"A camada '{camada.name()}' aparece mais de uma vez no lote.")
        anterior = camada.subsetString()
        novo = condicao.strip()
        if combinar and anterior:
            novo = f"({anterior}) AND ({novo})" if novo else anterior
        historico[camada.id()] = anterior
        plano.append((camada, novo))

    alteradas = []
    try:
        for camada, novo in plano:
            # Inclui a camada na reversão mesmo se o provedor falhar ao aplicar.
            alteradas.append(camada)
            if not camada.setSubsetString(novo):
                raise RuntimeError(
                    f"Filtro recusado em '{camada.name()}': {novo!r}. "
                    "Verifique os campos e a sintaxe do provedor."
                )
            camada.updateExtents()
            camada.triggerRepaint()
    except Exception as erro:
        falhas = []
        for camada in reversed(alteradas):
            try:
                if not camada.setSubsetString(historico[camada.id()]):
                    raise RuntimeError("O provedor recusou o filtro anterior.")
                camada.updateExtents()
                camada.triggerRepaint()
            except Exception as reversao:
                falhas.append(f"{camada.name()}: {reversao}")
        if falhas:
            projeto.setDirty(True)
            raise RuntimeError(
                "Falha na aplicação e na restauração de filtros. Revise as camadas: "
                + "; ".join(falhas)
            ) from erro
        raise

    projeto.setDirty(True)
    return historico


def restaurar_filtros(historico, projeto=None):
    """Restaura os filtros retornados por aplicar_filtros(), sem combiná-los."""
    return aplicar_filtros(historico, combinar=False, projeto=projeto)


# Auxiliares das ferramentas 2–10. Imports locais mantêm o filtro independente.
def _camada_vetorial(entrada, projeto):
    if isinstance(entrada, QgsVectorLayer):
        camada = entrada
    else:
        camada = projeto.mapLayer(entrada)
        if camada is None:
            candidatas = projeto.mapLayersByName(entrada)
            if len(candidatas) != 1:
                raise ValueError(f"Camada ausente ou nome ambíguo: {entrada!r}")
            camada = candidatas[0]
    if not isinstance(camada, QgsVectorLayer) or not camada.isValid():
        raise ValueError("A entrada deve ser uma camada vetorial válida.")
    if camada.isEditable():
        raise ValueError(f"Finalize a edição de '{camada.name()}' antes de processar.")
    return camada


def _lista_camadas(entradas, projeto):
    if isinstance(entradas, (str, QgsVectorLayer)):
        entradas = [entradas]
    camadas = [_camada_vetorial(e, projeto) for e in entradas]
    if not camadas or len({c.id() for c in camadas}) != len(camadas):
        raise ValueError("Informe ao menos uma camada, sem repetições.")
    return camadas


def _crs_valido(crs):
    from qgis.core import QgsCoordinateReferenceSystem
    resultado = crs if isinstance(crs, QgsCoordinateReferenceSystem) else QgsCoordinateReferenceSystem(crs)
    if not resultado.isValid():
        raise ValueError(f"SRC inválido: {crs!r}")
    return resultado


def _exigir_metros(crs):
    from qgis.core import QgsUnitTypes
    if not crs.isValid() or crs.isGeographic() or crs.mapUnits() != QgsUnitTypes.DistanceMeters:
        raise ValueError("Use um SRC projetado em metros, adequado à área de estudo.")


def _numero_positivo(valor, nome):
    import math
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not math.isfinite(valor) or valor <= 0:
        raise ValueError(f"{nome} deve ser um número positivo e finito.")


def _nova_saida(caminho, extensao):
    from pathlib import Path
    saida = Path(caminho).expanduser().resolve()
    if saida.suffix.lower() != extensao:
        raise ValueError(f"O arquivo de saída deve terminar em {extensao}.")
    if saida.exists():
        raise FileExistsError(f"A saída já existe: {saida}")
    saida.parent.mkdir(parents=True, exist_ok=True)
    return saida


def _processar(algoritmo, parametros, projeto):
    import processing
    from qgis.core import QgsProcessingContext, QgsProcessingFeedback, QgsApplication
    if QgsApplication.processingRegistry().algorithmById(algoritmo) is None:
        raise RuntimeError(f"Habilite Processing e o provedor nativo: {algoritmo}")
    contexto = QgsProcessingContext()
    contexto.setProject(projeto)
    resultado = processing.run(algoritmo, parametros, context=contexto, feedback=QgsProcessingFeedback())
    camada = resultado["OUTPUT"]
    if not isinstance(camada, QgsVectorLayer):
        camada = QgsVectorLayer(str(camada), algoritmo.split(":")[-1], "ogr")
    if not camada.isValid():
        raise RuntimeError(f"Saída inválida de {algoritmo}.")
    return camada


def _entregar(camada, nome, adicionar, projeto):
    camada.setName(nome)
    if adicionar:
        projeto.addMapLayer(camada)
    return camada


def _copiar(camada):
    from qgis.core import QgsFeatureRequest
    copia = camada.materialize(QgsFeatureRequest())
    if not copia.isValid():
        raise RuntimeError("Não foi possível criar a cópia de trabalho.")
    return copia


# 2) Exportação em lote: um GeoPackage separado para cada camada.
def exportar_camadas_lote(camadas, pasta_saida, projeto=None):
    """Exemplo: exportar_camadas_lote(['municipios', 'lotes'], 'C:/saida').

    Retorna lista de caminhos .gpkg. Não sobrescreve arquivos; nomes recebem
    prefixo numérico para distinguir camadas com nomes semelhantes.
    """
    from pathlib import Path
    import re
    from qgis.core import QgsVectorFileWriter
    projeto = projeto if projeto is not None else QgsProject.instance()
    entradas = _lista_camadas(camadas, projeto)
    plano = []
    for indice, camada in enumerate(entradas, 1):
        nome = re.sub(r'[^\w-]+', '_', camada.name()).strip('_')[:80] or 'camada'
        plano.append((camada, _nova_saida(Path(pasta_saida) / f"{indice:02d}_{nome}.gpkg", '.gpkg')))
    caminhos = []
    for camada, saida in plano:
        opcoes = QgsVectorFileWriter.SaveVectorOptions()
        opcoes.driverName = "GPKG"
        opcoes.fileEncoding = "UTF-8"
        opcoes.layerName = "dados"
        opcoes.onlySelectedFeatures = False
        retorno = QgsVectorFileWriter.writeAsVectorFormatV3(camada, str(saida), projeto.transformContext(), opcoes)
        if retorno[0] != QgsVectorFileWriter.NoError:
            raise RuntimeError(f"Erro na exportação de {camada.name()}: {retorno}")
        caminhos.append(str(saida))
    return caminhos


# 3) Reprojeção real das coordenadas; não apenas atribuição de SRC.
def reprojetar_sirgas2000_lote(camadas, crs_destino="EPSG:4674", adicionar=False, projeto=None):
    """Exemplo: reprojetar_sirgas2000_lote(['lotes'], 'EPSG:31983', True).

    4674 produz graus; 31983 é UTM 23S em metros. Escolha o fuso correto.
    Usa o contexto de transformação do projeto, incluindo suas grades.
    Retorna novas camadas em memória; use exportar_camadas_lote para salvar.
    """
    projeto = projeto if projeto is not None else QgsProject.instance()
    destino = _crs_valido(crs_destino)
    if "SIRGAS2000" not in destino.description().upper().replace(" ", ""):
        raise ValueError("Escolha um SRC SIRGAS 2000 válido.")
    entradas = _lista_camadas(camadas, projeto)
    if any(not c.crs().isValid() for c in entradas):
        raise ValueError("Todas as fontes precisam de SRC conhecido e válido.")
    saidas = []
    for camada in entradas:
        saida = _processar("native:reprojectlayer", {"INPUT": camada, "TARGET_CRS": destino, "OUTPUT": "memory:"}, projeto)
        saidas.append(_entregar(saida, camada.name() + "_sirgas2000", adicionar, projeto))
    return saidas


# 4) Buffers planos em metros; exige projeção métrica antes de executar.
def criar_buffers(camada, distancia_m, dissolver=False, segmentos=12, adicionar=False, projeto=None):
    """Exemplo: criar_buffers('pontos_utm', 100, adicionar=True).

    Retorna camada poligonal em memória. Não executa buffer em graus.
    segmentos é a resolução por quarto de círculo; dissolver une os buffers.
    """
    projeto = projeto if projeto is not None else QgsProject.instance()
    origem = _camada_vetorial(camada, projeto)
    _exigir_metros(origem.crs())
    _numero_positivo(distancia_m, "Distância")
    if isinstance(segmentos, bool) or not isinstance(segmentos, int) or segmentos < 1:
        raise ValueError("segmentos deve ser um inteiro positivo.")
    saida = _processar("native:buffer", {"INPUT": origem, "DISTANCE": distancia_m, "SEGMENTS": segmentos,
                        "END_CAP_STYLE": 0, "JOIN_STYLE": 0, "MITER_LIMIT": 2,
                        "DISSOLVE": bool(dissolver), "OUTPUT": "memory:"}, projeto)
    return _entregar(saida, origem.name() + "_buffer", adicionar, projeto)


# 5) Área elipsoidal em hectares, calculada numa cópia com novo campo.
def calcular_areas_hectares(camada, campo="area_ha", elipsoide="GRS80", adicionar=False, projeto=None):
    """Exemplo: calcular_areas_hectares('lotes', adicionar=True).

    GRS80 é apropriado ao SIRGAS2000; o SRC de origem deve estar correto.
    Geometrias ausentes recebem NULL; polígonos inválidos interrompem o lote.
    Não substitui um campo existente e não edita os dados originais.
    """
    from qgis.core import QgsDistanceArea, QgsField, QgsUnitTypes, QgsWkbTypes
    from qgis.PyQt.QtCore import QVariant
    projeto = projeto if projeto is not None else QgsProject.instance()
    origem = _camada_vetorial(camada, projeto)
    if origem.geometryType() != QgsWkbTypes.PolygonGeometry or not origem.crs().isValid():
        raise ValueError("Informe uma camada de polígonos com SRC válido.")
    if not isinstance(campo, str) or not campo.strip() or origem.fields().indexFromName(campo) >= 0:
        raise ValueError("Informe um nome de campo novo e não vazio.")
    medidor = QgsDistanceArea()
    medidor.setSourceCrs(origem.crs(), projeto.transformContext())
    if not medidor.setEllipsoid(elipsoide):
        raise ValueError("Elipsoide não reconhecido.")
    copia = _copiar(origem)
    if not copia.dataProvider().addAttributes([QgsField(campo, QVariant.Double)]):
        raise RuntimeError("Falha ao criar o campo de área.")
    copia.updateFields()
    indice = copia.fields().indexFromName(campo)
    alteracoes = {}
    for feicao in copia.getFeatures():
        geometria = feicao.geometry()
        valor = None
        if not geometria.isNull() and not geometria.isEmpty():
            if not geometria.isGeosValid():
                raise ValueError(f"Geometria inválida na feição {feicao.id()}.")
            valor = medidor.convertAreaMeasurement(medidor.measureArea(geometria), QgsUnitTypes.AreaHectares)
        alteracoes[feicao.id()] = {indice: valor}
        if len(alteracoes) >= 1000:
            if not copia.dataProvider().changeAttributeValues(alteracoes):
                raise RuntimeError("Falha ao gravar áreas na cópia.")
            alteracoes.clear()
    if alteracoes and not copia.dataProvider().changeAttributeValues(alteracoes):
        raise RuntimeError("Falha ao gravar áreas na cópia.")
    return _entregar(copia, origem.name() + "_areas", adicionar, projeto)


# 6) Remoção de campos inteiramente NULL ou texto vazio numa cópia.
def limpar_colunas_vazias(camada, proteger=("id", "fid"), adicionar=False, projeto=None):
    """Exemplo: copia, removidos = limpar_colunas_vazias('cadastro').

    Zero e False são dados válidos. Protege campos indicados e chaves do
    provedor. Recusa fontes filtradas ou sem feições para evitar falsos vazios.
    Retorna (nova camada, lista de nomes removidos).
    """
    from qgis.core import NULL
    projeto = projeto if projeto is not None else QgsProject.instance()
    origem = _camada_vetorial(camada, projeto)
    if origem.subsetString():
        raise ValueError("Remova o filtro da camada antes de revisar campos vazios.")
    campos = origem.fields()
    protegidos = set(proteger) | {campos[i].name() for i in origem.dataProvider().pkAttributeIndexes()}
    candidatos = {i for i, f in enumerate(campos) if f.name() not in protegidos}
    total = 0
    for feicao in origem.getFeatures():
        total += 1
        for indice in tuple(candidatos):
            valor = feicao[indice]
            if not (valor is None or valor == NULL or isinstance(valor, str) and not valor.strip()):
                candidatos.remove(indice)
    if total == 0:
        raise ValueError("Não é possível inferir campos vazios em uma camada sem feições.")
    nomes = [campos[i].name() for i in sorted(candidatos)]
    copia = _copiar(origem)
    indices = [copia.fields().indexFromName(nome) for nome in nomes]
    if indices and not copia.dataProvider().deleteAttributes(indices):
        raise RuntimeError("Falha ao remover campos da cópia.")
    copia.updateFields()
    return _entregar(copia, origem.name() + "_limpa", adicionar, projeto), nomes


# 7) Merge concatena feições e atributos; não dissolve polígonos.
def unificar_camadas(camadas, crs_destino=None, adicionar=False, projeto=None):
    """Exemplo: unificar_camadas(['lotes_norte', 'lotes_sul'], adicionar=True).

    Camadas devem ter o mesmo tipo básico de geometria e SRC válido.
    O algoritmo harmoniza campos; revise conflitos de tipos e IDs na saída.
    Sem crs_destino, usa o SRC da primeira camada.
    """
    projeto = projeto if projeto is not None else QgsProject.instance()
    entradas = _lista_camadas(camadas, projeto)
    if len(entradas) < 2 or len({c.geometryType() for c in entradas}) != 1:
        raise ValueError("Informe duas ou mais camadas com o mesmo tipo de geometria.")
    if any(not c.crs().isValid() for c in entradas):
        raise ValueError("Todas as fontes precisam de SRC válido.")
    destino = _crs_valido(crs_destino if crs_destino is not None else entradas[0].crs())
    saida = _processar("native:mergevectorlayers", {"LAYERS": entradas, "CRS": destino, "OUTPUT": "memory:"}, projeto)
    return _entregar(saida, "camadas_unificadas", adicionar, projeto)


# 8) Exporta a composição atual do canvas, incluindo estilos e rótulos.
def exportar_mapa_png(caminho, largura=1920, altura=1080, dpi=300, canvas=None):
    """Exemplo: exportar_mapa_png('C:/saida/mapa.png').

    Execute com a interface gráfica do QGIS. Dimensões são pixels.
    Preserva camadas e extensão do canvas (ajustada à proporção de saída).
    Não inclui legendas de layout ou seleção; não sobrescreve arquivo.
    """
    from qgis.core import QgsMapSettings, QgsMapRendererParallelJob
    from qgis.PyQt.QtCore import QSize
    if any(isinstance(v, bool) or not isinstance(v, int) or v <= 0 for v in (largura, altura, dpi)):
        raise ValueError("Largura, altura e DPI devem ser inteiros positivos.")
    if canvas is None:
        from qgis.utils import iface
        if iface is None:
            raise RuntimeError("Execute no QGIS Desktop ou forneça um canvas.")
        canvas = iface.mapCanvas()
    configuracao = QgsMapSettings(canvas.mapSettings())
    if not configuracao.layers() or configuracao.extent().isEmpty():
        raise ValueError("O mapa deve conter camadas visíveis e extensão válida.")
    saida = _nova_saida(caminho, ".png")
    configuracao.setOutputSize(QSize(largura, altura))
    configuracao.setOutputDpi(dpi)
    trabalho = QgsMapRendererParallelJob(configuracao)
    trabalho.start()
    trabalho.waitForFinished()
    if trabalho.errors():
        raise RuntimeError("Erros na renderização: " + "; ".join(e.message for e in trabalho.errors()))
    imagem = trabalho.renderedImage()
    if imagem.isNull() or not imagem.save(str(saida), "PNG"):
        raise RuntimeError("Não foi possível salvar o mapa PNG.")
    return str(saida)


# 9) Grade regular em projeção métrica; extensão da camada de referência.
def criar_grade_amostral(camada_referencia, espacamento_m, tipo=0, adicionar=False, projeto=None):
    """Exemplo: criar_grade_amostral('area_utm', 250, tipo=0, adicionar=True).

    tipo: 0=pontos, 1=linhas, 2=retângulos, 3=losangos, 4=hexágonos.
    A grade cobre o retângulo da extensão, sem recorte ao polígono de estudo.
    Para limitar a amostragem, recorte/intersecte depois com sua área válida.
    """
    projeto = projeto if projeto is not None else QgsProject.instance()
    referencia = _camada_vetorial(camada_referencia, projeto)
    _exigir_metros(referencia.crs())
    _numero_positivo(espacamento_m, "Espaçamento")
    if isinstance(tipo, bool) or not isinstance(tipo, int) or tipo not in range(5):
        raise ValueError("tipo deve ser um inteiro de 0 a 4.")
    referencia.updateExtents()
    if referencia.extent().isEmpty():
        raise ValueError("A extensão precisa ter largura e altura positivas.")
    saida = _processar("native:creategrid", {"TYPE": tipo, "EXTENT": referencia.extent(),
                        "HSPACING": espacamento_m, "VSPACING": espacamento_m,
                        "HOVERLAY": 0, "VOVERLAY": 0, "CRS": referencia.crs(), "OUTPUT": "memory:"}, projeto)
    return _entregar(saida, referencia.name() + "_grade", adicionar, projeto)


# 10) Estatística numérica sem carregar toda a tabela em uma lista.
def imprimir_estatisticas_atributos(camada, campos=None, projeto=None):
    """Exemplo: resumo = imprimir_estatisticas_atributos('lotes', ['area_ha']).

    Sem campos, usa todos os atributos numéricos. Exibe e retorna contagem,
    nulos, inválidos, soma, mínimo, máximo, média e desvio padrão populacional.
    Ignora NULL, NaN e infinitos. Respeita o filtro atual, não a seleção.
    """
    import math
    from qgis.core import NULL
    projeto = projeto if projeto is not None else QgsProject.instance()
    origem = _camada_vetorial(camada, projeto)
    if campos is None:
        campos = [f.name() for f in origem.fields() if f.isNumeric()]
    elif isinstance(campos, str):
        campos = [campos]
    campos = list(campos)
    if not campos or len(set(campos)) != len(campos):
        raise ValueError("Informe campos numéricos existentes, sem repetições.")
    indices = {}
    for nome in campos:
        indice = origem.fields().indexFromName(nome)
        if indice < 0 or not origem.fields()[indice].isNumeric():
            raise ValueError(f"Campo ausente ou não numérico: {nome}")
        indices[nome] = indice
    resumo = {nome: {"contagem": 0, "nulos": 0, "invalidos": 0, "soma": 0.0,
                     "minimo": None, "maximo": None, "media": 0.0, "_m2": 0.0} for nome in campos}
    for feicao in origem.getFeatures():
        for nome, indice in indices.items():
            dados = resumo[nome]
            valor = feicao[indice]
            if valor is None or valor == NULL:
                dados["nulos"] += 1
                continue
            try:
                valor = float(valor)
            except (TypeError, ValueError, OverflowError):
                dados["invalidos"] += 1
                continue
            if not math.isfinite(valor):
                dados["invalidos"] += 1
                continue
            dados["contagem"] += 1
            dados["soma"] += valor
            dados["minimo"] = valor if dados["minimo"] is None else min(dados["minimo"], valor)
            dados["maximo"] = valor if dados["maximo"] is None else max(dados["maximo"], valor)
            delta = valor - dados["media"]
            dados["media"] += delta / dados["contagem"]
            dados["_m2"] += delta * (valor - dados["media"])
    for nome, dados in resumo.items():
        m2 = dados.pop("_m2")
        dados["desvio_padrao"] = math.sqrt(max(0.0, m2 / dados["contagem"])) if dados["contagem"] else None
        if not dados["contagem"]:
            dados["media"] = None
        print(f"{origem.name()} / {nome}: {dados}")
    return resumo
