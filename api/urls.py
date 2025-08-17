"""Rutas públicas de la API (Django REST Framework).

Resumen de endpoints principales:
- Auth OAuth2 (GET):
  - /api/auth/oauth2/start: inicia flujo OAuth2 (PKCE), devuelve URL de autorización.
  - /api/auth/oauth2/callback: callback para intercambio de código por tokens.
- Registro (POST):
  - /api/usuarios/registro: registro de usuario (tradicional u OAuth2 asistido).
- Consultas (GET):
  - /api/voluntariados?carrera=...: voluntariados por carrera.
  - /api/carreras?area=...: nombres de carreras por área (o todas si no se envía área).
  - /api/carreras/mapa-curricular?carrera=...: nombres de materias del mapa curricular.
  - /api/carreras/mapa-curricular/descripcion?materia=...: descripción de una materia.
  - /api/escuelas?carrera=...: escuelas que ofrecen la carrera.
  - /api/subareas?carrera=...: subáreas por carrera.
  - /api/subarea?nombre=...: detalle de una subárea.
  - /api/formulario?subarea=...: formulario por subárea.
  - /api/dashboard/formularios/promedio-por-carrera: promedio de resultados por carrera.
- Carga masiva (POST):
  - /api/bulk/carreras, /api/bulk/subareas, /api/bulk/escuelas,
    /api/bulk/voluntariados, /api/bulk/formularios, /api/bulk/mapas

Notas:
- Todos los endpoints retornan JSON.
- Los parámetros de consulta se pasan vía querystring.
- Ver docstrings de cada vista para detalles de payloads y códigos de estado.
"""
from django.urls import path

from api.views.escuelas import BulkCreateEscuelasAPIView
from api.views.formularios import BulkCreateFormulariosAPIView
from api.views.login import OAuth2StartAPIView, OAuth2CallbackAPIView
from api.views.mapa_curricular import BulkCreateMapaCurricularAPIView
from api.views.register import RegistroUsuarioView
from api.views.voluntariado import VoluntariadosPorCarreraAPIView, BulkCreateVoluntariadosAPIView
from api.views.carreras import SubareasPorCarreraAPIView, CarrerasPorAreaAPIView, EscuelasPorCarreraAPIView, \
    BulkCreateCarrerasAPIView
from api.views.subareas import (
    MapaCurricularNombresPorCarreraAPIView,
    DescripcionMateriaMapaCurricularAPIView,
    SubareaDetallePorNombreAPIView,
    FormularioPorSubareaAPIView, BulkCreateSubareasAPIView,
)
from api.views.stats import DashboardPromedioResultadosPorCarreraAPIView


urlpatterns = [
    # Auth (OAuth2)
    path('auth/oauth2/start', OAuth2StartAPIView.as_view(), name='oauth2-start'),
    path('auth/oauth2/callback', OAuth2CallbackAPIView.as_view(), name='oauth2-callback'),
    # Registro
    path('usuarios/registro', RegistroUsuarioView.as_view(), name='registro-usuario'),

    # GET METHODS
    # Voluntariados
    path('voluntariados', VoluntariadosPorCarreraAPIView.as_view(), name='voluntariados-por-carrera'),
    # Carreras
    path('carreras', CarrerasPorAreaAPIView.as_view(), name='carreras-por-area'),
    path('carreras/mapa-curricular', MapaCurricularNombresPorCarreraAPIView.as_view(), name='mapa-curricular-nombres'),
    path('carreras/mapa-curricular/descripcion', DescripcionMateriaMapaCurricularAPIView.as_view(), name='mapa-curricular-descripcion'),
    # Escuelas
    path('escuelas', EscuelasPorCarreraAPIView.as_view(), name='escuelas-por-carrera'),
    # Subáreas
    path('subareas', SubareasPorCarreraAPIView.as_view(), name='subareas-por-carrera'),
    path('subarea', SubareaDetallePorNombreAPIView.as_view(), name='subarea-detalle-por-nombre'),
    # Formularios
    path('formulario', FormularioPorSubareaAPIView.as_view(), name='formulario-por-subarea'),
    # Dashboard
    path('dashboard/formularios/promedio-por-carrera', DashboardPromedioResultadosPorCarreraAPIView.as_view(), name='dashboard-promedio-por-carrera'),


    # POST BULK METHODS
    path('bulk/carreras', BulkCreateCarrerasAPIView.as_view(), name='bulk-carreras'),
    path('bulk/subareas', BulkCreateSubareasAPIView.as_view(), name='bulk-subareas'),
    path('bulk/escuelas', BulkCreateEscuelasAPIView.as_view(), name='bulk-escuelas'),
    path('bulk/voluntariados', BulkCreateVoluntariadosAPIView.as_view(), name='bulk-voluntariados'),
    path('bulk/formularios', BulkCreateFormulariosAPIView.as_view(), name='bulk-formularios'),
    path('bulk/mapas', BulkCreateMapaCurricularAPIView.as_view(), name='bulk-formularios'),
]

