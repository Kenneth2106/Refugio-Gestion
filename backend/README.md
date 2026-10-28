# Backend

## Configuración local

1. Copia `.env.example` a `.env` y actualiza `DATABASE_URL` con las credenciales de PostgreSQL.
2. Sustituye `SECRET_KEY` por un secreto aleatorio. Puedes generarlo con `python -c "import secrets; print(secrets.token_urlsafe(48))"`.
3. Crea un entorno e instala las dependencias: `python -m venv .venv` y `.venv\Scripts\python.exe -m pip install -r requirements.txt`.
4. Desde esta carpeta, inicia el servidor con `.venv\Scripts\python.exe -m uvicorn app.main:app --reload`.
5. Abre `http://127.0.0.1:8000/` para iniciar sesión.

Si ya tenías creado el entorno virtual, vuelve a instalar las dependencias
después de actualizar el proyecto con
`.venv\Scripts\python.exe -m pip install -r requirements.txt`.

En producción configura `COOKIE_SECURE=true` y sirve la aplicación únicamente mediante HTTPS. La duración de las sesiones se configura con `SESSION_INACTIVITY_MINUTES` y `SESSION_MAX_MINUTES`.

La tabla `sesiones_activas` se crea al iniciar la aplicación. La tabla existente `usuarios` conserva sus columnas actuales.

## Despliegue en Vercel con Neon

- Crea el proyecto backend con `backend` como **Root Directory**. Vercel detecta FastAPI desde `app/main.py` y las dependencias desde `requirements.txt`.
- Configura las variables del backend en Vercel:
  - `DATABASE_URL`: cadena **pooled** de Neon para las peticiones de la aplicación.
  - `SECRET_KEY`: secreto aleatorio de al menos 32 bytes; no uses `JWT_SECRET`.
  - `FRONTEND_URL`: URL pública final del frontend.
  - `COOKIE_SECURE`: `true`.
- Vercel establece `VERCEL=1`; en ese entorno el motor SQLAlchemy usa `NullPool` para no conservar conexiones entre invocaciones.
- El frontend usa rutas de API relativas y cookies `SameSite=Lax`. Para mantenerlas, configura rewrites del proyecto frontend hacia el dominio del backend después del primer despliegue. No se requiere `ALLOWED_ORIGINS` mientras todas las llamadas pasen por ese proxy del mismo dominio.
- Neon ya contiene datos y una revisión Alembic `0003_caja_reportes_auditoria`; no restaures un dump encima. Ejecuta `alembic upgrade head` contra Neon solo si una migración posterior lo requiere, usando la cadena **directa** desde un entorno administrativo, nunca desde la función de Vercel.

## Caja y reportes (Sprints 5 y 6)

Aplica las migraciones antes de iniciar la versión nueva:
`python -m alembic upgrade head`.

- `GET /caja/pedidos-pendientes` lista pedidos abiertos de la sede seleccionada.
- `POST /caja/pedidos/{id}/pago` registra `EFECTIVO` o `TARJETA` y cierra el
  pedido por su total calculado; `GET /caja/pedidos/{id}/factura` consulta el
  comprobante.
- `GET /reportes/ventas` muestra únicamente pedidos cerrados y acepta `fecha_fin`
  (filtra el día de cierre en `America/Bogota`), `sede_id` y `medio_pago`.
  `GET /reportes/ventas/excel` exporta el mismo resultado filtrado. Ambas rutas
  comprueban rol y sedes autorizadas en backend.

Los precios de compra y venta, así como el código y nombre del producto, se
conservan como datos históricos en cada línea de pedido. Para ejecutar las
pruebas desde esta carpeta: `python -m pytest`.