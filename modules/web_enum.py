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
        res = subprocess.run(cmd_nmap, capture_output=True, text=True, check=False, timeout=180)
        with open(out_nmap, 'w') as f: f.write(res.stdout)
    except subprocess.TimeoutExpired: log_print(f"{R}[!] Nmap atingiu timeout e foi cancelado.{W}")
    except Exception as e: log_print(f"{R}[!] Erro no nmap web: {e}{W}")

    # 2. WhatWeb Fingerprinting
    is_wordpress = False
    if shutil.which("whatweb"):
        out_whatweb = os.path.join(workspace_dir, f"web_whatweb_{port}.txt")
        log_print(f"{Y}[>] WhatWeb Fingerprinting...{W}")
        try:
            res = subprocess.run(["whatweb", "-a", "1", url], capture_output=True, text=True, timeout=120)
            with open(out_whatweb, 'w') as f: f.write(res.stdout)
            if "WordPress" in res.stdout or "wp-content" in res.stdout:
                is_wordpress = True
                log_print(f"{R}[!] ATENÇÃO: Alvo é possivelmente WordPress! Modos WPScan serão ativados.{W}")
        except subprocess.TimeoutExpired: log_print(f"{R}[!] WhatWeb atingiu timeout e foi cancelado.{W}")
        except: pass

    # 2.5 WPScan (Apenas se WordPress for detetado)
    if is_wordpress and shutil.which("wpscan"):
        out_wpscan = os.path.join(workspace_dir, f"web_wpscan_{port}.txt")
        log_print(f"{Y}[>] A lançar WPScan em modo stealth (Plugins, Temas, Users)...{W}")
        try:
            # -e vp,vt,u enumera vulneracble plugins, themes e users. --batch tira perguntas interativas
            cmd_wpscan = ["wpscan", "--url", url, "-e", "vp,vt,u", "--random-user-agent", "--batch"]
            res = subprocess.run(cmd_wpscan, capture_output=True, text=True, timeout=600)  # Max 10 min
            with open(out_wpscan, 'w') as f: f.write(res.stdout)
        except subprocess.TimeoutExpired: log_print(f"{R}[!] WPScan demorou demasiado tempo (timeout) e foi abortado.{W}")
        except Exception as e: log_print(f"{R}[!] Erro wp_scan: {e}{W}")

    # 3. Nikto (Old School Barulhento para CGI e misconfigs)
    if shutil.which("nikto"):
        out_nikto = os.path.join(workspace_dir, f"web_nikto_{port}.txt")
        log_print(f"{Y}[>] Nikto Vulnerability Scan (Max 10m)...{W}")
        try:
            cmd_nikto = ["nikto", "-h", url, "-Tuning", "12389", "-maxtime", "10m", "-Format", "txt", "-o", out_nikto]
            subprocess.run(cmd_nikto, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=660) # 11 mins force kill
        except subprocess.TimeoutExpired: log_print(f"{R}[!] Nikto bloqueou além do limite de tempo! Abortado.{W}")
        except: pass

    # 4. Feroxbuster (Substitui FFUF - Diretórios base)
    wordlist = "/usr/share/wordlists/dirb/common.txt" 
    if os.path.exists(wordlist):
        if shutil.which("feroxbuster"):
            out_ferox = os.path.join(workspace_dir, f"web_ferox_{port}.txt")
            log_print(f"{Y}[>] Feroxbuster Dir Fuzzing... (Rápido e Recursivo){W}")
            try:
                cmd_ferox = ["feroxbuster", "-u", url, "-w", wordlist, "--silent", "--time-limit", "10m", "-o", out_ferox]
                subprocess.run(cmd_ferox, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=660)
                log_print(f"{G}[+] Feroxbuster concluído.{W}")
            except subprocess.TimeoutExpired: log_print(f"{R}[!] Feroxbuster forçado a parar por limite de tempo.{W}")
            except Exception as e: log_print(f"{R}[!] Erro no Feroxbuster: {e}{W}")
        elif shutil.which("ffuf"):
            out_ffuf = os.path.join(workspace_dir, f"web_ffuf_{port}.json")
            log_print(f"{Y}[>] FFUF (Fallback)...{W}")
            try:
                cmd_ffuf = ["ffuf", "-u", f"{url}/FUZZ", "-w", wordlist, "-t", "50", "-mc", "200,204,301,302,307,401,403", "-o", out_ffuf]
                subprocess.run(cmd_ffuf, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=600)
            except subprocess.TimeoutExpired: log_print(f"{R}[!] FFUF forçado a parar por limite de tempo.{W}")
            except: pass
    else:
        log_print(f"{Y}[-] Wordlist {wordlist} não encontrada. Ignorando Directory Fuzzing...{W}")

    # 5. Nuclei Vulnerability Scan
    if shutil.which("nuclei"):
        out_nuclei = os.path.join(workspace_dir, f"web_nuclei_{port}.txt")
        log_print(f"{Y}[>] Nuclei Vuln Scan (Tags: cves,exposures,misconfig)...{W}")
        try:
            # Corre apenas com tags que são fáceis de apanhar em CTFs ("low-hanging fruit")
            cmd_nuclei = ["nuclei", "-u", url, "-t", "cves,exposures,misconfiguration", "-o", out_nuclei, "-silent"]
            subprocess.run(cmd_nuclei, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception: pass

    # 6. SQLMAP Autónomo Crawler (Procurar e Injetar)
    if shutil.which("sqlmap"):
        out_sqlmap_dir = os.path.join(workspace_dir, f"sqlmap_{port}")
        log_print(f"{R}[>] SQLMap Automático (A procurar forms e parâmetros até profundeza 2)...{W}")
        try:
            # --crawl=2 faz o SQLMap procurar links; --forms testa formulários automaticamente
            cmd_sqlmap = ["sqlmap", "-u", url, "--batch", "--crawl", "2", "--forms", "--level", "2", "--risk", "2", "--output-dir", out_sqlmap_dir]
            subprocess.run(cmd_sqlmap, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            log_print(f"{R}[!] Erro no SQLMap: {e}{W}")

