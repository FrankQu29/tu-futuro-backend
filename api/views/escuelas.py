from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from api.models.escuela import Escuela
from api.models.escuela import Coordenadas  # EmbeddedDocument esperado para ubicacion


class BulkCreateEscuelasAPIView(APIView):
    """
    POST /api/bulk/escuelas
    Body: JSON array de objetos Escuela.
    Esquema esperado por elemento:
    {
      "nombre": "Universidad X",
      "ubicacion": [ {"lat": 19.43, "lng": -99.13}, {"lat": 19.44, "lng": -99.14} ],  # lista de coordenadas
      "type": "publica" | "privada",
      "carreras": ["Ingeniería", "Biología"],
      "costo": 12000.0
    }
    """

    def post(self, request):
        items = request.data
        if not isinstance(items, list):
            return Response({"detail": "Se esperaba un arreglo JSON."}, status=status.HTTP_400_BAD_REQUEST)

        def parse_ubicacion(value, idx):
            if not isinstance(value, list) or not value:
                raise ValueError(f"[index {idx}] 'ubicacion' debe ser una lista no vacía de objetos {{lat, lng}}.")
            coords = []
            for j, it in enumerate(value):
                if not isinstance(it, dict):
                    raise ValueError(f"[index {idx}] ubicacion[{j}] debe ser un objeto con 'lat' y 'lng'.")
                lat = it.get("lat")
                lng = it.get("lng")
                if lat is None or lng is None:
                    raise ValueError(f"[index {idx}] ubicacion[{j}] requiere 'lat' y 'lng'.")
                try:
                    coords.append(Coordenadas(lat=float(lat), lng=float(lng)))
                except Exception:
                    raise ValueError(f"[index {idx}] ubicacion[{j}] 'lat' y 'lng' deben ser numéricos.")
            return coords

        allowed_types = {"publica", "privada"}

        created_ids, errors = [], []
        for i, data in enumerate(items):
            try:
                if not isinstance(data, dict):
                    raise ValueError(f"[index {i}] cada elemento debe ser un objeto JSON.")

                # Validación de campos requeridos
                required = ["nombre", "ubicacion", "type", "carreras", "costo"]
                missing = [f for f in required if data.get(f) in (None, "", [])]
                if missing:
                    raise ValueError(f"[index {i}] faltan campos requeridos: {', '.join(missing)}")

                nombre = str(data["nombre"]).strip()

                # Normalizar y validar type
                tipo = str(data["type"]).strip().lower()
                if tipo not in allowed_types:
                    raise ValueError(f"[index {i}] 'type' inválido. Use: {', '.join(sorted(allowed_types))}")

                # Parsear ubicacion -> lista de Coordenadas
                ubicacion = parse_ubicacion(data["ubicacion"], i)

                # Carreras debe ser lista
                carreras = data["carreras"]
                if not isinstance(carreras, list) or not all(isinstance(c, str) for c in carreras):
                    raise ValueError(f"[index {i}] 'carreras' debe ser una lista de strings.")

                # Costo numérico
                try:
                    costo = float(data["costo"])
                except Exception:
                    raise ValueError(f"[index {i}] 'costo' debe ser numérico.")

                obj = Escuela(
                    nombre=nombre,
                    ubicacion=ubicacion,
                    type=tipo,
                    carreras=carreras,
                    costo=costo,
                )
                obj.save()
                created_ids.append(str(obj.id))
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
