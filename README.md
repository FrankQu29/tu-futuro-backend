# cardic-system-campras-inter

Una API en Django (DRF) para explorar carreras, subáreas, mapas curriculares, escuelas y voluntariados, con soporte opcional de MongoDB (MongoEngine) y utilidades para recolectar datos desde fuentes públicas (Wikipedia, Wikidata y Google Places).

- Estado: en desarrollo
- Lenguaje: Python 3.10+
- Framework: Django 4.x + Django REST Framework
- Base de datos: SQLite (por defecto), MongoDB opcional para documentos (MongoEngine)


## Tabla de Contenidos
- Descripción y objetivos
- Arquitectura y stack
- Variables de entorno
- Puesta en marcha (local)
- Uso con Docker
- Endpoints principales (API)
- Modelos de datos
- Utilidades de datos (scrapers y helpers)
- Ejemplos de uso (cURL)
- Despliegue (tips)
- Desarrollo y contribución


## Descripción y objetivos
Esta API expone recursos relacionados con:
- Carreras (licenciaturas/oficios) y sus subáreas
- Mapa curricular (materias) por carrera
- Escuelas/universidades y su ubicación/tipo
- Voluntariados asociados a carreras
- Formularios y resultados asociados a subáreas
- Estadísticas agregadas (p. ej., promedio de resultados por carrera)
- Flujo OAuth2 (inicio/callback) como base para autenticación futura

Además incluye utilidades para recolectar datos desde Internet (Wikipedia, Wikidata, Google Places) y cargarlos a la base.


## Arquitectura y stack
- Django + Django REST Framework (DRF)
- Modelos de dominio implementados con MongoEngine (colecciones en MongoDB). Si no se configura MONGO_URI, el proyecto sigue funcionando con SQLite para el stack Django estándar (sin depender de MongoDB).
- Estructura principal:
  - app `api/` con modelos, vistas y urls
  - `project/settings.py` con configuración y conexión opcional a MongoDB
  - Dockerfile y docker-compose.yml para ejecución contenerizada


## Variables de entorno
Configúralas en tu entorno o en un archivo `.env` (se usa python-dotenv):

- ALLOWED_HOSTS: lista separada por comas de hosts permitidos ("miapp.com,www.miapp.com")
- CSRF_TRUSTED_ORIGINS: orígenes confiables CSRF ("https://miapp.com,https://*.miapp.com")
- MONGO_URI: cadena de conexión a MongoDB Atlas/local (opcional). Si falta, se registra un warning y se omite la conexión.
- OAUTH_CLIENT_ID, OAUTH_AUTH_ENDPOINT, OAUTH_REDIRECT_URI, OAUTH_TOKEN_ENDPOINT, OAUTH_SCOPE: usados por las vistas OAuth2 (`/api/auth/oauth2/*`).
- GOOGLE_MAPS_API_KEY: requerido únicamente para las utilidades de Google Places en `api/universities_by_state.py`.


## Puesta en marcha (local)
Requisitos: Python 3.10+ (recomendado 3.11), pip y virtualenv.

1) Clonar y entrar al proyecto:
   git clone <repo_url>
   cd cardic-system-campras-inter

2) Crear entorno virtual e instalar dependencias:
   python -m venv .venv
   source .venv/bin/activate   # en Windows: .venv\Scripts\activate
   pip install -r requirements.txt

3) Variables de entorno (opcional para MongoDB y OAuth2):
   cp .env.example .env   # si provees uno, o exporta variables manualmente

4) Ejecutar el servidor de desarrollo:
   python manage.py runserver

Servidor por defecto: http://127.0.0.1:8000/
Endpoints de la API: prefijo /api/ (ver sección siguiente).


## Uso con Docker
- Construir y levantar con docker-compose:
  docker-compose up --build

- O usando Dockerfile y variables vía `--env-file`:
  docker build -t cardic-api .
  docker run -p 8000:8000 --env-file .env cardic-api


## Endpoints principales (API)
Prefijo base: /api/

Auth (OAuth2, GET):
- /api/auth/oauth2/start?provider=google → inicia flujo OAuth2 (PKCE), devuelve URL de autorización
- /api/auth/oauth2/callback?code=...&state=... → callback para intercambio de código por tokens

Registro (POST):
- /api/usuarios/registro → registro de usuario (tradicional u OAuth2 asistido)

Consultas (GET):
- /api/voluntariados?carrera=... → voluntariados por carrera
- /api/carreras?area=... → nombres de carreras por área (o todas)
- /api/carreras/mapa-curricular?carrera=... → nombres de materias del mapa curricular
- /api/carreras/mapa-curricular/descripcion?materia=... → descripción de una materia
- /api/escuelas?carrera=... → escuelas que ofrecen la carrera
- /api/subareas?carrera=... → subáreas por carrera
- /api/subarea?nombre=... → detalle de una subárea
- /api/formulario?subarea=... → formulario por subárea
- /api/dashboard/formularios/promedio-por-carrera → promedio de resultados por carrera

Carga masiva (POST):
- /api/bulk/carreras
- /api/bulk/subareas
- /api/bulk/escuelas
- /api/bulk/voluntariados
- /api/bulk/formularios
- /api/bulk/mapas

Notas:
- Todos los endpoints retornan JSON.
- Parámetros de consulta por querystring.
- Revisa los docstrings de cada vista y `api/urls.py` para detalles de payloads y códigos de estado.


## Modelos de datos (resumen)
Los documentos MongoEngine (colecciones) principales:

- Carrera (collection: carreras)
  - nombre: str
  - descripcion: str
  - main_area: str (choices: sociales, ciencias, salud, humanidades)
  - videos: list[str]
  - sub_areas: list[str]

- Subarea (collection: subareas)
  - nombre: str
  - introduccion: str
  - descripcion: str
  - videos_escuela: list
  - lecciones: list[Leccion] (titulo, videos, descripcion)
  - carrera: str
  - progreso: int (default=0)
  - total_lecciones: int (default=0)

- MapaCurricular (collection: mapa_curricular)
  - nombre: str
  - descripcion: str
  - carrera: str

- Escuela (collection: escuelas)
  - nombre: str
  - ubicacion: list[{lat: float, lng: float}]
  - type: str (publica | privada)
  - carreras: list[str]
  - costo: float

- Voluntariado (collection: voluntariados)
  - carrera: str
  - titulo: str
  - descripcion: str
  - ubicacion: str
  - salario: float
  - permalink: str

- Formulario (collection: formularios)
  - nombre: str
  - descripcion: str
  - preguntas: list
  - respuestas: list
  - resultados: float | null
  - subarea: str

- User (collection: user)
  - first_name, last_name, email, ubicacion, discapacidad, carrera: str
  - main_area: str (choices MAIN_AREAS)
  - intereses: list
  - zona: bool

Nota: En el código más reciente, los campos marcados como "required" fueron relajados en los modelos para permitir cargas flexibles; las vistas realizan validaciones adicionales cuando corresponde.


## Utilidades de datos (scrapers y helpers)
- api/carreras_sources.py
  - wikipedia_buscar_licenciaturas(seeds, ...): busca en Wikipedia títulos y extractos
  - wikidata_buscar_licenciaturas_por_area(area, ...): SPARQL genérico contra Wikidata
  - normalizar_a_carrera(items): mapea los resultados al esquema Carrera
  - guardar_json(data, filename): guarda resultados en carpeta `salidas/`
  - cargar_en_bd(carreras): inserta/actualiza documentos Carrera en MongoDB

- api/universities_by_state.py (Google Places)
  - buscar_universidades(consulta, ...): Text Search en Places
  - top_5_por_tipo(estado): hasta 5 públicas y 5 privadas, deduplicado
  - universidades_por_estados(estados): arma un dict por estado
  - guardar_universidades_json(data, filename): persiste JSON en `salidas/`
  - Requiere GOOGLE_MAPS_API_KEY

Archivos de salida de ejemplo en `salidas/`.


## Ejemplos de uso (cURL)
- Listar carreras por área:
  curl -s "http://localhost:8000/api/carreras?area=ciencias"

- Obtener escuelas que ofrecen una carrera:
  curl -s "http://localhost:8000/api/escuelas?carrera=Ingeniería"

- Voluntariados por carrera:
  curl -s "http://localhost:8000/api/voluntariados?carrera=Ingeniería"

- Nombres de materias del mapa curricular:
  curl -s "http://localhost:8000/api/carreras/mapa-curricular?carrera=Ingeniería"

- Descripción de una materia:
  curl -s "http://localhost:8000/api/carreras/mapa-curricular/descripcion?materia=Cálculo"

- Subáreas por carrera:
  curl -s "http://localhost:8000/api/subareas?carrera=Ingeniería"

- Formulario por subárea:
  curl -s "http://localhost:8000/api/formulario?subarea=Matemáticas Básicas"


## Despliegue (tips)
- Establece DEBUG=False y SECRET_KEY segura en producción.
- Define ALLOWED_HOSTS y, si corresponde, CSRF_TRUSTED_ORIGINS.
- Si usas MongoDB Atlas, configura MONGO_URI. La conexión se intenta al arrancar con timeout bajo y registra warning si falla (no bloquea el arranque).
- Para OAuth2, completa OAUTH_CLIENT_ID, OAUTH_AUTH_ENDPOINT, OAUTH_REDIRECT_URI, OAUTH_TOKEN_ENDPOINT, OAUTH_SCOPE. Las vistas OAuth2 son un stub que deberás completar con el intercambio real de tokens y verificación de id_token.


## Desarrollo y contribución
- Requisitos de desarrollo: pip install -r requirements.txt
- Tests: (placeholder) `api/tests.py` — agrega tus pruebas aquí.
- Estilo: recomendamos flake8/black (no incluidos por defecto)
- Contribuciones: abre issues y PRs con descripciones claras. Documenta endpoints y datos esperados en los docstrings de vistas o en este README.


---
© 2025. Proyecto educativo/demostrativo. Ajusta y extiende según tus necesidades.
