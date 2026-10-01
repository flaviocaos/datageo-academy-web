"""Esquema editorial: não injeta parágrafos, exemplos nem respostas genéricos."""
from textwrap import dedent

def cap(titulo, teoria, codigo, tabela, tarefa, resposta, ampliacao, revisao):
    return dict(titulo=titulo, teoria=teoria.split('\n\n'), codigo=dedent(codigo).strip()+'\n',
                tabela=tabela, tarefa=tarefa, resposta=resposta, ampliacao=ampliacao, revisao=revisao)
