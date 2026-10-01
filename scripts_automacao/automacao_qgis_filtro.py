"""Filtros por atributos em camadas vetoriais carregadas no QGIS 3.

Execute no editor do Console Python do QGIS ou carregue o arquivo assim:

    from pathlib import Path
    exec(Path('/caminho/automacao_qgis_filtro.py').read_text(encoding='utf-8'))
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

Não altera atributos ou geometrias, não exporta dados e não salva o projeto.
O filtro será persistido no projeto apenas se você decidir salvá-lo no QGIS.
Nenhum filtro é aplicado automaticamente ao executar este arquivo.

Referência: https://api.qgis.org/api/classQgsVectorLayer.html
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
