from datetime import date
from typing import List
from fastapi import File, UploadFile
from src.decorator import controller, get, post
from src.service import HotelService


@controller('/hotel')
class HotelController:
    def __init__(self) -> None:
        self.hotel_service = HotelService()

    @get('/order')
    def order(self, start_date: date, end_date: date) -> List[dict]:
        hotel_order_list = self.hotel_service.get_hotel_order_list(
            start_date=start_date,
            end_date=end_date
        )

        return hotel_order_list

    @get('/list')
    def list(self) -> List[dict]:
        hotel_list = self.hotel_service.get_hotel_list()
        return hotel_list

    @post('/upload_csv')
    async def upload_csv(self, hotel_seq: int, csv_file: UploadFile = File()) -> bool:
        csv_content = await csv_file.read()
        response = await self.hotel_service.insert_hotel_data_from_csv(hotel_seq, csv_content)

        return response
