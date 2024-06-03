import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from config.logger import logger

load_dotenv()

MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_PORT = int(os.getenv('MYSQL_PORT'))
MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')


class MySQLConnection:
    def __init__(self):
        try:
            self.engine = create_engine(
                f"mysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@"
                f"{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
            )
            Session = sessionmaker(bind=self.engine)
            self.session = Session()

        except Exception as e:
            logger.log("error", f"Erro ao conectar com o banco de dados. {e}")


    def get_session(self):
        return self.session


    def close_connection(self):
        self.session.close()


    def get_database(self):
        return MYSQL_DATABASE
    
    
    def get_connection(self):
        return self.engine.connect()


    def return_dict(self, obj):
        return {col.name: getattr(obj, col.name) for col in obj.__table__.columns}


    def execute_select_query(self, query):
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))
                results = result.fetchall()
                return results
        except Exception as e:
            logger.log("error", f"Erro ao executar query de select. {e}")
            return []


    def execute_single_select_query(self, query):
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query))
                results = result.fetchone()
                return results
        except Exception as e:
            logger.log("error", f"Erro ao executar query de select. {e}")
            return []
    

    def get_mapping(self):
        query = """
            SELECT 
            	cl.id, 
                CONCAT(cl.nome, ' ', cl.sobrenome) nome, 
                re.nome, 
                en.latitude, 
                en.longitude, 
                en.bairro,
                en.cidade
            FROM home_sentinel.cliente cl
                JOIN home_sentinel.residencia re ON re.cliente_id = cl.id
            	JOIN home_sentinel.endereco en ON en.residencia_id = re.id
            ORDER BY cl.id;"""
        
        return self.execute_select_query(query)
    
    def get_login(self, email, senha):
        query = f"""
            SELECT id, nome, email
            FROM home_sentinel.usuario
            WHERE email = '{email}' AND senha = MD5('{senha}');
        """
                
        result = self.execute_single_select_query(query)

        if result:
            return result
        else:
            return None