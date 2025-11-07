from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.v1.api import api_router
from app.core.exceptions import AppException


def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=400,  # Using 400 for business logic errors as a default
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
        )


app = FastAPI()

add_exception_handlers(app)

app.include_router(api_router, prefix="/api/v1")


@app.get("/healthz")
def health_check():
    return {"status": "ok"}
