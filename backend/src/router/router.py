from fastapi import APIRouter
from src.controller import LogController, UserController

# 여기서 controller들 router 등록해야 함

router = APIRouter()
router.include_router(LogController.router)
router.include_router(UserController.router)