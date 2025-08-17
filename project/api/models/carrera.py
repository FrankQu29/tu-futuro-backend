from mongoengine import Document, StringField, ListField
from .constants import MAIN_AREAS

class Carrera(Document):
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
            "main_area",  # Filtrado por ubicación
            "sub_areas"
        ],
    }

