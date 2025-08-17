from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from api.models.formulario import Formulario


class BulkCreateFormulariosAPIView(APIView):
    """
    POST /api/bulk/formularios
    Body: JSON array de objetos Formulario
    """
    def post(self, request):
        items = request.data
        if not isinstance(items, list):
            return Response({"detail": "Se esperaba un arreglo JSON."}, status=status.HTTP_400_BAD_REQUEST)

        created_ids, errors = [], []
        for i, data in enumerate(items):
            try:
                obj = Formulario(**data)
                obj.save()
                created_ids.append(str(obj.id))
            except Exception as e:
                errors.append({"index": i, "error": str(e)})

        if created_ids and not errors:
            return Response({"created": len(created_ids), "ids": created_ids}, status=status.HTTP_201_CREATED)
        if created_ids and errors:
            return Response({"created": len(created_ids), "ids": created_ids, "failed": len(errors), "errors": errors}, status=status.HTTP_207_MULTI_STATUS)
        return Response({"failed": len(errors), "errors": errors}, status=status.HTTP_400_BAD_REQUEST)
