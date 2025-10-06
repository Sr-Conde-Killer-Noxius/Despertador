import requests
import time
import os
import random
import gc
from flask import Flask, jsonify
from threading import Thread
from waitress import serve

# --- VARIÁVEL GLOBAL PARA MONITORAMENTO ---
last_successful_ping_loop = time.time()

# --- LÓGICA DO SERVIDOR WEB ---
app = Flask(__name__)

@app.route('/')
def health_check():
    global last_successful_ping_loop
    seconds_since_last_ping = time.time() - last_successful_ping_loop
    
    if seconds_since_last_ping > 660:
        response = jsonify(status="unhealthy", pinger_thread_status="stopped_responding", seconds_since_last_ping=seconds_since_last_ping)
        response.status_code = 503
        return response
    
    return jsonify(status="ok", pinger_thread_status="running", seconds_since_last_ping=seconds_since_last_ping)

# --- LÓGICA DE PING ROBUSTA E INTELIGENTE ---

# AJUSTE 1: Configuração do método HTTP para cada URL
URLS_TO_PING = {
    # Formato: "Nome do Serviço": ("MÉTODO", "URL")
    "N8N Automations": ("POST", "https://n8n-automations-64do.onrender.com/webhook/0d392286-37b6-4433-a9da-c75ebc63b6d3"),
    "Evolution API": ("GET", "https://evolution-api-lpf9.onrender.com/")
}

RENDER_EXTERNAL_URL = os.environ.get('RENDER_EXTERNAL_URL')
if RENDER_EXTERNAL_URL:
    # O autoping deve usar o método GET
    URLS_TO_PING["Self (Pinger)"] = ("GET", RENDER_EXTERNAL_URL)
    print(f"[INFO] Autoping habilitado para: {RENDER_EXTERNAL_URL}")

def pinger_task():
    global last_successful_ping_loop
    while True:
        print("\n" + "="*40)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Iniciando nova rodada de pings...")
        print("="*40)

        # AJUSTE 2: Lógica para usar o método HTTP correto para cada requisição
        for name, (method, url) in URLS_TO_PING.items():
            try:
                print(f"[PINGER] Requisitando para '{name}' com método {method}...")
                
                if method == "POST":
                    response = requests.post(url, timeout=30)
                else: # Assume GET para todos os outros casos
                    response = requests.get(url, timeout=30)

                print(f"[PINGER] Resposta de '{name}': Status {response.status_code}")
            except Exception as e:
                print(f"[ERRO] Falha inesperada ao pingar '{name}': {e}")
        
        print("-"*40)
        
        last_successful_ping_loop = time.time()
        
        gc.collect()
        print("[INFO] Limpeza de memória realizada.")
        
        sleep_time_seconds = random.randint(60, 600)
        total_minutes = sleep_time_seconds / 60
        print(f"[TIMER] Ciclo concluído. Próxima rodada em {sleep_time_seconds} segundos (~{total_minutes:.1f} minutos).")
        
        for segundo in range(sleep_time_seconds):
            if (segundo + 1) % 60 == 0:
                minutos_passados = (segundo + 1) / 60
                print(f"[TIMER] Contando... {minutos_passados:.0f} de ~{total_minutes:.0f} minutos se passaram.")
            time.sleep(1)

def run_pinger_supervisor():
    while True:
        try:
            pinger_task()
        except Exception as e:
            print(f"\n[SUPERVISOR-ERRO] A TAREFA DE PING FALHOU COMPLETAMENTE: {e}")
            print("[SUPERVISOR] REINICIANDO A TAREFA EM 60 SEGUNDOS...")
            time.sleep(60)

# --- INICIALIZAÇÃO ---
if __name__ == "__main__":
    pinger_thread = Thread(target=run_pinger_supervisor)
    pinger_thread.daemon = True
    pinger_thread.start()

    port = int(os.environ.get("PORT", 5000))
    serve(app, host='0.0.0.0', port=port)