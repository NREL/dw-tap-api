from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.controllers.random_controller import router as random_router
from app.controllers.wtk_data_controller import router as wtk_data_router
from app.controllers.era5_data_controller import router as era5_data_router

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

app.include_router(wtk_data_router, prefix="/wtk-data", tags=["wtk-database"])
app.include_router(era5_data_router, prefix="/era5-data", tags=["era5-database"])
app.include_router(random_router, prefix="/random", tags=["random"])

@app.get("/healthcheck")
def read_root():
    return {"status": "up"}

handler = Mangum(app)
