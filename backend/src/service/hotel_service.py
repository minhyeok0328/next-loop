import pandas as pd
import io
import json
from sqlalchemy import Table, create_engine, MetaData, insert
from sqlalchemy.exc import SQLAlchemyError


DB: dict = {
    'address': '192.168.0.9',
    'user': 'next-loop',
    'password': '1234',
    'database': 'next-loop'
}

class HotelService:
    def __init__(self) -> None:
        try:
            self.db = create_engine(f"mariadb+pymysql://{DB['user']}:{DB['password']}@{DB['address']}/{DB['database']}")
            self.metadata = MetaData()
            self.hotel_order_table = Table('hotel_order', self.metadata, autoload_with=self.db)
        except Exception as error:
            print('Database Connection Error:')
            print(error)

    async def insert_hotel_data_from_csv(self, hotel_seq: int, csv_content: bytes):
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

                    # 기존 order_seq는 다른 호텔의 order_seq와 중복될 수 있기 때문에 제거
                    del row_dict['order_seq']

                    row_dict = {k: (None if v == '\\N' else v) for k, v in row_dict.items()}

                    if 'contents' in row_dict and isinstance(row_dict['contents'], dict):
                        row_dict['contents'] = json.dumps(row_dict['contents'])

                    insert_query = insert(self.hotel_order_table).values(**row_dict)
                    connection.execute(insert_query)

                trans.commit()
            except SQLAlchemyError as e:
                trans.rollback()
                print(f"insert_hotel_data_from_csv | Database Query Error: {e}")
                return False

        return True
