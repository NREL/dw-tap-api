from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
from app.controllers.random_controller import router as random_router
from app.controllers.wtk_data_controller import router as wtk_data_router
from app.controllers.era5_data_controller import router as era5_data_router
from app.middleware import AuditMiddleware, LoggingMiddleware
from app.exception_handlers import log_unhandled_exceptions, log_validation_errors
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="WindWatts API")

app.add_middleware(LoggingMiddleware)  # Logging middleware first
app.add_middleware(AuditMiddleware)    # Audit middleware second

app.add_exception_handler(Exception, log_unhandled_exceptions)
app.add_exception_handler(RequestValidationError, log_validation_errors)

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

app.include_router(wtk_data_router, prefix="/wtk", tags=["wtk-data"])
app.include_router(era5_data_router, prefix="/era5", tags=["era5-data"])
app.include_router(random_router, prefix="/random", tags=["random"])

@app.get("/healthcheck")
def read_root():
    return {"status": "up"}

handler = Mangum(app)
