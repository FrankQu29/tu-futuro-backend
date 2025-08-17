
from mongoengine import StringField, FloatField, Document

class Voluntariado(Document):
    carrera = StringField(required=True)
    titulo = StringField(required=True)
    descripcion = StringField(required=True)
    ubicacion = StringField(required=True)
    salario = FloatField(required=True)
    permalink = StringField(required=True)
