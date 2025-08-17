from mongoengine import Document, StringField, FloatField, ListField

class Formulario(Document):
    nombre = StringField(required=True)
    descripcion = StringField(required=True)
    preguntas = ListField(required=True)
    respuestas = ListField(required=True)
    resultados = FloatField(required=True, default=None)
    subarea = StringField(required=True)

    meta = {
        "collection": "formularios",
        # Alias de conexión si usas múltiples bases: "db_alias": "default",
        # Índices recomendados:
        "indexes": [
            "resultados",  # Búsqueda por nombre
            "subarea",  # Filtrado por ubicación
        ],
    }