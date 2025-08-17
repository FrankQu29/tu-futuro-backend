from mongoengine import Document, StringField, FloatField, ListField

class Formulario(Document):
    """Modelo de Formulario.

    Representa un formulario de evaluación asociado a una subárea.

    Campos:
    - nombre (str, requerido): Título del formulario.
    - descripcion (str, requerido): Descripción del objetivo del formulario.
    - preguntas (list, requerido): Lista de preguntas (estructura libre según front).
    - respuestas (list, requerido): Lista de respuestas o estructura capturada.
    - resultados (float, requerido, default=None): Puntaje o resultado calculado.
    - subarea (str, requerido): Nombre de la subárea a la que pertenece.
    """
    nombre = StringField()
    descripcion = StringField()
    preguntas = ListField()
    respuestas = ListField()
    resultados = FloatField(default=None)
    subarea = StringField()

    meta = {
        "collection": "formularios",
        # Alias de conexión si usas múltiples bases: "db_alias": "default",
        # Índices recomendados:
        "indexes": [
            "resultados",  # Consultas por resultado
            "subarea",  # Filtrado por subárea
        ],
    }