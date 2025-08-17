from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.models.mapa_curricular import MapaCurricular
from api.models.subarea import Subarea, Leccion
from api.models.formulario import Formulario

class BulkCreateSubareasAPIView(APIView):
    """
    POST /api/bulk/subareas
    Body: JSON array de objetos Subarea
    """
    def post(self, request):
        items = request.data
        if not isinstance(items, list):
            return Response({"detail": "Se esperaba un arreglo JSON."}, status=status.HTTP_400_BAD_REQUEST)

        created_ids, errors = [], []
        for i, data in enumerate(items):
            try:
                payload = dict(data)

                # Normalización: lecciones puede venir como lista de dicts
                if "lecciones" in payload and isinstance(payload["lecciones"], list):
                    payload["lecciones"] = [
                        Leccion(**l) if not isinstance(l, Leccion) else l
                        for l in payload["lecciones"]
                    ]

                # Asegurar que videos_escuela sea lista
                if "videos_escuela" in payload and not isinstance(payload["videos_escuela"], list):
                    raise ValueError("El campo 'videos_escuela' debe ser una lista.")

                # Validar campos mínimos esperados
                for field in ("nombre", "introduccion", "descripcion", "carrera", "lecciones", "videos_escuela"):
                    if field not in payload:
                        raise ValueError(f"Falta el campo requerido '{field}'.")

                obj = Subarea(**payload)
                obj.validate()  # validación explícita para mejores mensajes
                obj.save()
                created_ids.append(str(obj.id))
            except Exception as e:
                errors.append({"index": i, "error": str(e)})

        if created_ids and not errors:
            return Response({"created": len(created_ids), "ids": created_ids}, status=status.HTTP_201_CREATED)
        if created_ids and errors:
            return Response({"created": len(created_ids), "ids": created_ids, "failed": len(errors), "errors": errors}, status=status.HTTP_207_MULTI_STATUS)
        return Response({"failed": len(errors), "errors": errors}, status=status.HTTP_400_BAD_REQUEST)

class SubareaDetallePorNombreAPIView(APIView):
    """
    GET /api/subarea?nombre=<nombre_subarea>
    Retorna el documento completo de Subarea cuyo nombre coincide (case-insensitive).
    """
    def get(self, request):
        nombre = request.query_params.get("nombre")
        if not nombre:
            return Response({"detail": "Falta el parámetro 'nombre'."}, status=status.HTTP_400_BAD_REQUEST)

        subarea_norm = nombre.strip()
        subarea = Subarea.objects(nombre__iexact=subarea_norm).first()
        if not subarea:
            return Response({"detail": "Subarea no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        data = {
            "id": str(subarea.id),
            "nombre": subarea.nombre,
            "introduccion": subarea.introduccion,
            "descripcion": subarea.descripcion,
            "videos_escuela": list(subarea.videos_escuela or []),
            "carrera": subarea.carrera,
            "lecciones": [
                {
                    "titulo": lec.titulo,
                    "videos": list(lec.videos or []),
                    "descripcion": lec.descripcion,
                }
                for lec in (subarea.lecciones or [])
            ],
        }
        return Response(data, status=status.HTTP_200_OK)

class MapaCurricularNombresPorCarreraAPIView(APIView):
    """
    GET /api/carreras/mapa-curricular?carrera=<nombre_carrera>
    Retorna una lista con los nombres del mapa curricular de la carrera indicada.
    Si 'mapa_curricular' es una lista de strings, se devuelve tal cual.
    Si es una lista de objetos, se extrae la clave 'nombre' de cada elemento.
    """

    def get(self, request):
        carrera_param = request.query_params.get("carrera")
        if not carrera_param:
            return Response({"detail": "Falta el parámetro 'carrera'."}, status=status.HTTP_400_BAD_REQUEST)

        materias = MapaCurricular.objects(carrera__iexact=carrera_param.strip()).only("nombre")
        nombres = [m.nombre for m in materias]
        return Response(nombres, status=status.HTTP_200_OK)

class DescripcionMateriaMapaCurricularAPIView(APIView):
    """
    GET /api/carreras/mapa-curricular/descripcion?materia=<nombre_materia>
    Retorna la descripción de la materia dentro del mapa curricular (primer match).
    """

    def get(self, request):
        materia = request.query_params.get("materia")
        if not materia:
            return Response({"detail": "Falta el parámetro 'materia'."}, status=status.HTTP_400_BAD_REQUEST)

        doc = MapaCurricular.objects(nombre__iexact=materia.strip()).only("descripcion").first()
        if not doc:
            return Response({"detail": "Materia no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"descripcion": doc.descripcion}, status=status.HTTP_200_OK)

class FormularioPorSubareaAPIView(APIView):
    """
    GET /api/formulario?subarea=<nombre_subarea>
    Retorna el documento completo de Formulario asociado a la subárea indicada (match case-insensitive).
    """
    def get(self, request):
        subarea = request.query_params.get("subarea")
        if not subarea:
            return Response({"detail": "Falta el parámetro 'subarea'."}, status=status.HTTP_400_BAD_REQUEST)

        subarea_norm = subarea.strip()
        formulario = Formulario.objects(subarea__iexact=subarea_norm).first()
        if not formulario:
            return Response({"detail": "Formulario no encontrado para la subárea indicada."}, status=status.HTTP_404_NOT_FOUND)

        data = {
            "id": str(formulario.id),
            "nombre": formulario.nombre,
            "descripcion": formulario.descripcion,
            "preguntas": formulario.preguntas,
            "respuestas": formulario.respuestas,
            "resultados": formulario.resultados,
            "subarea": formulario.subarea,
        }
        return Response(data, status=status.HTTP_200_OK)

class SubareasPorCarreraAPIView(APIView):
    """
    GET /api/subareas?carrera=<nombre_carrera>
    Lista las subáreas pertenecientes a una carrera (case-insensitive).
    """
    def get(self, request):
        carrera = request.query_params.get("carrera")
        if not carrera:
            return Response({"detail": "Falta el parámetro 'carrera'."}, status=status.HTTP_400_BAD_REQUEST)

        qs = Subarea.objects(carrera__iexact=carrera.strip()).only(
            "nombre", "introduccion", "descripcion", "videos_escuela", "carrera", "lecciones"
        )
        result = []
        for s in qs:
            result.append({
                "id": str(s.id),
                "nombre": s.nombre,
                "introduccion": s.introduccion,
                "descripcion": s.descripcion,
                "videos_escuela": list(s.videos_escuela or []),
                "carrera": s.carrera,
                "lecciones": [
                    {
                        "titulo": lec.titulo,
                        "videos": list(lec.videos or []),
                        "descripcion": lec.descripcion,
                    }
                    for lec in (s.lecciones or [])
                ],
            })
        return Response(result, status=status.HTTP_200_OK)