import mysql.connector
from datetime import datetime


def conexao_banco():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sysprintdb",
        database="logs_impressoras",
    )


def verificar_e_gerenciar_limite(conn, user):
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT `Max Prints`, `End Date`, (
            SELECT COUNT(*) FROM print_logs
            WHERE `User` = %s
        ) AS `Total Prints`
        FROM print_limits
        WHERE `User` = %s;
    """
    cursor.execute(query, (user, user))
    result = cursor.fetchone()

    if not result:
        print(
            f"Adicionando usuário {user} na tabela print_limits"
            "com o limite padrão de impressões"
        )
        insert_query = """
            INSERT INTO print_limits (
            `User`,
            `Max Prints`,
            `Start Date`,
            `End Date`,
            `Last Reset Date`
            )
            VALUES (
            %s, %s, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 1 MONTH), CURDATE()
            )
        """
        cursor.execute(insert_query, (user, 10))
        conn.commit()
        print(f"Limite de impressões adicionado para {user}.")
        return True

    print(f"Verificando limite para {user}...")
    current_date = datetime.now().date()
    end_date = result["End Date"]

    print(f"\nLimite máximo de impressões: {result['Max Prints']}")
    print(f"Impressões totais feitas até o momento: {result['Total Prints']}")
    print(f"Data final para o limite de impressões: {end_date}")

    if current_date >= end_date:
        print(f"Resetando limite de impressões para {user}.")
        reset_query = """
            UPDATE print_limits
            SET `Start Date` = CURDATE(),
                `End Date` = DATE_ADD(CURDATE(), INTERVAL 1 MONTH)
                `Last Reset Date` = CURDATE()
            WHERE `User` %s;
        """
        cursor.execute(reset_query, (user,))
        conn.commit()
        print(f"O limite de impressões para {user} foi resetado.")
        return True

    max_prints = result["Max Prints"]
    total_prints = result["Total Prints"]
    print(f"Limite de impressões para {user}: {max_prints}")
    print(f"Total de impressões feitas: {total_prints}")
    return total_prints < max_prints


def inserir_dados(conn, df):
    cursor = conn.cursor()

    query = (
        "INSERT INTO print_logs (`Time`, `User`, `Pages`, `Copies`, "
        "`Printer`, `Document Name`, `Client`, `Paper Size`, `Language`, "
        "`Duplex`, `Grayscale`, `Size`) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )

    check_query = "SELECT COUNT(*) FROM print_logs WHERE `Time` = %s AND `User` = %s"

    for _, row in df.iterrows():
        data = (
            row["Time"],
            row["User"],
            row["Pages"],
            row["Copies"],
            row["Printer"],
            row["Document Name"],
            row["Client"],
            row["Paper Size"],
            row["Language"],
            row["Duplex"],
            row["Grayscale"],
            row["Size"],
        )

        print(f"\nVerificando impressões para {row['User']}...")

        if not verificar_e_gerenciar_limite(conn, row["User"]):
            print(f"\nUsuário {row['User']} atingiu o limite de impressões.")
            continue

        cursor.execute(check_query, (row["Time"], row["User"]))
        result = cursor.fetchone()

        if result[0] == 0:
            print(f"\nInserindo no banco de dados: {data}")
            cursor.execute(query, data)
        else:
            print(f"\nRegistro já existente no banco de dados:\n{data}")

    conn.commit()
    print("\nDados inseridos no banco.")
