"""
VERIFICACION DEL PROVIDER (lado provider de Pact).

Toma el contrato generado por el consumer (pacts/front-tienda-tienda-api.json)
y lo verifica contra la API REAL corriendo: hace cada peticion del contrato y
comprueba que la respuesta cumple (status y FORMA del cuerpo, por tipos).

Variables de entorno:
  PROVIDER_URL -> URL base de la API (por defecto http://localhost:3000)
  PACT_FILE    -> ruta al contrato (por defecto ../pacts/front-tienda-tienda-api.json)

Sale con codigo 0 si cumple y 1 si no (sirve de quality gate en el pipeline).
"""
import os
import sys

from pact import Verifier

PROVIDER_URL = os.environ.get("PROVIDER_URL", "http://localhost:3000")
PACT_FILE = os.environ.get("PACT_FILE", "../pacts/front-tienda-tienda-api.json")


def main():
    print(f"Verificando el provider en {PROVIDER_URL}")
    print(f"Contra el contrato {PACT_FILE}")

    verifier = Verifier(provider="tienda-api", provider_base_url=PROVIDER_URL)

    # Pact llama a este endpoint antes de cada interaccion para poner al
    # provider en el estado declarado ("existen productos en el catalogo").
    exito, _ = verifier.verify_pacts(
        PACT_FILE,
        provider_states_setup_url=f"{PROVIDER_URL}/api/_pact/state",
    )

    if exito == 0:
        print("\nOK - el provider CUMPLE el contrato del consumer.")
        sys.exit(0)
    print("\nFALLO - el provider NO cumple el contrato. Revisa los cambios de la API.")
    sys.exit(1)


if __name__ == "__main__":
    main()
