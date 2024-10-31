from typing import List
from fastapi import File, UploadFile
from src.decorator import controller, get, post
from src.service import HotelService


@controller('/hotel')
class HotelController:
    def __init__(self) -> None:
        self.hotel_service = HotelService()

    @get('/order')
    async def order(self, start_date: str, end_date: str):
        return {}

    @get('/list')
    def list(self) -> List[dict]:
        hotel_list = self.hotel_service.get_hotel_list()
        return hotel_list

    @post('/upload_csv')
    async def upload_csv(self, hotel_seq: int, csv_file: UploadFile = File()):
        csv_content = await csv_file.read()
        response = await self.hotel_service.insert_hotel_data_from_csv(hotel_seq, csv_content)

        return response
