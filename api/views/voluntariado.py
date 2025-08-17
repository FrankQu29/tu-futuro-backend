from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.models.voluntariado import Voluntariado

class BulkCreateVoluntariadosAPIView(APIView):
    """
    POST /api/bulk/voluntariados
    Body: JSON array de objetos Voluntariado
    """
    def post(self, request):
        items = request.data
        if not isinstance(items, list):
            return Response({"detail": "Se esperaba un arreglo JSON."}, status=status.HTTP_400_BAD_REQUEST)

        created_ids, errors = [], []
        for i, data in enumerate(items):
            try:
                obj = Voluntariado(**data)
                obj.save()
                created_ids.append(str(obj.id))
            except Exception as e:
                errors.append({"index": i, "error": str(e)})

        if created_ids and not errors:
            return Response({"created": len(created_ids), "ids": created_ids}, status=status.HTTP_201_CREATED)
        if created_ids and errors:
            return Response({"created": len(created_ids), "ids": created_ids, "failed": len(errors), "errors": errors}, status=status.HTTP_207_MULTI_STATUS)
        return Response({"failed": len(errors), "errors": errors}, status=status.HTTP_400_BAD_REQUEST)


class VoluntariadosPorCarreraAPIView(APIView):
    """
    GET /api/voluntariados?carrera=<nombre_carrera>
    Parámetros de consulta:
    - carrera (str, requerido): nombre de la carrera para filtrar (case-insensitive).

    Respuesta: lista de voluntariados [{carrera, titulo, descripcion, ubicacion, salario, permalink}].
    """
    def get(self, request):
        carrera = request.query_params.get("carrera")
        if not carrera:
            return Response({"detail": "Falta el parámetro 'carrera'."}, status=status.HTTP_400_BAD_REQUEST)

        voluntariados = Voluntariado.objects(carrera__iexact=carrera)

        data = [
            {
                "carrera": v.carrera,
                "titulo": v.titulo,
                "descripcion": v.descripcion,
                "ubicacion": v.ubicacion,
                "salario": v.salario,
                "permalink": v.permalink,
            }
            for v in voluntariados
        ]
        return Response(data, status=status.HTTP_200_OK)
