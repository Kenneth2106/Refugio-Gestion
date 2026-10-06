import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse

from app.auth.router import router as auth_router
from app.admin.router import router as admin_router
from app.catalogo.router import router as catalogo_router
from app.core.settings import FRONTEND_URL
from app.inventario.router import router as inventario_router
from app.sedes.router import router as sedes_router
from app.usuarios.router import router as usuarios_router
from app.ventas.router import router as ventas_router

logger = logging.getLogger(__name__)

app = FastAPI(title="Sistema Refugio Gestión")

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(usuarios_router)
app.include_router(sedes_router)
app.include_router(catalogo_router)
app.include_router(inventario_router)
app.include_router(ventas_router)


# No expone excepciones internas al cliente ni registra tokens o contraseñas.
@app.exception_handler(Exception)
async def unexpected_error_handler(
    _request: Request,
    _exc: Exception,
) -> JSONResponse:
    logger.error("Unhandled application error")
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"},
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    # Omite valores enviados y sanea los mensajes de campos de contraseña.
    sanitized_errors = []
    for error in exc.errors():
        safe_error = dict(error)
        safe_error.pop("input", None)
        location = safe_error.get("loc", ())
        if "password" in location:
            safe_error.pop("ctx", None)
            safe_error["msg"] = "Campo de contraseña inválido"
        sanitized_errors.append(safe_error)
    return JSONResponse(status_code=422, content={"detail": sanitized_errors})


@app.get("/")
def home() -> RedirectResponse:
    return RedirectResponse(url=f"{FRONTEND_URL}/login", status_code=303)


@app.get("/login")
def login_page() -> RedirectResponse:
    return RedirectResponse(url=f"{FRONTEND_URL}/login", status_code=307)


@app.get("/dashboard")
def dashboard() -> RedirectResponse:
    return RedirectResponse(url=f"{FRONTEND_URL}/dashboard", status_code=307)