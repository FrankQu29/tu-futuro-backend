"""
URL configuration for project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from api.views.escuelas import BulkCreateEscuelasAPIView
from api.views.formularios import BulkCreateFormulariosAPIView
# ... existing code ...
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
    path('api/usuarios/registro', RegistroUsuarioView.as_view(), name='registro-usuario'),
    # Voluntariados
    path('api/voluntariados/', VoluntariadosPorCarreraAPIView.as_view(), name='voluntariados-por-carrera'),
    # Carreras
    path('api/carreras', CarrerasPorAreaAPIView.as_view(), name='carreras-por-area'),
    path('api/carreras/mapa-curricular', MapaCurricularNombresPorCarreraAPIView.as_view(), name='mapa-curricular-nombres'),
    path('api/carreras/mapa-curricular/descripcion', DescripcionMateriaMapaCurricularAPIView.as_view(), name='mapa-curricular-descripcion'),
    # Escuelas
    path('api/escuelas', EscuelasPorCarreraAPIView.as_view(), name='escuelas-por-carrera'),
    # Subáreas
    path('api/subareas', SubareasPorCarreraAPIView.as_view(), name='subareas-por-carrera'),
    path('api/subarea', SubareaDetallePorNombreAPIView.as_view(), name='subarea-detalle-por-nombre'),
    # Formularios
    path('api/formulario', FormularioPorSubareaAPIView.as_view(), name='formulario-por-subarea'),
    # Dashboard
    path('api/dashboard/formularios/promedio-por-carrera', DashboardPromedioResultadosPorCarreraAPIView.as_view(), name='dashboard-promedio-por-carrera'),


    # POS METODS
    path('api/bulk/carreras', BulkCreateCarrerasAPIView.as_view(), name='bulk-carreras'),
    path('api/bulk/subareas', BulkCreateSubareasAPIView.as_view(), name='bulk-subareas'),
    path('api/bulk/escuelas', BulkCreateEscuelasAPIView.as_view(), name='bulk-escuelas'),
    path('api/bulk/voluntariados', BulkCreateVoluntariadosAPIView.as_view(), name='bulk-voluntariados'),
    path('api/bulk/formularios', BulkCreateFormulariosAPIView.as_view(), name='bulk-formularios'),
    path('api/bulk/mapas', BulkCreateMapaCurricularAPIView.as_view(), name='bulk-formularios'),

]

