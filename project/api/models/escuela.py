
from mongoengine import Document, StringField, FloatField, ListField, EmbeddedDocument, EmbeddedDocumentField


class Coordenadas(EmbeddedDocument):
    lat = FloatField(required=True)
    lng = FloatField(required=True)

class Escuela(Document):
    nombre = StringField(required=True)
    ubicacion = ListField(EmbeddedDocumentField(Coordenadas), required=True)
    type = StringField(choices=["publica", "privada"], required=True)
    carreras = ListField(required=True)
    costo = FloatField(required=True)

    meta = {
        "collection": "escuelas",
        # Alias de conexión si usas múltiples bases: "db_alias": "default",
        # Índices recomendados:
        "indexes": [
            "nombre",  # Búsqueda por nombre
            "ubicacion",  # Filtrado por ubicación
            {"fields": ["carreras"]}  # Búsqueda por elemento en la lista
        ],
    }