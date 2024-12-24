import os
import pandas as pd
from banco import conexao_banco, inserir_dados
from csv_para_xlsx import csv_para_xlsx


def main():
    caminho_csv = (
        "C:/Program Files (x86)/PaperCut Print Logger/logs/csv/"
        "papercut-print-log-all-time.csv"
    )

    caminho_xlsx = (
        "C:/Users/ana.beatriz/Documents/Ana/Projetos/SysPrint/testes/teste1.xlsx"
    )
    if not os.path.exists(caminho_xlsx) or (
        os.path.getmtime(caminho_csv) > os.path.getmtime(caminho_xlsx)
    ):
        print("O arquivo CSV foi modificado\n\nGerando um novo XLSX")
        csv_para_xlsx(caminho_csv, caminho_xlsx)
    else:
        print(
            "O CSV não foi modificado desde a última verificação\n\nUsando o XLSX existente"
        )

    df = pd.read_excel(caminho_xlsx)

    # Converte os campos para valores aceitos pelo tipo "boolean"
    df["Duplex"] = df["Duplex"].map({"DUPLEX": 1, "NOT DUPLEX": 0})
    df["Grayscale"] = df["Grayscale"].map({"GRAYSCALE": 1, "NOT GRAYSCALE": 0})

    conn = conexao_banco()
    inserir_dados(conn, df)
    conn.close()
    print("\nConcluído.")


if __name__ == "__main__":
    main()
