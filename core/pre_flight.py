import os
import shutil
import sys
from core.utils import G, R, Y, B, W, log_print

DEPENDENCIES = ["nmap"]

def pre_flight_check():
    """Verifica se ferramentas necessárias estão instaladas no PATH."""
    log_print(f"{B}[*] A iniciar Pre-flight Check...{W}")
    missing = []
    for tool in DEPENDENCIES:
        if shutil.which(tool) is None:
            missing.append(tool)
    
    if missing:
        log_print(f"{R}[!] FERRAMENTAS EM FALTA: {', '.join(missing)}{W}")
        log_print(f"{Y}[!] Por favor instale-as antes de continuar.{W}")
        sys.exit(1)
    
    log_print(f"{G}[+] Dependências principais validadas.{W}\n")
