# TechNova - Auditoría de Seguridad Web 🛡️

**TechNova** es una aplicación web transaccional (tienda de componentes de PC) utilizada como laboratorio para la demostración práctica de identificación, explotación y mitigación de vulnerabilidades de lógica de negocio y control de acceso.

Este repositorio documenta el ciclo completo de remediación de software para la asignatura **Seguridad para plataformas web (CIB402)** del Instituto Profesional AIEP (Sede Bellavista).

---

## 📋 Resumen de la Auditoría

El proyecto consistió en auditar una línea base vulnerable (`baseline`), identificar fallas críticas que permitían el fraude financiero y la fuga de datos, y aplicar controles defensivos directamente en la capa lógica del servidor (Backend).

### Vulnerabilidades Mitigadas (Controles Implementados)
*   **[C-01] Control de Acceso Roto (BAC):** Se implementó validación estricta de rol (`admin`) en el backend para evitar la fuga masiva de datos personales (RUTs, correos) y el sabotaje del catálogo.
*   **[C-02] Fraude de Precios (BLV):** Se eliminó la confianza ciega en el *payload* del cliente. El servidor ahora calcula el total financiero consultando directamente el precio oficial en la base de datos.
*   **[C-03] Acceso Horizontal No Autorizado (IDOR):** Se integró verificación de propiedad (Dueño) interceptando el ID del pedido, bloqueando la lectura de boletas ajenas.
*   **[C-04] Abuso de Inventario (BLV):** Se implementó validación de límites lógicos en el backend, forzando números enteros positivos y bloqueando compras que superen el stock físico, evitando inventarios negativos.

---

## 🗂️ Estructura del Repositorio

*   `/app.py`: Archivo principal del backend (Controladores Flask y lógica de negocio).
*   `/technova.db`: Base de datos SQLite local.
*   `/templates/` y `/static/`: Capa de presentación (Frontend, HTML/JS/CSS).
*   `/docs/evidencias/baseline/`: Evidencias fotográficas de la explotación exitosa de las vulnerabilidades en el estado inicial.
*   `/docs/evidencias/final/`: Evidencias fotográficas que demuestran el bloqueo de los ataques tras la implementación de los controles.

---

## ⚙️ Instalación y Ejecución

Para levantar el entorno local de TechNova, sigue estos pasos:

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/Skullcandu/technova.git](https://github.com/Skullcandu/technova.git)
   cd technova
   
---

   Instalar las dependencias:
Asegúrate de tener Python instalado y ejecuta:


pip install -r requirements.txt
(Nota: Flask es la dependencia principal).

Ejecutar el servidor:

python app.py
Acceder a la aplicación:
Abre tu navegador web en http://127.0.0.1:5000

🔍 Guía de Reproducción (Para Evaluación Técnica)
El repositorio utiliza etiquetas (tags) de Git para facilitar la revisión del código "Antes" y "Después" de la auditoría.

1. Ver el estado vulnerable original:
Para ejecutar la tienda con todas sus vulnerabilidades abiertas (Fraude a $1, IDOR, Inventario negativo, fuga de RUTs), viaja en el tiempo a la etiqueta baseline:

git checkout baseline
2. Ver el estado seguro final:
Para volver a la versión protegida con los controles C-01 a C-04 aplicados y el entorno saneado:

git checkout final
(Nota: Después de revisar un tag antiguo, puedes volver a la rama principal escribiendo git checkout main).
