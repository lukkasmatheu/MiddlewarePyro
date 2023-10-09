import os
import subprocess
import time
import signal

GREEN = "\033[0;32m"
RED = "\033[1;31m"

print(GREEN + "Iniciando Middleware")

nameserver_process = subprocess.Popen("python3 -m Pyro5.nameserver", shell=True)
server_process = None

try:
    time.sleep(2)
    server_process = subprocess.Popen("python3 server/server.py", shell=True)
    print(GREEN + "[Servidor Iniciado Com Sucesso]")
    time.sleep(1)  # Aguarde um momento para que o servidor seja inicializado
except:
    print(RED + "Erro ao executar script de servidor")

try:
    subprocess.call("python3 client/client.py", shell=True)
    print(GREEN + "[Cliente iniciado com Sucesso]")
except:
    print(RED + "Erro ao executar script de cliente")

try:
    
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print(GREEN + "Encerrando o programa...")

    # Encerre os subprocessos explicitamente
    if server_process:
        server_process.terminate()
    nameserver_process.terminate()

print(GREEN + "Programa encerrado com sucesso")