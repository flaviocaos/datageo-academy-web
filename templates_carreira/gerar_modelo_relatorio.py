"""Gera um template Word OOXML real, sem dependências externas.

Execute: python templates_carreira/gerar_modelo_relatorio.py
O arquivo resultante é editável no Word e no LibreOffice.
"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET

W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
ET.register_namespace('w', W)
ET.register_namespace('r', R)


def element(parent, tag, attrs=None, text=None):
    node = ET.SubElement(parent, f'{{{W}}}{tag}',
                         {f'{{{W}}}{k}': str(v) for k, v in (attrs or {}).items()})
    if text is not None:
        node.text = text
        node.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    return node


def paragraph(parent, text='', style='Normal', bold=False):
    p = element(parent, 'p')
    props = element(p, 'pPr')
    element(props, 'pStyle', {'val': style})
    run = element(p, 'r')
    if bold:
        element(element(run, 'rPr'), 'b')
    element(run, 't', text=text)
    return p


def table(parent, headers, rows):
    tbl = element(parent, 'tbl')
    props = element(tbl, 'tblPr')
    element(props, 'tblW', {'w': 0, 'type': 'auto'})
    element(props, 'tblLayout', {'type': 'fixed'})
    borders = element(props, 'tblBorders')
    for edge in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        element(borders, edge, {'val': 'single', 'sz': 4, 'color': 'D9E3ED'})
    margins = element(props, 'tblCellMar')
    for edge in ['top', 'left', 'bottom', 'right']:
        element(margins, edge, {'w': 95, 'type': 'dxa'})
    grid = element(tbl, 'tblGrid')
    width = 9638 // len(headers)
    for _ in headers:
        element(grid, 'gridCol', {'w': width})
    for index, row in enumerate([headers] + rows):
        tr = element(tbl, 'tr')
        trprops = element(tr, 'trPr')
        element(trprops, 'cantSplit')
        if index == 0:
            element(trprops, 'tblHeader')
        for text in row:
            cell = element(tr, 'tc')
            cp = element(cell, 'tcPr')
            element(cp, 'tcW', {'w': width, 'type': 'dxa'})
            element(cp, 'shd', {'fill': '0B2F5B' if index == 0 else ('F1F6FA' if index % 2 else 'FFFFFF')})
            p = paragraph(cell, text, 'TableHeader' if index == 0 else 'TableText')
    paragraph(parent, '', 'TableText')


def page(parent, title):
    p = element(parent, 'p')
    element(element(p, 'r'), 'br', {'type': 'page'})
    paragraph(parent, title, 'Heading1')


def field(parent, name):
    simple = element(parent, 'fldSimple', {'instr': name})
    element(element(simple, 'r'), 't', text='1')


def xml(node):
    return ET.tostring(node, encoding='utf-8', xml_declaration=True)


def gerar():
    document = ET.Element(f'{{{W}}}document')
    body = element(document, 'body')
    paragraph(body, 'DATAGEO ACADEMY', 'Brand')
    paragraph(body, 'INTELIGÊNCIA GEOGRÁFICA · DOCUMENTAÇÃO TÉCNICA', 'Subtitle')
    paragraph(body, '', 'Normal')
    paragraph(body, 'RELATÓRIO TÉCNICO', 'Title')
    paragraph(body, 'Laudos ambientais e análises territoriais', 'Subtitle')
    paragraph(body, '[TÍTULO DO ESTUDO / EMPREENDIMENTO]', 'Heading1')
    paragraph(body, '[Município – UF | Área de estudo]', 'Placeholder')
    table(body, ['CONTROLE DO DOCUMENTO', 'PREENCHIMENTO'], [
        ['Código / revisão', '[RT-000 / Rev. 00]'], ['Contratante', '[Razão social / identificação]'],
        ['Responsável técnico', '[Nome / formação / registro, quando aplicável]'],
        ['Data de emissão', '[DD/MM/AAAA]'], ['Classificação', '[Público / interno / restrito]']])
    paragraph(body, 'COMO UTILIZAR ESTE MODELO', 'Heading2')
    paragraph(body, 'Substitua os campos entre colchetes por informações verificadas. '
              'Remova orientações antes de emitir a versão final. Identifique itens não aplicáveis '
              'e justifique-os. Adapte o escopo, os critérios e a responsabilidade técnica ao serviço.', 'Note')
    paragraph(body, 'Modelo editável • Não contém resultados, pareceres ou certificações pré-aprovados.', 'Caption')

    page(body, '01 · Identificação, escopo e rastreabilidade')
    paragraph(body, '1.1 Identificação do projeto', 'Heading2')
    table(body, ['CAMPO', 'REGISTRO'], [
        ['Empreendimento / atividade', '[Nome, atividade, endereço e identificação cadastral]'],
        ['Objeto e finalidade', '[Pergunta técnica, uso previsto e destinatários]'],
        ['Área / período do estudo', '[Limites, extensão e intervalo de observação]'],
        ['Equipe / responsabilidades', '[Autores, revisores e funções]'],
        ['Referência do serviço', '[Contrato, solicitação, processo ou termo de referência]']])
    paragraph(body, '1.2 Objetivos e limites', 'Heading2')
    paragraph(body, '[Descreva o objetivo geral, os objetivos específicos, as entregas e o que está fora do escopo.]', 'Placeholder')
    paragraph(body, '1.3 Histórico de revisões', 'Heading2')
    table(body, ['REVISÃO / DATA', 'ALTERAÇÃO', 'AUTOR / APROVAÇÃO'], [
        ['[00 / data]', '[Emissão inicial]', '[Nome / situação]'],
        ['[01 / data]', '[Descrição da alteração]', '[Nome / situação]']])
    paragraph(body, '1.4 Síntese executiva', 'Heading2')
    paragraph(body, '[Resuma o contexto, método, principais achados, limitações e recomendações. '
              'Preencha após concluir a análise. Não apresente conclusões sem evidências.]', 'Placeholder')

    page(body, '02 · Bases de dados e metodologia')
    paragraph(body, '2.1 Inventário de fontes', 'Heading2')
    table(body, ['BASE / ORIGEM', 'DATA / ESCALA / RESOLUÇÃO', 'USO / LIMITAÇÕES'], [
        ['[Imagem / fonte / versão]', '[Aquisição / resolução]', '[Uso, cobertura de nuvens e restrições]'],
        ['[Vetor / órgão / acesso]', '[Atualização / escala]', '[Finalidade, licença e precisão]'],
        ['[Campo / instrumento]', '[Campanha / precisão]', '[Método e representatividade]']])
    paragraph(body, '2.2 Referência espacial e medidas', 'Heading2')
    table(body, ['PARÂMETRO', 'DEFINIÇÃO / EVIDÊNCIA'], [
        ['SRC de origem / destino', '[Datum, projeção, EPSG, fuso, hemisfério e unidade]'],
        ['Transformação', '[Operação, grades, parâmetros e precisão informada]'],
        ['Época / componente vertical', '[Época, referência de altitude ou não aplicável]'],
        ['Áreas / distâncias', '[Método plano ou elipsoidal, CRS de cálculo e unidades]']])
    paragraph(body, 'SIRGAS2000 geográfico (EPSG:4674) usa graus. Não adote um fuso UTM único para qualquer '
              'área. Confirme o CRS real das fontes antes de transformar coordenadas.', 'Note')
    paragraph(body, '2.3 Procedimento reprodutível', 'Heading2')
    paragraph(body, '[Liste etapas, softwares/versões, parâmetros, regras topológicas, tolerâncias, '
              'amostragem, fórmulas e critérios de validação. Informe identificação dos scripts e dados.]', 'Placeholder')
    paragraph(body, '2.4 Critérios de avaliação', 'Heading2')
    paragraph(body, '[Identifique requisitos do projeto e referências aplicáveis, com edição, data e fonte. '
              'Diferencie critérios técnicos adotados de requisitos externos.]', 'Placeholder')

    page(body, '03 · Diagnóstico ambiental e territorial')
    paragraph(body, '3.1 Caracterização da área', 'Heading2')
    paragraph(body, '[Descreva localização, relevo, hidrografia, cobertura e uso do solo, infraestrutura '
              'e contexto de ocupação, conforme o escopo e as fontes disponíveis.]', 'Placeholder')
    paragraph(body, '3.2 Observações e evidências', 'Heading2')
    table(body, ['ID / LOCAL', 'OBSERVAÇÃO / FONTE', 'EVIDÊNCIA / INCERTEZA'], [
        ['[E-01 / coordenadas e CRS]', '[Achado e data]', '[Foto, mapa ou dado / limitação]'],
        ['[E-02 / setor]', '[Achado e data]', '[Referência verificável]'],
        ['[E-03 / setor]', '[Achado e data]', '[Referência verificável]']])
    paragraph(body, '3.3 Aspectos, impactos e condicionantes', 'Heading2')
    table(body, ['ASPECTO / RECEPTOR', 'ANÁLISE / CRITÉRIO', 'RESULTADO / REFERÊNCIA'], [
        ['[Uso do solo / receptor]', '[Método e critério]', '[Resultado demonstrado]'],
        ['[Água / solo / vegetação]', '[Método e critério]', '[Resultado ou não avaliado]']])
    paragraph(body, 'Separe observação direta, informação de terceiros e inferência analítica. '
              'Explique a base de cada avaliação e registre lacunas de informação.', 'Note')
    paragraph(body, '3.4 Registro fotográfico', 'Heading2')
    paragraph(body, '[INSERIR FOTOGRAFIA / CROQUI]', 'Placeholder')
    paragraph(body, 'Figura 1 — [Descrição, local, data, autoria e direção de tomada, quando pertinente].', 'Caption')

    page(body, '04 · Resultados, mapas e controle de qualidade')
    paragraph(body, '4.1 Indicadores e resultados', 'Heading2')
    table(body, ['INDICADOR / UNIDADE', 'RESULTADO', 'MÉTODO / PRECISÃO'], [
        ['[Área / ha]', '[Valor calculado]', '[CRS e fórmula]'],
        ['[Classe / extensão]', '[Valor / distribuição]', '[Fonte e período]'],
        ['[Outro indicador]', '[Valor]', '[Método e incerteza]']])
    paragraph(body, '4.2 Produto cartográfico', 'Heading2')
    paragraph(body, '[INSERIR MAPA COM LEGENDA, ESCALA, NORTE, SRC, FONTES E DATA]', 'Placeholder')
    paragraph(body, 'Mapa 1 — [Título, elaboração, fontes e período de referência].', 'Caption')
    paragraph(body, '4.3 Validação geométrica, topológica e temática', 'Heading2')
    table(body, ['VERIFICAÇÃO', 'RESULTADO / EXCEÇÃO', 'EVIDÊNCIA / REVISOR'], [
        ['SRC e transformação', '[Conforme / pendente / N.A.]', '[Registro]'],
        ['Validade geométrica', '[Erros iniciais e finais]', '[Saída da validação]'],
        ['Sobreposição / lacunas', '[Regra e exceções]', '[Camada / IDs]'],
        ['Conectividade / atributos', '[Resultado e tolerância]', '[Registro]']])
    paragraph(body, '4.4 Limitações e incertezas', 'Heading2')
    paragraph(body, '[Informe limitações de escala, cobertura, temporalidade, precisão, amostragem, '
              'transformação e métodos. Explique como afetam os resultados e sua utilização.]', 'Placeholder')

    page(body, '05 · Conclusões e recomendações')
    paragraph(body, '5.1 Conclusões fundamentadas', 'Heading2')
    paragraph(body, '[Responda aos objetivos com base nos resultados apresentados, citando tabelas, '
              'mapas e evidências. Declare aspectos inconclusivos e investigações necessárias.]', 'Placeholder')
    paragraph(body, '5.2 Plano de ação', 'Heading2')
    table(body, ['AÇÃO / PRIORIDADE', 'RESPONSÁVEL / PRAZO', 'CRITÉRIO DE VERIFICAÇÃO'], [
        ['[Ação 1 / prioridade]', '[Nome / prazo]', '[Indicador e evidência]'],
        ['[Ação 2 / prioridade]', '[Nome / prazo]', '[Indicador e evidência]'],
        ['[Ação 3 / prioridade]', '[Nome / prazo]', '[Indicador e evidência]']])
    paragraph(body, '5.3 Condições de utilização', 'Heading2')
    paragraph(body, '[Defina o uso adequado dos resultados, a validade temporal, as restrições de '
              'generalização e as condições que exigem atualização do estudo.]', 'Placeholder')
    paragraph(body, '5.4 Responsabilidade e aprovação', 'Heading2')
    table(body, ['ELABORAÇÃO', 'REVISÃO / APROVAÇÃO'], [
        ['[Nome / formação / registro aplicável]', '[Nome / função]'],
        ['[Documento de responsabilidade, se aplicável]', '[Critério de aceite e pendências]'],
        ['[Local e data]', '[Local e data]'],
        ['[Assinatura]', '[Assinatura]']])
    paragraph(body, 'A assinatura e a emissão final cabem aos profissionais responsáveis. '
              'Este modelo não substitui revisão técnica nem determina habilitação para o serviço.', 'Note')

    page(body, '06 · Referências, anexos e entrega')
    paragraph(body, '6.1 Referências utilizadas', 'Heading2')
    paragraph(body, '[Autor / instituição. Título. Edição ou versão. Data. URL e data de acesso, quando aplicável.]', 'Placeholder')
    paragraph(body, 'Referências iniciais para o sistema de referência e validação:', 'Normal')
    paragraph(body, 'IBGE — SIRGAS2000 e Projeto Mudança do Referencial Geodésico. '
              'https://www.ibge.gov.br/geociencias/informacoes-sobre-posicionamento-geodesico/sirgas.html', 'Caption')
    paragraph(body, 'QGIS — Topology Checker. '
              'https://docs.qgis.org/3.44/en/docs/user_manual/plugins/core_plugins/plugins_topology_checker.html', 'Caption')
    paragraph(body, '6.2 Relação de anexos', 'Heading2')
    table(body, ['ANEXO', 'CONTEÚDO / IDENTIFICAÇÃO'], [
        ['A', '[Mapas e memoriais]'], ['B', '[Dados e dicionário de atributos]'],
        ['C', '[Registro de campo e fotografias]'], ['D', '[Checklist topológico, erros e exceções]'],
        ['E', '[Scripts, parâmetros e versões]'], ['F', '[Documentos complementares aplicáveis]']])
    paragraph(body, '6.3 Conferência antes da emissão', 'Heading2')
    for texto in ['[ ] Campos preenchidos; orientações e exemplos removidos.',
                  '[ ] Tabelas, unidades, fontes e referências conferidas.',
                  '[ ] Mapas legíveis; figuras e anexos identificados.',
                  '[ ] CRS, tolerâncias e resultados de validação documentados.',
                  '[ ] Conclusões sustentadas por evidências; limitações declaradas.',
                  '[ ] Revisão técnica, assinaturas e versão de entrega registradas.']:
        paragraph(body, texto, 'TableText')
    paragraph(body, 'ENTREGA FINAL: [DOCX editável / PDF emitido / base geoespacial / anexos e manifesto de arquivos].', 'Note')

    sect = element(body, 'sectPr')
    for tag, rel in [('headerReference', 'rId2'), ('footerReference', 'rId3')]:
        ref = element(sect, tag, {'type': 'default'})
        ref.set(f'{{{R}}}id', rel)
    element(sect, 'pgSz', {'w': 11906, 'h': 16838})
    element(sect, 'pgMar', {'top': 1134, 'right': 1134, 'bottom': 1134, 'left': 1134, 'header': 567, 'footer': 567, 'gutter': 0})

    styles = ET.Element(f'{{{W}}}styles')
    for name, size, color, bold in [('Normal', 21, '243746', False), ('Title', 64, '0B2F5B', True),
        ('Brand', 30, '0B2F5B', True), ('Subtitle', 23, '167380', False),
        ('Heading1', 32, '0B2F5B', True), ('Heading2', 25, '167380', True),
        ('Placeholder', 21, '516879', False), ('Note', 19, '243746', False),
        ('Caption', 18, '516879', False), ('TableText', 18, '243746', False),
        ('TableHeader', 18, 'FFFFFF', True)]:
        style = element(styles, 'style', {'type': 'paragraph', 'styleId': name})
        if name == 'Normal':
            style.set(f'{{{W}}}default', '1')
        element(style, 'name', {'val': name})
        if name != 'Normal':
            element(style, 'basedOn', {'val': 'Normal'})
        pp = element(style, 'pPr')
        element(pp, 'spacing', {'after': 160 if name not in ('TableText', 'TableHeader') else 60, 'line': 265, 'lineRule': 'auto'})
        if name.startswith('Heading'):
            element(pp, 'keepNext')
            element(pp, 'outlineLvl', {'val': 0 if name == 'Heading1' else 1})
        if name == 'Note':
            element(pp, 'shd', {'fill': 'EBF8EE'})
        rp = element(style, 'rPr')
        element(rp, 'rFonts', {'ascii': 'Calibri', 'hAnsi': 'Calibri', 'cs': 'Calibri'})
        element(rp, 'sz', {'val': size})
        element(rp, 'color', {'val': color})
        if bold:
            element(rp, 'b')

    header = ET.Element(f'{{{W}}}hdr')
    paragraph(header, 'DATAGEO ACADEMY  |  [Projeto / código / revisão]', 'Caption')
    footer = ET.Element(f'{{{W}}}ftr')
    p = paragraph(footer, '[Classificação do documento]  •  Página ', 'Caption')
    field(p, 'PAGE')
    element(element(p, 'r'), 't', text=' de ')
    field(p, 'NUMPAGES')
    settings = ET.Element(f'{{{W}}}settings')
    element(settings, 'updateFields', {'val': 'true'})
    rels = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>
<Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
</Relationships>'''
    rootrels = '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''
    types = '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>
<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>
<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
</Types>'''
    destino = Path(__file__).with_name('modelo_relatorio_tecnico.docx')
    with ZipFile(destino, 'w', ZIP_DEFLATED) as arquivo:
        for name, content in {'[Content_Types].xml': types, '_rels/.rels': rootrels,
                'word/_rels/document.xml.rels': rels, 'word/document.xml': xml(document),
                'word/styles.xml': xml(styles), 'word/header1.xml': xml(header),
                'word/footer1.xml': xml(footer), 'word/settings.xml': xml(settings)}.items():
            arquivo.writestr(name, content)
    print(destino)


if __name__ == '__main__':
    gerar()
