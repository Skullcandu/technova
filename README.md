# TechNova – Laboratorio para el Taller de Seguridad para Plataformas Web

Tienda ficticia de componentes de PC, **deliberadamente vulnerable**. Úsala solo en tu equipo (127.0.0.1).

## Ejecutar
```
pip install -r requirements.txt
python app.py        # http://127.0.0.1:5000
```
Para reiniciar los datos, borra `technova.db` y vuelve a ejecutar.

**Antes de tocar nada:** `git init && git add . && git commit -m "baseline" && git tag baseline` (entregable: evidencia del estado inicial).

## Usuarios de prueba
| Usuario | Contraseña | Rol |
|---|---|---|
| admin | admin123 | admin |
| ana | ana123 | cliente |
| luis | luis123 | cliente |

## Cumple los mínimos del taller (sección 4)
Persistencia (SQLite) · operaciones que modifican estado (compra, stock, reseñas, edición de productos) · 2 roles (cliente/admin) · proceso de negocio (compra) · frontend ↔ API REST.

## Etapa 1 – Punto de partida
- **Proceso principal:** seleccionar producto → ver precio → verificar stock → carrito → aplicar cupón → calcular total → comprar → descontar stock.
- **Actores:** cliente, administrador, (atacante externo).
- **Activos candidatos:** credenciales, sesiones, datos personales (email, RUT), pedidos, inventario/precios, cupones, base de datos.
- **Arquitectura:** navegador (HTML/JS) → API Flask (`app.py`) → SQLite (`technova.db`).
- **Endpoints:** `/api/login`, `/api/me`, `/api/products`, `/api/products/<id>/reviews`, `/api/checkout`, `/api/orders`, `/api/orders/<id>`, `/api/admin/users`, `/api/admin/products/<id>`.

## Hipótesis a comprobar (NO asumir: demostrar con pruebas)
El taller pide evidencia, así que estas son solo pistas de por dónde empezar. Cada una debe pasar por *situación inicial → prueba → resultado → evidencia → interpretación*, y algunas pueden resultar no explotables o de menor impacto (útil para la sección 22).

1. **Autenticación/criptografía:** ¿cómo se almacenan las contraseñas? ¿hay límite de intentos?
2. **Validación de entradas:** login y búsqueda de productos construyen consultas SQL.
3. **Gestión de sesiones:** ¿qué contiene la cookie `sid`? ¿es predecible? ¿banderas? ¿se invalida al salir?
4. **Control de acceso:** `/api/orders/<id>` y las rutas de administración.
5. **XSS:** cómo se muestran las reseñas y otros datos en el navegador.
6. **Lógica de negocio (BLV, mínimo 3 flujos):** origen del precio en la compra, validación de cantidades, stock, cupones (reutilización/acumulación), orden del proceso.
7. **Configuración HTTP y errores:** cabeceras de seguridad, mensajes de error, modo debug.
8. **Logging:** ¿queda registro de intentos fallidos y operaciones críticas?
9. **CSRF:** acciones que modifican estado.
10. **Protección de datos:** qué devuelve la API sobre los usuarios.

## Cómo usarlo en el taller
1. Documentar baseline (commit/tag + evidencias).
2. Definir 8–12 requisitos verificables (ID, descripción, activo, problema, prueba, prioridad; ASVS como respaldo).
3. Diseñar y ejecutar pruebas; registrar hallazgos y priorizar.
4. Implementar ≥ 4 controles; reprobar con la misma prueba.
5. Mostrar al menos un control que bloquee el abuso **sin romper** el uso legítimo (ej.: precio calculado en servidor sin impedir la compra normal).
6. Completar matriz de trazabilidad, riesgo residual, medida no implementada y recomendación descartada.

> Pruebas de seguridad únicamente sobre esta app en local.
