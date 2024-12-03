import pandas as pd

# Caminho do arquivo a ser processado
file_path = (
    'C:/Program Files (x86)/PaperCut Print Logger/logs/csv/'
    'papercut-print-log-all-time.csv'
    )

# Leitura do arquivo completo, independente da pandas
with open(file_path, 'r') as file:
    linhas = file.readlines()

# Dividisão das colunas de acordo com os elementos da linha 2
cabecalho = linhas[1].strip().split(',')
novo_cabecalho = [col for col in cabecalho if col not in ('Height', 'Width')]

dados = linhas[2].strip().split(',')
novos_dados = [dado for dado in dados if dado]

print(f"Colunas: {len(novo_cabecalho)}")
print(f"Linhas: {len(novos_dados)}")

df = pd.DataFrame([novos_dados], columns=novo_cabecalho)

output_path = (
    'C:/Users/ana.beatriz/Documents/Ana/Projetos/'
    'Projeto Transformar Planilhas/Resultados Testes/teste4.xlsx'
    )

df.to_excel(output_path, index=False, engine='openpyxl')
