from mongoengine import Document, StringField, ListField, EmbeddedDocumentField, EmbeddedDocument


class Leccion(EmbeddedDocument):
    titulo = StringField(required=True)
    videos = ListField(StringField(required=True))
    descripcion = StringField(required=True)

class Subarea(Document):
    """Modelo de Subárea.

    Subdivisión de una carrera con contenidos y recursos asociados.

    Campos:
    - nombre (str, requerido): Nombre de la subárea.
    - introduccion (str, requerido): Texto introductorio.
    - descripcion (str, requerido): Descripción detallada.
    - videos_escuela (list, requerido): Recursos audiovisuales de apoyo.
    - carrera (str, requerido): Nombre de la carrera a la que pertenece.
    """
    nombre = StringField(required=True)
    introduccion = StringField(required=True)
    descripcion = StringField(required=True)
    videos_escuela = ListField(required=True)
    lecciones = ListField(EmbeddedDocumentField("Leccion"), required=True)
    carrera = StringField(required=True)

    meta = {
        "collection": "subareas",
        # Alias de conexión si usas múltiples bases: "db_alias": "default",
        # Índices recomendados:
        "indexes": [
            "nombre",  # Búsqueda por nombre
            "carrera",  # Filtrado por carrera
        ],
    }