import pymysql

# Configuração da conexão com o banco de dados MySQL remoto
host = '192.168.2.131'  # Altere para o IP ou nome do host do computador remoto
user = 'sysprint'  # Nome de usuário criado para acesso remoto
password = 'farti@2025'  # Senha do usuário
database = 'teste_rc'  # Nome do banco de dados

try:
    # Estabelece a conexão com o banco de dados
    connection = pymysql.connect(
        host=host,
        user=user,
        password=password,
        database=database,
        port=3306  # Porta padrão do MySQL
    )

    # Se a conexão for bem-sucedida
    print(f"Conexão estabelecida com sucesso no banco de dados '{database}'!")
    
    # Fechar a conexão após o teste
    connection.close()

except pymysql.MySQLError as e:
    # Se ocorrer algum erro de conexão
    print(f"Erro ao conectar ao MySQL: {e}")
