# Pacotes avançados DataGeo Academy

Os quatro arquivos são módulos independentes de Python 3.10 ou superior,
com dez funções cada. Não executam operações ao serem importados.

Instale as dependências em um ambiente virtual:

```shell
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\python.exe -m pip install numpy pandas scipy scikit-learn geopandas shapely pyproj rasterio
```

| Arquivo | Dez ferramentas |
| --- | --- |
| `canivete_ia_geospatial.py` | Preparação de atributos; blocos espaciais; classificação; regressão; K-Means; DBSCAN; anomalias; PCA; validação espacial; classificação de raster por janelas. |
| `canivete_analise_preditiva.py` | Regularização temporal; defasagens; divisão temporal; Ridge; Random Forest; previsão recursiva; tendência linear; IDW; RBF; métricas e validação em blocos. |
| `canivete_ciencia_dados.py` | Leitura de CSV; diagnóstico; padronização de colunas; conversão numérica; preenchimento de lacunas; deduplicação; outliers; agregação; correlações; relatório JSON. |
| `canivete_programacao_dados.py` | Leitura vetorial; criação de pontos; reprojeção SIRGAS 2000; reparo geométrico; buffers; junção espacial; dissolve; recorte vetorial; recorte raster; grade amostral. |

Exemplo no diretório dos scripts:

```python
import canivete_analise_preditiva as kit
valores_futuros, modelo = kit.prever_tendencia([10, 12, 14, 16], passos=3)
print(valores_futuros)  # [18. 20. 22.]
```

Cada função contém instruções e exemplo em português. Buffers, grades, DBSCAN,
IDW e blocos exigem coordenadas em um CRS projetado adequado, em metros.
SIRGAS 2000 EPSG:4674 é geográfico; selecione uma zona UTM para medidas métricas.
Para classificação raster, as bandas devem corresponder aos atributos de treino.

Separe dados futuros ou blocos geográficos para medir a generalização. Ajuste
imputação e escala apenas dentro do treino. As previsões são estimativas que
precisam de validação com os dados e o contexto do projeto.

O teste integrado usa somente dados sintéticos e arquivos temporários:

```shell
python tests/verificar_pacotes_avancados.py
```

Ele verifica as quarenta funções e os quatro links de download no site.
