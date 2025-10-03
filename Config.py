import mysql.connector
from mysql.connector import Error

class ConfigBanco:
    _modo = "produção"

    @staticmethod
    def usar_banco_producao():
        ConfigBanco._modo = "produção"

    @staticmethod
    def usar_banco_teste():
        ConfigBanco._modo = "teste"

    @staticmethod
    def banco_atual():
        return "Produção" if ConfigBanco._modo == "produção" else "Teste"

    @staticmethod
    def obter_conexao():
        try:
            if ConfigBanco._modo == "produção":
                return mysql.connector.connect(
                    host='10.233.43.215',
                    user='troadmin',
                    password='eleTROn1c_flop3#W!w',
                    database='site_eletronicaX',
                    charset='utf8mb4',
                    connection_timeout=30
                )
            else:
                return mysql.connector.connect(
                    host='10.233.43.215',
                    user='troadmin',
                    password='eleTROn1c_flop3#W!w',
                    database='site_eletronicaX_teste',
                    charset='utf8mb4',
                    connection_timeout=30
                )
        except Error as e:
            print(f"Erro ao conectar ao banco: {e}")
            return None
