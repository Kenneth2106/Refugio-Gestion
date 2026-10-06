from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, RedirectResponse

from app.auth.router import router as auth_router
from app.auth.models import SesionActiva
from app.core.database import Base, engine
from app.core.settings import FRONTEND_URL
from app.sedes.models import Mesa, Sede
from app.sedes.router import router as sedes_router
from app.usuarios.models import Usuario, UsuarioSede
from app.usuarios.router import router as usuarios_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema Refugio Gestión")

app.include_router(auth_router)
app.include_router(usuarios_router)
app.include_router(sedes_router)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
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