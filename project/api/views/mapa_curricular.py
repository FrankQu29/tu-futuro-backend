from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
# ... existing code ...
from api.models.mapa_curricular import MapaCurricular

class CreateMapaCurricularAPIView(APIView):
    """
    POST /api/mapa-curricular
    Body: objeto JSON con {nombre, descripcion, carrera}
    """
    def post(self, request):
        data = request.data or {}
        required = ["nombre", "descripcion", "carrera"]
        missing = [f for f in required if not data.get(f)]
        if missing:
            return Response({"detail": f"Faltan campos: {', '.join(missing)}"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            doc = MapaCurricular(
                nombre=str(data["nombre"]).strip(),
                descripcion=str(data["descripcion"]).strip(),
                carrera=str(data["carrera"]).strip(),
            )
            doc.save()
            return Response(
                {
                    "id": str(doc.id),
                    "nombre": doc.nombre,
                    "descripcion": doc.descripcion,
                    "carrera": doc.carrera,
                },
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ... existing code ...

class BulkCreateMapaCurricularAPIView(APIView):
    """
    POST /api/bulk/mapa-curricular
    Body: arreglo JSON de objetos con {nombre, descripcion, carrera}
    """
    def post(self, request):
        items = request.data
        if not isinstance(items, list):
            return Response({"detail": "Se esperaba un arreglo JSON."}, status=status.HTTP_400_BAD_REQUEST)

        created_ids, errors = [], []
        for i, data in enumerate(items):
            try:
                for f in ("nombre", "descripcion", "carrera"):
                    if not data.get(f):
                        raise ValueError(f"Falta campo obligatorio: {f}")
                doc = MapaCurricular(
                    nombre=str(data["nombre"]).strip(),
                    descripcion=str(data["descripcion"]).strip(),
                    carrera=str(data["carrera"]).strip(),
                )
                doc.save()
                created_ids.append(str(doc.id))
            except Exception as e:
                errors.append({"index": i, "error": str(e)})

        if created_ids and not errors:
            return Response({"created": len(created_ids), "ids": created_ids}, status=status.HTTP_201_CREATED)
        if created_ids and errors:
            return Response(
                {"created": len(created_ids), "ids": created_ids, "failed": len(errors), "errors": errors},
                status=status.HTTP_207_MULTI_STATUS,
            )
        return Response({"failed": len(errors), "errors": errors}, status=status.HTTP_400_BAD_REQUEST)