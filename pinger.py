import requests
import time
import os
import random

# Lista de URLs dos seus serviços
URLS_TO_PING = [
    "https://n8n-automations-64do.onrender.com/webhook/a591ac5b-ecbd-430b-9929-2b9f49ef57a7",
    "https://evolution-api-lpf9.onrender.com/"
]

# Loop infinito para pingar as URLs periodicamente
while True:
    print("Iniciando rodada de pings...")
    for url in URLS_TO_PING:
        try:
            response = requests.get(url, timeout=30)
            print(f"Ping para {url} - Status: {response.status_code}")
        except requests.RequestException as e:
            print(f"Falha ao pingar {url}: {e}")
    
    # Gera um tempo de espera aleatório entre 60 (1 min) e 600 (10 min) segundos
    sleep_time = random.randint(60, 600)
    
    print(f"Aguardando {sleep_time} segundos ({sleep_time/60:.2f} minutos) para a próxima rodada.")
    time.sleep(sleep_time)