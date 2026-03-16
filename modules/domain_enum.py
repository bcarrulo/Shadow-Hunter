import os
import subprocess
import shutil
import requests
import re
import socket
from core.utils import G, R, Y, B, W, log_print

def is_ip(target):
    """Verifica se o alvo é um IP ou um domínio."""
    return re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target) is not None

def get_crt_subdomains(domain):
    """Busca nativa via Python usando a Certificate Transparency (crt.sh)."""
    subdomains = set()
    log_print(f"{Y}[>] A pesquisar na base de dados crt.sh (Native Python)...{W}")
    try:
        url = f"https://crt.sh/?q=%25.{domain}&output=json"
        response = requests.get(url, timeout=20)
        if response.status_code == 200:
            data = response.json()
            for entry in data:
                name = entry['name_value'].lower()
                # crt.sh muitas vezes tem domínios concatenados com \n
                if '\n' in name:
                    for sub in name.split('\n'):
                        if '*' not in sub:
                            subdomains.add(sub.strip())
                else:
                    if '*' not in name:
                        subdomains.add(name.strip())
    except Exception as e:
        log_print(f"{R}[!] Erro ao conectar ao crt.sh: {e}{W}")
    
    return subdomains

def run_subdomain_enum(domain, workspace_dir):
    """
    Função principal que combina OS, crt.sh nativo e Subfinder.
    Depois, filtra os vivos com httpx ou nativo.
    """
    if is_ip(domain):
        log_print(f"{Y}[*] O alvo {domain} é um IP único. Saltando enumeração de subdomínios.{W}")
        return False
        
    log_print(f"\n{B}==================================================={W}")
    log_print(f"{B}    [!] A INICIAR ENUMERAÇÃO DE SUBDOMÍNIOS [!]{W}")
    log_print(f"{B}==================================================={W}")
    
    all_subdomains = set()
    
    # 1. Native crt.sh
    crt_subs = get_crt_subdomains(domain)
    all_subdomains.update(crt_subs)
    log_print(f"{G}[+] Encontrados {len(crt_subs)} subdomínios no crt.sh.{W}")
    
    # 2. Subfinder (Se estiver instalado)
    if shutil.which("subfinder"):
        log_print(f"{Y}[>] A iniciar Subfinder...{W}")
        try:
            cmd = ["subfinder", "-d", domain, "-silent"]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            for line in res.stdout.splitlines():
                if line.strip():
                    all_subdomains.add(line.strip())
            log_print(f"{G}[+] Subfinder concluído.{W}")
        except subprocess.TimeoutExpired:
            log_print(f"{R}[!] Subfinder levou demasiado tempo e foi interrompido.{W}")
        except Exception as e:
            log_print(f"{R}[!] Erro no subfinder: {e}{W}")
            
    # Guarda todos os domínios em RAW
    raw_file = os.path.join(workspace_dir, "subdomains_all.txt")
    with open(raw_file, "w") as f:
        for sub in sorted(all_subdomains):
            f.write(sub + "\n")
            
    log_print(f"{B}[*] Total de Subdomínios Únicos: {len(all_subdomains)}{W}")
    
    # 3. Filtrar os que estão VIVOS (Alive)
    alive_file = os.path.join(workspace_dir, "subdomains_alive.txt")
    log_print(f"{Y}[>] A verificar domínios vivos (Resolução e HTTP)...{W}")
    
    if shutil.which("httpx") or shutil.which("httpx-toolkit"):
        httpx_bin = "httpx" if shutil.which("httpx") else "httpx-toolkit"
        try:
            cmd = [httpx_bin, "-l", raw_file, "-silent", "-o", alive_file]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
            log_print(f"{G}[+] HTTPX finalizado. Resultados em {alive_file}{W}")
        except Exception as e:
            log_print(f"{R}[!] Erro no httpx: {e}{W}")
    else:
        log_print(f"{Y}[*] Ferramenta httpx não encontrada. A usar resolução nativa lenta (Sockets)...{W}")
        alive = []
        for sub in list(all_subdomains):
            try:
                socket.gethostbyname(sub)
                alive.append(sub)
                log_print(f"    {G}[ALIVE] {sub}{W}")
            except:
                pass
        with open(alive_file, "w") as f:
            for a in alive: f.write(a + "\n")
            
    # Contar quantos estão vivos
    if os.path.exists(alive_file):
        with open(alive_file, "r") as f:
            vivos_count = len(f.readlines())
        log_print(f"{G}[!] Encontrados {vivos_count} subdomínios ATIVOS e respondendo!{W}")
        return True
    
    return False
