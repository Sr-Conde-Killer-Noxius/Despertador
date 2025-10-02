import requests
import time
import os
import random
from flask import Flask
from threading import Thread

# --- INÍCIO DA LÓGICA DO SERVIDOR WEB ---

# Cria a aplicação web com Flask
app = Flask(__name__)

# Cria um "endpoint" (uma URL) que o Render pode verificar.
# Quando o Render acessar a URL principal do seu serviço, esta função responderá.
@app.route('/')
def health_check():
    return "Este service is running."

# --- FIM DA LÓGICA DO SERVIDOR WEB ---


# --- INÍCIO DA LÓGICA DE PING (SEU CÓDIGO ORIGINAL) ---

# Colocamos seu código original dentro de uma função
def run_pinger():
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

# --- FIM DA LÓGICA DE PING ---


# --- INICIALIZAÇÃO ---

if __name__ == "__main__":
    # 1. Cria e inicia a thread que vai rodar a lógica de pings em segundo plano
    pinger_thread = Thread(target=run_pinger)
    pinger_thread.daemon = True  # Permite que o programa principal encerre a thread
    pinger_thread.start()

    # 2. Inicia o servidor web, que ficará ativo para responder ao Render
    # O Render define a porta através de uma variável de ambiente PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)