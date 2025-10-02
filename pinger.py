import requests
import time
import os

# Lista de URLs dos seus serviços
URLS_TO_PING = [
    "https://n8n-automations-64do.onrender.com",
    "https://your-evolution-api-url.onrender.com" # Adicione a URL da Evolution API aqui
]

# Intervalo em segundos (ex: 5 minutos = 300 segundos)
PING_INTERVAL = 300 

while True:
    print("Iniciando rodada de pings...")
    for url in URLS_TO_PING:
        try:
            response = requests.get(url, timeout=30)
            print(f"Ping para {url} - Status: {response.status_code}")
        except requests.RequestException as e:
            print(f"Falha ao pingar {url}: {e}")
    
    print(f"Aguardando {PING_INTERVAL} segundos para a próxima rodada.")
    time.sleep(PING_INTERVAL)