# Alcance aprobado para Sprints 1 a 6

Este alcance amplía la entrega previamente aprobada para los Sprints 1 a 4,
según la solicitud de completar el proyecto hasta el Sprint 6.

## Incluido

- **Sprint 1:** HU-01, HU-02, HU-03, HU-05, HU-06, HU-34, HU-36 y HU-37.
- **Sprint 2:** HU-04, HU-07, HU-08, HU-09, HU-10 y HU-35.
- **Sprint 3:** HU-11, HU-12, HU-13, HU-16 y HU-18.
- **Sprint 4:** HU-19, HU-20, HU-21, HU-22, HU-23, HU-24, HU-25 y HU-33.
- **Sprint 5:** HU-14, HU-15, HU-26, HU-27, HU-28, HU-29 y HU-30.
- **Sprint 6:** HU-17, HU-31, HU-32, HU-38, HU-39 y HU-40.

## Excluido

HU-14 y HU-15 no se incorporan como permisos asignables: el administrador
conserva las capacidades operativas globales ya confirmadas. También queda
excluido todo lo definido en la sección 18 de la propuesta comercial.

## Exclusiones transversales de esta entrega

- La interfaz usa HTML5/CSS3/JavaScript nativo y consume endpoints REST/JSON.
- Despliegue con Nginx, TLS o Gunicorn.
- Funcionalidades no listadas expresamente en los Sprints 1 a 6.

## Decisiones funcionales confirmadas

- El administrador es global, no tiene sedes asignadas y puede consultar las
  sedes del negocio. Siempre tiene capacidades de mesero y cajero; estas no
  son asignables ni desactivables por separado. Meseros y cajeros no
  administradores solo operan en sedes asignadas.
- La sede de trabajo seleccionada se almacena en la sesión asociada al `jti`;
  el backend valida en cada petición que siga autorizada para el usuario.
- El inventario se carga por sede mediante una operación de administrador que
  permite crear la existencia inicial y sumar unidades posteriormente. No se
  permite reducir manualmente la existencia; los pedidos la descuentan.
- El proveedor tiene un ID generado por la base de datos, un nombre único por
  coincidencia exacta y un número de contacto opcional. Cada producto se asocia
  con un proveedor. El precio de compra no puede superar el precio de venta.
- Los usuarios nuevos quedan activos al crearse; el alta no recibe un campo
  `estado`. Por decisión posterior, el correo electrónico es obligatorio y se
  valida al crear una cuenta; en una actualización parcial puede omitirse.
- HU-18 permite consultar usuarios, sedes, productos, proveedores, inventario,
  pedidos abiertos y estados de mesas.
- Un JWT válido se renueva en cada petición autenticada, con expiración a los
  3 minutos de actividad y un límite absoluto de 30 minutos desde el login.

## Aprobación posterior: interfaz web

- La interfaz usa HTML5, CSS3 y JavaScript nativo, sin React.
- La sidebar mantiene los mismos módulos para todos los usuarios. Al entrar a
  un módulo no permitido, se muestra un aviso de permisos; el backend sigue
  siendo quien valida autorización en cada petición.
- La interfaz cubre los módulos backend en alcance: usuarios, sedes, catálogo,
  inventario, mesas, pedidos, caja, facturación visible en pantalla y reportes
  de ventas exportables a Excel.