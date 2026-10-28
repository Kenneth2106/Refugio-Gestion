# Refugio Gestión

Aplicación web para la gestión de El Refugio Bar. El frontend está hecho con
HTML, CSS y JavaScript; consume la API REST de FastAPI. La base de datos es
PostgreSQL y su estructura se administra con Alembic.

## Documentación del proyecto

- [Flujo funcional actual y roadmap](docs/FLUJO_Y_ROADMAP.md)
- [Alcance aprobado de Sprints 1 a 4](docs/alcance_sprint_1_4.md)
- [Matriz de verificación y resultados](docs/VERIFICACION_SPRINT_1_4.md)

## Requisitos

- Windows 10/11 (los comandos de esta guía usan PowerShell).
- Python 3.11 o posterior.
- Node.js y npm compatibles con Vite 8.
- PostgreSQL instalado y en ejecución.
- El código fuente del proyecto.

## Preparar PostgreSQL

Crea una base de datos vacía llamada `refugio_db` (por ejemplo, desde pgAdmin o
con `createdb refugio_db`). Asegúrate de tener un usuario de PostgreSQL con
permisos para conectarse y crear tablas.

No es necesario crear las tablas manualmente: se crearán con las migraciones
de Alembic en el paso siguiente. No ejecutes esta guía sobre una base con datos
que quieras conservar: las instrucciones para una base nueva no migran ni
respaldan datos de otra instalación.

## Configurar y ejecutar el backend

Abre PowerShell en la carpeta `backend`:

```powershell
cd ruta\al\proyecto\backend
```

1. Crea un entorno virtual e instala las dependencias:

   ```powershell
   py -3.11 -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

2. Crea tu archivo local de configuración y edítalo:

   ```powershell
   Copy-Item .env.example .env
   notepad .env
   ```

   Configura al menos estos valores en `backend\.env`:

   ```dotenv
   DATABASE_URL=postgresql+psycopg://USUARIO:CONTRASENA@localhost:5432/refugio_db
   SECRET_KEY=REEMPLAZAR_POR_UN_SECRETO_ALEATORIO_DE_AL_MENOS_32_BYTES
   SESSION_INACTIVITY_MINUTES=3
   SESSION_MAX_MINUTES=30
   COOKIE_SECURE=false
   FRONTEND_URL=http://127.0.0.1:5175
   ```

   Sustituye `USUARIO` y `CONTRASENA` por las credenciales de PostgreSQL. Si la
   contraseña contiene caracteres especiales, codifícala para URL. Genera un
   secreto JWT aleatorio con:

   ```powershell
   .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

   Pega el resultado como `SECRET_KEY`. No compartas ni subas `backend\.env` al
   repositorio.

3. Aplica las migraciones a la base configurada:

   ```powershell
   .\.venv\Scripts\python.exe -m alembic upgrade head
   ```

4. Inicia el backend y deja esta terminal abierta:

   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
   ```

   La API estará disponible en `http://127.0.0.1:8000` y su documentación
   interactiva en `http://127.0.0.1:8000/docs`.

## Crear el primer administrador en una base nueva

Las migraciones crean el esquema, pero **no crean cuentas de usuario**. Para
una instalación nueva, crea la primera cuenta administradora una sola vez con
el siguiente comando, desde la carpeta `backend`, en otra ventana de
PowerShell. Te pedirá la contraseña sin mostrarla en pantalla y la guardará
con bcrypt:

```powershell
@'
from getpass import getpass
from pydantic import EmailStr, TypeAdapter
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.usuarios.models import Usuario

identificacion = input("Identificacion: ").strip()
nombre = input("Nombre completo: ").strip()
nombre_usuario = input("Nombre de usuario: ").strip().lower()
email = str(TypeAdapter(EmailStr).validate_python(input("Correo electronico: ").strip()))
password = getpass("Contrasena (8 a 72 bytes): ")
if len(password.encode("utf-8")) < 8 or len(password.encode("utf-8")) > 72:
    raise SystemExit("La contrasena debe tener entre 8 y 72 bytes.")
if password != getpass("Confirma la contrasena: "):
    raise SystemExit("Las contrasenas no coinciden.")

db = SessionLocal()
try:
    usuario = Usuario(
        identificacion=identificacion,
        nombre=nombre,
        nombre_usuario=nombre_usuario,
        email=email,
        hashed_password=get_password_hash(password),
        estado=True,
        es_admin=True,
        es_mesero=True,
        es_cajero=True,
    )
    db.add(usuario)
    db.commit()
    print("Administrador creado.")
finally:
    db.close()
'@ | .\.venv\Scripts\python.exe -
```

Ejecuta este procedimiento únicamente cuando no exista ya el administrador
inicial. Si falla por un dato duplicado, revisa las cuentas existentes antes
de volver a intentarlo. Conserva la contraseña de forma segura: no se puede
recuperar desde el hash almacenado.

La base `refugio_db` ya preparada para esta instalación tiene la migración
aplicada y el usuario `kenneth` creado; no repitas el procedimiento anterior
en esa base.

## Configurar y ejecutar el frontend

Abre una segunda ventana de PowerShell en la carpeta `frontend`:

```powershell
cd ruta\al\proyecto\frontend
npm install
npm run dev
```

Abre `http://127.0.0.1:5175` en el navegador. Mantén abiertas las dos
terminales (backend y frontend) mientras usas la aplicación. El servidor de
desarrollo del frontend reenvía las peticiones de la API al backend en el
puerto `8000`.

## Detener los servicios

En cada terminal, presiona `Ctrl+C`. Para volver a iniciar, repite los
comandos de Uvicorn y Vite; no es necesario reinstalar dependencias ni volver
a aplicar migraciones si no hubo cambios.
