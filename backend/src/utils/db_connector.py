import os
from sqlalchemy import Table, create_engine, MetaData
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv


load_dotenv()
CONFIG: dict = {
    'DB_ADDRESS': os.getenv('DB_ADDRESS'),
    'DB_USER': os.getenv('DB_USER'),
    'DB_PASSWORD': os.getenv('DB_PASSWORD'),
    'DB_DATABASE': os.getenv('DB_DATABASE'),
}

class DBConnector:
    def __init__(self) -> None:
        try:
            self.db = create_engine(f"mariadb+pymysql://{CONFIG['DB_USER']}:{CONFIG['DB_PASSWORD']}@{CONFIG['DB_ADDRESS']}/{CONFIG['DB_DATABASE']}")
            self.metadata = MetaData()
        except Exception as error:
            print(f'Database Connection Error: {error}')
    
    def get_table(self, table_name: str):
        return Table(table_name, self.metadata, autoload_with=self.db)
            
    def fetch_all(self, query):
        with self.db.connect() as connection:
            trans = connection.begin()
            try:
                result = connection.execute(query)
                trans.commit()
                return result.fetchall()
            except SQLAlchemyError as e:
                trans.rollback()
                print(f"fetchall | Database Query Error: {e}")
                return []

    def query(self, query):
        with self.db.connect() as connection:
            trans = connection.begin()
            try:
                connection.execute(query)
                trans.commit()
                return True
            except SQLAlchemyError as e:
                trans.rollback()
                print(f"query | Database Query Error: {e}")
                return False
        
