# Alcance aprobado para Sprints 1 a 4

## Incluido

- **Sprint 1:** HU-01, HU-02, HU-03, HU-05, HU-06, HU-34, HU-36 y HU-37.
- **Sprint 2:** HU-04, HU-07, HU-08, HU-09, HU-10 y HU-35.
- **Sprint 3:** HU-11, HU-12, HU-13, HU-16 y HU-18.
- **Sprint 4:** HU-19, HU-20, HU-21, HU-22, HU-23, HU-24, HU-25 y HU-33.

## Excluido

No implementar HU-14, HU-15, HU-17, HU-26 a HU-32 ni HU-38 a HU-40.
También queda excluido todo lo definido en la sección 18 de la propuesta
comercial.

## Exclusiones transversales de esta entrega

- En la implementación inicial del backend, frontend; queda incorporada por
  aprobación posterior como una entrega HTML5/CSS3/JavaScript que consume los
  endpoints existentes REST/JSON.
- Exportación a Excel.
- Despliegue con Nginx, TLS o Gunicorn.
- Pagos, cierre de pedidos y otras funcionalidades posteriores al alcance
  definido para el Sprint 4.

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
- El proveedor tiene un ID generado por la base de datos y un nombre único por
  coincidencia exacta. Cada producto se asocia con un proveedor.
- Los usuarios nuevos quedan activos al crearse; el alta no recibe un campo
  `estado`. El correo electrónico heredado del backend se conserva opcional y
  no es requisito de HU-07.
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
  inventario, mesas y pedidos abiertos. No añade pagos, cierre, reportes,
  exportación ni despliegue.