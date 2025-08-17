# ... existing code ...
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from django.utils.crypto import get_random_string
from urllib.parse import urlencode
import base64
import os
import hashlib

from api.models.user import User

# ... existing code ...

class OAuth2StartAPIView(APIView):
    """
    GET /auth/oauth2/start?provider=google
    Devuelve la URL de autorización para redirigir al usuario (Authorization Code + PKCE).
    El frontend redirige a 'auth_url'.
    """
    def get(self, request):
        provider = request.query_params.get("provider")
        if not provider:
            return Response({"detail": "Falta 'provider'."}, status=status.HTTP_400_BAD_REQUEST)

        # TODO: Cargar config real por proveedor (client_id, scopes, endpoints)
        # Ejemplo con placeholders (ajusta según el proveedor):
        client_id = getattr(settings, "OAUTH_CLIENT_ID", None)
        auth_endpoint = getattr(settings, "OAUTH_AUTH_ENDPOINT", None)
        redirect_uri = getattr(settings, "OAUTH_REDIRECT_URI", None)
        scope = getattr(settings, "OAUTH_SCOPE", "openid email profile")

        if not all([client_id, auth_endpoint, redirect_uri]):
            return Response({"detail": "Config OAuth2 incompleta en settings."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # PKCE (code_verifier y code_challenge)
        code_verifier = base64.urlsafe_b64encode(os.urandom(40)).rstrip(b"=").decode("utf-8")
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode("utf-8")).digest()
        ).rstrip(b"=").decode("utf-8")

        # Guardar state y code_verifier en sesión/almacén seguro para validarlos en el callback
        state = get_random_string(24)
        request.session["oauth2_state"] = state
        request.session["oauth2_code_verifier"] = code_verifier
        request.session["oauth2_provider"] = provider

        params = {
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": scope,
            "state": state,
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            # Algunos proveedores aceptan 'prompt' o 'access_type'
        }
        auth_url = f"{auth_endpoint}?{urlencode(params)}"
        return Response({"auth_url": auth_url}, status=status.HTTP_200_OK)

# ... existing code ...

class OAuth2CallbackAPIView(APIView):
    """
    GET /auth/oauth2/callback?code=...&state=...
    Intercambia el 'code' por tokens, valida el id_token y registra/inicia sesión al usuario.
    """
    def get(self, request):
        code = request.query_params.get("code")
        state = request.query_params.get("state")
        sess_state = request.session.get("oauth2_state")
        code_verifier = request.session.get("oauth2_code_verifier")
        provider = request.session.get("oauth2_provider")

        if not code or not state:
            return Response({"detail": "Faltan parámetros 'code' o 'state'."}, status=status.HTTP_400_BAD_REQUEST)
        if not sess_state or state != sess_state:
            return Response({"detail": "State inválido."}, status=status.HTTP_400_BAD_REQUEST)
        if not code_verifier:
            return Response({"detail": "Falta code_verifier en sesión."}, status=status.HTTP_400_BAD_REQUEST)

        # Limpiar state/PKCE de sesión para evitar replay
        for k in ["oauth2_state", "oauth2_code_verifier", "oauth2_provider"]:
            request.session.pop(k, None)

        # Cargar configuración
        client_id = getattr(settings, "OAUTH_CLIENT_ID", None)
        token_endpoint = getattr(settings, "OAUTH_TOKEN_ENDPOINT", None)
        redirect_uri = getattr(settings, "OAUTH_REDIRECT_URI", None)
        if not all([client_id, token_endpoint, redirect_uri]):
            return Response({"detail": "Config OAuth2 incompleta en settings."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Intercambio de código por tokens (sin cliente secreto al usar PKCE en front-only o público)
        # Aquí deberías llamar al token_endpoint con:
        # {
        #   grant_type: "authorization_code",
        #   code,
        #   redirect_uri,
        #   client_id,
        #   code_verifier
        # }
        # TODO: Realizar petición HTTP al token_endpoint y manejar errores.
        # Ejemplo (placeholder):
        tokens = {
            # "access_token": "...",
            # "id_token": "...",
            # "refresh_token": "...",
            # "expires_in": 3600,
            # "token_type": "Bearer",
        }
        # TODO: Verificar cryptográficamente el id_token (firma, iss, aud, exp) y extraer claims.
        # claims = decode_and_verify_id_token(tokens["id_token"])

        # Suponiendo claims extraídos:
        claims = {
            # "email": "usuario@ejemplo.com",
            # "given_name": "Nombre",
            # "family_name": "Apellido",
            # "sub": "proveedor_user_id"
        }

        email = claims.get("email")
        if not email:
            return Response({"detail": "No se pudo obtener el email del proveedor."}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar o crear usuario base
        usuario = User.objects(email__iexact=email).first()
        if not usuario:
            # Si tu registro requiere más campos, aquí podrías rellenarlos con claims o pedirlos luego al front.
            usuario = User(
                first_name=claims.get("given_name") or "NA",
                last_name=claims.get("family_name") or "NA",
                email=email,
                ubicacion="NA",
                discapacidad="NA",
                carrera="NA",
                main_area="NA",
            )
            try:
                usuario.save()
            except Exception:
                return Response({"detail": "No se pudo crear el usuario."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Estrategia de sesión:
        # A) Cookie de sesión segura (recomendado para web): autentica al usuario en Django y setea cookie.
        # B) JWT propio: emitir access/refresh tokens desde tu backend (fuera del alcance de este stub).
        # Aquí devolvemos un payload mínimo:
        data = {
            "id": str(usuario.id),
            "email": usuario.email,
            "first_name": usuario.first_name,
            "last_name": usuario.last_name,
            "carrera": usuario.carrera,
            # "access_token": "<tu_token_si_emites_JWT>",
        }
        return Response(data, status=status.HTTP_200_OK)
# ... existing code ...
