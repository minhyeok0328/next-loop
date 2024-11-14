from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
from src import router

app = FastAPI()
app.include_router(router.router)

# Prometheus metrics setup
Instrumentator().instrument(app).expose(app)