import pandas as pd


def csv_para_xlsx(caminho_csv, caminho_xlsx):
    # Leitura do CSV
    with open(caminho_csv, "r") as file:
        linhas = file.readlines()

    # Novo cabeçalho sem as colunas 'Height' e 'Width'
    cabecalho = linhas[1].strip().split(",")
    novo_cabecalho = [col for col in cabecalho if col not in ("Height", "Width")]

    # Processamento dos novos dados
    dados = linhas[2].strip().split(",")
    novos_dados = [dado for dado in dados if dado]

    # Novo DataFrame
    df = pd.DataFrame([novos_dados], columns=novo_cabecalho)

    # DataFrame para Excel/.xlsx
    df.to_excel(caminho_xlsx, index=False, engine="openpyxl")

    print(f"Arquivo convertido de {caminho_csv} para {caminho_xlsx}.")

    return df
