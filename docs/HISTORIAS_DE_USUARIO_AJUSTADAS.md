# Historias de usuario ajustadas a la implementación

Este documento describe el alcance funcional que existe en el código y las
decisiones posteriores que cambiaron las historias originales. Complementa, no
reemplaza, [Historias_de_usuario_y_casos_de_uso_v2.md](./Historias_de_usuario_y_casos_de_uso_v2.md).
La implementación y las pruebas de aceptación se resumen en
[VERIFICACION_SPRINT_1_4.md](./VERIFICACION_SPRINT_1_4.md).

**Estado:** “Implementada” significa que el comportamiento está cubierto por
la API y/o la interfaz y por la evidencia indicada en el informe de
verificación. “Parcial” identifica un criterio expresamente pendiente; no se
considera terminado por existir un modelo o una preparación técnica.

## Requerimientos transversales

| HU | Criterios ajustados a lo que hace el sistema | Estado y diferencia relevante |
|---|---|---|
| **HU-01 — Inicio de sesión** | La autenticación requiere identificación, contraseña y cuenta activa. Un usuario inactivo no ingresa. Usuario inexistente y contraseña incorrecta producen el mismo mensaje genérico. Las contraseñas persistidas usan bcrypt. La API autoriza cada operación; la barra lateral conserva los mismos módulos y la interfaz muestra un aviso al entrar a uno no permitido. | **Parcial:** no hay TLS en esta entrega, por lo que no se certifica el transporte cifrado de la contraseña. La interfaz no oculta los enlaces por rol: decisión posterior solicitada por el cliente. |
| **HU-02 — Expiración de sesión** | El backend controla 3 minutos de inactividad y un máximo absoluto de 30 minutos desde el login. Las peticiones autenticadas renuevan la expiración por inactividad, sin extender el máximo absoluto. Al expirar, la API deniega la petición y la interfaz retorna al login; las operaciones no guardadas no se persisten en el navegador. | **Implementada.** |
| **HU-03 — Sesión única** | Un login nuevo revoca en base de datos las sesiones anteriores del usuario. La petición siguiente con el `jti` revocado no se autoriza. | **Parcial:** el dispositivo desplazado recibe denegación y vuelve a autenticarse, pero no se distingue con un aviso específico de “sesión reemplazada”. |
| **HU-04 — Autorización por sede** | El backend comprueba en cada petición el estado de la cuenta, roles actuales, sede seleccionada y asignaciones vigentes. Meseros y cajeros operativos solo consultan/operan en sus sedes asignadas. | **Implementada con decisión aprobada:** el administrador es global y no requiere asignaciones de sede; por ello no se limita a “sus sedes” como decía la historia original. |
| **HU-05 — Validación de formularios** | Pydantic valida tipos, formatos, longitudes, obligatoriedad y valores permitidos antes de persistir. La interfaz presenta los errores de validación recibidos. | **Implementada** para los contratos cubiertos por la API. La obligatoriedad de cada campo se define en las HU y esquemas del módulo correspondiente. |
| **HU-06 — Cierre manual** | Cerrar sesión revoca la sesión asociada al `jti`, elimina la cookie y exige un nuevo login para peticiones protegidas. | **Implementada.** |
| **HU-34 — JWT y petición protegida** | El JWT se valida por firma y expiración. Su `jti` debe existir y permanecer activo en la tabla de sesiones. Los roles y sedes se vuelven a consultar en la base de datos; los datos del token no sustituyen la autorización vigente. | **Implementada.** La expiración por inactividad se renueva en peticiones autenticadas, pero el vencimiento absoluto de 30 minutos no se renueva. |

## Sprint 1 y Sprint 2 — administración y acceso

| HU | Criterios ajustados a lo que hace el sistema | Estado y diferencia relevante |
|---|---|---|
| **HU-07 — Alta de usuario** | Solo administrador crea cuentas. Se requieren identificación, nombre, nombre de usuario, correo válido, contraseña y rol. Identificación, nombre de usuario y correo deben ser únicos. La cuenta nueva queda activa automáticamente. Meseros/cajeros requieren una o más sedes; el administrador no tiene asignaciones porque su acceso es global. | **Implementada con decisión posterior:** el correo es obligatorio al crear, aunque la HU original no lo exigía; el estado activo se asigna automáticamente y no se captura en el alta. |
| **HU-08 — Edición e inactivación de usuario** | El administrador modifica datos, roles y sedes. Inactivar bloquea el login y revoca las sesiones vigentes. Los roles y sedes actualizados afectan las peticiones siguientes. Las cuentas se conservan, no se borran físicamente. | **Implementada.** |
| **HU-09 — Capacidades de administrador** | El administrador tiene acceso administrativo y también capacidades de mesero y cajero; esos roles adicionales no se activan/desactivan en combinaciones individuales. Las operaciones de sede siguen sujetas a sus dependencias de autorización. | **Implementada con cambio aprobado:** no están disponibles las cuatro combinaciones configurables de la HU original. |
| **HU-10 — Alta de sede** | Solo administrador crea sedes con código, nombre y dirección. El código es único. Una sede activa puede asignarse a usuarios operativos y administrar su inventario. | **Implementada.** |
| **HU-35 — Mesas por sede** | Solo administrador crea y mantiene mesas. El número es único dentro de cada sede. Las mesas se conservan e inactivan en lugar de borrarse; el estado operativo se presenta como LIBRE u OCUPADA según exista un pedido abierto. | **Implementada.** |
| **HU-36 — Protección de credenciales y errores** | Las contraseñas se guardan como bcrypt. Los mensajes de error al usuario son controlados y los errores inesperados no entregan trazas. Los logs no deben exponer contraseñas ni tokens completos. | **Implementada según la verificación de backend;** el transporte TLS queda fuera de esta entrega. |
| **HU-37 — Validación e inyección** | Las entradas se validan en backend. El acceso a datos se realiza con ORM/consultas parametrizadas, no concatenando valores de usuario en SQL. Los valores inválidos se rechazan con errores controlados. | **Implementada según la revisión y las pruebas documentadas.** |

## Sprint 3 — catálogo y sede de trabajo

| HU | Criterios ajustados a lo que hace el sistema | Estado y diferencia relevante |
|---|---|---|
| **HU-11 — Producto** | Solo administrador crea productos en un catálogo central. Se requieren código único, nombre, precios de venta y compra, estado y proveedor. Los importes se manejan como decimales. La cantidad no pertenece al producto: el stock se mantiene por sede. | **Implementada.** |
| **HU-12 — Proveedores** | Solo administrador registra proveedores. El nombre es único y se puede guardar un número de contacto opcional. Cada producto debe referenciar un proveedor existente. No hay compras ni abastecimiento. | **Implementada.** El número se añadió a petición posterior; la HU original no lo definía como obligatorio. |
| **HU-13 — Selección de sede** | La sede autorizada única se selecciona automáticamente; con varias, el usuario elige. La selección se guarda en la sesión vinculada al `jti`, y el backend la vuelve a validar en cada petición. Mesas, inventario y pedidos se limitan a esa sede. | **Implementada.** Aplica a usuarios operativos y administrador global. |
| **HU-16 — Consulta y modificación de productos** | El administrador consulta y modifica el catálogo central; los cambios se comparten entre sedes. Un producto se puede inactivar/reactivar, no borrar físicamente, para conservar referencias e historial. | **Implementada.** La inactivación evita que un producto esté disponible para nuevas operaciones; no elimina sus referencias históricas. |
| **HU-18 — Información general** | El administrador consulta información general en modo lectura: usuarios, sedes, mesas, inventario, productos/proveedores y pedidos abiertos. El acceso a sedes se aplica según las reglas actuales; el administrador es global. | **Implementada** para el resumen que entrega el endpoint. No equivale a reportes de ventas ni habilita edición desde ese resumen. |

## Sprint 4 — mesas, inventario y pedidos

| HU | Criterios ajustados a lo que hace el sistema | Estado y diferencia relevante |
|---|---|---|
| **HU-19 — Consulta de mesas** | Meseros ven solo las mesas de la sede seleccionada, con estado LIBRE u OCUPADA. No hay asignación fija de mesero a mesa. | **Implementada.** |
| **HU-20 — Selección de mesa** | Una mesa libre permite crear pedido. Si ya tiene pedido ABIERTO, la consulta devuelve ese pedido y evita crear otro. | **Implementada**, incluida la protección de concurrencia en base de datos. |
| **HU-21 — Inventario disponible** | El inventario se consulta por sede en unidades completas. Los productos con cantidad cero se identifican como “Out of stock”; el selector de pedidos solo ofrece cantidades positivas y el backend vuelve a validar antes de guardar. | **Parcial:** los productos que aún no tienen una fila de inventario no aparecen en la consulta de existencias, aunque tampoco se pueden seleccionar ni agregar a pedidos. |
| **HU-22 — Crear pedido** | Se valida la existencia antes de guardar. El pedido queda ABIERTO y asociado a usuario, sede, mesa y fecha/hora. Las líneas guardan el precio vigente de cada producto. El descuento de inventario ocurre en la misma transacción. | **Implementada.** |
| **HU-23 — Añadir al pedido** | Solo se añaden productos a un pedido ABIERTO. Se validan y descuentan unidades atómicamente; cada línea conserva usuario y fecha/hora de registro. | **Implementada.** |
| **HU-24 — Estado de mesas** | Una mesa con pedido ABIERTO aparece OCUPADA. Volverá a LIBRE cuando no quede pedido abierto asociado. | **Parcial:** la ocupación al abrir está implementada; no existe cierre de pedido en esta entrega, por lo que no se puede ejecutar ni verificar el retorno a LIBRE tras cerrar. |
| **HU-25 — Consulta de pedido** | Se consulta estado, detalle y total solo para pedidos de la sede autorizada/seleccionada. | **Parcial:** se puede consultar el estado ABIERTO, detalle y total. El estado CERRADO no está disponible porque no se implementó el cierre. |
| **HU-33 — Descuento de inventario** | El sistema descuenta unidades enteras al crear pedido o añadir líneas, solo de la sede del pedido. Si no hay cantidad suficiente, rechaza toda la operación sin dejar inventario negativo. | **Implementada parcialmente por decisión aprobada para Sprint 4:** no se incluyen traslados entre sedes, mínimos ni alertas de reposición. |

## Decisiones de implementación que sustituyen ambigüedades

- **Roles y sedes:** el administrador es global; meseros y cajeros no administradores
  requieren asignaciones de sede. Los roles vigentes se consultan en base de datos.
- **Correo:** obligatorio y validado al crear usuario; opcional en una actualización
  parcial. Se aplica unicidad en el modelo.
- **Estado de alta de usuario:** las cuentas se crean activas; no se solicita el
  estado inicial en el formulario.
- **Proveedor:** el nombre es único. Por petición posterior se añadió un número
  de contacto opcional; no se incorporaron otros datos no solicitados.
- **Sede seleccionada:** queda guardada en la fila de sesión por `jti`, no se confía
  solo en el token ni en un parámetro proporcionado por cada endpoint.
- **Carga de inventario:** administrador puede crear existencia inicial o sumar
  unidades por sede. No se expone una operación de reducción manual.
- **Productos:** catálogo central; stock independiente por sede. Se conserva el
  producto y sus referencias al inactivarlo/reactivarlo.
- **Pedidos y concurrencia:** un índice único parcial impide más de un pedido
  ABIERTO por mesa. Las existencias se bloquean/descuentan transaccionalmente y
  las líneas guardan su propio precio vigente.
- **Cierre:** el modelo contempla los estados ABIERTO/CERRADO, pero no hay endpoint
  para cerrar pedidos, registrar pagos ni liberar mesas por cierre.

## Fuera del alcance implementado

No se consideran implementadas HU-14, HU-15, HU-17, HU-26 a HU-32 ni HU-38 a
HU-40. En particular, no hay pagos, facturación, cierre de pedidos, reportes de
ventas, exportación a Excel, bitácora general de operaciones, ni garantía
certificada de rendimiento o concurrencia de 20 usuarios. HU-33 se limita al
descuento de existencias necesario para HU-22/HU-23. También permanece excluido
todo lo indicado en la sección 18 de la propuesta comercial, así como el
despliegue con Nginx, TLS o Gunicorn.

La suite y el test extremo a extremo se reportan en
[VERIFICACION_SPRINT_1_4.md](./VERIFICACION_SPRINT_1_4.md); allí se detallan las
pruebas, la matriz de criterios y las limitaciones que no se pudieron verificar.
