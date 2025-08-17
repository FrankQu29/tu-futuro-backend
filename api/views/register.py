
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json

from api.models.user import User


@method_decorator(csrf_exempt, name="dispatch")
class RegistroUsuarioView(View):
    """
    POST /api/usuarios/registro
    Content-Type: application/json

    Cuerpo esperado (registro tradicional):
    {
      "first_name": "...",
      "last_name": "...",
      "email": "...",
      "ubicacion": "...",
      "discapacidad": "...",
      "carrera": "...",
      "main_area": "..."
    }

    Cuerpo alternativo (pensado para OAuth2):
    {
      "oauth_provider": "google|github|... ",
      "oauth_token": "token_o_id_token_del_proveedor",
      "email": "...",
      "first_name": "...",
      "last_name": "...",
      "ubicacion": "...",
      "discapacidad": "...",
      "carrera": "...",
      "main_area": "..."
    }

    Notas de diseño para OAuth2:
    - En una integración real, valida oauth_token con el proveedor (p.ej., verificación de ID Token JWT).
    - Tras validar, crea/recupera el usuario por email (o sub del proveedor) y enlaza la cuenta.
    - Puedes añadir campos al modelo (p.ej., provider, provider_id) en una iteración posterior.
    """

    def post(self, request):
        try:
            payload = json.loads(request.body.decode("utf-8"))
        except Exception:
            return JsonResponse({"detail": "JSON inválido."}, status=400)

        oauth_provider = payload.get("oauth_provider")
        oauth_token = payload.get("oauth_token")

        # Si decides validar campos obligatorios, descomenta y ajusta:
        # required_fields = ["first_name", "last_name", "email", "ubicacion", "discapacidad", "carrera", "main_area"]
        # missing = [f for f in required_fields if not payload.get(f)]
        # if missing:
        #     return JsonResponse({"detail": f"Faltan campos: {', '.join(missing)}"}, status=400)

        email = payload["email"].strip().lower()

        if oauth_provider:
            if not oauth_token:
                return JsonResponse({"detail": "Falta 'oauth_token' para el registro OAuth2."}, status=400)
            # TODO: Verificar el token con el proveedor y extraer claims.

        existente = User.objects(email__iexact=email).first()
        if existente:
            return JsonResponse({"detail": "El email ya está registrado."}, status=409)

        try:
            # Si no te envían 'zona', pon un valor por defecto para cumplir con el required=True del modelo
            zona_val = bool(payload.get("zona", False))

            usuario = User(
                first_name=payload["first_name"].strip(),
                last_name=payload["last_name"].strip(),
                email=email,
                ubicacion=payload["ubicacion"].strip(),
                discapacidad=payload["discapacidad"].strip(),
                carrera=payload["carrera"].strip(),
                main_area=payload["main_area"].strip(),
                zona=zona_val,
            )
            usuario.save()
        except Exception as e:
            # IMPORTANTE: convertir la excepción a string para que sea serializable en JSON
            return JsonResponse({"detail": str(e)}, status=500)

        data = {
            "id": str(usuario.id),
            "first_name": usuario.first_name,
            "last_name": usuario.last_name,
            "email": usuario.email,
            "ubicacion": usuario.ubicacion,
            "discapacidad": usuario.discapacidad,
            "carrera": usuario.carrera,
            "main_area": usuario.main_area,
            "zona": usuario.zona,
        }
        return JsonResponse(data, status=201)
# ... existing code ...
