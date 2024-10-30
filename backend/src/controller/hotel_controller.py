from fastapi import File, UploadFile
from src.decorator import controller, get


# 참고용 controller 
@controller('/hotel')
class HotelController:

    @get('/order')
    async def order(self, start_date: str, end_date: str):
        return {}

    @get('/list')
    async def list(self):
        return {}
        
    @get('/upload_csv')
    async def upload_csv(self, file: UploadFile):
        return {}
