from mongoengine import StringField, Document

class MapaCurricular(Document):
    """Modelo de Mapa Curricular.

    Representa una materia o nodo dentro del mapa curricular de una carrera.

    Campos:
    - nombre (str, requerido): Nombre de la materia.
    - descripcion (str, requerido): Descripción de la materia.
    - carrera (str, requerido): Nombre de la carrera a la que pertenece.
    """
    nombre = StringField()
    descripcion = StringField()
    carrera = StringField()

    meta = {
        "collection": "mapa_curricular",
        # Alias de conexión si usas múltiples bases: "db_alias": "default",
        # Índices recomendados:
        "indexes": [
            "nombre",  # Búsqueda por nombre
            "carrera",  # Filtrado por carrera
        ],
    }