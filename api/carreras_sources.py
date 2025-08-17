"""carreras_sources.py
Utilidades para recolectar datos de licenciaturas/carreras desde fuentes públicas.

Este módulo provee funciones para:
- Buscar posibles licenciaturas en Wikipedia (API de MediaWiki, sin API key).
- Consultar Wikidata mediante SPARQL (opcional) para enriquecer resultados.
- Normalizar resultados al esquema del modelo Carrera (nombre, descripcion, main_area...)
- Guardar resultados en JSON en la carpeta 'salidas/'.
- (Opcional) Cargar resultados directamente a la base de datos (MongoEngine) como documentos Carrera.

Advertencias y límites:
- Las APIs públicas pueden cambiar su formato o imponer límites de cuota.
- Las consultas aquí son heurísticas; revise manualmente los resultados antes de cargarlos en producción.
- El campo 'main_area' se infiere de términos de búsqueda si se proveen; de lo contrario queda vacío.

Ejemplos de uso (desde consola Python/Django shell):

    from api.carreras_sources import wikipedia_buscar_licenciaturas, normalizar_a_carrera, guardar_json, cargar_en_bd

    seeds = [
        {"termino": "Licenciatura en Ingeniería" , "main_area": "ciencias"},
        {"termino": "Licenciatura en Derecho"    , "main_area": "humanidades"},
        {"termino": "Licenciatura en Medicina"   , "main_area": "ciencias"},
        {"termino": "Licenciatura en Contaduría" , "main_area": "sociales"},
    ]

    resultados = wikipedia_buscar_licenciaturas(seeds, max_por_termino=8)
    carreras = normalizar_a_carrera(resultados)
    guardar_json(carreras, filename="licenciaturas_wikipedia.json")
    # Opcional: cargar en BD (MongoEngine debe estar configurado en settings)
    # cargar_en_bd(carreras)

"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

import requests

# Endpoints públicos
WIKI_API_URL = "https://es.wikipedia.org/w/api.php"
WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"


def wikipedia_buscar_licenciaturas(seeds: List[Dict[str, str]], max_por_termino: int = 10, timeout: int = 15) -> List[Dict[str, str]]:
    """Realiza búsquedas en Wikipedia para una lista de términos seed.

    Parámetros:
    - seeds: lista de objetos {"termino": str, "main_area": str?}.
      Se consulta Wikipedia por 'termino' y se obtiene título y extracto.
    - max_por_termino: máximo de páginas por término.
    - timeout: segundos de timeout por petición HTTP.

    Retorna:
    - list[dict]: cada item incluye {"title", "extract", "url", "main_area"?}
    """
    resultados: List[Dict[str, str]] = []
    session = requests.Session()

    for seed in seeds:
        termino = str(seed.get("termino", "")).strip()
        if not termino:
            continue
        main_area = seed.get("main_area")

        params = {
            "action": "query",
            "format": "json",
            "prop": "extracts|info",
            "generator": "search",
            "gsrsearch": termino,
            "gsrlimit": max_por_termino,
            # Extracto breve en texto plano
            "exintro": 1,
            "explaintext": 1,
            # URL info
            "inprop": "url",
        }
        try:
            resp = session.get(WIKI_API_URL, params=params, timeout=timeout)
            data = resp.json()
        except Exception:
            continue

        pages = (data.get("query", {}) or {}).get("pages", {})
        for _, page in pages.items():
            title = page.get("title")
            extract = page.get("extract")
            fullurl = page.get("fullurl")
            if not title:
                continue
            item = {
                "title": title,
                "extract": extract or "",
                "url": fullurl or "",
            }
            if main_area:
                item["main_area"] = main_area
            resultados.append(item)

    return resultados


def wikidata_buscar_licenciaturas_por_area(area_palabra_clave: str, limite: int = 50, timeout: int = 20) -> List[Dict[str, str]]:
    """Consulta Wikidata para items relacionados a licenciaturas por palabra clave.

    Nota: Esta consulta es genérica y busca etiquetas/escrituras que contengan
    la palabra clave en español; puede traer falsos positivos.

    Parámetros:
    - area_palabra_clave: por ejemplo "ingeniería", "derecho", "medicina".
    - limite: tope de resultados.

    Retorna:
    - list[dict]: items con {"label", "description", "wikidata", "wikipedia"}
    """
    # SPARQL simplificado: busca entidades con label o altLabel que contengan el término en es.
    query = f"""
    SELECT ?item ?itemLabel ?itemDescription ?eswiki WHERE {{
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "es". }}
      ?item rdfs:label ?itemLabel.
      FILTER(CONTAINS(LCASE(?itemLabel), LCASE("{area_palabra_clave}"))).
      OPTIONAL {{ ?item schema:description ?itemDescription FILTER (lang(?itemDescription) = "es"). }}
      OPTIONAL {{ ?eswiki schema:about ?item ; schema:isPartOf <https://es.wikipedia.org/>. }}
    }} LIMIT {int(limite)}
    """
    headers = {
        "Accept": "application/sparql-results+json",
        "User-Agent": "cardic-system/1.0 (licenciaturas; contacto: ejemplo@example.com)",
    }
    try:
        resp = requests.get(WIKIDATA_SPARQL_URL, params={"query": query}, headers=headers, timeout=timeout)
        data = resp.json()
    except Exception:
        return []

    resultados: List[Dict[str, str]] = []
    for b in data.get("results", {}).get("bindings", []):
        label = (b.get("itemLabel") or {}).get("value")
        desc = (b.get("itemDescription") or {}).get("value")
        item_uri = (b.get("item") or {}).get("value")
        eswiki = (b.get("eswiki") or {}).get("value")
        if not label:
            continue
        resultados.append({
            "title": label,
            "extract": desc or "",
            "wikidata": item_uri or "",
            "url": eswiki or "",
            "main_area": area_palabra_clave,
        })
    return resultados


def normalizar_a_carrera(items: List[Dict[str, str]]) -> List[Dict[str, Optional[str]]]:
    """Convierte resultados de Wikipedia/Wikidata al esquema de Carrera.

    Salida mínima por elemento:
    {
      "nombre": str,
      "descripcion": str,
      "main_area": str | "",
      "videos": [],
      "sub_areas": []
    }
    """
    carreras: List[Dict[str, Optional[str]]] = []
    for it in items:
        nombre = it.get("title") or it.get("label") or ""
        if not nombre:
            continue
        carreras.append({
            "nombre": nombre,
            "descripcion": (it.get("extract") or it.get("description") or "").strip(),
            "main_area": (it.get("main_area") or "").strip() if isinstance(it.get("main_area"), str) else "",
            "videos": [],
            "sub_areas": [],
            # Información de origen útil (no existe en el modelo, se omite al guardar en BD)
            "_source_url": it.get("url", ""),
            "_source_wikidata": it.get("wikidata", ""),
        })
    return carreras


def guardar_json(data, filename: str = "licenciaturas.json", carpeta: str = "salidas") -> None:
    """Guarda datos como JSON en la carpeta indicada."""
    Path(carpeta).mkdir(parents=True, exist_ok=True)
    ruta = Path(carpeta) / filename
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Archivo guardado en: {ruta.resolve()}")


def cargar_en_bd(carreras: List[Dict[str, Optional[str]]]) -> Dict[str, int]:
    """Inserta carreras en MongoDB usando el modelo Carrera.

    Nota: Ignora claves que no estén en el modelo (p.ej., _source_url). Si existe un
    nombre duplicado, intenta actualizar la descripción (estrategia simple). Ajusta
    según tu necesidad.
    """
    try:
        from api.models.carrera import Carrera  # Import local para evitar dependencias en tiempo de import
    except Exception as e:
        print("No se pudo importar el modelo Carrera:", e)
        return {"created": 0, "updated": 0, "failed": 0}

    created = updated = failed = 0
    for item in carreras:
        data = {k: v for k, v in item.items() if k in {"nombre", "descripcion", "main_area", "videos", "sub_areas"}}
        try:
            # Estrategia: upsert por nombre (case-insensitive)
            existente = Carrera.objects(nombre__iexact=data.get("nombre", "")).first()
            if existente:
                # Actualizar campos básicos si vienen no vacíos
                changed = False
                for k in ("descripcion", "main_area"):
                    val = data.get(k)
                    if val:
                        setattr(existente, k, val)
                        changed = True
                if isinstance(data.get("videos"), list) and data.get("videos"):
                    existente.videos = data["videos"]
                    changed = True
                if isinstance(data.get("sub_areas"), list) and data.get("sub_areas"):
                    existente.sub_areas = data["sub_areas"]
                    changed = True
                if changed:
                    existente.save()
                    updated += 1
                else:
                    # No cambios efectivos, contar como actualizado sin modificaciones
                    updated += 1
            else:
                obj = Carrera(**data)
                obj.save()
                created += 1
        except Exception as e:
            print(f"Error guardando '{data.get('nombre', 'N/A')}':", e)
            failed += 1
    resumen = {"created": created, "updated": updated, "failed": failed}
    print("Resumen carga en BD:", resumen)
    return resumen


if __name__ == "__main__":
    # Pequeño runner manual si ejecutas: python -m api.carreras_sources
    seeds = [
        {"termino": "Licenciatura en Ingeniería", "main_area": "ciencias"},
        {"termino": "Licenciatura en Derecho", "main_area": "humanidades"},
        {"termino": "Licenciatura en Medicina", "main_area": "ciencias"},
        {"termino": "Licenciatura en Contaduría", "main_area": "sociales"},
    ]
    wiki = wikipedia_buscar_licenciaturas(seeds, max_por_termino=6)
    # También podrías sumar resultados desde Wikidata por área
    # wd = wikidata_buscar_licenciaturas_por_area("ingeniería", limite=20)
    carreras = normalizar_a_carrera(wiki)
    guardar_json(carreras, filename=f"licenciaturas_wikipedia.json")
    print("Listo. Revisa la carpeta 'salidas/'.")
