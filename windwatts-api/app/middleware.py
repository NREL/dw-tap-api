from fastapi import Request
import time
from app.logging_setup import logger

async def log_requests(request: Request, call_next):
    start_time = time.time()
    body = await request.body()
    logger.info(f"➡️ REQUEST: {request.method} {request.url} | Body: {body.decode() or 'No Body'}")
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"⬅️ RESPONSE: {request.method} {request.url} | Status: {response.status_code} | Time: {process_time:.2f}s")
    return response
