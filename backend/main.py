from fastapi import FastAPI
from src import router

app = FastAPI()
app.include_router(router.router)
