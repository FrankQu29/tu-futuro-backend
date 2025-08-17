from mongoengine import Document, StringField, BooleanField, ListField

from api.models.constants import MAIN_AREAS


class User(Document):
    """Modelo de Usuario del sistema.

    Campos:
    - first_name (str, req.): Nombre.
    - last_name (str, req.): Apellidos.
    - email (str, req.): Correo electrónico único de contacto.
    - ubicacion (str, req.): Ubicación (libre, p.ej. estado/ciudad).
    - discapacidad (str, req.): Información de discapacidad (si aplica).
    - carrera (str, req.): Carrera de interés/estudio.
    - main_area (str, choices=MAIN_AREAS): Área principal asociada.
    - zona (bool, req.): Bandera genérica (p.ej., zona geográfica preferente).
    """
    first_name = StringField()
    last_name = StringField()
    email = StringField()
    ubicacion = StringField()
    discapacidad = StringField()
    carrera = StringField()
    main_area = StringField(choices=MAIN_AREAS)
    intereses = ListField()
    zona = BooleanField()

    meta = {
        "collection": "user",
        "indexes": [
            "carrera",  # Búsqueda por carrera
            "main_area",  # Filtrado por área
        ],
    }