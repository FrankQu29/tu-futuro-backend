
from mongoengine import Document, StringField, FloatField, ListField, EmbeddedDocument, EmbeddedDocumentField


class Coordenadas(EmbeddedDocument):
    """Documento embebido para coordenadas geográficas.

    Campos:
    - lat (float, requerido)
    - lng (float, requerido)
    """
    lat = FloatField()
    lng = FloatField()

class Escuela(Document):
    """Modelo de Escuela/Universidad.

    Campos:
    - nombre (str, requerido): Nombre de la institución.
    - ubicacion (list[Coordenadas], requerido): Uno o varios puntos geográficos.
    - type (str, requerido, choices=[publica, privada]): Naturaleza de la institución.
    - carreras (list[str], requerido): Carreras ofrecidas (por nombre).
    - costo (float, requerido): Costo o colegiatura referencial.

    Índices: nombre, ubicacion y arreglo carreras.
    """
    nombre = StringField()
    ubicacion = ListField(EmbeddedDocumentField(Coordenadas))
    type = StringField(choices=["publica", "privada"])
    carreras = ListField()
    costo = FloatField()

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