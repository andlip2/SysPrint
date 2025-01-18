# Importa a função listar_impressoras
from listar_impressoras import listar_impressoras  # Salve a função anterior em listar_impressoras.py

# Função principal
def executar_para_impressoras_virtuais():
    impressoras = listar_impressoras()
    for impressora in impressoras:
        if impressora["Tipo"] == "Virtual":
            nome_impressora = impressora["Nome"]
            print(f"Executando para impressora virtual: {nome_impressora}")
            
            # Substitua pelo código que deve ser executado para impressoras virtuais
            realizar_operacao_com_impressora_virtual(nome_impressora)

# Função de exemplo para realizar operações com impressoras virtuais
def realizar_operacao_com_impressora_virtual(nome_impressora):
    # Exemplo de operação: apenas imprimir o nome
    print(f"Operação realizada com a impressora: {nome_impressora}")

# Executa o script principal
if __name__ == "__main__":
    executar_para_impressoras_virtuais()
