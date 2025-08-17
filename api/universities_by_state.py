# places_universidades_por_estado.py
"""Utilidades para consultar universidades por estado usando Google Places.

Este módulo realiza búsquedas en la API de Google Places para obtener universidades
públicas y privadas por estado de México y genera archivos JSON con los resultados.

Requisitos:
- Variable de entorno GOOGLE_MAPS_API_KEY con una API Key válida de Google Maps/Places.
- requests instalado.

Funciones principales:
- buscar_universidades: ejecuta la consulta a Places y retorna resultados normalizados.
- top_5_por_tipo: obtiene hasta 5 públicas y 5 privadas por estado (deduplicadas).
- universidades_por_estados: procesa múltiples estados y agrega manejo de errores.
- guardar_universidades_json: persiste resultados a disco en carpeta 'salidas/'.

Advertencias y límites:
- La API de Places tiene cuotas y costos; usa parámetros con moderación.
- La paginación de Places usa next_page_token y puede requerir esperas breves; aquí
  se limita a 3 páginas por simplicidad.
"""
import os
import requests
from urllib.parse import urlencode
# Python
import json
from datetime import datetime
from pathlib import Path

API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")  # export GOOGLE_MAPS_API_KEY="tu_api_key"

PLACES_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"

def guardar_universidades_json(data, filename="universidades_mx.json", carpeta="salidas"):
    """Guarda un diccionario/lista de universidades como JSON en disco.

    Parámetros:
    - data: objeto serializable a JSON (dict o list) con la estructura de universidades.
    - filename (str): nombre del archivo de salida (por defecto universidades_mx.json).
    - carpeta (str): carpeta de salida; se crea si no existe (por defecto 'salidas').

    Retorna:
    - None. Crea/actualiza un archivo en la ruta especificada e imprime la ruta absoluta.
    """
    Path(carpeta).mkdir(parents=True, exist_ok=True)
    ruta = Path(carpeta) / filename
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Archivo guardado en: {ruta.resolve()}")

def buscar_universidades(consulta, region="mx", max_results=10):
    """Busca universidades en Google Places por consulta libre.

    Parámetros:
    - consulta (str): texto de búsqueda (ej. "universidad pública en Puebla, México").
    - region (str): código de región para sesgo de resultados (por defecto 'mx').
    - max_results (int): máximo de resultados acumulados a retornar.

    Detalles de implementación:
    - Usa el endpoint Text Search de Places y pagina hasta 3 iteraciones o hasta
      alcanzar max_results.
    - Normaliza resultados extrayendo name, lat, lng y formatted_address cuando existen.

    Retorna:
    - list[dict]: lista de universidades con llaves name, lat, lng, formatted_address.
    """
    params = {
        "query": consulta,
        "type": "university",
        "region": region,
        "key": API_KEY
    }
    resultados = []
    page = 0
    next_page_token = None

    while len(resultados) < max_results and page < 3:
        if next_page_token:
            params = {"pagetoken": next_page_token, "key": API_KEY}
        resp = requests.get(PLACES_URL, params=params, timeout=20)
        data = resp.json()
        if data.get("status") not in ("OK", "ZERO_RESULTS"):
            break

        for r in data.get("results", []):
            loc = r.get("geometry", {}).get("location", {})
            if "lat" in loc and "lng" in loc and r.get("name"):
                resultados.append({
                    "name": r["name"],
                    "lat": loc["lat"],
                    "lng": loc["lng"],
                    "formatted_address": r.get("formatted_address")
                })
            if len(resultados) >= max_results:
                break

        next_page_token = data.get("next_page_token")
        if not next_page_token:
            break
        page += 1

    return resultados

def top_5_por_tipo(estado):
    """Obtiene hasta 5 universidades públicas y 5 privadas para un estado.

    Estrategia:
    - Lanza dos búsquedas independientes (pública, privada) con un tope mayor (20)
      para tener margen y luego deduplicar por nombre.
    - Recorta la lista resultante a 5 por tipo, retornando una estructura homogenizada.

    Parámetros:
    - estado (str): nombre del estado de México (ej. "Puebla").

    Retorna:
    - list[dict]: lista combinada (públicas + privadas), cada item:
      {"name": str, "type": "publica|privada", "position": {"lat": float, "lng": float}}
    """
    publicas_raw = buscar_universidades(f"universidad pública en {estado}, México", max_results=20)
    privadas_raw = buscar_universidades(f"universidad privada en {estado}, México", max_results=20)

    # Deduplicar por nombre (case-insensitive)
    def dedup(lista):
        seen = set()
        out = []
        for item in lista:
            key = item["name"].strip().lower()
            if key in seen:
                continue
            seen.add(key)
            out.append(item)
        return out

    publicas = dedup(publicas_raw)[:5]
    privadas = dedup(privadas_raw)[:5]

    # Estructura final
    publicas_fmt = [
        {"name": u["name"], "type": "publica", "position": {"lat": u["lat"], "lng": u["lng"]}}
        for u in publicas
    ]
    privadas_fmt = [
        {"name": u["name"], "type": "privada", "position": {"lat": u["lat"], "lng": u["lng"]}}
        for u in privadas
    ]
    return publicas_fmt + privadas_fmt

def universidades_por_estados(estados):
    """Construye un diccionario de universidades por lista de estados.

    Parámetros:
    - estados (list[str]): nombres de estados de México.

    Comportamiento:
    - Por cada estado, intenta obtener top_5_por_tipo.
    - Si ocurre un error (HTTP, API, datos), captura y registra el error en el valor.

    Retorna:
    - dict[str, list|dict]: para cada estado, una lista de universidades o un
      objeto {"error": str} si falló.
    """
    salida = {}
    for estado in estados:
        try:
            salida[estado] = top_5_por_tipo(estado)
        except Exception as e:
            salida[estado] = {"error": str(e)}
    return salida

if __name__ == "__main__":
    # Ejemplo de uso: 10 universidades para algunos estados
    # Python
    estados = [
        "Aguascalientes",
        "Baja California",
        "Baja California Sur",
        "Campeche",
        "Coahuila",
        "Colima",
        "Chiapas",
        "Chihuahua",
        "Ciudad de México",
        "Durango",
        "Guanajuato",
        "Guerrero",
        "Hidalgo",
        "Jalisco",
        "Estado de México",
        "Michoacán",
        "Morelos",
        "Nayarit",
        "Nuevo León",
        "Oaxaca",
        "Puebla",
        "Querétaro",
        "Quintana Roo",
        "San Luis Potosí",
        "Sinaloa",
        "Sonora",
        "Tabasco",
        "Tamaulipas",
        "Tlaxcala",
        "Veracruz",
        "Yucatán",
        "Zacatecas",
    ]
    #data = universidades_por_estados(estados)
    #import json
    #print(json.dumps(data, ensure_ascii=False, indent=2))
    # Python
    data = universidades_por_estados(estados)

    # Conteo por estado (ignorando estados con error)
    counts_by_state = {
        estado: len(unis)
        for estado, unis in data.items()
        if isinstance(unis, list)
    }

    # Total global
    total_universidades = sum(counts_by_state.values())

    print("Conteo por estado:")
    for estado, count in counts_by_state.items():
        print(f"- {estado}: {count}")

    print(f"\nTotal global: {total_universidades}")


    # Opción 1: nombre fijo
    guardar_universidades_json(data)

    # Opción 2: nombre con timestamp
    ts_name = f"universidades_mx_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    guardar_universidades_json(data, filename=ts_name)
