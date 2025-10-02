import requests
import time
import os
import random
from flask import Flask, jsonify
from threading import Thread

# --- VARIÁVEL GLOBAL PARA MONITORAMENTO ---
# Armazena o timestamp do último ciclo de ping bem-sucedido
last_successful_ping_loop = time.time()


# --- INÍCIO DA LÓGICA DO SERVIDOR WEB APRIMORADA ---

app = Flask(__name__)

@app.route('/')
def health_check():
    global last_successful_ping_loop
    # Calcula há quanto tempo o último ping ocorreu
    seconds_since_last_ping = time.time() - last_successful_ping_loop
    
    # Se o último ping ocorreu há mais de 11 minutos (660s), algo está errado.
    # O máximo normal seria 10 minutos (600s) + tempo de requisição.
    if seconds_since_last_ping > 660:
        # Retorna um erro 503 (Serviço Indisponível)
        # Isso fará com que o Render veja o serviço como "unhealthy"
        response = jsonify(status="unhealthy", pinger_thread_status="stopped_responding", seconds_since_last_ping=seconds_since_last_ping)
        response.status_code = 503
        return response
    
    return jsonify(status="ok", pinger_thread_status="running", seconds_since_last_ping=seconds_since_last_ping)

# --- FIM DA LÓGICA DO SERVIDOR WEB ---


# --- INÍCIO DA LÓGICA DE PING ROBUSTA ---

URLS_TO_PING = {
    "N8N Automations": "https://n8n-automations-64do.onrender.com/webhook/a591ac5b-ecbd-430b-9929-2b9f49ef57a7",
    "Evolution API": "https://evolution-api-lpf9.onrender.com/"
}

def pinger_task():
    global last_successful_ping_loop
    while True:
        print("\n" + "="*40)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Iniciando nova rodada de pings...")
        print("="*40)

        for name, url in URLS_TO_PING.items():
            try:
                print(f"[PINGER] Requisitando para '{name}'...")
                response = requests.get(url, timeout=30)
                print(f"[PINGER] Resposta de '{name}': Status {response.status_code}")
            # MELHORIA 1: Captura QUALQUER erro durante a requisição, não só de rede
            except Exception as e:
                print(f"[ERRO] Falha inesperada ao pingar '{name}': {e}")
        
        print("-"*40)
        
        # Atualiza o timestamp para mostrar que o ciclo foi concluído com sucesso
        last_successful_ping_loop = time.time()
        
        sleep_time_seconds = random.randint(60, 600)
        total_minutes = sleep_time_seconds / 60
        print(f"[TIMER] Ciclo concluído. Próxima rodada em {sleep_time_seconds} segundos (~{total_minutes:.1f} minutos).")
        
        for segundo in range(sleep_time_seconds):
            if (segundo + 1) % 60 == 0:
                minutos_passados = (segundo + 1) / 60
                print(f"[TIMER] Contando... {minutos_passados:.0f} de ~{total_minutes:.0f} minutos se passaram.")
            time.sleep(1)

# MELHORIA 2: Loop de "Supervisor" para garantir que o pinger nunca pare
def run_pinger_supervisor():
    while True:
        try:
            pinger_task()
        except Exception as e:
            print(f"\n[SUPERVISOR-ERRO] A TAREFA DE PING FALHOU COMPLETAMENTE: {e}")
            print("[SUPERVISOR] REINICIANDO A TAREFA EM 60 SEGUNDOS...")
            time.sleep(60)

# --- FIM DA LÓGICA DE PING ---


# --- INICIALIZAÇÃO ---

if __name__ == "__main__":
    # Inicia a thread com o SUPERVISOR, não a tarefa diretamente
    pinger_thread = Thread(target=run_pinger_supervisor)
    pinger_thread.daemon = True
    pinger_thread.start()

    from waitress import serve
    port = int(os.environ.get("PORT", 5000))
    serve(app, host='0.0.0.0', port=port)