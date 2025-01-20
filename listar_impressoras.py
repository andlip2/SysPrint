import win32print

def listar_impressoras():
    printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
    impressoras = []
    for printer in printers:
        printer_name = printer[2]  # Nome da impressora
        port_name = "Desconhecida"
        tipo = "Desconhecido"

        try:
            printer_info = win32print.GetPrinter(printer[0], 2)
            port_name = printer_info.get('pPortName', "Desconhecida")
        except Exception:
            if printer[1]:
                port_name = printer[1]
            else:
                port_name = "Desconhecida"

        if any(keyword in port_name.lower() for keyword in ["pdf", "xps", "onenote", "fax"]):
            tipo = "Virtual"
        elif "\\\\" in printer_name or "network" in printer_name.lower() or "\\" in port_name:
            tipo = "Física (Rede)"
        else:
            tipo = "Física (Local)"

        impressoras.append({
            "Nome": printer_name,
            "Porta": port_name,
            "Tipo": tipo
        })

    return impressoras

def obter_impressoras_virtuais():
    """
    Retorna uma lista com os nomes de todas as impressoras virtuais encontradas.
    """
    impressoras = listar_impressoras()
    impressoras_virtuais = [
        impressora["Nome"] for impressora in impressoras if impressora["Tipo"] == "Virtual"
    ]
    return impressoras_virtuais

def comparar_impressoras(nome_impressora):
    """
    Compara o nome de uma impressora com a lista de impressoras virtuais.

    :param nome_impressora: Nome da impressora a ser comparada (string).
    :return: True se a impressora for virtual, False caso contrário.
    """
    # Obtém a lista de impressoras virtuais
    impressoras_virtuais = obter_impressoras_virtuais()
    # Remove espaços extras e realiza a comparação
    nome_impressora = nome_impressora.strip()
    if nome_impressora in impressoras_virtuais:
        return True
    else:
        return False
