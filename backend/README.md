# Backend

## Configuración local

1. Copia `.env.example` a `.env` y actualiza `DATABASE_URL` con las credenciales de PostgreSQL.
2. Sustituye `SECRET_KEY` por un secreto aleatorio. Puedes generarlo con `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
3. Crea un entorno e instala las dependencias: `python -m venv .venv` y `.venv\Scripts\python.exe -m pip install -r requirements.txt`.
4. Desde esta carpeta, inicia el servidor con `.venv\Scripts\python.exe -m uvicorn app.main:app --reload`.
5. Abre `http://127.0.0.1:8000/` para iniciar sesión.

En producción configura `COOKIE_SECURE=true` y sirve la aplicación únicamente mediante HTTPS. La expiración del JWT se controla con `ACCESS_TOKEN_EXPIRE_MINUTES`.

La tabla `sesiones_activas` se crea al iniciar la aplicación. La tabla existente `usuarios` conserva sus columnas actuales.