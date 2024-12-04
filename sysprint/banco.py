import mysql.connector


def conexao_banco():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sysprintdb",
        database="logs_impressoras",
    )


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

        cursor.execute(check_query, (row["Time"], row["User"]))
        result = cursor.fetchone()

        if result[0] == 0:
            print(f"\nInserindo no banco de dados: {data}")
            cursor.execute(query, data)
        else:
            print(f"\nRegistro já existente no banco de dados:\n{data}")

    conn.commit()
