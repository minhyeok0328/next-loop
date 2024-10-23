from fastapi import APIRouter
from src.controller import LogController

# 여기서 controller들 다 등록해야 함

router = APIRouter()
router.include_router(LogController.router)