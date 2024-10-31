from datetime import date
import os
import pandas as pd
import io
import json
from sqlalchemy import Table, create_engine, MetaData, insert, select
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv


load_dotenv()
CONFIG: dict = {
    'DB_ADDRESS': os.getenv('DB_ADDRESS'),
    'DB_USER': os.getenv('DB_USER'),
    'DB_PASSWORD': os.getenv('DB_PASSWORD'),
    'DB_DATABASE': os.getenv('DB_DATABASE'),
}

class HotelService:
    def __init__(self) -> None:
        try:
            self.db = create_engine(f"mariadb+pymysql://{CONFIG['DB_USER']}:{CONFIG['DB_PASSWORD']}@{CONFIG['DB_ADDRESS']}/{CONFIG['DB_DATABASE']}")
            self.metadata = MetaData()
            self.hotel_order_table = Table('hotel_order', self.metadata, autoload_with=self.db)
            self.hotel_list_table = Table('hotel_list', self.metadata, autoload_with=self.db)
        except Exception as error:
            print(f'Database Connection Error: {error}')
            
    def get_hotel_order_list(self, start_date: date, end_date: date):
        with self.db.connect() as connection:
            try:
                trans = connection.begin()

                hotel_order_query = select(self.hotel_order_table).where(
                    self.hotel_order_table.c.check_out.between(start_date, end_date)
                ).order_by(self.hotel_order_table.c.check_out.desc())

                response = [dict(row._mapping) for row in connection.execute(hotel_order_query).fetchall()]

                trans.commit()
                return response
            except SQLAlchemyError as e:
                print(f"get_hotel_order_list | Database Query Error: {e}")
                trans.rollback()
                return []

    def get_hotel_list(self):
        with self.db.connect() as connection:
            try:
                trans = connection.begin()

                hotel_list_query = select(self.hotel_list_table).order_by(self.hotel_list_table.c.hotel_name.desc())
                response = connection.execute(hotel_list_query).fetchall()
                hotel_list = [dict(row._mapping) for row in response]

                trans.commit()
                return hotel_list
            except SQLAlchemyError as e:
                print(f"get_hotel_list | Database Query Error: {e}")
                trans.rollback()
                return []

    def insert_hotel_data_from_csv(self, hotel_seq: int, csv_content: bytes):
        csv_reader = io.StringIO(csv_content.decode('utf-8'))
        csv_reader.seek(0)

        df = pd.read_csv(csv_reader)

        with self.db.connect() as connection:
            trans = connection.begin()
            try:
                for _, row in df.iterrows():
                    row_dict = row.to_dict()

                    # 어떤 호텔의 주문 데이터 인지 구분할 수 있는 값이 없어서 임의로 추가한 값
                    # mariadb/init.sql의 hotel_list table 참고
                    row_dict['hotel_seq'] = hotel_seq

                    # 기존 csv 파일에 있는 order_seq는 다른 csv 파일의 order_seq와 중복될 수 있기 때문에 제거
                    del row_dict['order_seq']

                    row_dict = {k: (None if v == '\\N' else v) for k, v in row_dict.items()}

                    if 'contents' in row_dict and isinstance(row_dict['contents'], dict):
                        row_dict['contents'] = json.dumps(row_dict['contents'])

                    insert_query = insert(self.hotel_order_table).values(**row_dict)
                    connection.execute(insert_query)

                trans.commit()
                return True
            except SQLAlchemyError as e:
                trans.rollback()
                print(f"insert_hotel_data_from_csv | Database Query Error: {e}")
                return False
