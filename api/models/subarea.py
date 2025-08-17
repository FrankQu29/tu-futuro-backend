from mongoengine import Document, StringField, ListField, EmbeddedDocumentField, EmbeddedDocument, FloatField, IntField


class Leccion(EmbeddedDocument):
    titulo = StringField()
    videos = ListField(StringField())
    descripcion = StringField()

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
    nombre = StringField()
    introduccion = StringField()
    descripcion = StringField()
    videos_escuela = ListField()
    lecciones = ListField(EmbeddedDocumentField("Leccion"))
    carrera = StringField()
    progreso = IntField(default=0)
    total_lecciones = IntField(default=0)

    meta = {
        "collection": "subareas",
        # Alias de conexión si usas múltiples bases: "db_alias": "default",
        # Índices recomendados:
        "indexes": [
            "nombre",  # Búsqueda por nombre
            "carrera",  # Filtrado por carrera
        ],
    }