import requests
import time
import os
import random
from flask import Flask
from threading import Thread

# --- INÍCIO DA LÓGICA DO SERVIDOR WEB ---

app = Flask(__name__)

@app.route('/')
def health_check():
    return "Pinger service is running and actively monitoring."

# --- FIM DA LÓGICA DO SERVIDOR WEB ---


# --- INÍCIO DA LÓGICA DE PING APRIMORADA ---

# Melhoria 1: Usar um dicionário para dar nomes amigáveis aos serviços
URLS_TO_PING = {
    "N8N Automations": "https://n8n-automations-64do.onrender.com/webhook/a591ac5b-ecbd-430b-9929-2b9f49ef57a7",
    "Evolution API": "https://evolution-api-lpf9.onrender.com/"
}

def run_pinger():
    while True:
        print("\n" + "="*40)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Iniciando nova rodada de pings...")
        print("="*40)

        for name, url in URLS_TO_PING.items():
            try:
                # Melhoria 1: Log mais claro com o nome do serviço
                print(f"[PINGER] Requisitando para '{name}'...")
                response = requests.get(url, timeout=30)
                print(f"[PINGER] Resposta de '{name}': Status {response.status_code}")
            except requests.RequestException as e:
                print(f"[ERRO] Falha ao pingar '{name}': {e}")
        
        print("-"*40)

        # Melhoria 2: Lógica do timer ativo
        sleep_time_seconds = random.randint(60, 600)
        total_minutes = sleep_time_seconds / 60
        print(f"[TIMER] Entrando em modo de espera por {sleep_time_seconds} segundos (~{total_minutes:.1f} minutos).")
        
        # Loop que espera 1 segundo de cada vez e imprime a cada minuto
        for segundo in range(sleep_time_seconds):
            # A cada 60 segundos, imprime uma mensagem de "pulso"
            if (segundo + 1) % 60 == 0:
                minutos_passados = (segundo + 1) / 60
                print(f"[TIMER] Contando... {minutos_passados:.0f} de ~{total_minutes:.0f} minutos se passaram.")
            time.sleep(1)

# --- FIM DA LÓGICA DE PING ---


# --- INICIALIZAÇÃO ---

if __name__ == "__main__":
    pinger_thread = Thread(target=run_pinger)
    pinger_thread.daemon = True
    pinger_thread.start()

    port = int(os.environ.get("PORT", 5000))
    # Desativa os logs padrão do Flask para deixar nossos logs mais limpos
    from waitress import serve
    serve(app, host='0.0.0.0', port=port)