import subprocess
import os
from core.utils import G, R, Y, B, W, log_print

def run_ftp_anon_check(target, port, workspace_dir):
    log_print(f"\n{B}[*] (AUTO-MODE) A verificar FTP Anonymous Login em {target}:{port}...{W}")
    out_file = os.path.join(workspace_dir, f"ftp_anon_{port}.txt")
    cmd = ["nmap", "-sV", "-p", str(port), "--script=ftp-anon", target]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        with open(out_file, 'w') as f:
            f.write(result.stdout)
            
        if "Anonymous FTP login allowed" in result.stdout:
            log_print(f"{G}[!!!] SUCESSO: Login Anónimo Permitido em FTP ({port})!{W}")
            log_print(f"{G}Detalhes salvos em: {out_file}{W}")
        else:
            log_print(f"{Y}[-] Sem login anónimo no FTP ({port}).{W}")
            
    except Exception as e:
        log_print(f"{R}[!] Erro no módulo FTP: {e}{W}")
