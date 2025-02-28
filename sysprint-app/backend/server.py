from flask import Flask, jsonify, request
from sqlalchemy import create_engine, text

app = Flask(__name__)

DB_URL = "mysql+pymysql://admin_user:admsysp%4025@192.168.1.226:3306/sysprint"
engine = create_engine(DB_URL)


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']
    # Aqui você validaria o login
    if username == "admin" and password == "password":  # Exemplo simples
        return jsonify({"sucess": True})
    else:
        return jsonify({"sucess": True})


@app.route('/dashboard-data', methods=['GET'])
def get_dashboard_data():
    try:
        with engine.connect() as connection:
            # Pegando a contagem de impressões por mês no ano atual
            query = text("""
                SELECT EXTRACT(MONTH FROM Time) AS month, COUNT(*) AS impressions
                FROM logs
                WHERE YEAR(Time) = YEAR(CURRENT_DATE())
                GROUP BY month
                ORDER BY month
            """)
            result = connection.execute(query)
            data = result.fetchall()

            # Criando um dicionário para mapear os meses com nomes
            month_map = {
                1: "Jan", 2: "Fev", 3: "Mar", 4: "Abr", 5: "Mai", 6: "Jun",
                7: "Jul", 8: "Ago", 9: "Set", 10: "Out", 11: "Nov", 12: "Dez"
            }

            # Formatando os dados para enviar ao frontend
            months = [month_map[row[0]] for row in data]  # Converte número do mês para nome
            impressions = [row[1] for row in data]  # Número de impressões por mês

        return jsonify({"months": months, "impressions": impressions})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/sector-data', methods=['GET'])
def get_sector_data():
    try:
        with engine.connect() as connection:
            # Pegando a contagem de impressões por setor
            query = text("""
                SELECT u.Department, COUNT(*) AS impressions
                FROM logs l
                JOIN users u ON l.User = u.User
                GROUP BY u.Department
            """)
            result = connection.execute(query)
            data = result.fetchall()

            # Formatando os dados para enviar ao frontend
            sectors = [row[0] for row in data]  # Departamentos
            impressions = [row[1] for row in data]  # Número de impressões por setor

        return jsonify({"sectors": sectors, "impressions": impressions})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
