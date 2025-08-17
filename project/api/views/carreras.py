from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.models.carrera import Carrera
from api.models.escuela import Escuela
from api.models.subarea import Subarea
from api.models.constants import MAIN_AREAS

class BulkCreateCarrerasAPIView(APIView):
    """
    POST /api/bulk/carreras
    Body: JSON array de objetos Carrera
    """
    def post(self, request):
        items = request.data
        if not isinstance(items, list):
            return Response({"detail": "Se esperaba un arreglo JSON."}, status=status.HTTP_400_BAD_REQUEST)

        created_ids, errors = [], []
        for i, data in enumerate(items):
            try:
                obj = Carrera(**data)
                obj.save()
                created_ids.append(str(obj.id))
            except Exception as e:
                errors.append({"index": i, "error": str(e)})

        if created_ids and not errors:
            return Response({"created": len(created_ids), "ids": created_ids}, status=status.HTTP_201_CREATED)
        if created_ids and errors:
            return Response({"created": len(created_ids), "ids": created_ids, "failed": len(errors), "errors": errors}, status=status.HTTP_207_MULTI_STATUS)
        return Response({"failed": len(errors), "errors": errors}, status=status.HTTP_400_BAD_REQUEST)


class CarrerasPorAreaAPIView(APIView):
    """
    GET /api/carreras?area=<area>
    - Si 'area' se envía: retorna lista de nombres de carreras con main_area == area (case-insensitive).
    - Si no se envía: retorna todos los nombres de carreras.
    """
    def get(self, request):
        area = request.query_params.get("area")
        if area:
            area_norm = area.strip().lower()
            if area_norm not in MAIN_AREAS:
                return Response({"detail": "Área inválida."}, status=status.HTTP_400_BAD_REQUEST)
            qs = Carrera.objects(main_area__iexact=area_norm)
        else:
            qs = Carrera.objects

        nombres = [c.nombre for c in qs.only("nombre")]
        return Response(nombres, status=status.HTTP_200_OK)


class EscuelasPorCarreraAPIView(APIView):
    """
    GET /api/escuelas?carrera=<nombre_carrera>
    Retorna los documentos de Escuela cuya lista 'carreras' contiene la carrera indicada.
    """
    def get(self, request):
        carrera = request.query_params.get("carrera")
        if not carrera:
            return Response({"detail": "Falta el parámetro 'carrera'."}, status=status.HTTP_400_BAD_REQUEST)

        carrera_norm = carrera.strip()
        # Coincidencia exacta de elemento en el arreglo 'carreras'
        escuelas = Escuela.objects(carreras=carrera_norm).only(
            "nombre", "ubicacion", "carreras", "costo", "type"
        )

        def serialize_ubicacion(ubis):
            # ubis es una lista de EmbeddedDocument Coordenadas con atributos lat y lng
            try:
                return [{"lat": u.lat, "lng": u.lng} for u in (ubis or [])]
            except Exception:
                # fallback si viniera como dicts ya simples
                return [{"lat": u.get("lat"), "lng": u.get("lng")} for u in (ubis or []) if isinstance(u, dict)]

        data = [
            {
                "nombre": e.nombre,
                "ubicacion": serialize_ubicacion(e.ubicacion),
                "carreras": e.carreras,
                "costo": e.costo,
                "type": e.type,
            }
            for e in escuelas
        ]
        return Response(data, status=status.HTTP_200_OK)

# ... existing code ...

class SubareasPorCarreraAPIView(APIView):
    """
    GET /api/subareas?carrera=<nombre_carrera>
    Retorna una lista con los nombres de subáreas asociadas a la carrera indicada.
    """
    def get(self, request):
        carrera = request.query_params.get("carrera")
        if not carrera:
            return Response({"detail": "Falta el parámetro 'carrera'."}, status=status.HTTP_400_BAD_REQUEST)

        carrera_norm = carrera.strip()
        subareas = Subarea.objects(carrera__iexact=carrera_norm).only("nombre")
        nombres = [s.nombre for s in subareas]
        return Response(nombres, status=status.HTTP_200_OK)