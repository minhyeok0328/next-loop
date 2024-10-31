from sqlalchemy import insert, select
from src.utils import DBConnector

class HotelRepository:
    def __init__(self, db_connector: DBConnector):
        self.db_connector = db_connector
        self.hotel_order_table = self.db_connector.get_table('hotel_order')
        self.hotel_list_table = self.db_connector.get_table('hotel_list')

    def get_hotel_order_list(self, start_date, end_date):
        hotel_order_query = select(self.hotel_order_table).where(
            self.hotel_order_table.c.check_out.between(start_date, end_date)
        ).order_by(self.hotel_order_table.c.check_out.desc())
        return self.db_connector.fetch_all(hotel_order_query)

    def get_hotel_list(self):
        hotel_list_query = select(self.hotel_list_table).order_by(self.hotel_list_table.c.hotel_name.desc())
        return self.db_connector.fetch_all(hotel_list_query)

    def insert_hotel_data(self, row_dict):
        insert_query = insert(self.hotel_order_table).values(**row_dict)
        return self.db_connector.query(insert_query)
