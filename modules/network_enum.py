import os
import subprocess
from core.utils import G, R, Y, B, W, log_print

def get_scan_args(profile):
    """Mapeia os perfis de scan aos argumentos do nmap"""
    profiles = {
        'fast': '-p 1-1000 -T4 --open --max-retries 2 --host-timeout 5m -sV -sC',
        'deep': '-p- -A --script vuln -T4 --host-timeout 30m',
        'vuln': '-sV --script vuln -T4 --max-retries 3 --host-timeout 20m',
        'stealth': '-sS -p- -T4 --max-retries 2',
    }
    return profiles.get(profile, profiles['fast'])

def run_network_scan(target, profile, workspace_dir):
    """Executa scans de rede com nmap com auto-exportação (-oA)."""
    log_print(f"\n{B}[*] (FASE 2) A Iniciar Network Enum para {target}...{W}")
    
    scan_args = get_scan_args(profile).split()
    nmap_out_base = os.path.join(workspace_dir, f"nmap_{profile}")
    
    cmd = ["nmap"] + scan_args + ["-oA", nmap_out_base, target]
    
    log_print(f"{Y}[>] A executar: {' '.join(cmd)}{W}")
    
    try:
        # Fazer timeout de emergência de 35 minutos caso alguma script vulnere o bloqueie
        subprocess.run(cmd, check=True, timeout=2100)
        log_print(f"{G}[+] Resultados Nmap guardados em: {nmap_out_base}.nmap / .xml / .gnmap{W}")
    except subprocess.TimeoutExpired:
        log_print(f"{R}[!] Nmap ultrapassou o limite de tempo estrito (35 minutos) e foi cancelado.{W}")
    except subprocess.CalledProcessError as e:
        log_print(f"{R}[!] Erro ao executar ferramenta de scan: {e}{W}")
    except KeyboardInterrupt:
        log_print(f"\n{R}[!] Scan Nmap interrompido pelo utilizador.{W}")
