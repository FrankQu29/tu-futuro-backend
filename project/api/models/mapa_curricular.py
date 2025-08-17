from mongoengine import StringField, Document

class MapaCurricular(Document):
    nombre = StringField(required=True)
    descripcion = StringField(required=True)
    carrera = StringField(required=True)

    meta = {
        "collection": "mapa_curricular",
        # Alias de conexión si usas múltiples bases: "db_alias": "default",
        # Índices recomendados:
        "indexes": [
            "nombre",  # Búsqueda por nombre
            "carrera",  # Filtrado por ubicación
        ],
    }