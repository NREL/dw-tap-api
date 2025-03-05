from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.controllers.random_controller import router as random_router
from app.controllers.wind_data_controller import router as wind_data_router

app = FastAPI()

origins = [
    "http://localhost",
    "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(wind_data_router, prefix="/wtk-data", tags=["wtk-database"])
app.include_router(random_router, prefix="/random", tags=["random"])

@app.get("/healthcheck")
def read_root():
    return {"status": "up"}

handler = Mangum(app)
