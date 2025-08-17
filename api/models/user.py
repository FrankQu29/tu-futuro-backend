from mongoengine import Document, StringField, BooleanField

from api.models.constants import MAIN_AREAS


class User(Document):
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
            "carrera",  # Búsqueda por nombre
            "main_area",  # Filtrado por ubicación
        ],
    }