# Sabores del Valle Banquetería

Plataforma web de catering y banquetería desarrollada con **Django** para la **Evaluación Sumativa N° 3 de Programación Back End (TI3041)** de INACAP. Incluye un catálogo público de servicios, un cotizador de eventos en sesión (`request.session`) y un panel operativo protegido para el personal.

## Ficha de registro

| Campo | Detalle |
|---|---|
| **Nombre de la Organización o Plataforma** | Sabores del Valle Banquetería |
| **Modelo de Negocio / Giro** | Servicio de catering y banquetería para matrimonios, eventos corporativos y celebraciones |
| **Integrantes del Equipo** | Fernando Chandia Molina |
| **Entidad de Contexto / Agrupación (ORM)** | `TipoMenu` |
| **Entidad Principal Gestionable (ORM)** | `ServicioCatering` |
| **Propósito de la Sesión (request.session)** | Cotizador de evento: selección de servicios por número de invitados, validación de mínimo/máximo por servicio y cálculo de subtotal, 10% de servicio de garzones, IVA 19% y total final |

---

## Tecnologías

- Python 3.12 o superior (desarrollado con Python 3.15)
- Django 6.1.3
- Pillow 13.0.0 (manejo de imágenes)
- python-dotenv 1.2.4 (variables de entorno)
- SQLite (base de datos de desarrollo)
- Bootstrap 5.3 y Bootstrap Icons (por CDN)

---

## Instalación paso a paso

Comandos para **PowerShell en Windows**. En macOS/Linux se indica la alternativa.

**1. Clonar el repositorio**

```powershell
git clone https://github.com/mystl-e/sabores-del-valle.git
cd sabores-del-valle
```

**2. Crear y activar el entorno virtual**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

> macOS/Linux: `python3 -m venv .venv` y `source .venv/bin/activate`
> Si PowerShell bloquea la activación: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

**3. Instalar dependencias**

```powershell
pip install -r requirements.txt
```

**4. Configurar variables de entorno**

```powershell
Copy-Item .env.example .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copiar la clave generada en `SECRET_KEY` dentro del archivo `.env`.

> macOS/Linux: `cp .env.example .env`

**5. Aplicar migraciones y cargar datos iniciales**

```powershell
python manage.py migrate
python manage.py poblar_datos
```

El comando `poblar_datos` carga 5 tipos de menú, 10 servicios de catering y 3 usuarios de prueba. Es idempotente: se puede ejecutar varias veces sin duplicar registros. Con `python manage.py poblar_datos --reset` se borra y recarga el catálogo.

**6. Ejecutar el servidor**

```powershell
python manage.py runserver
```

Abrir http://127.0.0.1:8000/

---

## Credenciales de prueba

| Usuario | Contraseña | Tipo | Acceso |
|---|---|---|---|
| `admin` | `Admin.2026` | Superusuario (rol Administrador) | Todo el sitio, Gestión y Django Admin |
| `coordinador` | `Coord.2026` | Staff (rol Coordinador de eventos) | Gestión (CRUD) y Django Admin con permisos de staff |
| `cliente` | `Cliente.2026` | Usuario estándar (rol Cliente) | Catálogo, cotizador y confirmación de solicitudes |

---

## Rutas principales

| Ruta | Descripción | Acceso |
|---|---|---|
| `/` | Catálogo público con búsqueda, filtro, orden y paginación | Público |
| `/servicio/<slug>/` | Ficha de detalle del servicio | Público |
| `/cotizacion/` | Cotizador de evento (colección en sesión) | Público |
| `/cotizacion/comprobante/` | Comprobante de la última solicitud | Usuario autenticado |
| `/cuentas/registro/` · `/cuentas/login/` · `/cuentas/perfil/` | Registro, inicio de sesión y perfil | Público / autenticado |
| `/gestion/` | Backoffice: listado, crear, editar, baja lógica y reactivar | Solo staff |
| `/admin/` | Django Admin personalizado | Solo staff |

---

## Funcionalidades por criterio de evaluación

### Criterio 2.1.1 — Configuración, entorno y capa de datos
- Entorno virtual `.venv`, `requirements.txt` con versiones fijadas y `.gitignore` que excluye `.venv`, `__pycache__`, `.env`, `db.sqlite3` y `media/`.
- Variables sensibles (`SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`) en `.env` con python-dotenv; plantilla en `.env.example`.
- **`TipoMenu`** (entidad de contexto): nombre único, descripción y vigencia.
- **`ServicioCatering`** (entidad principal):
  - `tipo_menu`: `ForeignKey` con `on_delete=models.PROTECT`.
  - `codigo` único (formato `CAT-001`) y `slug` generado automáticamente para las URL.
  - `precio_por_persona`, `minimo_invitados` y `maximo_invitados` con `MinValueValidator`.
  - `estado` con opciones cerradas (`TextChoices`): Disponible, Temporada agotada, Suspendido.
  - `imagen` (`ImageField`) y `activo` para la baja lógica.
  - `clean()` valida que el máximo de invitados no sea menor al mínimo.
- **`Perfil`** (app `usuarios`): relación 1 a 1 con `User`, con RUT (validación de dígito verificador módulo 11), teléfono y rol institucional. Se crea automáticamente con una señal `post_save`.
- Comando personalizado `poblar_datos`.

### Criterio 2.1.2 — Django Admin a medida
- `site_header`, `site_title` e `index_title` con la identidad de Sabores del Valle.
- `ServicioCateringAdmin` registrado con `@admin.register`: `list_display`, `list_filter` (tipo de menú, estado, vigencia), `search_fields`, `list_editable` (precio, estado, vigencia) y `fieldsets` en 5 secciones.
- Extras: `list_select_related`, vista previa de imagen, acciones masivas de baja lógica y reactivación, conteo de servicios por tipo de menú con `annotate(Count)` e inline de perfil en el admin de usuarios.

### Criterio 2.1.3 — CRUD en el frontend
- **C:** `ServicioCateringForm` (ModelForm) con Bootstrap 5, `enctype="multipart/form-data"`, `request.FILES` y validaciones `clean_codigo()` (formato y unicidad), `clean_precio_por_persona()`, `clean_minimo_invitados()`, `clean_maximo_invitados()`, `clean_imagen()` (máx. 2 MB) y `clean()` cruzado.
- **R:** catálogo con Bootstrap Cards, búsqueda multi-campo con objetos `Q` (nombre, código y descripción, insensible a tildes), filtro por tipo de menú, ordenamiento y `Paginator`. Detalle por `slug`.
- **U:** edición con formulario precargado (`instance=servicio`).
- **D:** baja lógica (`activo=False`) con pantalla de confirmación previa y opción de reactivar.

### Criterio 2.1.4 — Sesiones, seguridad e IA
- **Cotizador en `request.session`:**
  - Agregar servicios validando disponibilidad y cupo (mínimo/máximo de invitados).
  - Modificar la cantidad de invitados, eliminar servicios individuales y vaciar la cotización.
  - Desglose: subtotal + 10% servicio de garzones = neto; IVA 19% sobre el neto; total final (redondeo a pesos con `Decimal`).
  - Context processor `catering.context_processors.cotizacion` que muestra el contador en el navbar.
  - Confirmación que genera un comprobante con folio (`SV-AAAAMMDD-XXXX`) y vacía la sesión.
- **Autenticación:** registro (usuario + perfil), login, logout por POST y vista de perfil.
- **Control de acceso:** vistas de gestión con `@login_required` y `@user_passes_test(es_staff)`; un usuario sin permisos recibe una página 403 propia.
- **CSRF:** `{% csrf_token %}` en todos los formularios POST.

### Transversal — Interfaz y control de versiones
- Plantilla maestra `base.html` con navbar responsivo, Django Messages Framework y diseño responsivo con Bootstrap 5.
- Historial de commits descriptivos por cada etapa del desarrollo.

---

## Reglas de negocio del cotizador

| Regla | Detalle |
|---|---|
| Disponibilidad | Solo se cotizan servicios vigentes y en estado Disponible |
| Cupo | Los invitados deben estar entre el mínimo y el máximo del servicio |
| Precios | La sesión guarda solo el id del servicio y los invitados; los precios se leen siempre desde la base de datos |
| Servicio de garzones | 10% sobre el subtotal (forma parte del precio del servicio, afecto a IVA) |
| IVA | 19% sobre el neto (subtotal + servicio) |
| Servicios dados de baja | Si un servicio deja de estar disponible mientras está en la cotización, se quita automáticamente y se avisa al usuario |

---

## Bitácora de uso de Inteligencia Artificial

Durante el desarrollo se utilizó **Claude (Anthropic)** como asistente técnico. Todas las respuestas fueron revisadas, probadas en el proyecto y adaptadas a los requerimientos del negocio.

### Caso 1 — Arquitectura del modelo ORM

**Prompt:**
> Necesito modelar en Django un catálogo de servicios de catering agrupados por tipo de menú. La pauta exige ForeignKey con PROTECT, un código único o slug, al menos un valor numérico con MinValueValidator, un estado con choices, un ImageField y baja lógica. ¿Cómo estructuro los modelos?

**Respuesta técnica de la IA:**
Propuso dos modelos: `TipoMenu` como entidad de contexto y `ServicioCatering` como entidad principal. La relación usa `ForeignKey(on_delete=models.PROTECT, related_name='servicios')`, el estado usa `TextChoices`, el slug se genera en `save()` con `slugify` y la vigencia se maneja con un booleano `activo`. También sugirió un `clean()` a nivel de modelo para validar reglas entre campos.

**Adaptación aplicada:**
Se definieron `minimo_invitados` y `maximo_invitados` como los "cupos" del negocio, porque luego los usa el cotizador en sesión para validar cada servicio. El slug se genera combinando código y nombre (`cat-003-asado-campestre`), lo que garantiza unicidad porque el código es único. Se comprobó en el admin que `PROTECT` impide borrar un tipo de menú con servicios asociados.

### Caso 2 — Optimización de consultas y búsqueda insensible a tildes

**Prompt:**
> La búsqueda del catálogo con `Q(nombre__icontains=q)` encuentra "cóctel" pero no "coctel" ni "CÓCTEL". Uso SQLite. ¿Cómo hago una búsqueda que ignore tildes y mayúsculas sin cambiar de motor de base de datos? ¿Y cómo evito consultas repetidas al mostrar el tipo de menú de cada servicio?

**Respuesta técnica de la IA:**
Explicó que SQLite compara texto literal y no trata "o" y "ó" como iguales. Propuso un campo oculto `texto_busqueda` que guarda código, nombre, descripción e incluye **normalizados** (sin tildes y en minúsculas con `unicodedata`), llenado automáticamente en `save()`, y agregar `Q(texto_busqueda__contains=normalizar(q))` a la búsqueda. Para el problema N+1 recomendó `select_related('tipo_menu')` en el catálogo, la gestión y el cotizador, `list_select_related` en el admin y `annotate(Count('servicios'))` para contar servicios por tipo de menú en una sola consulta.

**Adaptación aplicada:**
Se mantuvieron las condiciones `Q` originales por nombre, código y descripción, y se agregó la búsqueda normalizada como una condición más. Al probar, `poblar_datos` no llenaba el nuevo campo: `update_or_create` guarda solo los campos indicados (`update_fields`). Se corrigió `save()` para incluir `texto_busqueda` y `slug` en `update_fields`. Esta misma revisión permitió detectar y reparar un registro creado con el slug vacío, que provocaba un error `NoReverseMatch` en el catálogo.

### Caso 3 — Seguridad: control de acceso, CSRF y sesión

**Prompt:**
> ¿Cómo protejo las vistas del CRUD para que solo el personal pueda usarlas, usando @login_required y @user_passes_test? Además, en el cotizador en sesión, ¿qué datos debo guardar para que un usuario no pueda manipular los precios?

**Respuesta técnica de la IA:**
Recomendó combinar `@login_required` con `@user_passes_test` y una función `es_staff`. Si el usuario está autenticado pero no es staff, lanza `PermissionDenied` (error 403) en lugar de redirigirlo al login en bucle. Sugirió que las acciones que modifican datos (baja lógica, reactivar, logout, operaciones del cotizador) acepten solo POST con `{% csrf_token %}` usando `@require_POST`. Para la sesión, propuso guardar solo `{id_servicio: {'invitados': N}}` y calcular precios y totales siempre desde la base de datos, marcando `session.modified = True` al cambiar el diccionario.

**Adaptación aplicada:**
Se creó una página `403.html` con la identidad del sitio. La confirmación de la cotización exige sesión iniciada, y la cotización de un visitante anónimo se conserva al hacer login. Se agregó `quitar_no_disponibles()` para que un servicio dado de baja mientras estaba en la cotización se elimine automáticamente con un aviso. Se verificó que un POST sin token CSRF es rechazado (403), que un cliente no puede entrar a `/gestion/` y que un anónimo es redirigido al login.

### Reflexión sobre el uso ético de la IA
La IA se usó como apoyo para diseñar y depurar, no como reemplazo del análisis propio. Cada propuesta se ejecutó y probó en el proyecto. Los errores detectados en las pruebas, como el campo de búsqueda vacío o el slug faltante, se analizaron y corrigieron entendiendo su causa antes de aplicar el cambio.

---

## Estructura del proyecto

```
sabores-del-valle/
├── catering/                  # Catálogo, CRUD y cotizador
│   ├── management/commands/poblar_datos.py
│   ├── templatetags/formato.py          # filtros |clp y |color_estado
│   ├── admin.py
│   ├── context_processors.py            # contador de la cotización
│   ├── cotizacion.py                    # lógica de la colección en sesión
│   ├── forms.py                         # ServicioCateringForm
│   ├── mixins.py                        # BootstrapFormMixin
│   ├── models.py                        # TipoMenu y ServicioCatering
│   ├── utils.py                         # normalizar()
│   ├── views.py                         # catálogo y detalle
│   ├── views_cotizacion.py
│   └── views_gestion.py                 # backoffice protegido
├── usuarios/                  # Registro, login y perfil
│   ├── admin.py · forms.py · models.py · validators.py · views.py · urls.py
├── config/                    # settings.py y urls.py del proyecto
├── templates/                 # base.html, 403.html y plantillas por app
├── static/css/estilos.css
├── media/                     # imágenes subidas (no se versiona)
├── .env.example
├── requirements.txt
└── manage.py
```
