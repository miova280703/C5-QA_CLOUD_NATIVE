import requests
from requests.auth import HTTPBasicAuth

# Configuración de tu Azure DevOps
ORGANIZATION = "iovanamirandaltcerti"
PROJECT = "reto-modulo5"
PIPELINE_ID = "1"  # El ID de tu pipeline en Azure DevOps
PAT_TOKEN = "Token Azure"  # Tu token de Azure DevOps

url = f"https://dev.azure.com/{ORGANIZATION}/{PROJECT}/_apis/build/builds?definitions={PIPELINE_ID}&api-version=7.0"

# Autenticación con PAT (Personal Access Token)
response = requests.get(url, auth=HTTPBasicAuth('', PAT_TOKEN))

if response.status_code == 200:
    builds = response.json().get("value", [])
    dataset = []
    
    for i, build in enumerate(builds[:10], start=1):  # Tomamos los últimos 10
        # Extraer fechas y estado desde Azure DevOps
        committed_at = build.get("queueTime")
        deployed_at = build.get("finishTime")
        result = build.get("result") # 'succeeded', 'failed', etc.
        
        failed = True if result == "failed" else False
        
        item = {
            "id": f"d{i}",
            "committed_at": committed_at,
            "deployed_at": deployed_at,
            "failed": failed
        }
        dataset.append(item)
    
    import json
    print(json.dumps(dataset, indent=2))
else:
    print(f"Error al conectar con Azure DevOps: {response.status_code}")