import anthropic
import os
import re
from datetime import datetime
from serpapi import GoogleSearch

anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def buscar_data_id(nombre_negocio: str, serpapi_key: str) -> str:
    params = {
        "engine": "google_maps",
        "q": nombre_negocio,
        "api_key": serpapi_key,
        "hl": "es",
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    lugares = results.get("local_results", [])
    if not lugares:
        raise Exception("No se encontró el negocio. Intenta con un nombre más específico.")

    print(f"\nNegocio encontrado: {lugares[0].get('title', nombre_negocio)}")
    return lugares[0].get("data_id", "")


def obtener_resenas(nombre_busqueda: str, serpapi_key: str) -> tuple[str, list[dict]]:
    print("\nBuscando el negocio en Google Maps...")

    data_id = buscar_data_id(nombre_busqueda, serpapi_key)

    print("Obteniendo reseñas...")
    params = {
        "engine": "google_maps_reviews",
        "data_id": data_id,
        "api_key": serpapi_key,
        "hl": "es",
    }

    search = GoogleSearch(params)
    results = search.get_dict()

    if "error" in results:
        raise Exception(f"Error de SerpAPI: {results['error']}")

    nombre_negocio = results.get("place_info", {}).get("title", nombre_busqueda)

    resenas_raw = results.get("reviews", [])
    if not resenas_raw:
        raise Exception("No se encontraron reseñas.")

    resenas = []
    for r in resenas_raw:
        texto = r.get("snippet", "").strip()
        estrellas = r.get("rating", 3)
        if texto:
            resenas.append({"texto": texto, "estrellas": int(estrellas)})

    print(f"Se encontraron {len(resenas)} reseñas de: {nombre_negocio}")
    return nombre_negocio, resenas


def generar_respuesta(resena: str, estrellas: int, nombre: str, tipo: str, tono: str) -> str:
    prompt = f"""Eres el community manager de {nombre}, un {tipo}.
Tu tono de comunicación es {tono}.

Un cliente dejó esta reseña de Google con {estrellas} estrellas:
"{resena}"

ESTRUCTURA OBLIGATORIA (en este orden):
1. Hook de primera línea: máximo 6 palabras, genera urgencia o curiosidad
2. Respuesta personalizada mencionando detalles específicos de la reseña
3. Una sola CTA al final

REGLAS:
- Máximo 80 palabras en total
- Si es positiva (4-5 estrellas): agradece específicamente, invita a volver
- Si es negativa (1-2 estrellas): empatía, reconoce el problema, ofrece resolverlo fuera de la plataforma
- Si es neutral (3 estrellas): agradece, reconoce el punto de mejora, invita a volver
- Sin hashtags, sin párrafos largos
- En español latino, tono directo y confiable
- Termina con el nombre del negocio

Devuelve SOLO la respuesta lista para publicar, sin explicaciones."""

    message = anthropic_client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text.strip()


def guardar_resultados(resultados: list[dict], nombre_negocio: str):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"respuestas_{nombre_negocio.replace(' ', '_')}_{timestamp}.txt"
    ruta = os.path.join(os.path.dirname(__file__), nombre_archivo)

    with open(ruta, "w", encoding="utf-8") as f:
        f.write(f"RESPUESTAS GENERADAS PARA: {nombre_negocio}\n")
        f.write(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        f.write("=" * 60 + "\n\n")

        for i, r in enumerate(resultados, 1):
            f.write(f"RESEÑA #{i} — {'⭐' * r['estrellas']}\n")
            f.write(f"Cliente: {r['resena_original']}\n\n")
            f.write(f"Tu respuesta:\n{r['respuesta_generada']}\n")
            f.write("-" * 60 + "\n\n")

    print(f"\nArchivo guardado en: {ruta}")
    return ruta


def main():
    print("\n=== GENERADOR DE RESPUESTAS DESDE GOOGLE MAPS ===\n")

    serpapi_key = os.environ.get("SERPAPI_KEY")
    if not serpapi_key:
        serpapi_key = input("Pega tu SerpAPI key: ").strip()

    nombre_busqueda = input("Nombre y ciudad del negocio (ej: Nolensville Hot Chicken Nashville): ").strip()

    tipo = input("Tipo de negocio (restaurante, hotel, tienda...): ").strip() or "restaurante"
    tono = input("Tono de respuesta [profesional y cercano]: ").strip() or "profesional y cercano"

    nombre_negocio, resenas = obtener_resenas(nombre_busqueda, serpapi_key)

    print(f"\nGenerando respuestas para {len(resenas)} reseña(s)...")

    resultados = []
    for i, r in enumerate(resenas, 1):
        print(f"  Procesando reseña {i}/{len(resenas)}...", end=" ")
        respuesta = generar_respuesta(r["texto"], r["estrellas"], nombre_negocio, tipo, tono)
        resultados.append({
            "estrellas": r["estrellas"],
            "resena_original": r["texto"],
            "respuesta_generada": respuesta
        })
        print("✓")

    print("\n" + "=" * 60)
    for i, r in enumerate(resultados, 1):
        print(f"\nRESEÑA #{i} ({'⭐' * r['estrellas']})")
        print(f"Cliente: {r['resena_original']}")
        print(f"\nRespuesta:\n{r['respuesta_generada']}")
        print("-" * 60)

    guardar = input("\n¿Guardar resultados en archivo? (s/n): ").strip().lower()
    if guardar == "s":
        guardar_resultados(resultados, nombre_negocio)


if __name__ == "__main__":
    main()
