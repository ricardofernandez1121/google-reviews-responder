"""
SCRIPT 3 - SMS PARA CONSEGUIR RESEÑAS
Lee el reporte de OpenTable y manda SMS personalizados
pidiendo reseña en Google a clientes recientes.
"""

import os
import csv
import json
from datetime import datetime, timedelta
from twilio.rest import Client

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")

REGISTRO_FILE = "registro_sms_enviados.json"


def cargar_registro_enviados() -> set:
    ruta = os.path.join(os.path.dirname(__file__), REGISTRO_FILE)
    if os.path.exists(ruta):
        with open(ruta, "r") as f:
            data = json.load(f)
            return set(data.get("enviados", []))
    return set()


def guardar_registro_enviados(enviados: set):
    ruta = os.path.join(os.path.dirname(__file__), REGISTRO_FILE)
    existing = {}
    if os.path.exists(ruta):
        with open(ruta, "r") as f:
            existing = json.load(f)
    existing["enviados"] = list(enviados)
    existing["ultimo_envio"] = datetime.now().isoformat()
    with open(ruta, "w") as f:
        json.dump(existing, f, indent=2)


def leer_clientes_opentable(archivo_csv: str, dias_atras: int = 2) -> list[dict]:
    clientes = []
    fecha_limite = datetime.now() - timedelta(days=dias_atras)

    with open(archivo_csv, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        for row in reader:
            # OpenTable usa estos encabezados — ajustar si son diferentes
            nombre = row.get("First Name", "").strip()
            apellido = row.get("Last Name", "").strip()
            telefono = row.get("Phone", "").strip()
            fecha_str = row.get("Visit Date", "").strip()

            if not telefono or not nombre:
                continue

            # Limpiar teléfono — dejar solo números y +
            telefono_limpio = "".join(c for c in telefono if c.isdigit() or c == "+")
            if not telefono_limpio.startswith("+"):
                telefono_limpio = "+1" + telefono_limpio  # asumir USA

            # Filtrar por fecha reciente
            try:
                fecha_visita = datetime.strptime(fecha_str, "%Y-%m-%d")
                if fecha_visita < fecha_limite:
                    continue
            except ValueError:
                try:
                    fecha_visita = datetime.strptime(fecha_str, "%m/%d/%Y")
                    if fecha_visita < fecha_limite:
                        continue
                except ValueError:
                    continue

            clientes.append({
                "nombre": nombre,
                "apellido": apellido,
                "nombre_completo": f"{nombre} {apellido}".strip(),
                "telefono": telefono_limpio,
                "fecha_visita": fecha_str
            })

    return clientes


def generar_mensaje(nombre: str, nombre_negocio: str, google_link: str) -> str:
    return (
        f"Hi {nombre}! Thanks for dining with us at {nombre_negocio} 🙏\n\n"
        f"We'd love to hear about your experience. "
        f"Could you leave us a quick Google review?\n\n"
        f"{google_link}\n\n"
        f"Reply STOP to unsubscribe."
    )


def enviar_sms(telefono: str, mensaje: str, client: Client) -> bool:
    try:
        message = client.messages.create(
            body=mensaje,
            from_=TWILIO_PHONE_NUMBER,
            to=telefono
        )
        return message.sid is not None
    except Exception as e:
        print(f"    Error enviando a {telefono}: {e}")
        return False


def main():
    print("\n=== SISTEMA DE SMS PARA RESEÑAS ===\n")

    # Verificar credenciales de Twilio
    if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
        print("Faltan credenciales de Twilio. Configura estas variables:")
        print("  $env:TWILIO_ACCOUNT_SID = 'tu-sid'")
        print("  $env:TWILIO_AUTH_TOKEN = 'tu-token'")
        print("  $env:TWILIO_PHONE_NUMBER = 'tu-numero-twilio'")
        return

    # Datos del negocio
    nombre_negocio = input("Nombre del negocio: ").strip()
    google_link = input("Link directo de Google Reviews del negocio: ").strip()
    archivo_csv = input("Ruta del archivo CSV de OpenTable: ").strip().strip('"')
    dias = input("¿Clientes de cuántos días atrás? [1]: ").strip()
    dias = int(dias) if dias.isdigit() else 1

    # Leer clientes
    print(f"\nLeyendo clientes de los últimos {dias} día(s)...")
    try:
        clientes = leer_clientes_opentable(archivo_csv, dias)
    except FileNotFoundError:
        print(f"No se encontró el archivo: {archivo_csv}")
        return

    if not clientes:
        print("No se encontraron clientes recientes en el archivo.")
        return

    print(f"Clientes encontrados: {len(clientes)}")

    # Filtrar los que ya recibieron SMS
    enviados = cargar_registro_enviados()
    clientes_nuevos = [c for c in clientes if c["telefono"] not in enviados]
    omitidos = len(clientes) - len(clientes_nuevos)

    if omitidos > 0:
        print(f"Omitidos (ya recibieron SMS): {omitidos}")

    if not clientes_nuevos:
        print("Todos los clientes ya recibieron SMS anteriormente.")
        return

    print(f"SMS a enviar: {len(clientes_nuevos)}")

    # Mostrar preview
    print(f"\nEjemplo de mensaje:")
    print("-" * 50)
    print(generar_mensaje(clientes_nuevos[0]["nombre"], nombre_negocio, google_link))
    print("-" * 50)

    confirmacion = input(f"\n¿Enviar {len(clientes_nuevos)} SMS? (s/n): ").strip().lower()
    if confirmacion != "s":
        print("Cancelado.")
        return

    # Enviar SMS
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    exitosos = 0
    fallidos = 0

    for i, cliente in enumerate(clientes_nuevos, 1):
        print(f"  Enviando {i}/{len(clientes_nuevos)} → {cliente['nombre_completo']}...", end=" ")
        mensaje = generar_mensaje(cliente["nombre"], nombre_negocio, google_link)
        exito = enviar_sms(cliente["telefono"], mensaje, client)

        if exito:
            enviados.add(cliente["telefono"])
            exitosos += 1
            print("✓")
        else:
            fallidos += 1
            print("✗")

    # Guardar registro
    guardar_registro_enviados(enviados)

    print(f"\n{'=' * 50}")
    print(f"Enviados exitosamente: {exitosos}")
    print(f"Fallidos:              {fallidos}")
    print(f"Registro actualizado — no se repetirán envíos.")


if __name__ == "__main__":
    main()
