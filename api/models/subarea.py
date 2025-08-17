from mongoengine import Document, StringField, ListField

class Subarea(Document):
    nombre = StringField(required=True)
    introduccion = StringField(required=True)
    descripcion = StringField(required=True)
    videos_escuela = ListField(required=True)
    carrera = StringField(required=True)

    meta = {
        "collection": "subareas",
        # Alias de conexión si usas múltiples bases: "db_alias": "default",
        # Índices recomendados:
        "indexes": [
            "nombre",  # Búsqueda por nombre
            "carrera",  # Filtrado por ubicación
        ],
    }