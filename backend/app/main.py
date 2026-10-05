from pathlib import Path

from fastapi import Depends, FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.auth.router import router as auth_router
from app.auth.router import SesionAutenticada, get_current_session
from app.sedes.router import router as sedes_router
from app.usuarios.router import router as usuarios_router
from app.core.database import Base, engine

# Importar todos los modelos para que se creen las tablas
from app.auth.models import SesionActiva  # noqa: F401
from app.sedes.models import Sede, Mesa  # noqa: F401
from app.usuarios.models import Usuario, UsuarioSede  # noqa: F401

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema Refugio Gestión")
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")

app.include_router(auth_router)
app.include_router(sedes_router)
app.include_router(usuarios_router)


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
    return RedirectResponse(url="/login", status_code=303)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={},
    )


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    session: SesionAutenticada = Depends(get_current_session),
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "email": session.usuario.email,
            "expires_at": session.expires_at,
        },
    )