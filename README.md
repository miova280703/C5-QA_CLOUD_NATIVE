# Tienda de Malabares — QA Cloud-Native
 
Reto práctico del **Módulo 5 — QA Cloud-Native: Automatización Inteligente con IA Generativa** (Lite Thinking).
 
Sobre una tienda web sencilla (API REST en Node.js/Express + front de una sola página) se construye un flujo de calidad completo:
 
| Fase | Qué se construye | Dónde |
|---|---|---|
| 1 | Datos de prueba reproducibles con Faker y semilla fija | `app-tienda/datos/` |
| 2 | Pipeline CI/CD en Azure Pipelines con quality gates | `pipeline/` |
| 3 | E2E con Playwright + Screenplay + pytest-bdd, ligados a Azure Test Plans | `e2e/` |
| 4 | Las mismas pruebas en navegadores reales (Sauce Labs) | `e2e/conftest.py` + stage `E2E_Sauce` |
| 5 | Docker, Azure Container Registry y contract testing con Pact | `app-tienda/Dockerfile`, `pact/` |
| 6 | Métricas DORA, pirámide de pruebas y riesgos | `metricas/` + documento de soporte |
 
---
 
## 1. Estructura del repositorio
 
```
app-tienda/    La app bajo prueba
  servidor/      server.js (API + sirve el front)
  public/        index.html (front SPA)
  datos/         generar-datos.js (Faker, semilla fija)  ->  genera db.json
  Dockerfile     imagen de la app (healthcheck en /api/health)
e2e/           Framework E2E: Playwright + Screenplay + pytest-bdd
  features/      tienda.feature (Gherkin: keywords en inglés, texto en español)
  steps/         test_tienda.py (steps de pytest-bdd)
  screenplay/    actor, abilities, interactions, tasks, questions
  tools/         publicar_test_plan.py (resultados -> Azure Test Plans)
  conftest.py    BASE_URL, reset de estado, soporte Sauce Labs
pipeline/      azure-pipelines.yml y tests/ (smoke-api.js, carga-simple.js)
pact/          Contract testing: consumer/, provider/, pacts/
metricas/      calcular-dora.js y deployments.json
```
 
---
 
## 2. Requisitos
 
| Herramienta | Versión | Para qué |
|---|---|---|
| Node.js | 20 o superior | App, smoke, carga y métricas |
| Python | 3.11 o 3.12 | E2E y Pact |
| Docker | reciente | Contenedor (Fase 5) |
| Git | cualquiera | Control de versiones |
 
Cuentas (según lo que quieras ejecutar): **GitHub** (código), **Azure DevOps** (pipeline y Test Plans), **Azure** (ACR, opcional), **Sauce Labs** (opcional).
 
---
 
## 3. Correr la app
 
```bash
cd app-tienda
npm install        # instala dependencias y genera datos/db.json (postinstall)
npm start          # http://localhost:3000
```
 
- Front: http://localhost:3000/
- API: `GET /api/productos`, `GET /api/productos/:id`, `POST /api/pedidos`, `GET /api/pedidos`
- Salud: http://localhost:3000/api/health
- Otro puerto: `PORT=8080 npm start`
### Datos de prueba (Fase 1)
 
```bash
cd app-tienda
npm run generar    # regenera datos/db.json
```
 
`generar-datos.js` usa `faker.seed(2128)`: **mismos datos en cualquier máquina**. Genera 30 productos en 4 categorías (`clavas`, `pelotas`, `diabolos`, `fuego`) con `id`, `nombre`, `categoria`, `precio`, `descripcion` y `stock`.
 
> **¿Por qué `db.json` no se versiona?** Es un artefacto derivado: el script y la semilla fijan el resultado, así que regenerarlo siempre da el mismo archivo. Versionarlo mete ruido en los commits, puede desalinearse del generador y, con datos reales, expondría información sensible. Lo regeneran el pipeline (stage Build) y el Dockerfile. Está en el `.gitignore`.
 
---
 
## 4. Pruebas rápidas (smoke y carga)
 
Con la app corriendo en otra terminal:
 
```bash
cd pipeline/tests
 
# Smoke: health, catálogo, producto, 404, filtro, front y crear pedido
BASE_URL=http://localhost:3000 node smoke-api.js
 
# Carga con SLA (exit 1 si no se cumple)
BASE_URL=http://localhost:3000 CONCURRENCIA=15 DURACION_S=8 node carga-simple.js
```
 
| Variable | Por defecto | Significado |
|---|---|---|
| `BASE_URL` | `http://localhost:3000` | App bajo prueba |
| `CONCURRENCIA` | 10 | Usuarios virtuales |
| `DURACION_S` | 6 | Duración en segundos |
| `SLA_P95_MS` | 800 | p95 máximo permitido (ms) |
| `SLA_ERROR_PCT` | 1 | Tasa de error máxima (%) |
 
**Ver el gate en rojo:** `SLA_P95_MS=1 node carga-simple.js` termina con `exit 1`.
 
---
 
## 5. Pruebas E2E (Fase 3)
 
Con la app corriendo:
 
```bash
cd e2e
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
pytest
```
 
- Gherkin en `features/tienda.feature`: 4 escenarios (catálogo, carrito, pedido y carrito vacío).
- Los steps no usan Playwright directamente: delegan en el patrón **Screenplay** (`screenplay/`): Actor, Abilities, Interactions, Tasks y Questions.
- La URL se controla con `BASE_URL` (por defecto `http://localhost:3000`).
- Informe JUnit: `pytest --junitxml=resultados/junit-chromium.xml`.
### Vínculo con Azure Test Plans
 
- Cada escenario lleva un tag **`@TC<id>`** con el ID de su Test Case (`@TC4` a `@TC7`).
- `tools/publicar_test_plan.py` lee el JUnit y marca cada caso como Passed o Failed vía REST. Se ejecuta en el pipeline con un PAT (ver sección 8).
- Si cambias los casos en tu plan, actualiza los tags del `.feature`.
---
 
## 6. Contract testing con Pact (Fase 5)
 
Contrato entre el front (**consumer** `front-tienda`) y la API (**provider** `tienda-api`) para `GET /api/productos`.
 
```bash
# 1) Generar el contrato (no necesita la API)
cd pact/consumer
pip install -r requirements.txt
pytest -v        # escribe pact/pacts/front-tienda-tienda-api.json
 
# 2) Verificar la API real (con la app corriendo en :3000)
cd ../provider
pip install -r requirements.txt
python verificar_provider.py    # exit 0 = cumple, exit 1 = rompe el contrato
```
 
- La API expone `POST /api/_pact/state`, que Pact llama antes de cada interacción.
- El archivo del contrato **sí se versiona**.
- Los `PendingDeprecationWarning` son avisos de la librería, no errores. Para ocultarlos: `pytest -v -W ignore::PendingDeprecationWarning`.
- **Probar que atrapa una ruptura:** en `app-tienda/servidor/server.js`, en `GET /api/productos`, cambia `res.json(lista)` por `res.json(lista.map(({ precio, ...r }) => ({ ...r, valor: precio })))`. La verificación debe fallar; revierte el cambio y debe pasar.
---
 
## 7. Contenedor y Azure Container Registry (Fase 5)
 
```bash
cd app-tienda
docker build -t app-tienda .
docker run -d --name tienda -p 3001:3000 app-tienda
curl localhost:3001/api/health
curl localhost:3001/api/productos
docker ps          # tras ~30 s debe aparecer (healthy)
docker rm -f tienda
```
 
El Dockerfile empaqueta la app, **genera los datos con Faker al construir** y define `HEALTHCHECK` sobre `/api/health`.
 
> **Nota técnica:** las dependencias se instalan con `--ignore-scripts`. En ese paso del build solo se copió el `package.json`, así que el `postinstall` (que ejecuta `datos/generar-datos.js`) fallaría con `exit code 1`. Los datos se generan después, en un paso explícito.
 
**Publicar en ACR:** el stage `Deploy` del pipeline lo hace cuando se lanza con el parámetro `publicarAcr` marcado (ver sección 8). Resultado: `<servidor>.azurecr.io/app-tienda:<build>` y `:latest`.
 
---
 
## 8. Pipeline en Azure (Fase 2)
 
`pipeline/azure-pipelines.yml`
 
```
Build -> SmokeTests -> { LoadTest | E2E | E2E_Sauce (opcional) | Contract } -> Deploy
```
 
| Gate | Dónde | Falla cuando |
|---|---|---|
| 1 | SmokeTests: «Smoke test de la API» | Cualquier verificación falla |
| 2 | LoadTest: «Prueba de carga» | p95 ≥ SLA o error ≥ 1 % (`exit 1`) |
| 3 | E2E: «E2E: app + pytest» | Algún escenario falla |
| 4 | E2E_Sauce | Algún escenario falla en el navegador remoto (solo con `usarSauce`) |
| 5 | Contract: «Provider: verificar contrato» | La API no cumple el contrato |
 
**Deploy solo corre si todos los gates anteriores pasan.** La app y las pruebas corren en el mismo paso, porque los procesos en segundo plano mueren al terminar un paso y los stages no comparten máquina.
 
### Conectar GitHub a Azure Pipelines
 
1. En Azure DevOps crea un proyecto.
2. **Pipelines → Create Pipeline → GitHub (YAML)** y autoriza la app «Azure Pipelines» en GitHub con acceso a este repositorio.
3. Elige **Existing Azure Pipelines YAML file**, rama `main` o `master`, y `/pipeline/azure-pipelines.yml`.
4. Las organizaciones nuevas pueden necesitar solicitar los jobs paralelos gratuitos de Microsoft: https://aka.ms/azpipelines-parallelism-request
### Parámetros al lanzar («Run pipeline»)
 
| Parámetro | Valor | Efecto |
|---|---|---|
| `slaP95Ms` | `800` | Corrida en **verde** |
| `slaP95Ms` | `1` | Fuerza el gate de carga en **rojo**; Deploy se omite |
| `slaErrorPct` | `1` | SLA de tasa de error |
| `usarSauce` | marcado | Ejecuta el stage `E2E_Sauce` |
| `publicarAcr` | marcado | El stage Deploy publica la imagen en ACR |
 
### Variables del pipeline (Pipelines → Edit → Variables)
 
Todas las credenciales van como **secret**. Nunca se escriben en archivos del repositorio.
 
| Variable | Secreta | Se usa para |
|---|---|---|
| `AZURE_DEVOPS_PAT` | Sí | Actualizar Test Plans (scope **Test Management: Read & write**) |
| `SAUCE_USERNAME` | Sí | Sauce Labs (con `usarSauce`) |
| `SAUCE_ACCESS_KEY` | Sí | Sauce Labs (con `usarSauce`) |
| `ACR_LOGIN_SERVER` | No | Publicar en ACR (ej. `miregistro.azurecr.io`) |
| `ACR_USERNAME` | No | Publicar en ACR (usuario administrador) |
| `ACR_PASSWORD` | Sí | Publicar en ACR |
 
`TEST_PLAN_ID` y `TEST_SUITE_ID` están en la sección `variables` del YAML; ajústalos a tu plan.
 
> Los secretos no se evalúan en las condiciones de un stage de Azure. Por eso Sauce y ACR se activan con **parámetros** y no con una condición sobre la variable secreta.
 
---
 
## 9. Ejecución en la nube con Sauce Labs (Fase 4)
 
Se activa con el parámetro `usarSauce`. `conftest.py` detecta `SAUCE=1` más las credenciales y exporta el grid remoto y las capabilities (Windows 11, Chrome, última versión). El stage:
 
1. arranca la app y abre un túnel **Sauce Connect** con `--proxy-localhost allow` (sin él, el navegador remoto no ve `localhost:3000`);
2. ejecuta `pytest --headed` contra Sauce (necesario para grabar video);
3. cierra el túnel y publica resultados.
| | Local | Sauce Labs |
|---|---|---|
| Navegador | Chromium local | Chrome real en Windows 11 |
| Activación | nada | `SAUCE=1` + credenciales |
| Acceso a la app | `localhost:3000` directo | Túnel Sauce Connect |
| Modo | headless | `--headed` |
| Código de pruebas | igual | igual |
 
La región por defecto es `us-west-1`. Si tu cuenta es de otra región, cámbiala en `--region` del túnel y en `SAUCE_REGION` del stage.
 
---
 
## 10. Métricas DORA (Fase 6)
 
```bash
cd metricas
node calcular-dora.js          # lee deployments.json
```
 
`deployments.json` contiene una entrada por corrida del pipeline: `deployed_at`, `committed_at` (opcional), `failed` y `restored_at` si falló. Otro archivo: `DEPLOYMENTS_FILE=ruta.json node calcular-dora.js`.
 
Resultado con las corridas reales (muestra pequeña, estimados razonados):
 
| Métrica | Valor | Nivel |
|---|---|---|
| Frecuencia de despliegue | 0.62 por día | Alto |
| Lead time for changes | 5 min 2 s | Elite |
| Tasa de fallo de cambios | 33.3 % (1 de 3) | Bajo |
| MTTR | 8.6 min aprox. | Elite |
 
La tasa de fallo mide corridas del pipeline que fallaron. El fallo fue atrapado por un quality gate **antes** del Deploy, así que ningún cambio roto llegó a producción.
 
---
 
## 11. Pirámide de pruebas y riesgos
 
| Capa | Qué la compone |
|---|---|
| Unitarias / datos | Validación de datos en Build; generador con semilla fija (**brecha:** faltan unitarias de la lógica del servidor) |
| Integración / API | Smoke de API, contrato Pact, carga con SLA |
| E2E | Playwright + Screenplay + pytest-bdd (4 escenarios), Chromium y Sauce Labs |
 
**Riesgos de calidad y mitigaciones**
 
1. **La API acepta pedidos inválidos** (no valida stock ni cantidad positiva; el front usa un correo por defecto). *Mitigación:* validar en el servidor y agregar pruebas unitarias y de API.
2. **E2E frágiles** por `data-testid`, datos y estado en memoria. *Mitigación:* `data-testid` como contrato, semilla fija, `POST /api/test/reset` y Pact para detectar cambios de API.
3. **Dependencias externas y secretos** (Azure, Sauce, PAT, credenciales de ACR). *Mitigación:* variables secretas rotadas, service principal en lugar del usuario administrador, parámetros que desactivan lo opcional.
---
 
## 12. Decisiones de diseño
 
- **Screenplay sobre Page Objects:** las pruebas expresan intención de negocio (tasks y questions) y la UI queda aislada.
- **Gherkin en español con keywords en inglés:** legible para negocio y compatible con las herramientas.
- **Gates dentro del pipeline:** cualquier falla detiene el despliegue.
- **App y prueba en el mismo paso:** requisito de Azure Pipelines para procesos en segundo plano.
- **Contrato versionado, datos no:** el contrato Pact es una especificación; `db.json` es derivable.
- **Usuario administrador de ACR:** simplificación para una cuenta de prueba. En un entorno real: service principal o identidad administrada.
---
 
## 13. Solución de problemas
 
| Síntoma | Causa probable |
|---|---|
| «No hosted parallelism has been purchased or granted» | Falta la aprobación de jobs paralelos (sección 8) |
| El E2E no encuentra `smoke-api.js` o los tests | `APP_DIR` y `TEST_DIR` del YAML no coinciden con tus carpetas |
| `docker build` falla en `npm install` | Dockerfile sin `--ignore-scripts` (sección 7) |
| `Connection refused ... localhost port 3000` al verificar Pact | La API no está corriendo; levántala con `npm start` |
| Pact: el estado del provider falla | Falta `POST /api/_pact/state` en `server.js` |
| El stage Sauce aparece «Skipped» | No se marcó el parámetro `usarSauce` |
| El túnel de Sauce no queda listo | Región o credenciales incorrectas; revisa el log `sc.log` del paso |
| Test Plans no se actualiza | `AZURE_DEVOPS_PAT` ausente, sin scope de Test Management o plan en otro proyecto |
| `pact-python` falla al instalar | Usa Python 3.11 o un entorno Linux (trae un Ruby embebido) |
 
---
 
## 14. Seguridad
 
- No subas credenciales al repositorio (PAT, claves de Sauce, contraseña de ACR).
- `datos/db.json`, `node_modules/`, `.venv/` y `resultados/` están en el `.gitignore`.
- Rota cualquier secreto que hayas pegado por error en un chat, una captura o un commit.
- Al terminar el reto, elimina el grupo de recursos de Azure para no consumir créditos.