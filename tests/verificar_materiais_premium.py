"""Valida os 60 downloads, conteúdo e integridade dos GeoPackages.

Uso: python tests/verificar_materiais_premium.py
Requer geopandas e pyogrio para validar as geometrias de todas as camadas.
"""
from pathlib import Path
from html.parser import HTMLParser
import re
import sqlite3
import geopandas as gpd
import pyogrio

ROOT=Path(__file__).resolve().parents[1]
FOLDERS={'templates_gis':'.txt','bancos_dados':'.gpkg','portfolios_cases':'.md',
         'roadmaps_aprendizado':'.md','exercicios_praticos':'.md','glossarios_tecnicos':'.md'}


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':
            self.links.append(dict(attrs))


def main():
    html=(ROOT/'index.html').read_text(encoding='utf-8')
    groups=re.findall(r'<details class="premium-collection".*?</details>',html,re.S)
    assert len(groups)==6
    links=[]
    for group in groups:
        cards=re.findall(r'<article class="premium-card premium-library-card">.*?</article>',group,re.S)
        assert len(cards)==10
        for card in cards:
            assert 'wa.me' not in card and 'Solicitar material' not in card
            assert 'Disponibilidade sob consulta' not in card
            assert 'Baixar Material Now <span' in card
            parser=Links(); parser.feed(card)
            assert len(parser.links)==1
            a=parser.links[0]
            assert 'download' in a and 'target' not in a
            target=(ROOT/a['href']).resolve()
            assert target.is_relative_to(ROOT) and target.is_file()
            assert target.name==a['download']
            links.append(target)
    assert len(links)==len(set(links))==60
    camadas=0
    for pasta,extension in FOLDERS.items():
        arquivos=list((ROOT/pasta).iterdir())
        assert len(arquivos)==10 and all(a.is_file() and a.suffix==extension for a in arquivos)
        assert set(arquivos)=={p for p in links if p.parent==ROOT/pasta}
        for arquivo in arquivos:
            if extension!='.gpkg':
                text=arquivo.read_text(encoding='utf-8')
                assert len(text)>2200 and len(text.split())>280,(arquivo,len(text))
                assert '## ' in text and 'DataGeo Academy' in text
                if pasta=='glossarios_tecnicos':
                    assert text.count('### ')==12
                if pasta=='roadmaps_aprendizado':
                    assert text.count('### Etapa ')==8
                if pasta=='exercicios_praticos':
                    assert '## Gabarito comentado' in text
                continue
            with sqlite3.connect(arquivo) as con:
                assert con.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
                assert con.execute('PRAGMA foreign_key_check').fetchall()==[]
                assert con.execute('PRAGMA application_id').fetchone()[0]==0x47504B47
                doc=con.execute('SELECT conteudo FROM material_leia_me').fetchone()[0]
                assert 'DADOS SINTÉTICOS' in doc and 'EPSG:31982' in doc and len(doc)>2000
                assert con.execute('SELECT count(*) FROM material_dicionario').fetchone()[0]>5
                registros=con.execute('SELECT table_name,srs_id FROM gpkg_geometry_columns').fetchall()
                assert len(registros)>=1
                assert all(srid==31982 for _,srid in registros)
                for nome,_ in registros:
                    df=gpd.read_file(arquivo,layer=nome,engine='pyogrio')
                    assert len(df)>0 and df.crs.to_epsg()==31982
                    assert df.geometry.notna().all() and (~df.geometry.is_empty).all()
                    assert df.geometry.is_valid.all() and df.id.is_unique
                    assert df.sintetico.eq(1).all() and df.fonte.eq('simulacao_datageo').all()
                    camadas+=1
    # Valores demonstrativos conhecidos: áreas, séries e taxas.
    cobertura=next((ROOT/'bancos_dados').glob('02_*.gpkg'))
    df=gpd.read_file(cobertura,layer='cobertura')
    assert abs(df.area.sum()/10000-900)<1e-9
    assert abs(df.area_ha.sum()-900)<1e-9
    serie=next((ROOT/'bancos_dados').glob('10_*.gpkg'))
    df=gpd.read_file(serie,layer='observacoes')
    assert len(df)==24 and df.groupby('estacao').size().eq(12).all()
    assert not df.duplicated(['estacao','data_ref']).any()
    print(f'OK: 60 arquivos reais, seis pastas com dez itens, 60 downloads e {camadas} camadas GPKG válidas.')


if __name__=='__main__':
    main()
