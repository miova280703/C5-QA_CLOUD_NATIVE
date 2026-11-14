# pact/ - Contract testing (consumer <-> provider)

Contrato entre el **front** (consumer, `front-tienda`) y la **API de la Tienda**
(provider, `tienda-api`) para `GET /api/productos`.

```
pact/
|-- consumer/   cliente + test que GENERA el contrato  (pytest)
|-- provider/   verificador que COMPRUEBA la API real contra el contrato
`-- pacts/      contrato generado: front-tienda-tienda-api.json  (se versiona)
```

## Correr (Linux, Python 3.11)

```bash
# 1) Generar el contrato (no necesita la API)
cd pact/consumer
pip install -r requirements.txt
pytest -v                      # escribe ../pacts/front-tienda-tienda-api.json

# 2) Verificar la API real (con la app corriendo en :3000)
cd ../../app-tienda && npm start &       # otra terminal
cd ../pact/provider
pip install -r requirements.txt
python verificar_provider.py   # exit 0 = cumple, exit 1 = rompe el contrato
```

`pact-python` trae un Ruby embebido: si falla en tu maquina, usa Python 3.11 o
corre estos pasos en un contenedor/pipeline Linux.

## Demostrar que atrapa una ruptura (opcional, para el documento)
En `app-tienda/servidor/server.js`, en `GET /api/productos`, cambia
`res.json(lista)` por
`res.json(lista.map(({ precio, ...r }) => ({ ...r, valor: precio })))`.
Con la app reiniciada, `verificar_provider.py` debe FALLAR (falta `precio`).
Revierte el cambio y vuelve a verificar: debe pasar.

## Reto extra: monolito vs microservicios
Hoy conviene **mantener el monolito**: es una app pequena, un solo equipo, un
solo despliegue, y los E2E + este contrato cubren la integracion. Partirlo
anade costo (red, despliegues, observabilidad) sin beneficio claro. Si crece,
las costuras naturales y sus contratos serian:
- **Catalogo** (productos, stock) <- consumido por el front y por Pedidos:
  `GET /api/productos`, `GET /api/productos/:id`.
- **Pedidos** <- consumido por el front: `POST /api/pedidos`; y consume a
  Catalogo (existencia/precio/stock del producto).
- **Notificaciones** <- consume eventos de Pedidos (pedido creado).
Cada flecha seria un contrato Pact; el consumer lo define y el provider lo
verifica en su pipeline.
