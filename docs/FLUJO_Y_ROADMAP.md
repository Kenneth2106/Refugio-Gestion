# Flujo actual y trabajo pendiente

Este documento describe lo que existe en el repositorio a la fecha de esta
entrega. El alcance aprobado para Sprints 1 a 4 está en
[alcance_sprint_1_4.md](./alcance_sprint_1_4.md); los criterios por historia y
la evidencia de pruebas están en
[VERIFICACION_SPRINT_1_4.md](./VERIFICACION_SPRINT_1_4.md).

## 1. Componentes

- **Frontend:** HTML5, CSS y JavaScript nativo en `frontend/`. Vite ofrece el
  servidor de desarrollo en `127.0.0.1:5175` y reenvía las peticiones REST al
  backend en `127.0.0.1:8000`.
- **Backend:** FastAPI en `backend/app/`. Expone rutas REST/JSON, valida
  entradas con Pydantic, aplica autorización en dependencias y realiza las
  operaciones mediante SQLAlchemy.
- **Base de datos:** PostgreSQL. Alembic crea/actualiza el esquema mediante
  `backend/alembic/versions/`; la revisión incluida para este alcance es
  `0001_initial`.
- **Pruebas:** pytest contra PostgreSQL real. La suite crea un esquema de
  prueba aislado, aplica las migraciones y lo elimina al terminar.

## 2. Flujo de una petición

1. El usuario interactúa con un módulo del frontend.
2. JavaScript serializa el formulario y envía una petición REST/JSON con la
   cookie de sesión del mismo origen.
3. FastAPI valida el cuerpo y los parámetros antes de ejecutar el endpoint.
4. En una ruta protegida, las dependencias de autenticación consultan el JWT,
   el `jti` de sesión persistido, el estado/roles vigentes del usuario y, si
   corresponde, su acceso a la sede seleccionada.
5. El endpoint consulta o modifica datos con ORM. Las operaciones de pedido e
   inventario se confirman en la base dentro de una misma transacción.
6. FastAPI devuelve JSON; el frontend actualiza la vista o presenta un mensaje
   de error. El control visual del frontend no reemplaza la autorización del
   backend.

## 3. Recorrido funcional disponible

### 3.1 Inicio de sesión y control de sesión

1. El usuario envía identificación y contraseña a `POST /auth/login`.
2. El backend busca al usuario activo y compara la contraseña con su hash
   bcrypt. Un usuario inexistente y una contraseña incorrecta comparten el
   mensaje de error de autenticación.
3. Un nuevo inicio de sesión revoca las sesiones previas de esa cuenta,
   genera un `jti`, registra la sesión en PostgreSQL y emite una cookie JWT
   HttpOnly.
4. Las peticiones autenticadas pasan por `get_current_session`: se verifica el
   JWT y el `jti` activo en base de datos. Se consultan los roles y las sedes
   actuales, por lo que cambiar o inactivar al usuario tiene efecto en las
   siguientes peticiones.
5. La actividad renueva la expiración corta del token, pero nunca sobrepasa
   los 30 minutos desde el login. El vencimiento por inactividad es de 3
   minutos. Los límites se configuran mediante variables de entorno.
6. El frontend consulta `/auth/me` al iniciar y mientras detecta actividad;
   al recibir una sesión inválida, vuelve a la pantalla de ingreso.

### 3.2 Permisos, roles y selección de sede

- La sidebar es común. El frontend muestra un aviso al abrir un módulo sin
  permiso; cada operación continúa protegida por FastAPI.
- Solo el administrador puede administrar usuarios, sedes, mesas, proveedores,
  productos y cargar/sumar inventario.
- Los usuarios operativos pueden trabajar únicamente en sedes asignadas. Si
  tienen una sede autorizada, se selecciona automáticamente; si tienen varias,
  eligen una desde la barra superior.
- La sede seleccionada se guarda en la fila de sesión asociada al `jti`. La
  autorización se vuelve a comprobar cuando se consulta una sede.
- Conforme a la decisión confirmada, el administrador es global, no tiene
  asignaciones explícitas de sede y hereda capacidades de mesero y cajero.

### 3.3 Configuración administrativa

El administrador puede crear y mantener:

1. **Sedes:** con código único.
2. **Mesas:** asociadas a una sede, número único dentro de esa sede; se
   inactivan para conservar referencias, no se eliminan desde la interfaz.
3. **Usuarios:** identificación, nombre de usuario y correo electrónico
   obligatorios y únicos; contraseña con bcrypt, roles y sedes operativas
   asignadas. El correo se valida al crear; los usuarios se crean activos.
4. **Proveedores:** identificados por nombre único.
5. **Productos:** catálogo central con código único, nombre, precios de compra
   y venta, estado y proveedor. El botón “Delete” lo inactiva para conservar
   su historial y permite reactivarlo; no borra físicamente el registro. El
   producto no guarda cantidades de inventario.
6. **Inventario por sede:** la carga administrativa crea o incrementa la
   existencia de un producto para la sede de trabajo. No hay traslado entre
   sedes ni reducción manual de existencias.

El resumen de administración ofrece consulta de usuarios, sedes, productos,
proveedores, existencias, pedidos abiertos y estados de mesas.

### 3.4 Operación de mesero y pedidos

1. El mesero ve las mesas de la sede seleccionada. El estado operativo es
   `LIBRE` si no hay pedido abierto y `OCUPADA` si lo hay; no existe asignación
   fija de mesero a mesa.
2. Al consultar una mesa ocupada, el backend devuelve el pedido abierto
   existente. Una restricción única parcial en PostgreSQL impide dos pedidos
   abiertos para la misma mesa, incluso ante peticiones concurrentes.
3. En una mesa libre, el mesero puede iniciar un pedido `ABIERTO`, asociado al
   usuario, la sede, la mesa y su fecha/hora.
4. El backend valida producto y unidades disponibles antes de guardar. Bloquea
   registros de inventario en orden de producto, descuenta existencias, agrega
   las líneas y persiste el precio unitario vigente dentro de la misma
   transacción.
5. Al añadir productos a un pedido, este debe seguir `ABIERTO`; se registran el
   usuario y fecha/hora de la línea, se vuelve a validar stock y se descuenta
   inventario de esa sede. Los totales se calculan usando `Decimal`.
6. El detalle/total del pedido y su estado pueden consultarse dentro de la
   sede autorizada. Cambios posteriores al precio del producto no alteran las
   líneas ya registradas.

## 4. Estado por sprint

| Sprint | Historias | Estado en esta entrega |
|---|---|---|
| 1 | HU-01, 02, 03, 05, 06, 34, 36, 37 | Implementadas y verificadas en la suite backend. |
| 2 | HU-04, 07, 08, 09, 10, 35 | Implementadas y verificadas; las decisiones específicas del administrador se detallan arriba. |
| 3 | HU-11, 12, 13, 16, 18 | Implementadas y verificadas; catálogo central, proveedores y sede de trabajo. |
| 4 | HU-19, 20, 21, 22, 23, 24, 25 y el descuento mínimo de HU-33 | Operación abierta del mesero, consulta de mesas/inventario/pedidos, descuento transaccional y concurrencia verificados. No hay pagos ni cierre. |

La etiqueta “implementadas” resume funcionalidades del sprint; no significa
que todos los criterios visuales o de aceptación estén completos. Los estados
parciales y sus evidencias se indican en la matriz de verificación.

El informe existente registra **94 pruebas backend aprobadas** y la prueba de
integración de extremo a extremo con **14 de 14 pasos aprobados** en la
verificación documentada. Para el detalle y las limitaciones, consultar
[VERIFICACION_SPRINT_1_4.md](./VERIFICACION_SPRINT_1_4.md).

## 5. Trabajo futuro según backlog

El backlog fuente enumera dos sprints posteriores. Estas historias no están
incluidas en el alcance aprobado actual, así que esta lista es orientación,
no autorización para desarrollarlas.

### Sprint 5: caja y cierre

- **HU-26:** consultar pedidos pendientes de pago.
- **HU-27 y HU-28:** registrar pagos en efectivo o tarjeta; sin dividir pagos
  ni integrar datáfonos/pasarelas.
- **HU-29:** cerrar el pedido después del pago, registrar usuario/fecha de
  cierre y liberar la mesa.
- **HU-30:** generar/mostrar información de facturación; no incluye factura
  electrónica.
- El backlog también ubica **HU-14 y HU-15** en este sprint para que el
  administrador opere con capacidades de mesero/cajero. El alcance actual las
  excluye y la implementación vigente da al administrador esas capacidades
  directamente, según la decisión aprobada; cualquier trabajo adicional debe
  revisarse antes.

### Sprint 6: reportes, trazabilidad e integración

- **HU-17:** reporte consolidado de ventas del administrador, filtros y
  exportación Excel.
- **HU-31:** consulta y filtro del reporte de ventas del cajero.
- **HU-32:** exportación a Excel.
- **HU-33:** el descuento de stock requerido al registrar pedidos ya está
  implementado; revisar si el cliente requiere trabajo adicional antes de
  extenderlo. Traslados, stock mínimo y alertas están excluidos por la sección
  18 de la propuesta.
- **HU-38:** registro de auditoría de operaciones y eventos. El pedido ya
  conserva usuario, sede, mesa, fechas, líneas y estado; eso no equivale a un
  historial completo de eventos.
- **HU-39:** validar formalmente la adaptación responsive y confirmar el
  idioma de la interfaz con el cliente. La interfaz actual está en inglés.
- **HU-40:** medir objetivos explícitos de respuesta máxima de 2 segundos y
  concurrencia mínima de 20 usuarios, más pruebas operativas de carga.
- Ejecutar la integración final y las pruebas correspondientes a los nuevos
  criterios.

## 6. Límites actuales y exclusiones

- El pedido permanece `ABIERTO`: no hay pago, cierre, factura ni liberación de
  mesa mediante caja. Esas capacidades forman parte del trabajo posterior.
- No se implementaron reportes de ventas ni exportación a Excel.
- El frontend usa un servidor Vite de desarrollo ligado a `127.0.0.1`; no es
  una publicación para que otros equipos entren por red. Para uso en varios
  dispositivos hace falta acordar y preparar despliegue/red, proxy y HTTPS.
- Continúan excluidas las historias no incluidas en Sprints 1–4 y todas las
  funciones de la sección 18 de la propuesta comercial: entre otras, traslado
  de inventario, stock mínimo, alertas de reposición, nómina, turnos, reservas,
  compras/abastecimiento completo, domicilio, factura electrónica y división
  de pagos.
- El detalle de criterios parciales, decisiones, supuestos y evidencia está en
  [VERIFICACION_SPRINT_1_4.md](./VERIFICACION_SPRINT_1_4.md).
