from mongoengine import Document, StringField, ListField
from .constants import MAIN_AREAS

class Carrera(Document):
    """Modelo de Carrera.

    Representa una carrera universitaria/oficio dentro del sistema.

    Campos:
    - nombre (str, requerido): Nombre público de la carrera.
    - descripcion (str, requerido): Descripción breve de la carrera.
    - main_area (str, opcional, choices=MAIN_AREAS): Área principal a la que pertenece.
    - videos (list[str], requerido): Recursos audiovisuales recomendados.
    - sub_areas (list[str], requerido): Nombres de subáreas asociadas.

    Índices:
    - nombre: para búsquedas por nombre.
    - main_area: para filtros por área.
    - sub_areas: para búsquedas por pertenencia.
    """
    nombre = StringField(required=True)
    descripcion = StringField(required=True)
    main_area = StringField(choices=MAIN_AREAS)
    videos = ListField(required=True)
    sub_areas = ListField(required=True)

    meta = {
        "collection": "carreras",
        # Alias de conexión si usas múltiples bases: "db_alias": "default",
        # Índices recomendados:
        "indexes": [
            "nombre",  # Búsqueda por nombre
            "main_area",  # Filtrado por área
            "sub_areas"
        ],
    }

