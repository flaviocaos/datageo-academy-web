"""Testes de lógica com ArcPy simulado; não validam geoprocessamento real.

Execute com Python comum. O teste cobre reversão de filtros, estatísticas,
proteção de zeros e campos obrigatórios na limpeza, parâmetros de fishnet
e bloqueio de sobrescrita. Execute o kit no ArcGIS Pro para validar as APIs
e resultados geométricos com sua licença, versão e fontes de dados.
"""
from pathlib import Path
import runpy
import sys
from types import ModuleType, SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent


def main():
    chamadas = []
    fields = [SimpleNamespace(name="id", type="Integer", required=True),
              SimpleNamespace(name="valor", type="Double", required=False),
              SimpleNamespace(name="vazio", type="String", required=False),
              SimpleNamespace(name="zero", type="Integer", required=False)]
    linhas = [(1, 10, None, 0), (2, 20, "  ", 0), (3, None, "", 0), (4, float("nan"), None, 0)]
    existentes = {"fonte"}

    class SR:
        def __init__(self, wkid):
            self.type = "Geographic" if wkid == 4674 else "Projected"
            self.name = "GCS_SIRGAS_2000"
            self.GCS = self
            self.metersPerUnit = 1.0

    class Camada:
        isFeatureLayer = True
        isBroken = False
        def __init__(self, nome):
            self.name = self.longName = nome
            self.definitionQuery = "original = 1"
        def supports(self, propriedade):
            return propriedade == "DEFINITIONQUERY"

    class Ambiente:
        def __init__(self, **kwargs):
            self.valores = kwargs
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False

    class Cursor:
        def __init__(self, entrada, nomes):
            indices = [next(i for i, f in enumerate(fields) if f.name == n) for n in nomes]
            self.linhas = [tuple(l[i] for i in indices) for l in linhas]
        def __enter__(self):
            return iter(self.linhas)
        def __exit__(self, *args):
            return False

    def count(entrada):
        if isinstance(entrada, Camada) and entrada.definitionQuery == "INVALID":
            raise RuntimeError("Consulta recusada pelo provedor simulado.")
        return [str(len(linhas))]

    def describe(entrada):
        return SimpleNamespace(shapeType="Polygon", spatialReference=SR(31983), baseName="fonte",
                               extent=SimpleNamespace(XMin=0, YMin=0, XMax=100, YMax=100))

    def copy(entrada, saida):
        existentes.add(saida)

    def delete(saida, nomes):
        chamadas.append(("DeleteField", nomes))

    def fishnet(*args, **kwargs):
        chamadas.append(("Fishnet", args, kwargs))
        existentes.add(args[0])

    fake = ModuleType("arcpy")
    fake.Exists = lambda entrada: isinstance(entrada, Camada) or str(entrada) in existentes
    fake.Describe = describe
    fake.ListFields = lambda entrada: fields
    fake.ValidateTableName = lambda nome, workspace: nome
    fake.SpatialReference = SR
    fake.EnvManager = Ambiente
    fake.da = SimpleNamespace(SearchCursor=Cursor)
    fake.management = SimpleNamespace(GetCount=count, CopyFeatures=copy, DeleteField=delete, CreateFishnet=fishnet)
    anterior = sys.modules.get("arcpy")
    sys.modules["arcpy"] = fake
    try:
        kit = runpy.run_path(str(ROOT / "scripts_automacao" / "canivete_suico_arcgis.py"))
        a, b = Camada("a"), Camada("b")
        mapa = SimpleNamespace(listLayers=lambda: [a, b])
        historico = kit["aplicar_filtros"]({"a": "ativo = 1"}, mapa)
        assert a.definitionQuery == "(original = 1) AND (ativo = 1)"
        kit["restaurar_filtros"](historico)
        try:
            kit["aplicar_filtros"]({"a": "ativo = 1", "b": "INVALID"}, mapa, combinar=False)
        except RuntimeError:
            pass
        else:
            raise AssertionError("Falha simulada não foi propagada.")
        assert a.definitionQuery == b.definitionQuery == "original = 1"

        resumo = kit["imprimir_estatisticas_atributos"]("fonte", ["valor", "zero"])
        assert resumo["valor"]["media"] == 15 and resumo["valor"]["desvio_padrao"] == 5
        assert resumo["valor"]["nulos"] == resumo["valor"]["invalidos"] == 1
        assert resumo["zero"]["contagem"] == 4 and resumo["zero"]["soma"] == 0
        _, removidos = kit["limpar_colunas_vazias"]("fonte", "memory/limpa")
        assert removidos == ["vazio"] and chamadas[-1] == ("DeleteField", ["vazio"])
        try:
            kit["limpar_colunas_vazias"]("fonte", "memory/limpa")
        except FileExistsError:
            pass
        else:
            raise AssertionError("Uma saída existente foi aceita.")
        kit["criar_grade_fishnet"]("fonte", "memory/grade", 50)
        assert chamadas[-1][1][3:7] == (50, 50, 0, 0)
        assert chamadas[-1][2]["corner_coord"] == "100 100"
        print("PASS: filtros, reversão, estatísticas, limpeza e grade — ArcPy simulado.")
    finally:
        if anterior is None:
            del sys.modules["arcpy"]
        else:
            sys.modules["arcpy"] = anterior


if __name__ == "__main__":
    main()
