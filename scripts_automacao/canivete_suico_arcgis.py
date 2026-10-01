"""Canivete Suíço de Automação — dez ferramentas ArcPy para ArcGIS Pro 3.

Requer o Python do ArcGIS Pro e uma licença válida. Não funciona com um
Python comum sem ArcPy. Importe no Notebook/Console do Pro ou em um script:

    import sys
    sys.path.insert(0, r'C:/projeto/scripts_automacao')
    import canivete_suico_arcgis as kit
    kit.exportar_camadas_lote([r'C:/dados/base.gdb/municipios'], r'C:/saida/kit.gdb')

Nenhuma operação é executada ao importar. As operações de dados criam novas
feature classes em file geodatabase ou memory; não editam as fontes. Saídas
existentes são recusadas. Lotes não são transacionais: saídas já produzidas
podem permanecer se uma etapa seguinte falhar. Nenhum projeto é salvo.

Camadas respeitam consultas de definição e seleções atuais nas ferramentas
de geoprocessamento e cursores. Para processar a base completa, use o caminho
da feature class. A limpeza de campos exige entrada sem seleção ou filtro.
As ferramentas tratam coordenadas horizontais; não transformam altitudes.

Referências oficiais das APIs e ferramentas:
https://pro.arcgis.com/en/pro-app/3.4/arcpy/functions/listtransformations.htm
https://pro.arcgis.com/en/pro-app/3.6/tool-reference/data-management/calculate-geometry-attributes.htm
https://pro.arcgis.com/en/pro-app/3.4/tool-reference/data-management/create-fishnet.htm
https://pro.arcgis.com/en/pro-app/3.6/arcpy/mapping/mapframe-class.htm
https://pro.arcgis.com/en/pro-app/3.5/tool-reference/data-management/delete-field.htm
"""

from pathlib import Path
import math
import re
import arcpy


# Auxiliares: validação compartilhada sem execução automática.
def _descrever(entrada):
    if not arcpy.Exists(entrada):
        raise ValueError(f"Entrada inexistente ou indisponível: {entrada}")
    descricao = arcpy.Describe(entrada)
    if not hasattr(descricao, "shapeType"):
        raise ValueError("A entrada deve ser uma feature class ou camada vetorial.")
    return descricao


def _referencia(crs):
    referencia = arcpy.SpatialReference(crs) if isinstance(crs, int) else crs
    if not isinstance(referencia, arcpy.SpatialReference) or referencia.type not in ("Geographic", "Projected"):
        raise ValueError("Informe um WKID ou SpatialReference horizontal conhecido.")
    return referencia


def _positivo(valor, nome):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not math.isfinite(valor) or valor <= 0:
        raise ValueError(f"{nome} deve ser positivo e finito.")


def _geodatabase(caminho):
    pasta = Path(caminho).expanduser().resolve()
    if pasta.suffix.lower() != ".gdb":
        raise ValueError("Informe uma file geodatabase terminada em .gdb.")
    if not arcpy.Exists(str(pasta)):
        if pasta.exists():
            raise ValueError("A pasta existente não é uma geodatabase válida.")
        pasta.parent.mkdir(parents=True, exist_ok=True)
        arcpy.management.CreateFileGDB(str(pasta.parent), pasta.name)
    if arcpy.Describe(str(pasta)).workspaceType != "LocalDatabase":
        raise ValueError("A saída deve ser uma file geodatabase local.")
    return str(pasta)


def _saida(caminho):
    texto = str(caminho).replace("\\", "/")
    if texto.startswith("memory/"):
        workspace, nome = "memory", texto[len("memory/"):]
        saida = texto
    else:
        p = Path(caminho).expanduser().resolve()
        workspace, nome = _geodatabase(p.parent), p.name
        saida = str(Path(workspace) / nome)
    if not nome or "/" in nome or arcpy.ValidateTableName(nome, workspace) != nome:
        raise ValueError(f"Nome de saída inválido: {nome!r}")
    if arcpy.Exists(saida):
        raise FileExistsError(saida)
    return saida


def _entradas(camadas):
    if isinstance(camadas, (str, Path)) or hasattr(camadas, "isFeatureLayer"):
        camadas = [camadas]
    entradas = [str(c) if isinstance(c, Path) else c for c in camadas]
    if not entradas:
        raise ValueError("Informe pelo menos uma camada.")
    for entrada in entradas:
        _descrever(entrada)
    return entradas


# 1) Filtros por atributos: definition queries do mapa, sem excluir registros.
def aplicar_filtros(filtros, mapa=None, combinar=True):
    """Exemplo no Pro: aplicar_filtros({'municipios': "uf = 'SC'"}).

    mapa pode ser um objeto arcpy.mp.Map; sem ele, usa o mapa ativo de CURRENT.
    Use nome exato ou longName (Grupo\\Camada), único no mapa. combinar=False
    substitui o filtro; uma condição vazia nesse modo remove o filtro.
    Retorna [(camada, consulta_anterior)] para restaurar_filtros().
    A sintaxe SQL depende da fonte de dados; GetCount valida a nova consulta.
    """
    if not isinstance(filtros, dict) or not filtros:
        raise ValueError("Informe um dicionário de nomes e condições SQL.")
    if mapa is None:
        mapa = arcpy.mp.ArcGISProject("CURRENT").activeMap
    if mapa is None:
        raise ValueError("Abra um mapa ativo ou forneça um objeto Map.")
    plano, vistos = [], set()
    for nome, condicao in filtros.items():
        if not isinstance(nome, str) or not isinstance(condicao, str):
            raise ValueError("Nomes e condições devem ser strings.")
        candidatas = [c for c in mapa.listLayers() if c.name == nome or c.longName == nome]
        if len(candidatas) != 1:
            raise ValueError(f"Camada ausente ou nome ambíguo: {nome}")
        camada = candidatas[0]
        if not camada.isFeatureLayer or camada.isBroken or not camada.supports("DEFINITIONQUERY"):
            raise ValueError(f"Camada sem suporte a filtros: {nome}")
        if camada.longName in vistos:
            raise ValueError("Uma camada não pode aparecer duas vezes no lote.")
        vistos.add(camada.longName)
        anterior, nova = camada.definitionQuery, condicao.strip()
        if combinar and anterior:
            nova = f"({anterior}) AND ({nova})" if nova else anterior
        plano.append((camada, anterior, nova))
    alteradas = []
    try:
        for camada, anterior, nova in plano:
            alteradas.append((camada, anterior))
            camada.definitionQuery = nova
            arcpy.management.GetCount(camada)
    except Exception as erro:
        falhas = []
        for camada, anterior in reversed(alteradas):
            try:
                camada.definitionQuery = anterior
            except Exception as falha:
                falhas.append(f"{camada.longName}: {falha}")
        if falhas:
            raise RuntimeError("Restauração incompleta: " + "; ".join(falhas)) from erro
        raise
    return alteradas


def restaurar_filtros(historico):
    """Auxiliar: restaurar_filtros(historico) recupera as consultas anteriores."""
    for camada, anterior in historico:
        camada.definitionQuery = anterior


# 2) Exportação em lote para uma file geodatabase, sem sobrescrita.
def exportar_camadas_lote(camadas, geodatabase_saida):
    """Exemplo: exportar_camadas_lote([fc1, fc2], r'C:/saida/exportadas.gdb').

    Cria a GDB se necessário; nomes recebem prefixo numérico. Retorna caminhos.
    CopyFeatures preserva atributos e geometrias, respeitando seleção/filtro.
    """
    entradas = _entradas(camadas)
    gdb = _geodatabase(geodatabase_saida)
    plano = []
    for indice, entrada in enumerate(entradas, 1):
        nome = re.sub(r"[^\w]+", "_", _descrever(entrada).baseName).strip("_")[:80] or "camada"
        nome = arcpy.ValidateTableName(f"c{indice:02d}_{nome}", gdb)
        plano.append((entrada, _saida(Path(gdb) / nome)))
    with arcpy.EnvManager(overwriteOutput=False):
        for entrada, saida in plano:
            arcpy.management.CopyFeatures(entrada, saida)
    return [saida for _, saida in plano]


# 3) Reprojeção das coordenadas para um SRC SIRGAS 2000 escolhido pelo usuário.
def reprojetar_sirgas2000_lote(camadas, geodatabase_saida, wkid=4674, transformacao=None):
    """Exemplo: reprojetar_sirgas2000_lote([fc], r'C:/saida/sirgas.gdb', 31983).

    4674 usa graus; 31983 é UTM 23S. Se os datums diferirem, informe uma
    transformação retornada por arcpy.ListTransformations(origem, destino).
    Pode passar uma string ou dict {catalogPath: transformação} por fonte.
    O kit não escolhe automaticamente uma transformação geodésica arbitrária.
    """
    destino = _referencia(wkid)
    if "SIRGAS2000" not in destino.GCS.name.upper().replace("_", "").replace(" ", ""):
        raise ValueError("O destino precisa ser um SRC SIRGAS 2000.")
    entradas = _entradas(camadas)
    gdb = _geodatabase(geodatabase_saida)
    plano = []
    for indice, entrada in enumerate(entradas, 1):
        descricao = _descrever(entrada)
        origem = _referencia(descricao.spatialReference)
        escolhida = transformacao.get(descricao.catalogPath) if isinstance(transformacao, dict) else transformacao
        disponiveis = arcpy.ListTransformations(origem, destino, descricao.extent)
        if escolhida and escolhida not in disponiveis:
            raise ValueError(f"Transformação não disponível para {descricao.baseName}: {escolhida}")
        if origem.GCS.name != destino.GCS.name and not escolhida:
            raise ValueError(f"Informe transformação para {descricao.baseName}. Opções: {disponiveis}")
        nome = arcpy.ValidateTableName(f"c{indice:02d}_{descricao.baseName}_sirgas", gdb)
        plano.append((entrada, _saida(Path(gdb) / nome), escolhida or ""))
    with arcpy.EnvManager(overwriteOutput=False):
        for entrada, saida, operacao in plano:
            arcpy.management.Project(entrada, saida, destino, transform_method=operacao)
    return [saida for _, saida, _ in plano]


# 4) Buffer geodésico: a distância é declarada em metros, mesmo em SRC geográfico.
def criar_buffers(entrada, saida, distancia_m, dissolver=False):
    """Exemplo: criar_buffers(fc, r'C:/saida/kit.gdb/buffer_100m', 100).

    Usa método GEODESIC. dissolver=True une os buffers; não modifica a fonte.
    """
    _referencia(_descrever(entrada).spatialReference)
    _positivo(distancia_m, "Distância")
    destino = _saida(saida)
    with arcpy.EnvManager(overwriteOutput=False):
        arcpy.analysis.Buffer(entrada, destino, f"{distancia_m} Meters",
                              dissolve_option="ALL" if dissolver else "NONE", method="GEODESIC")
    return destino


# 5) Área geodésica em hectares; cria um novo campo em uma cópia da fonte.
def calcular_areas_hectares(entrada, saida, campo="area_ha"):
    """Exemplo: calcular_areas_hectares(lotes, 'memory/lotes_ha').

    Requer polígonos com SRC conhecido. Não substitui campos existentes.
    Verifique previamente a validade das geometrias da base de origem.
    """
    descricao = _descrever(entrada)
    _referencia(descricao.spatialReference)
    if descricao.shapeType != "Polygon":
        raise ValueError("O cálculo de hectares exige polígonos.")
    destino = _saida(saida)
    workspace = str(destino).replace("\\", "/").rsplit("/", 1)[0]
    if not isinstance(campo, str) or arcpy.ValidateFieldName(campo, workspace) != campo:
        raise ValueError("Nome de campo inválido.")
    if campo.casefold() in {f.name.casefold() for f in arcpy.ListFields(entrada)}:
        raise ValueError("O campo de área já existe na fonte.")
    with arcpy.EnvManager(overwriteOutput=False):
        arcpy.management.CopyFeatures(entrada, destino)
        arcpy.management.AddField(destino, campo, "DOUBLE")
        arcpy.management.CalculateGeometryAttributes(destino, [[campo, "AREA_GEODESIC"]], area_unit="HECTARES")
    return destino


# 6) Limpeza de campos vazios: análise integral e alteração só na cópia.
def limpar_colunas_vazias(entrada, saida, proteger=("id", "fid")):
    """Exemplo: copia, removidos = limpar_colunas_vazias(fc, 'memory/limpa').

    Considera vazio somente None ou texto sem conteúdo. Preserva 0, False,
    campos obrigatórios e nomes protegidos. Recusa filtros e seleções ativos.
    """
    _descrever(entrada)
    if hasattr(entrada, "isFeatureLayer"):
        if entrada.getSelectionSet() or entrada.supports("DEFINITIONQUERY") and entrada.definitionQuery:
            raise ValueError("Use a feature class sem filtros ou seleções para revisar colunas.")
    elif getattr(arcpy.Describe(entrada), "FIDSet", "") or getattr(arcpy.Describe(entrada), "whereClause", ""):
        raise ValueError("A entrada contém seleção ou filtro ativo.")
    protegidos = {nome.casefold() for nome in proteger}
    campos = [f.name for f in arcpy.ListFields(entrada) if not f.required and f.type not in ("OID", "Geometry", "GlobalID", "Blob", "Raster") and f.name.casefold() not in protegidos]
    vazios = set(range(len(campos)))
    total = 0
    if campos:
        with arcpy.da.SearchCursor(entrada, campos) as cursor:
            for linha in cursor:
                total += 1
                for indice in tuple(vazios):
                    valor = linha[indice]
                    if not (valor is None or isinstance(valor, str) and not valor.strip()):
                        vazios.remove(indice)
    else:
        total = int(arcpy.management.GetCount(entrada)[0])
    if total == 0:
        raise ValueError("Uma fonte sem feições não permite inferir colunas vazias.")
    remover = [nome for i, nome in enumerate(campos) if i in vazios]
    destino = _saida(saida)
    with arcpy.EnvManager(overwriteOutput=False):
        arcpy.management.CopyFeatures(entrada, destino)
        if remover:
            arcpy.management.DeleteField(destino, remover)
    return destino, remover


# 7) Merge concatena feições; não dissolve ou une seus limites.
def unificar_camadas(camadas, saida, wkid=None):
    """Exemplo: unificar_camadas([fc1, fc2], r'C:/saida/kit.gdb/merge').

    Exige mesmo tipo de geometria e mesmo datum. Para datums diferentes,
    reprojete explicitamente antes. Revise harmonização de campos e IDs.
    """
    entradas = _entradas(camadas)
    descricoes = [_descrever(e) for e in entradas]
    if len(entradas) < 2 or len({d.shapeType for d in descricoes}) != 1:
        raise ValueError("Informe duas ou mais fontes com o mesmo tipo de geometria.")
    referencias = [_referencia(d.spatialReference) for d in descricoes]
    destino_crs = _referencia(wkid) if wkid is not None else referencias[0]
    if any(sr.GCS.name != destino_crs.GCS.name for sr in referencias):
        raise ValueError("Reprojete as fontes ao mesmo datum antes do merge.")
    destino = _saida(saida)
    with arcpy.EnvManager(overwriteOutput=False, outputCoordinateSystem=destino_crs):
        arcpy.management.Merge(entradas, destino)
    return destino


# 8) PNG do quadro de mapa de um layout, com estilos e rótulos do projeto.
def exportar_mapa_png(caminho, nome_layout, nome_quadro, projeto="CURRENT", dpi=300):
    """Exemplo: exportar_mapa_png('C:/saida/mapa.png', 'A4', 'Mapa').

    Pode fornecer caminho .aprx para executar fora da interface. Exporta só
    o MapFrame; para a página inteira use Layout.exportToPNG separadamente.
    Dimensões vêm do quadro e do DPI; arquivo existente não é sobrescrito.
    """
    if isinstance(dpi, bool) or not isinstance(dpi, int) or dpi <= 0:
        raise ValueError("DPI deve ser um inteiro positivo.")
    destino = Path(caminho).expanduser().resolve()
    if destino.suffix.lower() != ".png" or destino.exists():
        raise ValueError("Informe um novo arquivo .png.")
    aprx = arcpy.mp.ArcGISProject(str(projeto)) if isinstance(projeto, (str, Path)) else projeto
    layouts = [l for l in aprx.listLayouts() if l.name == nome_layout]
    if len(layouts) != 1:
        raise ValueError("Layout ausente ou ambíguo.")
    quadros = [q for q in layouts[0].listElements("MAPFRAME_ELEMENT") if q.name == nome_quadro]
    if len(quadros) != 1 or quadros[0].map is None:
        raise ValueError("Quadro de mapa ausente, ambíguo ou sem mapa.")
    destino.parent.mkdir(parents=True, exist_ok=True)
    quadros[0].exportToPNG(str(destino), resolution=dpi)
    if not destino.is_file():
        raise RuntimeError("O ArcGIS não produziu o PNG esperado.")
    return str(destino)


# 9) Fishnet regular: linhas ou polígonos na extensão da camada.
def criar_grade_fishnet(referencia, saida, espacamento_m, tipo="POLYGON"):
    """Exemplo: criar_grade_fishnet(area_utm, 'memory/grade', 250).

    tipo pode ser POLYGON ou POLYLINE. Exige SRC projetado em metros.
    A grade cobre o retângulo envolvente, sem recorte ao polígono de estudo.
    """
    descricao = _descrever(referencia)
    sr = _referencia(descricao.spatialReference)
    if sr.type != "Projected" or not math.isclose(sr.metersPerUnit, 1.0, rel_tol=1e-9):
        raise ValueError("Escolha uma referência projetada em metros.")
    _positivo(espacamento_m, "Espaçamento")
    if tipo not in ("POLYGON", "POLYLINE"):
        raise ValueError("tipo deve ser POLYGON ou POLYLINE.")
    e = descricao.extent
    if not all(math.isfinite(v) for v in (e.XMin, e.YMin, e.XMax, e.YMax)) or e.XMax <= e.XMin or e.YMax <= e.YMin:
        raise ValueError("Extensão de referência inválida.")
    destino = _saida(saida)
    with arcpy.EnvManager(overwriteOutput=False, outputCoordinateSystem=sr):
        arcpy.management.CreateFishnet(destino, f"{e.XMin} {e.YMin}", f"{e.XMin} {e.YMin + 1}",
                                      espacamento_m, espacamento_m, 0, 0,
                                      corner_coord=f"{e.XMax} {e.YMax}", labels="NO_LABELS", geometry_type=tipo)
    return destino


# 10) Estatísticas numéricas por atributo, com leitura progressiva do cursor.
def imprimir_estatisticas_atributos(entrada, campos=None):
    """Exemplo: resumo = imprimir_estatisticas_atributos(fc, ['area_ha']).

    Sem campos, usa os numéricos. Retorna e imprime contagem, nulos, inválidos,
    soma, mínimo, máximo, média e desvio padrão populacional. Ignora NaN/Inf.
    """
    _descrever(entrada)
    tipos = {"SmallInteger", "Integer", "BigInteger", "Single", "Double"}
    numericos = {f.name for f in arcpy.ListFields(entrada) if f.type in tipos}
    nomes = sorted(numericos) if campos is None else [campos] if isinstance(campos, str) else list(campos)
    if not nomes or len(nomes) != len(set(nomes)) or not set(nomes) <= numericos:
        raise ValueError("Informe campos numéricos existentes, sem repetições.")
    resumo = {n: {"contagem": 0, "nulos": 0, "invalidos": 0, "soma": 0.0,
                  "minimo": None, "maximo": None, "media": 0.0, "_m2": 0.0} for n in nomes}
    with arcpy.da.SearchCursor(entrada, nomes) as cursor:
        for linha in cursor:
            for nome, valor in zip(nomes, linha):
                d = resumo[nome]
                if valor is None:
                    d["nulos"] += 1
                    continue
                try:
                    valor = float(valor)
                except (TypeError, ValueError, OverflowError):
                    d["invalidos"] += 1
                    continue
                if not math.isfinite(valor):
                    d["invalidos"] += 1
                    continue
                d["contagem"] += 1
                d["soma"] += valor
                d["minimo"] = valor if d["minimo"] is None else min(d["minimo"], valor)
                d["maximo"] = valor if d["maximo"] is None else max(d["maximo"], valor)
                delta = valor - d["media"]
                d["media"] += delta / d["contagem"]
                d["_m2"] += delta * (valor - d["media"])
    for nome, d in resumo.items():
        m2 = d.pop("_m2")
        d["desvio_padrao"] = math.sqrt(max(0.0, m2 / d["contagem"])) if d["contagem"] else None
        if not d["contagem"]:
            d["media"] = None
        print(f"{nome}: {d}")
    return resumo
