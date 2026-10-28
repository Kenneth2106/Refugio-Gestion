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

## Despliegue en Render con Neon

El backend es un Web Service con `backend` como raíz, el comando de inicio
`uvicorn app.main:app --host 0.0.0.0 --port $PORT` y las dependencias de
`requirements.txt`. Configura estas variables en Render:

- `DATABASE_URL`: URL pooled de Neon.
- `SECRET_KEY`: secreto aleatorio de al menos 32 bytes.
- `COOKIE_SECURE=true` y `COOKIE_SAMESITE=none` para permitir la sesión segura
  entre los dominios separados del frontend y el backend.
- `FRONTEND_URL`: URL pública del frontend.
- `ALLOWED_ORIGINS`: origen exacto del frontend, sin ruta ni barra final.

El frontend se publica como Static Site con raíz `frontend`, comando de build
`npm install && npm run build` y directorio de publicación `dist`. Define
`VITE_API_URL=https://refugio-gestion.onrender.com` en su entorno de build antes
de desplegar o volver a desplegar. Vite incorpora esta variable durante el
build. El código también acepta `VITE_API_BASE_URL` por compatibilidad, conserva
el proxy de Vite en desarrollo y usa el backend de Render como respaldo en
builds de producción.

Neon ya contiene datos y la revisión Alembic `0003_caja_reportes_auditoria`;
no restaures un dump encima. Ejecuta `alembic upgrade head` contra Neon solo si
se agrega una migración, usando la URL directa desde un entorno administrativo.

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