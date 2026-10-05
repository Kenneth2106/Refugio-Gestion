REFUGIO GESTIÓN
Casos de uso / Historias de usuario
Cliente
El Refugio Bar
Proveedor
Nexora Software
Documento
Historias de usuario, criterios de aceptación, diagramas de flujo y de caso de uso
Versión
2.0 — documento revisado
Base de referencia
Propuesta comercial REFUGIO GESTIÓN, versión 1.1
Alcance de la revisión
Verificación de redacción y coherencia frente a la propuesta comercial, incorporación
de los mockups de referencia y ajuste de la diagramación del documento


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 2
1. Objeto del documento
El presente documento desarrolla las historias de usuario derivadas de la propuesta comercial de REFUGIO GESTIÓN,
organizadas según los perfiles definidos en el sistema (Administrador, Mesero y Cajero) y los requerimientos transversales
de seguridad, control de acceso e inventario. Cada historia sigue el formato “Como [rol], quiero [funcionalidad], para
[beneficio]” e incluye sus criterios de aceptación, la trazabilidad con la sección correspondiente de la propuesta comercial,
un diagrama de flujo del proceso y un diagrama de caso de uso UML.
Esta versión 2.0 corresponde a la revisión del documento original: se verificó la redacción y la coherencia de cada historia
frente a la propuesta comercial, se ajustaron los criterios de aceptación que presentaban diferencias, se incorporaron
historias complementarias para requisitos de la propuesta que no contaban con historia asociada y se reorganizaron los
mockups de referencia en una sección independiente.
2. Contenido
A.
Requerimientos transversales — Autenticación y seguridad
HU-01 a HU-06, HU-34
B.
Perfil Administrador
HU-07 a HU-18
C.
Perfil Mesero
HU-19 a HU-25
D.
Perfil Cajero
HU-26 a HU-32
E.
Gestión de inventario (transversal)
HU-33
F.
Historias complementarias identificadas en la revisión
HU-35 a HU-40
G.
Matriz de trazabilidad con la propuesta comercial
HU-01 a HU-40
H.
Observaciones de la revisión
—
I.
Mockups de referencia
16 pantallas
3. Convenciones
• Cada historia de usuario ocupa una página e incluye encabezado, historia, criterios de aceptación, trazabilidad y sus dos
diagramas.
• Los estados de los pedidos se expresan como ABIERTO y CERRADO; los de las mesas, como LIBRE y OCUPADA.
• La numeración original de las historias se conserva para no afectar referencias previas; las historias incorporadas en la
revisión continúan la numeración a partir de HU-35.
• Los diagramas de flujo y de caso de uso corresponden a los del documento original, conservados sin modificación de
contenido.


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 3
A. Requerimientos transversales — Autenticación y seguridad
HU-01
—   Usuario del sistema
Inicio de sesión con identificación y contraseña
Como usuario del sistema, quiero iniciar sesión con mi identificación y contraseña, para acceder únicamente a las
funcionalidades autorizadas según mis roles y mis sedes.
Criterios de aceptación:
• El sistema valida que el usuario exista y se encuentre en estado ACTIVO.
• Un usuario inactivo no puede iniciar sesión, aunque las credenciales sean correctas.
• Las credenciales incorrectas muestran un mensaje genérico, sin revelar información técnica ni indicar si el error
corresponde al usuario o a la contraseña.
• La contraseña se valida contra un valor almacenado de forma cifrada; nunca se almacena ni se transmite en texto plano.
• Tras el inicio de sesión exitoso, el usuario solo visualiza las opciones de menú correspondientes a sus roles, permisos y
sedes autorizadas.
Trazabilidad: Propuesta comercial: 5, 7.1, 16.2, 16.5, 16.6
Diagrama de flujo — HU-01
Diagrama de caso de uso — HU-01


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 4
HU-02
—   Usuario del sistema
Cierre de sesión automático por inactividad
Como usuario del sistema, quiero que mi sesión se cierre automáticamente tras un periodo de inactividad, para
proteger la información si olvido cerrar sesión.
Criterios de aceptación:
• El sistema cierra la sesión automáticamente después de 3 minutos de inactividad.
• La sesión tiene además una duración máxima de 30 minutos, aun cuando exista actividad continua.
• El control del tiempo de inactividad se valida en el backend y no depende únicamente del navegador.
• Al expirar la sesión, el usuario es redirigido a la pantalla de inicio de sesión con un mensaje informativo de sesión expirada.
• Cualquier operación en curso no guardada debe reiniciarse tras el nuevo ingreso.
Trazabilidad: Propuesta comercial: 16, 16.2
Diagrama de flujo — HU-02
Diagrama de caso de uso — HU-02


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 5
HU-03
—   Usuario del sistema
Sesión única simultánea
Como usuario del sistema, quiero que no se permita mantener más de una sesión activa simultáneamente, para evitar
el uso indebido o compartido de mis credenciales.
Criterios de aceptación:
• Si el usuario inicia sesión en un segundo dispositivo o navegador, la sesión anterior se invalida en el backend.
• El sistema notifica en el dispositivo desplazado que la sesión activa fue cerrada por un nuevo inicio de sesión.
• La sesión invalidada no permite ejecutar nuevas peticiones, aunque la pantalla permanezca abierta.
Trazabilidad: Propuesta comercial: 16.2
Diagrama de flujo — HU-03
Diagrama de caso de uso — HU-03


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 6
HU-04
—   Usuario del sistema
Validación de autorización por sede
Como usuario del sistema, quiero que el sistema valide mi autorización sobre la sede antes de permitir una operación,
para evitar consultar o modificar información de una sede que no me corresponde.
Criterios de aceptación:
• El sistema verifica la relación usuario–rol–sede antes de mostrar mesas, inventario, pedidos o reportes.
• Un mesero o un cajero solo puede operar en las sedes para las que está autorizado; un administrador solo en las sedes
asignadas a su usuario.
• Un intento de acceso a una sede no autorizada es rechazado con un mensaje claro, sin exponer información de esa sede.
• La validación se ejecuta en el backend en cada petición y no se limita a ocultar opciones en la interfaz.
Trazabilidad: Propuesta comercial: 8, 16.1
Diagrama de flujo — HU-04
Diagrama de caso de uso — HU-04


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 7
HU-05
—   Usuario del sistema
Validación de campos obligatorios en formularios
Como usuario del sistema, quiero que los formularios validen los campos obligatorios antes de guardar, para evitar
registrar información incompleta o incorrecta.
Criterios de aceptación:
• El sistema no permite guardar un registro si falta un campo obligatorio e indica cuál es el campo pendiente.
• Se valida el tipo de dato, la longitud, el formato y los valores permitidos de cada campo.
• Los campos opcionales pueden dejarse vacíos sin bloquear el guardado.
• La validación se repite en el backend antes de persistir la información.
Trazabilidad: Propuesta comercial: 7, 14, 16.3
Diagrama de flujo — HU-05
Diagrama de caso de uso — HU-05


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 8
HU-06
—   Usuario del sistema
Cierre de sesión manual
Como usuario del sistema, quiero cerrar sesión manualmente, para finalizar de forma segura mi acceso al sistema.
Criterios de aceptación:
• El usuario puede cerrar sesión desde las opciones autorizadas del sistema (menú de perfil).
• Al cerrar sesión, el sistema invalida la sesión activa y el token asociado.
• Después del cierre, el usuario debe autenticarse nuevamente para acceder al sistema.
Trazabilidad: Propuesta comercial: 16.2
Diagrama de flujo — HU-06
Diagrama de caso de uso — HU-06


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 9
HU-34
—   Sistema
Protección de peticiones mediante JWT
Como usuario del sistema, quiero que mis peticiones estén protegidas mediante tokens JWT de corta duración, para
garantizar la seguridad de la sesión sin comprometer la usabilidad.
Criterios de aceptación:
• Al iniciar sesión correctamente, el sistema emite un token JWT con expiración (exp) igual al tiempo de inactividad definido (3
minutos), dentro de una sesión de máximo 30 minutos.
• El token contiene la identificación del usuario, sus roles y sus sedes autorizadas, utilizados para la validación de acceso.
• Cada petición al backend valida la firma y la fecha de expiración del JWT.
• Si el token expira o es inválido, el sistema rechaza la petición con un error controlado y redirige al inicio de sesión.
Trazabilidad: Propuesta comercial: 16, 16.1, 16.2
Diagrama de flujo — HU-34
Diagrama de caso de uso — HU-34


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 10
B. Perfil Administrador
HU-07
—   Administrador
Registro de nuevo usuario
Como administrador, quiero registrar un nuevo usuario indicando identificación, nombres, contraseña, estado, roles y
sede(s) autorizadas, para controlar quién puede acceder al sistema y con qué permisos.
Criterios de aceptación:
• Los campos obligatorios son: identificación, nombres, nombre de usuario, contraseña, estado y sede.
• El sistema valida que la identificación y el nombre de usuario no estén previamente registrados.
• El usuario debe quedar asociado al menos a un rol y a una sede cuando su función lo requiera.
• La contraseña se almacena cifrada mediante un mecanismo seguro de protección de credenciales.
• No se permite guardar el usuario si falta algún campo obligatorio.
Trazabilidad: Propuesta comercial: 7.1, 16.5
Diagrama de flujo — HU-07
Diagrama de caso de uso — HU-07


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 11
HU-08
—   Administrador
Edición o inactivación de usuario
Como administrador, quiero editar o inactivar un usuario existente, para mantener actualizada la información de acceso
del personal.
Criterios de aceptación:
• El administrador puede modificar nombres, sede(s), roles y estado del usuario.
• Un usuario inactivado no puede iniciar sesión desde ese momento y su sesión activa se invalida.
• Los cambios quedan reflejados de inmediato en los permisos de acceso, ya que se validan en cada petición.
• Los usuarios no se eliminan físicamente: se inactivan, para conservar la trazabilidad de las operaciones registradas.
Trazabilidad: Propuesta comercial: 7.1, 13, 16.1
Diagrama de flujo — HU-08
Diagrama de caso de uso — HU-08


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 12
HU-09
—   Administrador
Habilitación de permisos adicionales (mesero/cajero)
Como administrador, quiero habilitar los permisos adicionales de mesero y/o cajero sobre un usuario administrador,
para poder desempeñar funciones operativas cuando el negocio lo requiera.
Criterios de aceptación:
• Un usuario administrador puede tener configuradas las combinaciones: solo Administrador, Administrador+Mesero,
Administrador+Cajero o Administrador+Mesero+Cajero.
• Al iniciar sesión, el menú muestra únicamente las opciones de los roles habilitados.
• Las funcionalidades operativas siguen sujetas a la validación de sede autorizada (HU-04 y HU-13).
Trazabilidad: Propuesta comercial: 5.1, 6
Diagrama de flujo — HU-09
Diagrama de caso de uso — HU-09


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 13
HU-10
—   Administrador
Registro de nueva sede
Como administrador, quiero registrar una nueva sede con código, nombre y dirección, para habilitar la operación del
negocio en un nuevo punto.
Criterios de aceptación:
• Los campos obligatorios son: código de sede, nombre y dirección.
• El sistema valida que el código de sede sea único.
• No se permite guardar la sede si falta el código, el nombre o la dirección.
• La sede registrada queda disponible para ser asignada a usuarios y para gestionar su propio inventario.
Trazabilidad: Propuesta comercial: 7.2, 10
Diagrama de flujo — HU-10
Diagrama de caso de uso — HU-10


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 14
HU-11
—   Administrador
Registro de nuevo producto
Como administrador, quiero registrar un nuevo producto con código, nombre, precio de venta, precio de compra,
estado y proveedor, para mantener un catálogo estandarizado para todo el negocio.
Criterios de aceptación:
• Los campos obligatorios son: código, nombre, precio de venta, precio de compra, estado y proveedor.
• El sistema valida que el código del producto sea único.
• El código, el nombre y los precios del producto quedan disponibles, de forma estandarizada, para todas las sedes.
• La cantidad disponible no hace parte del registro del producto: el inventario se gestiona de forma independiente por sede
(HU-33).
• No se permite guardar el producto si falta algún campo obligatorio.
Trazabilidad: Propuesta comercial: 7.4, 10
Diagrama de flujo — HU-11
Diagrama de caso de uso — HU-11


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 15
HU-12
—   Administrador
Registro de proveedor y asociación a productos
Como administrador, quiero registrar un nuevo proveedor y asociarlo a uno o varios productos, para llevar control del
origen de los productos del catálogo.
Criterios de aceptación:
• El proveedor debe seleccionarse al registrar o editar un producto, por ser un campo obligatorio del producto.
• El sistema conserva la relación producto–proveedor para consultas posteriores.
• La gestión de compras y el proceso de abastecimiento se encuentran fuera del alcance del proyecto.
Trazabilidad: Propuesta comercial: 4, 7.4, 18
Diagrama de flujo — HU-12
Diagrama de caso de uso — HU-12


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 16
HU-13
—   Administrador
Selección de sede de trabajo
Como administrador, quiero seleccionar la sede sobre la cual voy a trabajar cuando tengo autorización sobre varias
sedes, para operar de forma organizada sin mezclar información entre sedes.
Criterios de aceptación:
• Si el administrador solo tiene una sede autorizada, el sistema la asigna automáticamente.
• Si tiene varias sedes autorizadas, el sistema le permite elegir la sede antes de continuar con la operación.
• Tras seleccionar la sede, solo se muestran las mesas, el inventario y los pedidos de esa sede.
• La sede seleccionada queda registrada en las operaciones realizadas durante la sesión.
Trazabilidad: Propuesta comercial: 6, 8
Diagrama de flujo — HU-13
Diagrama de caso de uso — HU-13


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 17
HU-14
—   Administrador con permiso de mesero
Toma de pedidos como mesero
Como administrador con permiso de mesero, quiero tomar pedidos igual que un mesero en la sede seleccionada, para
cubrir la operación cuando sea necesario.
Criterios de aceptación:
• El pedido registrado queda asociado al usuario administrador y a la sede seleccionada.
• El administrador solo ve las mesas, el inventario y los pedidos de la sede elegida.
• Al guardar el pedido se aplican las mismas validaciones y el mismo descuento de inventario definidos para el perfil mesero
(HU-22 y HU-33).
Trazabilidad: Propuesta comercial: 6
Diagrama de flujo — HU-14
Diagrama de caso de uso — HU-14


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 18
HU-15
—   Administrador con permiso de cajero
Procesamiento de pagos como cajero
Como administrador con permiso de cajero, quiero procesar pagos y cerrar pedidos igual que un cajero en la sede
seleccionada, para cubrir la operación de caja cuando sea necesario.
Criterios de aceptación:
• El administrador solo visualiza los pedidos abiertos de la sede seleccionada.
• El pago y el cierre quedan registrados con la información del usuario administrador que realizó la operación.
• Aplican las mismas reglas de pago definidas para el perfil cajero (HU-27 a HU-30).
Trazabilidad: Propuesta comercial: 6, 11
Diagrama de flujo — HU-15
Diagrama de caso de uso — HU-15


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 19
HU-16
—   Administrador
Consulta y modificación de productos
Como administrador, quiero consultar y modificar la información de los productos registrados, para mantener
actualizado el catálogo general del negocio.
Criterios de aceptación:
• El administrador puede consultar el listado de productos registrados con su código, nombre, precios y estado.
• Puede modificar los campos permitidos del producto.
• El sistema valida los campos obligatorios antes de guardar los cambios.
• La información general actualizada del producto se mantiene estandarizada para todas las sedes.
Trazabilidad: Propuesta comercial: 5.1, 7.4, 10
Diagrama de flujo — HU-16
Diagrama de caso de uso — HU-16


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 20
HU-17
—   Administrador
Reporte de ventas consolidado exportable
Como administrador, quiero consultar el reporte de ventas consolidado de las sedes autorizadas y exportarlo a Excel,
para apoyar la toma de decisiones sobre el negocio.
Criterios de aceptación:
• El reporte permite filtrar por fecha inicial, fecha final, sede (una o todas las autorizadas), estado del pedido y medio de pago.
• El reporte incluye, como mínimo: identificador del producto, nombre del producto, cantidad vendida, valor de compra, valor
de venta, ganancia y sede.
• El reporte solo incluye información de las sedes autorizadas para el usuario.
• El administrador puede exportar el resultado del reporte en formato Excel, conservando los filtros aplicados en pantalla.
Trazabilidad: Propuesta comercial: 12.2
Diagrama de flujo — HU-17
Diagrama de caso de uso — HU-17


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 21
HU-18
—   Administrador
Consulta de información general autorizada
Como administrador, quiero consultar la información general autorizada del sistema, para realizar seguimiento y control
de la operación.
Criterios de aceptación:
• El sistema muestra únicamente la información correspondiente a las funcionalidades autorizadas.
• La información visualizada respeta los permisos y las restricciones por sede cuando aplique.
• El administrador puede consultar la información sin modificarla cuando no tenga permiso de edición.
Trazabilidad: Propuesta comercial: 5.1, 16.1
Diagrama de flujo — HU-18
Diagrama de caso de uso — HU-18


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 22
C. Perfil Mesero
HU-19
—   Mesero
Consulta de mesas disponibles
Como mesero, quiero consultar las mesas disponibles en la sede para la que estoy autorizado, para saber en qué
mesa puedo registrar un nuevo pedido.
Criterios de aceptación:
• El sistema solo muestra las mesas de la(s) sede(s) autorizadas para el mesero.
• Cada mesa se visualiza con su estado actual (LIBRE u OCUPADA).
• El sistema no contempla la asignación fija de meseros a mesas.
Trazabilidad: Propuesta comercial: 5.2, 9, 18
Diagrama de flujo — HU-19
Diagrama de caso de uso — HU-19


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 23
HU-20
—   Mesero
Selección de mesa para nuevo pedido
Como mesero, quiero seleccionar la mesa sobre la cual registraré un pedido, para asociar correctamente el pedido a la
mesa del cliente.
Criterios de aceptación:
• Al seleccionar una mesa LIBRE, el sistema permite iniciar el registro del pedido.
• La mesa queda marcada como OCUPADA mientras el pedido permanezca en estado ABIERTO.
• Al seleccionar una mesa OCUPADA, el sistema muestra el pedido abierto asociado para su consulta o adición de
productos.
Trazabilidad: Propuesta comercial: 5.2, 9
Diagrama de flujo — HU-20
Diagrama de caso de uso — HU-20


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 24
HU-21
—   Mesero
Consulta de inventario disponible
Como mesero, quiero consultar el inventario disponible en la sede seleccionada, para saber qué productos puedo
ofrecer al cliente.
Criterios de aceptación:
• El inventario mostrado corresponde únicamente a la sede en la que opera el mesero.
• Los productos sin unidades disponibles se identifican claramente y no pueden agregarse al pedido.
• El inventario se presenta en unidades completas.
Trazabilidad: Propuesta comercial: 5.2, 10
Diagrama de flujo — HU-21
Diagrama de caso de uso — HU-21


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 25
HU-22
—   Mesero
Registro y guardado del pedido
Como mesero, quiero registrar los productos solicitados por el cliente y guardar el pedido, para dejar constancia formal
de lo que se debe preparar y cobrar.
Criterios de aceptación:
• El sistema valida la disponibilidad de cada producto en la sede antes de guardar el pedido.
• El pedido queda registrado en estado ABIERTO, asociado al usuario, a la sede, a la mesa y a la fecha/hora del registro.
• Al guardar el pedido se descuenta automáticamente el inventario correspondiente en la sede (HU-33).
• El pedido conserva el precio de venta vigente del producto al momento del registro.
Trazabilidad: Propuesta comercial: 9, 13
Diagrama de flujo — HU-22
Diagrama de caso de uso — HU-22


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 26
HU-23
—   Mesero
Adición de productos a pedido abierto
Como mesero, quiero añadir productos adicionales a un pedido que aún se encuentra abierto, para atender solicitudes
adicionales del cliente sin crear un pedido nuevo.
Criterios de aceptación:
• Solo es posible añadir productos mientras el pedido esté en estado ABIERTO.
• El sistema valida la disponibilidad del producto y descuenta el inventario de la sede al confirmar la adición.
• La adición queda registrada con el usuario y la fecha/hora de la operación.
Trazabilidad: Propuesta comercial: 5.2, 9, 13
Diagrama de flujo — HU-23
Diagrama de caso de uso — HU-23


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 27
HU-24
—   Mesero
Visualización del estado de las mesas
Como mesero, quiero visualizar el estado de las mesas como LIBRE u OCUPADA, para organizar la atención de los
clientes en la sede.
Criterios de aceptación:
• El estado de cada mesa se actualiza automáticamente al abrir o cerrar un pedido.
• Una mesa queda disponible (LIBRE) nuevamente una vez se cierra el pedido asociado.
• El estado mostrado corresponde únicamente a las mesas de la sede seleccionada.
Trazabilidad: Propuesta comercial: 5.2, 9
Diagrama de flujo — HU-24
Diagrama de caso de uso — HU-24


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 28
HU-25
—   Mesero
Consulta del estado de un pedido
Como mesero, quiero consultar el estado de un pedido que he registrado, para informar al cliente sobre el avance de
su solicitud.
Criterios de aceptación:
• El sistema muestra el estado actual del pedido (ABIERTO o CERRADO) con su detalle de productos y total.
• El mesero solo puede consultar los pedidos correspondientes a su(s) sede(s) autorizadas.
Trazabilidad: Propuesta comercial: 5.2, 9
Diagrama de flujo — HU-25
Diagrama de caso de uso — HU-25


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 29
D. Perfil Cajero
HU-26
—   Cajero
Consulta de pedidos pendientes de pago
Como cajero, quiero consultar los pedidos pendientes de pago en mi sede, para identificar qué pedidos debo procesar.
Criterios de aceptación:
• El sistema solo muestra los pedidos en estado ABIERTO correspondientes a la(s) sede(s) autorizada(s) del cajero.
• Cada pedido se presenta con mesa, usuario que lo registró, fecha/hora y valor total.
• Al seleccionar un pedido, el sistema muestra su detalle para continuar con el proceso de pago.
Trazabilidad: Propuesta comercial: 5.3, 11
Diagrama de flujo — HU-26
Diagrama de caso de uso — HU-26


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 30
HU-27
—   Cajero
Procesamiento de pago en efectivo
Como cajero, quiero procesar un pago en efectivo para un pedido abierto, para completar el cobro al cliente.
Criterios de aceptación:
• El sistema registra el medio de pago como EFECTIVO junto con el usuario y la fecha/hora de la operación.
• El sistema no permite dividir el valor del pedido entre varias personas.
• El valor cobrado corresponde al total del pedido calculado por el sistema, sin edición manual.
Trazabilidad: Propuesta comercial: 5.3, 11, 18
Diagrama de flujo — HU-27
Diagrama de caso de uso — HU-27


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 31
HU-28
—   Cajero
Procesamiento de pago con tarjeta
Como cajero, quiero procesar un pago con tarjeta para un pedido abierto, para ofrecer una alternativa de pago al
cliente.
Criterios de aceptación:
• El sistema registra el medio de pago como TARJETA junto con el usuario y la fecha/hora de la operación.
• No se aplica ninguna comisión adicional por el pago con tarjeta.
• El sistema no contempla la integración con datáfonos ni con pasarelas de pago.
Trazabilidad: Propuesta comercial: 5.3, 11
Diagrama de flujo — HU-28
Diagrama de caso de uso — HU-28


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 32
HU-29
—   Cajero
Cierre del pedido tras el pago
Como cajero, quiero cerrar el pedido una vez registrado el pago, para finalizar formalmente la venta.
Criterios de aceptación:
• El estado del pedido cambia de ABIERTO a CERRADO tras confirmar el pago.
• El cierre queda asociado al usuario cajero que realizó la operación y a la fecha/hora del cierre.
• La mesa asociada queda disponible (LIBRE) una vez finaliza el proceso.
• Un pedido CERRADO no admite adición ni modificación de productos.
Trazabilidad: Propuesta comercial: 9, 11, 13
Diagrama de flujo — HU-29
Diagrama de caso de uso — HU-29


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 33
HU-30
—   Cajero
Generación de información de facturación
Como cajero, quiero generar la información de facturación del pedido cerrado y visualizarla en pantalla, para entregar
al cliente un comprobante de su consumo.
Criterios de aceptación:
• La información de facturación se obtiene automáticamente de los datos del pedido, sin edición manual.
• El sistema contempla la generación de factura física o su visualización en pantalla.
• La factura electrónica no hace parte del alcance del proyecto.
Trazabilidad: Propuesta comercial: 11, 18
Diagrama de flujo — HU-30
Diagrama de caso de uso — HU-30


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 34
HU-31
—   Cajero
Consulta y filtro del reporte de ventas de la sede
Como cajero, quiero consultar y filtrar el reporte de ventas de mi sede por fecha, para revisar el desempeño de ventas
de mi turno o periodo.
Criterios de aceptación:
• El reporte permite filtrar por fecha inicial, fecha final y sede autorizada.
• El reporte solo incluye información de la(s) sede(s) autorizada(s) para el cajero.
• El reporte incluye, como mínimo: identificador del producto, nombre del producto, cantidad vendida, valor de compra, valor
de venta, ganancia y sede.
Trazabilidad: Propuesta comercial: 12.1
Diagrama de flujo — HU-31
Diagrama de caso de uso — HU-31


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 35
HU-32
—   Cajero
Exportación del reporte de ventas a Excel
Como cajero, quiero exportar el reporte de ventas autorizado en formato Excel, para compartir o archivar la información
de ventas fuera del sistema.
Criterios de aceptación:
• El archivo exportado conserva la misma información filtrada visualizada en pantalla.
• Solo se exportan los datos correspondientes a la(s) sede(s) autorizada(s) del cajero.
• La exportación no expone información de otras sedes ni campos no autorizados para el perfil.
Trazabilidad: Propuesta comercial: 12.1, 16.1
Diagrama de flujo — HU-32
Diagrama de caso de uso — HU-32


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 36
E. Gestión de inventario (transversal)
HU-33
—   Sistema
Descuento automático de inventario
Como sistema, quiero descontar automáticamente del inventario de la sede las unidades vendidas al guardar un
pedido, para mantener el inventario actualizado sin intervención manual adicional.
Criterios de aceptación:
• El descuento se aplica por unidad completa, incluyendo los cócteles definidos dentro del alcance.
• El descuento afecta únicamente el inventario de la sede donde se registró el pedido.
• Si no hay unidades suficientes disponibles, el sistema no permite guardar ese producto en el pedido.
• El traslado de inventario entre sedes, el manejo de stock mínimo y las alertas de reposición están fuera del alcance.
Trazabilidad: Propuesta comercial: 10, 18
Diagrama de flujo — HU-33
Diagrama de caso de uso — HU-33


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 37
F. Historias complementarias identificadas en la revisión
Las siguientes historias cubren requisitos que la propuesta comercial contempla dentro del alcance pero que no tenían una
historia de usuario asociada en el documento original. Se presentan con la misma estructura; sus diagramas de flujo y de
caso de uso se elaborarán una vez el cliente apruebe su incorporación.
HU-35
—   Administrador
Parametrización de mesas por sede
Como administrador, quiero registrar y mantener las mesas de cada sede, para que los meseros puedan asociar los
pedidos a una mesa existente.
Criterios de aceptación:
• Cada mesa se registra asociada a una única sede, con un identificador o número único dentro de esa sede.
• El sistema no permite eliminar una mesa que tenga pedidos asociados; se inactiva para conservar la trazabilidad.
• Las mesas registradas se visualizan en el módulo de pedidos de la sede correspondiente (HU-19).
Trazabilidad: Propuesta comercial: 4 (gestión de mesas), 9
HU-36
—   Sistema
Protección de credenciales y manejo controlado de errores
Como responsable del sistema, quiero que las credenciales y la información sensible estén protegidas y que los errores
se manejen de forma controlada, para reducir el riesgo de exposición de información.
Criterios de aceptación:
• Las contraseñas se almacenan mediante un mecanismo seguro de cifrado, nunca en texto plano.
• Los mensajes de error mostrados al usuario no revelan detalles técnicos, estructuras internas ni credenciales.
• La información sensible no se expone en la interfaz ni en los registros de operación.
Trazabilidad: Propuesta comercial: 16.5, 16.6
HU-37
—   Sistema
Validación de entradas y protección frente a inyección
Como responsable del sistema, quiero que todas las entradas se validen y que el acceso a datos sea seguro, para
evitar el procesamiento de información no válida y ataques de inyección.
Criterios de aceptación:
• Toda información ingresada por el usuario se valida en el backend antes de ser procesada.
• Las consultas a la base de datos utilizan mecanismos parametrizados o equivalentes.
• Los datos que no cumplan tipo, longitud, formato o valores permitidos son rechazados con un mensaje controlado.
Trazabilidad: Propuesta comercial: 16.3, 16.4
HU-38
—   Sistema
Registro y trazabilidad de operaciones
Como responsable del sistema, quiero que las operaciones relevantes queden registradas, para garantizar la
trazabilidad de pedidos, pagos y accesos.
Criterios de aceptación:
• Cada pedido registra, como mínimo: usuario, sede, mesa, fecha y hora, productos, cantidades y estado.
• El cierre del pedido registra el medio de pago y el usuario que realizó la operación.
• Los eventos relevantes de acceso y operación quedan almacenados para procesos de revisión.
• Dentro del alcance actual, el único reporte visible para los usuarios es el reporte de ventas.
Trazabilidad: Propuesta comercial: 13, 16.7
HU-39
—   Usuario del sistema
Interfaz responsive y navegación consistente


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 38
Como usuario del sistema, quiero una interfaz responsive y clara en el navegador Chrome, para operar cómodamente
desde distintos dispositivos y tamaños de ventana.
Criterios de aceptación:
• La interfaz se adapta a diferentes tamaños de ventana sin desconfiguraciones.
• La navegación es clara y organizada, con mensajes de confirmación y error en las operaciones relevantes.
• El idioma de la interfaz del frontend debe confirmarse con el cliente: la propuesta indica idioma inglés, mientras que los
mockups de referencia están en español.
Trazabilidad: Propuesta comercial: 14, 17
HU-40
—   Sistema
Rendimiento y concurrencia
Como responsable del sistema, quiero que las transacciones y consultas respondan en tiempos aceptables con varios
usuarios conectados, para no afectar la operación diaria del bar.
Criterios de aceptación:
• El tiempo máximo esperado de respuesta para transacciones y consultas es de 2 segundos en condiciones normales de
operación.
• El sistema soporta una concurrencia mínima de 20 usuarios simultáneos.
• Se ejecutan pruebas funcionales y de operación sobre las funcionalidades principales.
Trazabilidad: Propuesta comercial: 15
G. Matriz de trazabilidad con la propuesta comercial
La matriz relaciona cada historia de usuario con las secciones de la propuesta comercial (versión 1.1) que le dan origen.
Historia
Título
Actor
Propuesta comercial
HU-01
Inicio de sesión con identificación y contraseña
Usuario del sistema
5, 7.1, 16.2, 16.5, 16.6
HU-02
Cierre de sesión automático por inactividad
Usuario del sistema
16, 16.2
HU-03
Sesión única simultánea
Usuario del sistema
16.2
HU-04
Validación de autorización por sede
Usuario del sistema
8, 16.1
HU-05
Validación de campos obligatorios en formularios
Usuario del sistema
7, 14, 16.3
HU-06
Cierre de sesión manual
Usuario del sistema
16.2
HU-34
Protección de peticiones mediante JWT
Sistema
16, 16.1, 16.2
HU-07
Registro de nuevo usuario
Administrador
7.1, 16.5
HU-08
Edición o inactivación de usuario
Administrador
7.1, 13, 16.1
HU-09
Habilitación de permisos adicionales (mesero/cajero)
Administrador
5.1, 6
HU-10
Registro de nueva sede
Administrador
7.2, 10
HU-11
Registro de nuevo producto
Administrador
7.4, 10
HU-12
Registro de proveedor y asociación a productos
Administrador
4, 7.4, 18
HU-13
Selección de sede de trabajo
Administrador
6, 8
HU-14
Toma de pedidos como mesero
Administrador con permiso de
mesero
6
HU-15
Procesamiento de pagos como cajero
Administrador con permiso de
cajero
6, 11
HU-16
Consulta y modificación de productos
Administrador
5.1, 7.4, 10
HU-17
Reporte de ventas consolidado exportable
Administrador
12.2
HU-18
Consulta de información general autorizada
Administrador
5.1, 16.1
HU-19
Consulta de mesas disponibles
Mesero
5.2, 9, 18
HU-20
Selección de mesa para nuevo pedido
Mesero
5.2, 9
HU-21
Consulta de inventario disponible
Mesero
5.2, 10


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 39
Historia
Título
Actor
Propuesta comercial
HU-22
Registro y guardado del pedido
Mesero
9, 13
HU-23
Adición de productos a pedido abierto
Mesero
5.2, 9, 13
HU-24
Visualización del estado de las mesas
Mesero
5.2, 9
HU-25
Consulta del estado de un pedido
Mesero
5.2, 9
HU-26
Consulta de pedidos pendientes de pago
Cajero
5.3, 11
HU-27
Procesamiento de pago en efectivo
Cajero
5.3, 11, 18
HU-28
Procesamiento de pago con tarjeta
Cajero
5.3, 11
HU-29
Cierre del pedido tras el pago
Cajero
9, 11, 13
HU-30
Generación de información de facturación
Cajero
11, 18
HU-31
Consulta y filtro del reporte de ventas de la sede
Cajero
12.1
HU-32
Exportación del reporte de ventas a Excel
Cajero
12.1, 16.1
HU-33
Descuento automático de inventario
Sistema
10, 18
HU-35
Parametrización de mesas por sede
Administrador
4 (gestión de mesas), 9
HU-36
Protección de credenciales y manejo controlado de
errores
Sistema
16.5, 16.6
HU-37
Validación de entradas y protección frente a inyección
Sistema
16.3, 16.4
HU-38
Registro y trazabilidad de operaciones
Sistema
13, 16.7
HU-39
Interfaz responsive y navegación consistente
Usuario del sistema
14, 17
HU-40
Rendimiento y concurrencia
Sistema
15
H. Observaciones de la revisión
Ajustes realizados sobre el documento original y puntos que requieren confirmación del cliente o del equipo de diseño.
Elemento
Observación / ajuste realizado
Sección
HU-09
Se amplió la combinación de roles para incluir Administrador+Mesero+Cajero, dado que la propuesta
permite habilitar uno o varios roles operativos.
6
HU-11
Precio de compra, estado y proveedor se declaran obligatorios; se retiró la redacción que presentaba
el proveedor como opcional.
7.4
HU-11 / HU-33
Se separó el catálogo centralizado (código, nombre, precios) del inventario, que se gestiona por sede.
2, 10
HU-02 / HU-34
Se incorporó el tiempo máximo de sesión de 30 minutos, que no estaba contemplado en las historias
originales.
16
HU-31
Se homologaron los filtros del reporte del cajero (fecha inicial, fecha final y sede autorizada) y los
campos mínimos del reporte.
12.1
HU-01 / HU-07 /
HU-36
Se explicitó el almacenamiento cifrado de contraseñas y el manejo controlado de mensajes de error.
16.5, 16.6
HU-04 / HU-05 /
HU-34
Se aclaró que las validaciones de autorización y de datos se ejecutan en el backend y no solo en la
interfaz.
16
HU-26 / HU-32
Se homologó la expresión “sede(s) autorizada(s)”, ya que un cajero puede tener más de una sede
asignada.
5.3, 8
HU-35 a HU-40
Se incorporaron historias complementarias para cubrir requisitos de la propuesta sin historia asociada:
gestión de mesas, seguridad, trazabilidad, experiencia de usuario y rendimiento.
4, 13, 14, 15, 16
Mockups
Las figuras del documento anterior citaban rangos de historias incorrectos (p. ej. “HU-16 a HU-20” para
el perfil mesero). Las referencias se corrigieron en la sección G.
—
Mockups
El formulario de creación de producto muestra “Categoría” y “Stock mínimo”, y no muestra precio de
compra, estado ni proveedor. El manejo de stock mínimo está fuera de alcance; se recomienda ajustar
el formulario en la etapa de diseño UI/UX.
7.4, 18
Mockups
Las pantallas “Reporte de inventario” y “Cierre de caja” no corresponden a funcionalidades del alcance
actual (el único reporte contemplado es el de ventas). Se marcan como referenciales o candidatas a
una fase futura.
12, 13, 18
Mockups
Los mockups están en español, mientras que la propuesta indica interfaz del frontend en idioma inglés.
Se requiere confirmación del cliente.
14


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 40
I. Mockups de referencia
Los siguientes mockups ilustran cómo podría verse la interfaz de REFUGIO GESTIÓN para cada perfil. Son wireframes de
alto nivel pensados para dar contexto visual a las historias de usuario; el diseño final (colores de marca, tipografía y
componentes) se define en la etapa de diseño UI/UX del proyecto. Cada figura indica las historias de usuario que
representa.
Figura 1. Inicio de sesión (HU-01)
Figura 2. Sesión expirada por inactividad (HU-02, HU-34)
Figura 3. Sesión única simultánea (HU-03)
Figura 4. Cierre de sesión manual (HU-06)
Figura 5. Acceso denegado por sede no autorizada (HU-04)
Figura 6. Creación de producto y validación de campos obligatorios
(HU-05, HU-11)
El formulario debe incluir precio de compra, estado y proveedor; “Stock
mínimo” está fuera de alcance.
Figura 7. Gestión de usuarios (HU-07, HU-08)
Figura 8. Gestión de sedes (HU-10)


REFUGIO GESTIÓN — Casos de uso / Historias de usuario
Nexora Software · Versión 2.0
Página 41
Figura 9. Gestión de productos (catálogo centralizado) (HU-11,
HU-16)
Figura 10. Vista de mesas y estado por sede (HU-19, HU-20,
HU-24)
Figura 11. Registro de pedido y detalle de la mesa (HU-21, HU-22,
HU-23)
Figura 12. Procesamiento de pago y cierre del pedido (HU-26 a
HU-30)
Figura 13. Reporte de ventas consolidado (HU-17)
Figura 14. Reporte de inventario por sede (Referencial)
No corresponde a una historia del alcance actual: el único reporte
contemplado es el de ventas.
Figura 15. Vista de mesas (perfil mesero) (HU-19, HU-24)
Figura 16. Cierre de caja (Fuera de alcance)
No contemplado en la propuesta comercial; candidato a una fase futura.
NEXORA SOFTWARE — Soluciones tecnológicas para optimizar, conectar y transformar procesos.
