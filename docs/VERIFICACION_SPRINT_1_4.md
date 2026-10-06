# Verificación del backend — Sprints 1 a 4

## Resultado de ejecución

- Suite completa: **94 passed**, 0 failed, 1 warning deprecado de
  `starlette.testclient`/`httpx`; 146,64 s.
- Base usada: PostgreSQL real `refugio_db`. Cada prueba creó un esquema
  `test_refugio_<uuid>`, aplicó Alembic y eliminó únicamente ese esquema.
  No se ejecutaron pruebas ni limpieza sobre `public`; no fue necesario
  reiniciar la base.
- Integración reproducible: `test_hu_e2e_sprints_1_4`, 14 de 14 pasos
  aprobados; incluye peticiones concurrentes con clientes/sesiones
  independientes.
- Migraciones: upgrade desde esquema vacío, downgrade a `base` y nuevo upgrade
  aprobados en PostgreSQL.
- Rama de trabajo: `feature/sprint-1-4-backend`. Se usó una rama de fase con
  los cambios de las HUs incluidas, en vez de una rama por HU; no se integró a
  la rama principal.

## Matriz de criterios de aceptación

Los estados cubren el alcance acordado en
[alcance_sprint_1_4.md](./alcance_sprint_1_4.md). “Parcial” identifica criterios
de interfaz que no se pueden verificar sin frontend o cambios expresamente
pospuestos.

| HU | Criterio de aceptación | Estado | Evidencia |
|---|---|---|---|
| HU-01 | Valida existencia y estado ACTIVO al autenticar | cumple | `test_hu01_login_redirects_to_protected_dashboard`; `test_hu08_usuario_inactivo_no_puede_autenticarse` en [test_auth.py](../backend/tests/test_auth.py) y [test_usuarios.py](../backend/tests/test_usuarios.py) |
| HU-01 | Usuario inactivo no entra con la clave correcta | cumple | `test_hu08_usuario_inactivo_no_puede_autenticarse` en [test_usuarios.py](../backend/tests/test_usuarios.py) |
| HU-01 | Usuario inexistente y clave errónea reciben exactamente el mismo mensaje genérico | cumple | `test_hu01_usuario_inexistente_y_clave_erronea_comparten_mensaje` en [test_auth.py](../backend/tests/test_auth.py) |
| HU-01 | La contraseña se almacena como hash, no en texto plano | cumple | `test_hu36_password_persisted_as_bcrypt_hash` en [test_usuarios.py](../backend/tests/test_usuarios.py); `get_password_hash` en [security.py](../backend/app/core/security.py) |
| HU-01 | La contraseña no se transmite en texto plano | parcial | No se configuró ni verificó TLS porque despliegue/TLS están fuera del alcance. |
| HU-01 | El menú muestra opciones según roles y sedes autorizadas | parcial | Backend entrega roles/sedes en `GET /auth/me`; la interfaz de menú está fuera de alcance. [test_auth.py](../backend/tests/test_auth.py) |
| HU-02 | La sesión caduca tras 3 minutos de inactividad y se controla en backend | cumple | `test_hu02_inactivity_expires_session_on_backend` en [test_auth.py](../backend/tests/test_auth.py); paso 9 de [test_e2e_sprints_1_4.py](../backend/tests/test_e2e_sprints_1_4.py) |
| HU-02 | El límite absoluto es 30 minutos aun con actividad | cumple | `test_hu02_maximum_session_duration_expires_despite_activity`; paso 9 de [test_e2e_sprints_1_4.py](../backend/tests/test_e2e_sprints_1_4.py) |
| HU-02 | La expiración muestra una redirección y mensaje en pantalla | parcial | API devuelve 401 con motivo; frontend/redirección no está incluido. [auth/router.py](../backend/app/auth/router.py) |
| HU-02 | Operaciones no guardadas se reinician tras volver a ingresar | parcial | No verificable sin frontend; frontend fuera de alcance. |
| HU-03 | Un segundo login invalida la sesión anterior en backend | cumple | `test_hu03_new_login_invalidates_previous_token`; fila revocada en `test_hu03_previous_session_row_is_revoked_in_database`, [test_auth.py](../backend/tests/test_auth.py) |
| HU-03 | El dispositivo desplazado muestra aviso de sesión reemplazada | parcial | La petición antigua recibe 401; notificación visual requiere frontend. |
| HU-03 | La sesión invalidada no ejecuta nuevas peticiones | cumple | `test_hu03_new_login_invalidates_previous_token`; paso 10 de [test_e2e_sprints_1_4.py](../backend/tests/test_e2e_sprints_1_4.py) |
| HU-04 | Verifica relación usuario/rol/sede antes de operar | cumple | `test_hu04_usuario_solo_ve_sedes_asignadas`; paso 7 E2E, [test_usuarios.py](../backend/tests/test_usuarios.py) y [test_e2e_sprints_1_4.py](../backend/tests/test_e2e_sprints_1_4.py) |
| HU-04 | Mesero/cajero se limita a sedes asignadas; el admin se limita a las suyas | parcial | Acceso operativo de mesero se prueba. Por decisión confirmada, admin es global y no tiene sedes asignadas; difiere deliberadamente del texto original. [alcance_sprint_1_4.md](./alcance_sprint_1_4.md) |
| HU-04 | Rechaza sede no autorizada sin exponer sus datos | cumple | `test_hu04_mesero_no_accede_a_mesas_de_sede_no_asignada`; paso 7 E2E. |
| HU-04 | Autoriza en backend en cada petición | cumple | Dependencias `get_current_session`, `require_site_access` y `require_selected_site`; paso 7 E2E. [auth/router.py](../backend/app/auth/router.py) |
| HU-05 | Rechaza campos obligatorios ausentes e informa validación | cumple | Casos de campos requeridos de usuario, sede, mesa y producto en [test_usuarios.py](../backend/tests/test_usuarios.py), [test_sedes.py](../backend/tests/test_sedes.py) y [test_catalogo.py](../backend/tests/test_catalogo.py) |
| HU-05 | Valida tipo, formato y valores permitidos | cumple | Tests `test_hu05_*`; schemas Pydantic de usuarios, sedes, catálogo e inventario. |
| HU-05 | Los campos opcionales pueden omitirse | parcial | Se corrigió el correo heredado para que sea opcional (`test_hu07_usuario_sin_email_es_valido`). No existe un criterio exhaustivo por cada campo opcional. |
| HU-05 | Repite validación en backend | cumple | Schemas Pydantic y respuestas 422 de los casos `test_hu05_*`. |
| HU-06 | Cierre manual disponible desde el menú de perfil | parcial | El endpoint `POST /auth/logout` existe y se prueba; no se implementó menú/frontend. |
| HU-06 | Invalida sesión y token asociado | cumple | `test_hu06_logout_revokes_session_and_clears_cookie` en [test_auth.py](../backend/tests/test_auth.py) |
| HU-06 | Requiere autenticar de nuevo después del cierre | cumple | Mismo test HU-06 verifica 401 después del logout. |
| HU-34 | Login emite JWT con expiración inicial de 3 minutos y límite de sesión de 30 | cumple | `test_hu34_login_token_expires_after_inactivity_window`; pruebas HU-02 y paso 9 E2E. |
| HU-34 | Token lleva identificación, roles y sedes | cumple | `test_hu01_admin_session_exposes_roles_and_all_sites`; `user_roles` y `authorized_site_ids` en [auth/router.py](../backend/app/auth/router.py) |
| HU-34 | Cada petición valida firma/expiración y jti activo en base de datos | cumple | `get_current_session` en [auth/router.py](../backend/app/auth/router.py); pruebas HU-03 y HU-34. |
| HU-34 | JWT inválido/expirado se rechaza y redirige a login | parcial | Backend responde 401; redirección de navegador corresponde al frontend. |
| HU-07 | Campos obligatorios, usuario creado ACTIVO y sede según función | cumple | `test_hu07_crear_usuario_exitoso`, `test_hu07_usuario_operativo_sin_sede_retorna_422`; paso 2 E2E. El estado activo por defecto fue decisión confirmada. |
| HU-07 | Identificación y nombre de usuario únicos | cumple | `test_hu07_identificacion_duplicada_retorna_400`; pruebas de usuario duplicado/normalización en [test_usuarios.py](../backend/tests/test_usuarios.py) |
| HU-07 | Asigna al menos un rol y las sedes que requiere el usuario | cumple | `test_hu07_sin_rol_retorna_422`, `test_hu07_con_sede_valida_asigna_sede` |
| HU-07 | Contraseña se protege en base de datos | cumple | `test_hu36_password_persisted_as_bcrypt_hash`; bcrypt directo en [security.py](../backend/app/core/security.py) |
| HU-07 | No guarda si falta un campo obligatorio | cumple | Validaciones HU-05/HU-07. Correo no es obligatorio según los documentos y se conserva opcional por compatibilidad. |
| HU-08 | Admin modifica nombres, sedes, roles y estado | cumple | `test_hu08_editar_nombre_usuario`, `test_hu09_cambiar_roles_usuario` en [test_usuarios.py](../backend/tests/test_usuarios.py) |
| HU-08 | Inactivar bloquea login y revoca una sesión abierta | cumple | `test_hu08_usuario_inactivo_no_puede_autenticarse`; paso 11 E2E; conserva la fila de sesión revocada. |
| HU-08 | Cambios de rol/sede se reflejan de inmediato en sesión existente | cumple | `test_hu08_role_and_site_edits_apply_on_existing_session` |
| HU-08 | Usuario se inactiva, no se elimina físicamente | cumple | No hay endpoint DELETE; pruebas de inactivación/reactivación HU-08. |
| HU-09 | Configura combinaciones de roles de administrador | parcial | Cambio aprobado: admin siempre recibe capacidades admin/mesero/cajero; no se habilitan combinaciones separadas. `test_hu09_admin_always_receives_mesero_and_cajero_roles` y `test_hu09_roles_adicionales_son_solo_para_administrador`. |
| HU-09 | Menú refleja roles habilitados | parcial | API refleja los roles; UI fuera de alcance. |
| HU-09 | Operaciones siguen limitadas por sede | cumple | Dependencias de sede; pruebas HU-04 y E2E. |
| HU-10 | Código, nombre y dirección son requeridos | cumple | Pruebas `test_hu05_sede_*` y `test_hu10_crear_sede_exitosa` en [test_sedes.py](../backend/tests/test_sedes.py) |
| HU-10 | Código único | cumple | `test_hu10_codigo_sede_duplicado_retorna_400`; restricción única en Alembic. |
| HU-10 | Rechaza alta incompleta | cumple | Pruebas HU-05 de sede. |
| HU-10 | Sede puede asignarse y gestionar inventario propio | cumple | Pruebas de asignación HU-07, selección HU-13 e inventario HU-33. |
| HU-11 | Requiere código, nombre, precios, estado y proveedor | cumple | `test_hu11_producto_exige_todos_los_campos_incluido_proveedor` |
| HU-11 | Código de producto único | cumple | `test_hu11_codigo_producto_unico` |
| HU-11 | Catálogo central estandarizado entre sedes | cumple | `test_hu11_producto_usa_decimal_y_catalogo_es_central` |
| HU-11 | Cantidad no forma parte del producto | cumple | `test_hu11_cantidad_no_es_campo_del_producto`; inventario por sede en [inventario/models.py](../backend/app/inventario/models.py) |
| HU-11 | Rechaza producto incompleto | cumple | `test_hu11_producto_exige_todos_los_campos_incluido_proveedor` |
| HU-12 | Proveedor obligatorio al crear/editar producto | cumple | `test_hu11_producto_exige_todos_los_campos_incluido_proveedor`; validación de proveedor en [catalogo/router.py](../backend/app/catalogo/router.py) |
| HU-12 | Conserva relación producto–proveedor | cumple | `test_hu12_producto_conserva_relacion_con_proveedor` |
| HU-12 | No añade compras ni abastecimiento | cumple | No se encontraron endpoints de compras/abastecimiento. |
| HU-13 | Selecciona automáticamente cuando hay una sede | cumple | `test_hu13_una_sede_autorizada_seleccionada_automaticamente` |
| HU-13 | Permite elegir cuando hay varias sedes | cumple | `test_hu13_admin_elige_sede_y_se_guarda_en_la_sesion` |
| HU-13 | Mesas, inventario y pedidos respetan sede seleccionada | cumple | Pruebas HU-19/HU-21/HU-25; paso 7 E2E. |
| HU-13 | Registra sede seleccionada en la sesión | cumple | `test_hu13_admin_elige_sede_y_se_guarda_en_la_sesion`; columna en [auth/models.py](../backend/app/auth/models.py) |
| HU-16 | Lista productos con código, nombre, precios y estado | cumple | `test_hu16_administrador_consulta_y_modifica_catalogo` |
| HU-16 | Modifica campos permitidos | cumple | Mismo test HU-16. |
| HU-16 | Valida campos antes de guardar | cumple | `test_hu16_actualizacion_de_producto_rechaza_valores_nulos` |
| HU-16 | Cambios del catálogo se comparten entre sedes | cumple | `test_hu11_producto_usa_decimal_y_catalogo_es_central`; paso 12 E2E verifica snapshot del pedido. |
| HU-18 | Consulta información general de funcionalidades autorizadas | cumple | `test_hu18_informacion_general_autorizada`; `/admin/informacion-general` en [admin/router.py](../backend/app/admin/router.py) |
| HU-18 | Respeta permisos y restricciones de sede | cumple | Test de admin requerido y E2E de aislamiento de sedes. Admin global conforme a la decisión aprobada. |
| HU-18 | Consulta sin modificar información | cumple | El endpoint es GET de solo lectura; test HU-18. |
| HU-19 | Solo muestra mesas de sedes autorizadas | cumple | `test_hu19_mesero_ve_solo_mesas_de_su_sede`; paso 4 E2E. |
| HU-19 | Mesa muestra LIBRE u OCUPADA | cumple | `test_hu24_mesa_esta_ocupada_mientras_pedido_abierto`; respuesta de mesas. |
| HU-19 | No fija mesero a mesa | cumple | No hay asignación usuario-mesa en el modelo; `Mesa` depende de sede. |
| HU-20 | Mesa libre admite iniciar pedido | cumple | `test_hu20_mesa_ocupada_muestra_pedido_abierto_existente`; creación HU-22. |
| HU-20 | Mesa ocupada por pedido abierto | cumple | `test_hu24_mesa_esta_ocupada_mientras_pedido_abierto` |
| HU-20 | Al elegir mesa ocupada muestra pedido sin duplicarlo | cumple | `test_hu20_mesa_ocupada_muestra_pedido_abierto_existente`; paso 8 E2E. |
| HU-21 | Inventario corresponde solo a sede seleccionada | cumple | `test_hu21_inventario_es_solo_de_sede`; paso 7 E2E. |
| HU-21 | Producto sin unidades se identifica y no se añade | parcial | Backend rechaza faltantes/insuficientes; la presentación visual está fuera de alcance. `test_hu22_producto_sin_unidades_no_crea_pedido_ni_stock_negativo`; paso 6 E2E. |
| HU-21 | Existencias son unidades completas | cumple | `test_hu33_rechaza_cantidades_fraccionarias_y_no_positivas`; tipo entero/check de entrada. |
| HU-22 | Valida disponibilidad antes de guardar pedido | cumple | `test_hu22_producto_sin_unidades_no_crea_pedido_ni_stock_negativo` |
| HU-22 | Pedido ABIERTO asociado a usuario, sede, mesa y fecha/hora | cumple | `test_hu22_registro_abierto_descuenta_stock_y_guarda_precio_vigente` |
| HU-22 | Descuenta inventario de la sede transaccionalmente | cumple | Mismo test HU-22; paso 4 E2E; bloqueo de inventario en [ventas/router.py](../backend/app/ventas/router.py) |
| HU-22 | Conserva precio vigente al registrar | cumple | Test HU-22; paso 12 E2E confirma que un cambio posterior no altera el precio guardado. |
| HU-23 | Solo permite añadir a pedido ABIERTO | cumple | `test_hu23_agregar_producto_solo_a_pedido_abierto` |
| HU-23 | Valida unidades y descuenta existencias | cumple | Test HU-23 y paso 5 E2E. |
| HU-23 | Registra usuario y fecha/hora de la adición | cumple | Test HU-23 verifica detalle; campos `usuario_id`/`creado_en` de línea. |
| HU-24 | Estado de mesa se actualiza con el pedido | cumple | `test_hu24_mesa_esta_ocupada_mientras_pedido_abierto`; estado se deriva de pedido ABIERTO. |
| HU-24 | Mesa vuelve a LIBRE cuando el pedido se cierra | parcial | Cierre de pedidos está excluido; no hay ruta de cierre en Sprint 4. |
| HU-24 | Solo muestra mesas de sede seleccionada | cumple | HU-19 y paso 7 E2E. |
| HU-25 | Consulta estado, detalle y total del pedido | parcial | Detalle/total/ABIERTO se verifica en `test_hu25_consulta_detalle_total_y_restriccion_por_sede`; CERRADO depende del cierre excluido. |
| HU-25 | Restringe pedidos por sede autorizada | cumple | Mismo test HU-25; paso 7 E2E. |
| HU-33 | Descuenta unidades completas, incluyendo venta de productos | cumple | Pruebas HU-22/HU-23 y `test_hu33_rechaza_cantidades_fraccionarias_y_no_positivas` |
| HU-33 | Descuento solo afecta inventario de la sede del pedido | cumple | Paso 4 E2E y `test_hu21_inventario_es_solo_de_sede`. |
| HU-33 | Rechaza pedido/adición cuando no hay unidades suficientes | cumple | Pruebas HU-22/HU-23 y paso 6 E2E. |
| HU-33 | No implementa traslados, stock mínimo ni alertas | cumple | No se encontraron esas operaciones; carga/suma de inventario fue aprobada para Sprint 4. |
| HU-35 | Mesa pertenece a una sede y su número es único por sede | cumple | `test_hu35_numero_mesa_duplicado_en_misma_sede_retorna_400`; `test_hu35_mismo_numero_mesa_en_diferente_sede_es_valido` |
| HU-35 | Mesa con pedidos no se elimina físicamente; se inactiva | cumple | No hay endpoint DELETE; `test_hu35_inactivar_mesa`/`test_hu35_reactivar_mesa`. |
| HU-35 | Mesas aparecen en operación de su sede | cumple | `test_hu35_listar_mesas_de_sede`; HU-19. |
| HU-36 | Contraseñas protegidas con bcrypt | cumple | `test_hu36_password_persisted_as_bcrypt_hash`; implementación directa con bcrypt. |
| HU-36 | Errores no revelan detalles técnicos ni credenciales | cumple | `unexpected_error_handler` y validación de contraseña sanitizada en [main.py](../backend/app/main.py); tests de error genérico de login. |
| HU-36 | No escribe contraseñas/tokens completos en logs | cumple | Revisión estática: logging de error genérico; no se registran credenciales ni JWT. |
| HU-37 | Entradas se validan en backend | cumple | Schemas Pydantic con `extra="forbid"` y pruebas HU-05/HU-11/HU-33. |
| HU-37 | Consultas parametrizadas/ORM, sin SQL concatenado | cumple | Revisión estática: consultas SQLAlchemy ORM y `insert()` tipado para upsert de inventario; no se encontró SQL dinámico concatenado. |
| HU-37 | Datos inválidos se rechazan con error controlado | cumple | Prueba de entrada de inyección `test_hu01_hu37_invalid_inputs_and_credentials_are_rejected`; pruebas HU-05 y HU-33. |

## Prueba E2E: resultado por paso

Ejecutar con `pytest -s tests/test_e2e_sprints_1_4.py` desde `backend/` para
mostrar en consola el resultado paso a paso. Resultado: **14/14 PASS**.

| Paso | Resultado | Verificación |
|---:|---|---|
| 1 | PASS | Login admin; alta de sedes A/B, mesas, proveedor y producto. |
| 2 | PASS | Alta de meseros asignados a A y B. |
| 3 | PASS | Inventarios distintos cargados por sede. |
| 4 | PASS | Mesero A ve sus mesas, crea pedido, mesa ocupada; solo baja inventario A. |
| 5 | PASS | Adición al pedido descuenta de nuevo. |
| 6 | PASS | Rechaza adición sin existencias. |
| 7 | PASS | Rechaza acceso de A a mesas/pedidos B y selección de B; inventario sigue aislado. |
| 8 | PASS | Otro usuario autorizado consulta el pedido abierto existente sin duplicarlo. |
| 9 | PASS | Inactividad 3 min y máximo absoluto 30 min con actividad simulada. |
| 10 | PASS | Segundo login invalida el primer token en base de datos. |
| 11 | PASS | Usuario inactivado no puede hacer su siguiente petición. |
| 12 | PASS | Cambio de precio no modifica el precio histórico del pedido. |
| 13 | PASS | Carreras con conexiones/clientes separados: última unidad y misma mesa libre; stock no negativo y un solo pedido ABIERTO. |
| 14 | PASS | Esquema temporal parte vacío; Alembic upgrade, downgrade y re-upgrade. |

## Pendientes y límites de verificación

- No se probó interfaz, mensajes visibles, menú, redirección a login ni reinicio
  de cambios no guardados porque el frontend está expresamente excluido.
- No se verificó transporte TLS; Nginx/TLS/Gunicorn están excluidos. El backend
  protege la contraseña almacenada mediante bcrypt.
- Las longitudes de producto/proveedor y precisión monetaria implementadas
  (código 40, nombre 120, proveedor 120, `Numeric(12,2)`) no están fijadas por
  las historias. Son límites técnicos provisionales, no reglas funcionales
  confirmadas.
- El correo electrónico venía exigido por el backend preexistente, pero no es
  obligatorio en la propuesta ni en HU-07. Tras autorización del usuario se
  convirtió en opcional; se conserva por compatibilidad, no como criterio de
  aceptación.
- El estado de alta de usuario se define automáticamente como ACTIVO, conforme
  a la decisión del usuario, aunque HU-07 enumera estado entre los campos del
  registro.
- HU-04/HU-09 tienen una variación aprobada respecto del documento: admin
  global sin asignación de sedes y con capacidades inseparables de mesero y
  cajero.
- No se ejecutaron pruebas sobre `public` ni se borraron sus datos. Los
  esquemas de prueba se eliminan en el teardown de cada test.
- Se trabajó en una única rama de fase (`feature/sprint-1-4-backend`) y no en
  ramas individuales por HU. No se integró a la rama principal.

## Funcionalidades fuera de alcance encontradas

No se encontraron endpoints de pago, facturación, cierre de pedidos, reportes
de ventas, exportación a Excel, traslado entre sedes, stock mínimo, alertas de
reposición, trazabilidad general HU-38 ni funcionalidades de UI/despliegue.
El cierre ABIERTO→CERRADO y mesa→LIBRE queda preparado por el modelo de estado,
pero no expuesto como operación. HU-33 se incluyó expresamente en Sprint 4 por
decisión del usuario, aunque el backlog original la ubicaba en Sprint 6.
