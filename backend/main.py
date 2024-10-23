from typing import Union
from fastapi import FastAPI
from src.router import router

app = FastAPI()
app.include_router(router.router)


# 테스트용 예제 코드
@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

# app.include_router(LogController.router)