
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.models.carrera import Carrera
from api.models.formulario import Formulario

class DashboardPromedioResultadosPorCarreraAPIView(APIView):
    """
    GET /api/dashboard/formularios/promedio-por-carrera
    Recorre todas las carreras, toma sus subáreas y calcula el promedio de 'resultados'
    de los formularios asociados a esas subáreas (solo aquellos con 'resultados' != None).
    Retorna una lista con objetos { "carrera": <nombre>, "promedio": <float|null> }.
    """
    def get(self, request):
        resultados = []

        # Traer solo campos necesarios
        for carrera in Carrera.objects.only("nombre", "sub_areas"):
            subareas = carrera.sub_areas or []
            if not subareas:
                resultados.append({"carrera": carrera.nombre, "promedio": None})
                continue

            # Formularios con resultados no nulos para subáreas de la carrera
            formularios = Formulario.objects(
                subarea__in=subareas,
                resultados__ne=None
            ).only("resultados")

            valores = [f.resultados for f in formularios if isinstance(f.resultados, (int, float))]
            if not valores:
                resultados.append({"carrera": carrera.nombre, "promedio": None})
                continue

            promedio = sum(valores) / len(valores)
            resultados.append({"carrera": carrera.nombre, "promedio": promedio})

        return Response(resultados, status=status.HTTP_200_OK)
# ... existing code ...