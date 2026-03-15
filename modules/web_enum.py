import os
import subprocess
import shutil
from core.utils import G, R, Y, B, W, log_print

def run_web_fuzz(target, port, workspace_dir):
    """
    Executa enumeração web avançada combinando Nmap Scripts, WhatWeb, FFUF e Nuclei.
    """
    proto = "https" if port == 443 or port == 8443 else "http"
    url = f"{proto}://{target}:{port}" if not "http" in target else f"{target}:{port}"
        
    log_print(f"\n{B}[*] (AUTO-MODE) Entrada Web Detetada! Fuzzing Profundo em {url}...{W}")
    
    # 1. Nmap HTTP Enum Base
    out_nmap = os.path.join(workspace_dir, f"web_nmap_{port}.txt")
    cmd_nmap = ["nmap", "-p", str(port), "--script=http-enum,http-title,http-headers", target]
    try:
        log_print(f"{Y}[>] Nmap HTTP Scripts...{W}")
        res = subprocess.run(cmd_nmap, capture_output=True, text=True, check=False)
        with open(out_nmap, 'w') as f: f.write(res.stdout)
    except Exception as e: log_print(f"{R}[!] Erro no nmap web: {e}{W}")

    # 2. WhatWeb Fingerprinting
    if shutil.which("whatweb"):
        out_whatweb = os.path.join(workspace_dir, f"web_whatweb_{port}.txt")
        log_print(f"{Y}[>] WhatWeb Fingerprinting...{W}")
        try:
            res = subprocess.run(["whatweb", "-a", "1", url], capture_output=True, text=True)
            with open(out_whatweb, 'w') as f: f.write(res.stdout)
        except: pass
    
    # 3. FFUF Fuzzing (Diretórios base)
    if shutil.which("ffuf"):
        # Uma wordlist comum por default (em Kali Linux)
        wordlist = "/usr/share/wordlists/dirb/common.txt" 
        out_ffuf = os.path.join(workspace_dir, f"web_ffuf_{port}.json")
        
        if os.path.exists(wordlist):
            log_print(f"{Y}[>] FFUF Dir Fuzzing... (Isto pode demorar um bocado){W}")
            try:
                # -t 50 (threads), -mc 200,204,301,302,307,401,403 (match codes common)
                cmd_ffuf = ["ffuf", "-u", f"{url}/FUZZ", "-w", wordlist, "-t", "50", "-mc", "200,204,301,302,307,401,403", "-o", out_ffuf]
                subprocess.run(cmd_ffuf, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                log_print(f"{G}[+] Fuzzing completo.{W}")
            except Exception as e: log_print(f"{R}[!] Erro no FFUF: {e}{W}")
        else:
            log_print(f"{Y}[-] FFUF instalado, mas wordlist {wordlist} não encontrada. Ignorando...{W}")

    # 4. Nuclei Vulnerability Scan
    if shutil.which("nuclei"):
        out_nuclei = os.path.join(workspace_dir, f"web_nuclei_{port}.txt")
        log_print(f"{Y}[>] Nuclei Vuln Scan (Tags: cves,exposures,misconfig)...{W}")
        try:
            # Corre apenas com tags que são fáceis de apanhar em CTFs ("low-hanging fruit")
            cmd_nuclei = ["nuclei", "-u", url, "-t", "cves,exposures,misconfiguration", "-o", out_nuclei, "-silent"]
            subprocess.run(cmd_nuclei, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception: pass

