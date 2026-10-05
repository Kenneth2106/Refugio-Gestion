 Refugio Gestión   
  
Versión: 1.1  
           
  
 1. NEXORA SOFTWARE  
Nexora Software es una empresa dedicada al desarrollo de soluciones tecnológicas 
orientadas a mejorar y facilitar los procesos de diferentes tipos de negocios. Nuestro 
trabajo se enfoca en analizar las necesidades de cada organización y transformarlas en 
herramientas de software prácticas, modernas y fáciles de utilizar.  
Como empresa de desarrollo de software, buscamos crear soluciones que permitan a 
nuestros clientes organizar mejor su información, optimizar sus procesos y tener un mayor 
control sobre las actividades que realizan diariamente. Para esto, contamos con un 
enfoque basado en el análisis de requerimientos, diseño, desarrollo, implementación y 
mejora continua de sistemas de información.  
Nuestra trayectoria se ha construido a partir de más de 30 años de experiencia en el 
desarrollo e implementación de soluciones tecnológicas para diferentes sectores. 
Durante este tiempo, hemos participado en proyectos relacionados con sistemas de 
información, automatización de procesos, gestión empresarial, administración de datos y 
desarrollo de plataformas digitales, adquiriendo una amplia experiencia en el análisis de 
necesidades y creación de soluciones adaptadas a cada organización.  
Gracias a esta experiencia, Nexora Software cuenta con la capacidad para desarrollar 
soluciones confiables, escalables y orientadas a las necesidades reales de nuestros 
clientes. Como parte de nuestro compromiso con la innovación y la transformación digital, 
desarrollamos REFUGIO GESTIÓN, una solución diseñada para El Refugio Bar, aplicando 
nuestra experiencia en gestión de procesos, administración de información y desarrollo de 
sistemas para ofrecer una herramienta que permita mejorar el control de las operaciones 
del establecimiento, optimizar sus procesos y facilitar la toma de decisiones.  
 
  
  


seguridades basadas en el desarrollo de una aplicación web responsive, accesible desde el 
navegador Chrome, que garantice tiempos de respuesta ágiles y buenas prácticas de 
seguridad basadas en el estándar OWASP. Cada sede operará con su propio inventario, 
mientras que la información de productos (código y precio) se mantendrá centralizada y 
estandarizada para todo el negocio, permitiendo así consistencia en la operación sin 
importar la sede desde la cual se trabaje.  
Este alcance se enmarca en las funcionalidades descritas en las secciones de 
requerimientos por perfil (mesero, cajero y administrador) y requerimientos transversales, 
y excluye explícitamente aquellos puntos definidos en la sección de requerimientos fuera 
de alcance, los cuales podrán ser considerados en fases futuras del proyecto si el cliente 
así lo requiere.  
2. RESUMEN EJECUTIVO  
REFUGIO GESTIÓN será una aplicación web diseñada para apoyar la operación diaria de El 
Refugio Bar mediante la gestión centralizada de usuarios, sedes, productos, proveedores, 
pedidos, pagos, inventario y reportes de ventas.  
El sistema contará con tres perfiles principales de operación:  
• 
Administrador  
• 
Mesero  
• 
Cajero  
Cada perfil tendrá acceso únicamente a las funcionalidades autorizadas según sus 
permisos.  
La solución permitirá administrar múltiples sedes manteniendo una operación organizada. 
Los productos conservarán un código, nombre y precio estandarizados para el negocio, 
mientras que el inventario será gestionado de manera independiente para cada sede.  
De esta manera, una sede podrá tener una cantidad disponible diferente de un mismo 
producto, sin afectar la información general del catálogo de productos.  
REFUGIO GESTIÓN permitirá registrar pedidos, controlar el estado de las mesas, descontar 
automáticamente las unidades correspondientes del inventario al guardar un pedido, 
procesar pagos, cerrar ventas y generar reportes de acuerdo con el perfil autorizado.  
  


3. OBJETIVO DE LA SOLUCIÓN  
Desarrollar e implementar una aplicación web responsive denominada REFUGIO GESTIÓN, 
orientada a mejorar el control y la gestión de las operaciones de El Refugio Bar.  
La solución tendrá como objetivos principales:  
• 
Centralizar la gestión de la información operativa y administrativa.  
• 
Facilitar el registro y control de pedidos.  
• 
Gestionar la operación de múltiples sedes.  
• 
Controlar el inventario de manera independiente por sede.  
• 
Garantizar la trazabilidad de los pedidos y ventas realizadas.  
• 
Gestionar los accesos mediante usuarios, roles y permisos.  
• 
Facilitar el proceso de cobro y cierre de pedidos.  
• 
Generar reportes de ventas para apoyar la toma de decisiones.  
• 
Reducir errores derivados de procesos manuales.  
• 
Proteger la información mediante controles de seguridad aplicables al sistema.  
  
4. ALCANCE GENERAL DEL PROYECTO  
El proyecto contempla el desarrollo de una aplicación web responsive, accesible mediante 
el navegador Google Chrome, diseñada para operar desde computadores u otros 
dispositivos que dispongan de un navegador compatible.  
El sistema permitirá gestionar las operaciones de El Refugio Bar desde sus diferentes 
sedes, conservando una estructura centralizada para la información general del negocio y 
una gestión independiente para el inventario de cada sede.  
El alcance funcional contempla:  
• 
Parametrización y administración de usuarios.  
• 
Administración de roles y permisos.  
• 
Parametrización de sedes.  
• 
Administración de productos.  
• 
Administración de proveedores.  
• 
Gestión de mesas.  
• 
Registro y modificación de pedidos abiertos.  
• 
Consulta de inventario disponible.  


• 
Descuento automático del inventario al registrar pedidos.  
• 
Procesamiento de pagos.  
• 
Cierre de pedidos.  
• 
Generación de factura física visualizada en pantalla.  
• 
Generación y consulta de reportes de ventas.  
• 
Exportación de reportes autorizados a Excel.  
• 
Control de acceso según usuario, rol y sede.  
• 
Registro y trazabilidad de las operaciones realizadas.  
Las funcionalidades que no se encuentran incluidas en esta propuesta se detallan en el 
apartado “Funcionalidades fuera de alcance”.  
  
5. PERFILES DEL SISTEMA Y CONTROL DE ACCESO  
El sistema contará con tres perfiles principales:  
5.1 Administrador  
El administrador tendrá acceso a las funcionalidades de gestión y parametrización del 
sistema.  
Además, el administrador podrá contar con permisos operativos adicionales para 
desempeñar funciones de mesero y/o cajero, según la configuración definida para su 
usuario.  
Por lo tanto, un mismo usuario administrador podrá tener habilitados uno o varios roles 
operativos, dependiendo de las necesidades del negocio.  
  
  
  
  
 
 


El administrador podrá:  
• 
Administrar usuarios.  
• 
Parametrizar sedes.  
• 
Administrar productos.  
• 
Consultar información general autorizada.  
• 
Consultar reportes de ventas de todas las sedes.  
• 
Exportar reportes a Excel.  
• 
Tomar pedidos cuando tenga habilitada la función de mesero.  
• 
Procesar pagos y cerrar pedidos cuando tenga habilitada la función de cajero.  
El acceso a las funcionalidades adicionales estará determinado por los permisos asignados 
al usuario.  
 
5.2 Mesero  
El perfil de mesero estará orientado a la gestión de pedidos y mesas.  
El mesero podrá:  
• 
Acceder únicamente a las sedes para las cuales se encuentre autorizado.  
• 
Consultar las mesas disponibles en la sede seleccionada.  
• 
Seleccionar la mesa sobre la cual se registrará el pedido.  
• 
Consultar el inventario disponible en la sede seleccionada.  
• 
Registrar los productos solicitados por el cliente.  
• 
Guardar pedidos.  
• 
Añadir productos a un pedido existente mientras este se encuentre en estado 
ABIERTO.  
• 
Consultar el estado del pedido.  
• 
Visualizar el estado de las mesas como LIBRE u OCUPADA.  
Al guardar un pedido, el sistema realizará el descuento automático de las unidades 
correspondientes del inventario de la sede seleccionada.  
  


5.3 Cajero  
El perfil de cajero estará orientado al proceso de pago y cierre de pedidos.  
El cajero podrá:  
• 
Acceder a los pedidos correspondientes a la sede para la cual se encuentre 
autorizado.  
• 
Consultar pedidos que se encuentren pendientes de pago.  
• 
Procesar pagos en efectivo.  
• 
Procesar pagos con tarjeta.  
• 
Cerrar el pedido después de registrar el pago.  
• 
Cambiar el estado del pedido de ABIERTO a CERRADO.  
• 
Generar la información de facturación correspondiente al pedido.  
• 
Consultar reportes de ventas de su sede.  
• 
Filtrar los reportes de ventas por fecha.  
• 
Exportar los reportes autorizados a Excel.  
El sistema no contemplará la división de un mismo pago entre varias personas.  
Tampoco se aplicará una comisión adicional por pagos realizados mediante tarjeta.  
6. ADMINISTRADOR CON FUNCIONES DE MESERO Y 
CAJERO  
El sistema permitirá que un usuario con perfil de administrador pueda desempeñar 
adicionalmente funciones de mesero y/o cajero.  
Esta funcionalidad será controlada mediante permisos.  
Por ejemplo, un usuario administrador podrá tener configurado:  
• 
Rol de Administrador únicamente.  
• 
Administrador + Mesero.  
• 
Administrador + Cajero.  
Cuando el administrador ingrese al sistema, podrá acceder a las funcionalidades 
correspondientes a los roles que tenga habilitados.  


Operación del administrador como mesero  
Si el administrador tiene habilitado el permiso de mesero, el sistema permitirá seleccionar 
la sede sobre la cual realizará la operación.  
La selección funcionará de la siguiente manera:  
1. El sistema consultará las sedes autorizadas para el usuario.  
2. Si el usuario administrador tiene acceso a una sola sede, el sistema trabajará 
automáticamente con dicha sede.  
3. Si el administrador tiene autorización para operar en varias sedes, el sistema 
mostrará las sedes disponibles para que seleccione en cuál desea trabajar.  
4. Una vez seleccionada la sede, el sistema mostrará únicamente:  
a. Las mesas correspondientes a esa sede.  
b. El inventario disponible de esa sede.  
c. Los pedidos relacionados con esa sede.  
5. El pedido quedará registrado con la información del usuario que realizó la 
operación y la sede seleccionada.  
De esta manera, el administrador podrá tomar pedidos en diferentes sedes sin mezclar la 
información, el inventario ni las operaciones entre ellas.  
Operación del administrador como cajero  
Si el administrador tiene habilitado el permiso de cajero, podrá realizar las operaciones 
correspondientes al proceso de pago.  
Cuando tenga acceso a varias sedes, deberá seleccionar la sede sobre la cual realizará la 
operación. El sistema mostrará únicamente los pedidos abiertos correspondientes a dicha 
sede.  
Esto garantiza que los pagos y cierres de pedidos sean procesados dentro de la sede 
correcta.  
  
 


7. PARAMETRIZACIÓN DEL SISTEMA  
La parametrización permitirá configurar la información necesaria para el funcionamiento 
del sistema.  
Los campos obligatorios serán validados por el sistema y no permitirán guardar el registro 
si la información requerida se encuentra incompleta.  
Los campos opcionales podrán dejarse vacíos cuando su información no sea necesaria 
para el registro.  
  
7.1 Parametrización de usuarios  
Para crear un usuario se deberán registrar los siguientes campos:  
Campos obligatorios   
• 
Identificación del usuario.  
• 
Nombres.  
• 
Contraseña.  
• 
Estado del usuario.  
• 
Sede  
El sistema validará que:  
• 
La identificación no se encuentre registrada previamente.  
• 
El nombre de usuario sea único.  
El usuario tenga al menos un rol o conjunto de permisos asignado.  
• 
El usuario tenga al menos una sede autorizada cuando su función requiera operar 
sobre una sede.  
• 
Un usuario inactivo no pueda iniciar sesión.  
  
 


7.2 Parametrización de sedes  
Para registrar una sede se deberán ingresar los siguientes campos:  
Campos obligatorios  
• 
Código de sede.  
• 
Nombre de la sede.  
• 
Dirección.  
El sistema validará que el código de la sede sea único  
  
7.4 Parametrización de productos  
Para registrar un producto se deberán ingresar los siguientes campos:  
Campos obligatorios  
• 
Código del producto.  
• 
Nombre del producto.  
• 
Precio de venta.  
• 
Precio de compra 
• 
Estado del producto.  
• 
Proveedor  
8. VALIDACIÓN DE USUARIOS Y SEDES  
El sistema contará con un control de acceso basado en la relación entre:  
• 
Usuario.  
• 
Rol o permisos.  
• 
Sede o sedes autorizadas.  
Antes de permitir una operación relacionada con una sede, el sistema validará que el 
usuario tenga autorización para operar en ella.  


Por ejemplo: • Un mesero solo podrá registrar pedidos en las sedes 
asignadas.  
• 
Un cajero solo podrá procesar pagos correspondientes a las sedes autorizadas.  
• 
Un administrador podrá operar en varias sedes únicamente cuando estas hayan 
sido asignadas a su usuario.  
• 
Un usuario no podrá consultar ni modificar operaciones de una sede para la cual no 
tenga autorización.  
Cuando un usuario tenga acceso a varias sedes, el sistema permitirá seleccionar la sede 
antes de realizar operaciones que dependan de ella.  
La sede seleccionada determinará la información que podrá visualizarse durante la 
operación, incluyendo mesas, inventario y pedidos.  
Esta validación permitirá evitar operaciones no autorizadas y garantizar que la información 
de cada sede sea tratada correctamente.  
  
9. GESTIÓN DE PEDIDOS  
El proceso de gestión de pedidos funcionará de la siguiente manera:  
1. El usuario autorizado selecciona la sede, cuando aplique.  
2. El sistema valida que el usuario tenga permisos para operar en dicha sede.  
3. Se visualizan las mesas correspondientes a la sede seleccionada.  
4. El usuario selecciona una mesa.  
5. El sistema consulta el inventario disponible en la sede.  
6. El usuario selecciona los productos solicitados. 7. El sistema valida la disponibilidad 
del producto.  
8. El pedido se registra en estado ABIERTO.  
9. Al guardar el pedido, se descuenta automáticamente del inventario la cantidad 
correspondiente.  
10. Mientras el pedido permanezca abierto, podrán agregarse productos adicionales.  
11. Cada operación quedará asociada al usuario que realizó el pedido.  
12. La fecha del pedido corresponderá al momento en que fue solicitado.  
13. Una vez realizado el pago, el pedido podrá cerrarse.  
14. El estado cambiará de ABIERTO a CERRADO.  


La mesa permanecerá identificada como OCUPADA mientras tenga una operación abierta 
y podrá quedar disponible una vez finalice el proceso correspondiente.  
  
10. GESTIÓN DE INVENTARIO  
El inventario será administrado de manera independiente para cada sede.  
El sistema mantendrá centralizada la información general del producto, incluyendo:  
• 
Código.  
• 
Nombre.  
• 
Precio.  
• 
Inventario.  
Cada sede tendrá su propia cantidad disponible de inventario.  
Por ejemplo, un mismo producto podrá tener:  
• 
20 unidades disponibles en la Sede A. • 10 unidades disponibles en la Sede B.  
• 
0 unidades disponibles en la Sede C.  
El inventario será manejado por unidades completas.  
Los productos vendidos, incluidos los cócteles definidos dentro del alcance del negocio, 
serán descontados por unidad.  
El traslado de inventario entre sedes no se encuentra incluido en el alcance de esta 
propuesta.  
Tampoco se incluye el manejo de stock mínimo ni alertas automáticas de reposición.  
  
11. PROCESO DE PAGO Y CIERRE DE PEDIDOS  
El proceso de pago será realizado por usuarios que tengan autorizado el perfil o permiso 
de cajero.  
El sistema permitirá registrar pagos mediante:  


• 
Efectivo.  
• 
Tarjeta.  
Los pagos realizados con tarjeta no generarán una comisión adicional dentro del sistema.  
Para realizar el cierre:  
1. El cajero selecciona el pedido abierto.  
2. El sistema muestra la información correspondiente al pedido.  
3. Se registra el medio de pago.  
4. Se procesa el pago.  
5. El pedido cambia de estado ABIERTO a CERRADO.  
6. Se genera la información de facturación correspondiente.  
La información de facturación será obtenida a partir de los datos registrados en el sistema 
y del pedido procesado, evitando la modificación manual de información ya existente.  
El proyecto contempla la generación de factura física o visualización de la factura en 
pantalla.  
La factura electrónica no hace parte del alcance actual.  
No se permitirá dividir el valor de un mismo pedido entre varias personas.  
  
12. REPORTES DEL SISTEMA  
El sistema generará reportes de ventas de acuerdo con los permisos asignados a cada 
perfil.  
12.1 Reporte de ventas para cajero  
El cajero podrá consultar únicamente la información correspondiente a la sede o  
sedes para las cuales tenga autorización.  
El reporte permitirá filtrar por:  
• 
Fecha más reciente.  
• 
Fecha más antigua.  


• 
Sede autorizada.  
El reporte incluirá como mínimo los siguientes campos:  
• 
Número o identificador del producto  
• 
Nombre producto  
• 
Cantidad vendida  
• 
Valor compra  
• 
Valor venta  
• 
Ganancia  
• 
Sede  
El cajero podrá exportar el reporte autorizado en formato Excel.  
  
12.2 Reporte de ventas para administrador  
El administrador podrá consultar reportes correspondientes a todas las sedes que tenga 
autorización para visualizar.  
El reporte permitirá filtrar por:  
• 
Fecha inicial.  
• 
Fecha final.  
• 
Una sede específica.  
• 
Todas las sedes autorizadas.  
• 
Estado del pedido.  
• 
Medio de pago.  
El reporte incluirá como mínimo los siguientes campos:  
• 
Número o identificador del producto  
• 
Nombre producto  
• 
Cantidad vendida  
• 
Valor compra  
• 
Valor venta  
• 
Ganancia  
• 
Sede  
  


El administrador podrá consultar la información consolidada de las sedes autorizadas y 
exportar los resultados en formato Excel.  
13. TRAZABILIDAD Y REGISTRO DE OPERACIONES  
El sistema conservará información de las operaciones realizadas con el fin de garantizar 
trazabilidad.  
Cada pedido deberá registrar, como mínimo:  
• 
Usuario que realizó el pedido.  
• 
Sede donde se realizó la operación.  
• 
Mesa seleccionada.  
• 
Fecha y hora del registro.  
• 
Productos solicitados.  
• 
Cantidades.  
• 
Estado del pedido.  
Cuando se realice el cierre del pedido, se registrará la información correspondiente al 
proceso de pago y al usuario que realizó la operación, cuando aplique.  
Todos los registros operativos generados dentro del alcance del sistema serán 
almacenados.  
Sin embargo, dentro del alcance actual del proyecto, el reporte visible para los usuarios 
será el reporte de ventas, según los permisos establecidos  
14. REQUERIMIENTOS DE EXPERIENCIA DE USUARIO  
La solución contará con una interfaz diseñada para facilitar la operación diaria de los 
usuarios.  
Se contemplan los siguientes requerimientos:  
• 
Diseño responsive.  
• 
Adaptación de la interfaz a diferentes tamaños de ventana.  
• 
Navegación clara y organizada.  
• 
Formularios con validación de campos obligatorios.  
• 
Mensajes de confirmación y error para las operaciones relevantes.  
• 
Visualización organizada de la información.  
• 
Acceso a las funcionalidades según el perfil y permisos del usuario.  


• 
Interfaz del frontend en idioma inglés.  
La interfaz deberá mantener una correcta visualización y no presentar desconfiguraciones 
al modificar el tamaño de la ventana del navegador.  
15. RENDIMIENTO Y CONCURRENCIA  
REFUGIO GESTIÓN será desarrollado considerando los siguientes requerimientos de 
rendimiento:  
• 
Tiempo máximo esperado de respuesta para transacciones y consultas: 2 
segundos, bajo condiciones normales de operación y carga contempladas para el 
proyecto.  
• 
Soporte para una concurrencia mínima de 20 usuarios simultáneos.  
Se considerarán pruebas funcionales y de operación para validar el comportamiento de las 
funcionalidades principales del sistema.  
  
16. SEGURIDAD Y PRÁCTICAS OWASP APLICABLES  
La seguridad y el control de acceso del sistema se fundamentarán en las prácticas de la 
guía OWASP (Open Web Application Security Project) aplicables a la autenticación, gestión 
de sesiones y control de acceso. La autenticación se implementará mediante JSON Web 
Tokens (JWT), estableciendo un tiempo máximo de sesión de treinta (30) minutos y un 
tiempo de inactividad de tres (3) minutos. Si el usuario supera el período establecido de 
inactividad, la sesión será invalidada automáticamente y deberá autenticarse nuevamente. 
Estos controles serán gestionados y validados en el backend con el propósito de proteger 
las sesiones activas y reducir el riesgo de accesos no autorizados. 
 
La implementación incluirá, dentro del alcance del proyecto, los siguientes controles: 
16.1 Control de acceso y autorización  
El sistema validará que cada usuario únicamente pueda acceder a las funcionalidades 
correspondientes a sus roles y permisos.  


También se validará la autorización sobre las sedes, evitando que un usuario pueda operar, 
consultar o modificar información correspondiente a una sede que no tenga asignada.  
Este control busca reducir riesgos relacionados con accesos no autorizados.  
16.2 Autenticación y gestión de sesiones  
El acceso al sistema requerirá autenticación mediante credenciales de usuario.  
Se implementará:  
• 
Validación de usuarios activos.  
• 
Control de credenciales.  
• 
Cierre automático de sesión después de 3 minutos de inactividad.  
• 
Restricción de multisesión, evitando que un mismo usuario mantenga más de una 
sesión activa simultáneamente.  
• 
Invalidación de la sesión cuando el usuario cierre sesión o expire el tiempo de 
inactividad.  
16.3 Validación de datos de entrada  
Los datos ingresados mediante formularios serán validados antes de ser procesados.  
Se aplicarán controles sobre:  
• 
Campos obligatorios.  
• 
Tipo de información esperada.  
• 
Longitud de los datos.  
• 
Formatos válidos.  
• 
Valores permitidos.  
Esto permitirá reducir errores y evitar el procesamiento de información no válida.  
  


16.4 Protección frente a inyección  
Las operaciones que interactúen con la base de datos deberán implementar mecanismos 
seguros de acceso a los datos, evitando la construcción insegura de consultas a partir de 
información ingresada directamente por el usuario.  
Se utilizarán mecanismos de consulta parametrizada o equivalentes según la tecnología 
seleccionada para el desarrollo.  
16.5 Protección de información sensible  
Las contraseñas de los usuarios no serán almacenadas en texto plano.  
Se implementará un mecanismo seguro de almacenamiento de credenciales mediante 
técnicas de protección adecuadas para contraseñas.  
La información sensible será tratada evitando su exposición innecesaria en la interfaz, 
mensajes de error o registros de operación.  
16.6 Manejo controlado de errores  
Los mensajes mostrados al usuario no deberán revelar información técnica sensible, 
detalles internos de la base de datos, credenciales, estructuras internas o configuraciones 
del sistema.  
Los errores serán controlados para mostrar información comprensible para el usuario y 
conservar la información técnica necesaria para la administración y revisión del sistema.  
  
16.7 Registro y monitoreo de eventos relevantes  
El sistema conservará trazabilidad sobre operaciones importantes, incluyendo el registro 
de pedidos y la identificación del usuario que realizó la operación.  
Los eventos relevantes de acceso y operación podrán ser utilizados para identificar 
comportamientos anómalos y realizar procesos de revisión cuando sea necesario.  
  


17. PLATAFORMA TECNOLÓGICA  
REFUGIO GESTIÓN será implementado como una aplicación web, diseñada para ser 
utilizada mediante un navegador de internet.  
La solución no será desarrollada como una aplicación de escritorio ni como una aplicación 
móvil nativa.  
Las principales características de la plataforma serán:  
• 
Arquitectura basada en aplicación web.  
• 
Acceso mediante navegador.  
• 
Compatibilidad operativa contemplada para Google Chrome.  
• 
Interfaz responsive.  
• 
Acceso mediante autenticación de usuario.  
• 
Control de acceso basado en roles, permisos y sedes autorizadas.  
• 
Gestión centralizada de la información del negocio.  
• 
Operación diferenciada de inventario por sede.  
• 
Persistencia de la información en una base de datos.  
• 
Exportación de los reportes autorizados en formato Excel.  
La plataforma estará orientada a proporcionar una solución accesible, organizada y 
escalable para las necesidades definidas dentro del alcance del proyecto.  
  
18. FUNCIONALIDADES FUERA DE ALCANCE  
Las siguientes funcionalidades no se encuentran incluidas en el desarrollo contemplado en 
esta propuesta:  
• 
Traslado de inventario entre sedes.  
• 
Manejo de stock mínimo.  
• 
Alertas automáticas de reposición.  
• 
Manejo de nómina.  
• 
Reservas de productos.  
• 
Asignación fija de meseros a mesas.  
• 
Compras a proveedores.  
• 
Gestión del proceso completo de abastecimiento.  
• 
Generación de factura electrónica.  
• 
Manejo de Disaster Recovery Plan (DRP).  


• 
Manejo de turnos de trabajo.  
• 
Servicio a domicilio.  
• 
División de pagos entre varias personas para un mismo pedido.  
• 
Interacción directa del cliente final con el sistema.  
• 
Desarrollo de aplicación móvil nativa.  
Estas funcionalidades podrán ser evaluadas para futuras fases del proyecto, previa 
definición de alcance, tiempos y costos adicionales.  
  
19. TIEMPO ESTIMADO DEL PROYECTO  
El tiempo estimado para el desarrollo del proyecto es de:  
11 SEMANAS 20. METODOLOGÍA DE TRABAJO  
El proyecto será desarrollado utilizando una metodología Ágil.  
Esta metodología permitirá organizar el trabajo en etapas de desarrollo, priorizando las 
funcionalidades definidas en el alcance y facilitando el seguimiento continuo del proyecto.  
El proceso de trabajo estará orientado a:  
• 
Planificación de actividades.  
• 
Priorización de funcionalidades.  
• 
Desarrollo incremental.  
• 
Validación de funcionalidades.  
• 
Identificación y corrección de incidencias.  
• 
Seguimiento del avance del proyecto.  
21. PROPUESTA ECONÓMICA  
La inversión correspondiente al desarrollo de REFUGIO GESTIÓN, de acuerdo con el 
alcance definido en esta propuesta, es la siguiente:  
VALOR DEL PROYECTO  


$220.374.000 COP  
Valor expresado antes de IVA.  
El valor indicado corresponde al desarrollo de las funcionalidades y requerimientos 
contemplados dentro del alcance de la presente propuesta comercial.  
El IVA no se encuentra incluido en el valor anteriormente indicado y será aplicado 
conforme a la normativa tributaria vigente.  
Cualquier funcionalidad adicional, modificación significativa del alcance o requerimiento 
que se encuentre expresamente definido como fuera de alcance deberá ser evaluado de 
manera independiente, incluyendo su impacto en tiempo y costo.  
  
22. PROPUESTA DE VALOR  
Con REFUGIO GESTIÓN, El Refugio Bar contará con una solución tecnológica orientada a 
fortalecer el control de sus operaciones y centralizar la gestión de la información relevante 
para el negocio.  
La solución permitirá:  
• 
Mayor control sobre las operaciones realizadas en cada sede.  
• 
Gestión organizada de usuarios y permisos.  
• 
Validación de acceso de usuarios por sede.  
• 
Control del inventario de forma independiente por sede.  
• 
Registro y trazabilidad de los pedidos.  
• 
Mayor agilidad en la toma de pedidos.  
• 
Control del proceso de pago y cierre de ventas.  
• 
Consulta organizada de la información comercial.  
• 
Generación de reportes de ventas.  
• 
Exportación de información autorizada a Excel.  
• 
Reducción de errores derivados de procesos manuales.  
• 
Aplicación de controles de seguridad en funcionalidades relevantes.  
• 
Una plataforma web moderna, responsive y orientada a las necesidades operativas 
del negocio.  
NEXORA SOFTWARE presenta esta propuesta con el propósito de desarrollar una solución 
funcional, organizada y alineada con las necesidades definidas para El Refugio Bar.  


Nuestro compromiso es aportar conocimiento y experiencia en el desarrollo de soluciones 
tecnológicas para construir una herramienta que contribuya al mejoramiento de los 
procesos operativos y administrativos del negocio.  
NEXORA SOFTWARE  
Soluciones tecnológicas para optimizar, conectar y transformar procesos.  
  
