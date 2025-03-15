from flask import Flask, jsonify, request
from sqlalchemy import create_engine, table, text

app = Flask(__name__)

DB_URL = "mysql+pymysql://admin_user:admsysp%4025@192.168.1.226:3306/sysprint"
engine = create_engine(DB_URL)


# Tela de login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data["username"]
    password = data["password"]
    # Aqui você validaria o login
    if username == "admin" and password == "password":  # Exemplo simples
        return jsonify({"sucess": True})
    else:
        return jsonify({"sucess": True})


# Gráficos do dashboard
@app.route("/dashboard-data", methods=["GET"])
def get_dashboard_data():
    try:
        with engine.connect() as connection:
            # Pegando a contagem de impressões por mês no ano atual
            query = text(
                """
                SELECT EXTRACT(MONTH FROM Time) AS month, COUNT(*) AS impressions
                FROM logs
                WHERE YEAR(Time) = YEAR(CURRENT_DATE())
                GROUP BY month
                ORDER BY month
            """
            )
            result = connection.execute(query)
            data = result.fetchall()

            month_map = {
                1: "Jan",
                2: "Fev",
                3: "Mar",
                4: "Abr",
                5: "Mai",
                6: "Jun",
                7: "Jul",
                8: "Ago",
                9: "Set",
                10: "Out",
                11: "Nov",
                12: "Dez",
            }

            months = [month_map[row[0]] for row in data]
            impressions = [row[1] for row in data]

        return jsonify({"months": months, "impressions": impressions})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/sector-data", methods=["GET"])
def get_sector_data():
    try:
        with engine.connect() as connection:
            query = text(
                """
                SELECT u.Department, COUNT(*) AS impressions
                FROM logs l
                JOIN users u ON l.User = u.User
                GROUP BY u.Department
            """
            )
            result = connection.execute(query)
            data = result.fetchall()

            sectors = [row[0] for row in data]
            impressions = [row[1] for row in data]

        return jsonify({"sectors": sectors, "impressions": impressions})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Tabela de usuários
@app.route("/users-data", methods=["GET"])
def get_users_data():
    try:
        with engine.connect() as connection:
            query = text(
                """
                SELECT User, TotalPages, PrintLimit, Blocked, Department
                FROM users
                """
            )
            result = connection.execute(query)
            data = result.fetchall()

            users = [
                {
                    "user": row[0],
                    "total_pages": row[1],
                    "print_limit": row[2],
                    "blocked": row[3],
                    "department": row[4],
                }
                for row in data
            ]

        return jsonify(users)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Tabela de logs
@app.route("/logs-data", methods=["GET"])
def get_logs_data():
    try:
        with engine.connect() as connection:
            query = text(
                """
                SELECT Time, User, Pages, Copies, Printer, DocumentName, Client, PaperSize, Language, Duplex, Grayscale, Size
                FROM logs
                """
            )
            result = connection.execute(query)
            data = result.fetchall()

            logs = [
                {
                    "time": row[0],
                    "user": row[1],
                    "pages": row[2],
                    "copies": row[3],
                    "printer": row[4],
                    "documentname": row[5],
                    "client": row[6],
                    "papersize": row[7],
                    "language": row[8],
                    "duplex": row[9],
                    "grayscale": row[10],
                    "size": row[11],
                }
                for row in data
            ]

        return jsonify(logs)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/printers-data", methods=["GET"])
def get_printets_data():
    try:
        with engine.connect() as connection:
            query = text(
                """
                SELECT id_impressora, num_serie, modelo, departamento
                FROM impressoras
                """
            )
            result = connection.execute(query)
            data = result.fetchall()

            printers = [
                {
                    "id_impressora": row[0],
                    "num_serie": row[1],
                    "modelo": row[2],
                    "departamento": row[3],
                }
                for row in data
            ]

        return jsonify(printers)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Tabela de departamentos
@app.route("/departments-data", methods=["GET"])
def get_departments_data():
    try:
        with engine.connect() as connection:
            query = text(
                """
                SELECT id_departamento, nome
                FROM departamentos
                """
            )
            result = connection.execute(query)
            data = result.fetchall()

            departments = [
                {
                    "id_departamento": row[0],
                    "nome": row[1],
                }
                for row in data
            ]

        return jsonify(departments)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
