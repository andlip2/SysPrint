from leitor_excel import ler_excel
from banco import conexao_banco, inserir_dados


def main():
    caminho = (
        "C:/Users/ana.beatriz/Documents/Ana/Projetos/"
        "Projeto Transformar Planilhas/Resultados Testes/teste3.xlsx"
    )
    df = ler_excel(caminho)

    # Converte os campos para valores aceitos pelo tipo "boolean"
    df["Duplex"] = df["Duplex"].map({"DUPLEX": 1, "NOT DUPLEX": 0})
    df["Grayscale"] = df["Grayscale"].map({"GRAYSCALE": 1, "NOT GRAYSCALE": 0})

    conn = conexao_banco()
    inserir_dados(conn, df)
    conn.close()
    print("Concluído")


if __name__ == "__main__":
    main()
