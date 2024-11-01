from datetime import date
import pandas as pd
import io
import json
from src.utils import DBConnector
from src.repository import HotelRepository


class HotelService:
    def __init__(self) -> None:
        try:
            self.repository = HotelRepository(db_connector=DBConnector())
        except Exception as error:
            print(f'Database Connection Error: {error}')

    def get_hotel_order_list(self, start_date: date, end_date: date):
        query_result = self.repository.get_hotel_order_list(start_date=start_date, end_date=end_date)
        return  [dict(row._mapping) for row in query_result]

    def get_hotel_list(self):
        query_result = self.repository.get_hotel_list()
        return [dict(row._mapping) for row in query_result]

    async def insert_hotel_data_from_csv(self, hotel_seq: int, csv_content: bytes):
        csv_reader = io.StringIO(csv_content.decode('utf-8'))
        csv_reader.seek(0)

        df = pd.read_csv(csv_reader)

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

                self.repository.insert_hotel_data(row_dict=row_dict)

            return True
        except Exception as e:
            print(f'insert_hotel_data_from_csv | Error: {e}')
            return False
