import os
import socket
from datetime import datetime

# Cores para o terminal (Estética Hacker)
R = '\033[31m' # Red
G = '\033[32m' # Green
Y = '\033[33m' # Yellow
B = '\033[34m' # Blue
W = '\033[0m'  # White (Reset)

# Ficheiro de Log Base
LOG_FILE = f"scan_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"

def banner():
    # Limpa a tela (Windows ou Linux)
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{G}")
    print(r"""
   _____ _               _                 
  / ____| |             | |                
 | (___ | |__   __ _  __| | _____      __  
  \___ \| '_ \ / _` |/ _` |/ _ \ \ /\ / /  
  ____) | | | | (_| | (_| | (_) \ V  V /   
 |_____/|_| |_|\__,_|\__,_|\___/ \_/\_/    
    HU N T E R   E D I T I O N  v2.0
    """)
    print(f"{W}--------------------------------------------------")
    print(f"{Y}[*] Log Output: {LOG_FILE}{W}")
    print(f"{Y}[*] Operator: {os.getlogin() if os.name == 'nt' else os.getenv('USER')}{W}")
    print(f"{W}--------------------------------------------------\n")

def log_print(text):
    print(text)
    try:
        with open(LOG_FILE, 'a') as f:
            # Remove códigos de cor para o arquivo de texto
            clean_text = text.replace(R, '').replace(G, '').replace(Y, '').replace(B, '').replace(W, '')
            f.write(clean_text + "\n")
    except:
        pass

def get_vendor(mac_address):
    """Tenta obter o fabricante (Vendor) pelo MAC Address usando API ou DB local do Nmap"""
    try:
        return "Desconhecido"
    except:
        return "VendorNotFound"

def get_local_ip():
    """Tenta descobrir o IP local e sugere a rede /24"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return f"{ip.rsplit('.', 1)[0]}.0/24"
    except:
        return None

def setup_workspace(target):
    """Cria uma pasta para o alvo se não existir."""
    safe_target = target.replace("http://", "").replace("https://", "").replace("/", "_")
    workspace_dir = os.path.join(os.getcwd(), "scans", safe_target)
    
    if not os.path.exists(workspace_dir):
        os.makedirs(workspace_dir)
        print(f"{G}[+] Workspace criado em: {workspace_dir}{W}")
    else:
        print(f"{Y}[*] Workspace existente detetado em: {workspace_dir}{W}")
        
    return workspace_dir
