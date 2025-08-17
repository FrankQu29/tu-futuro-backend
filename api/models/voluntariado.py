
from mongoengine import StringField, FloatField, Document

class Voluntariado(Document):
    """Modelo de Voluntariado.

    Publicaciones de voluntariados asociados a carreras.

    Campos:
    - carrera (str, req.): Carrera objetivo del voluntariado.
    - titulo (str, req.): Título de la vacante/actividad.
    - descripcion (str, req.): Detalle de actividades/rol.
    - ubicacion (str, req.): Ubicación de la actividad.
    - salario (float, req.): Estimación de apoyo/estímulo (si aplica).
    - permalink (str, req.): Enlace permanente a la publicación.
    """
    carrera = StringField(required=True)
    titulo = StringField(required=True)
    descripcion = StringField(required=True)
    ubicacion = StringField(required=True)
    salario = FloatField(required=True)
    permalink = StringField(required=True)
