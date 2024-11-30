import pandas as pd

caminho = (
    "C:/Users/ana.beatriz/Documents/Ana/Projetos/"
    "Projeto Transformar Planilhas/Resultados Testes/teste3.xlsx"
)


def ler_excel(caminho):
    return pd.read_excel(caminho)
