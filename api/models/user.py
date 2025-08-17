from mongoengine import Document, StringField, BooleanField

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
    first_name = StringField(required=True)
    last_name = StringField(required=True)
    email = StringField(required=True)
    ubicacion = StringField(required=True)
    discapacidad = StringField(required=True)
    carrera = StringField(required=True)
    main_area = StringField(choices=MAIN_AREAS)
    #intereses = ListField(required=True)
    zona = BooleanField(required=True)

    meta = {
        "collection": "user",
        "indexes": [
            "carrera",  # Búsqueda por carrera
            "main_area",  # Filtrado por área
        ],
    }