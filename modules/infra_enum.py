import subprocess
import os
import shutil
from core.utils import G, R, Y, B, W, log_print

def run_dns_enum(target, workspace_dir):
    """
    Tenta Zone Transfer e outras queries DNS.
    """
    log_print(f"\n{B}[*] (AUTO-MODE) Entrada DNS Detetada (Porta 53). A testar axfr...{W}")
    out_file = os.path.join(workspace_dir, "dns_enum.txt")

    if shutil.which("dig"):
        try:
            # AXFR contra si próprio com nome dummy, em CTFs às vezes passa
            log_print(f"{Y}[>] Tentativa de Zone Transfer com 'dig'...{W}")
            res = subprocess.run(["dig", "axfr", f"@{target}"], capture_output=True, text=True)
            with open(out_file, 'w') as f: f.write(res.stdout)
        except Exception as e:
            log_print(f"{R}[!] Erro de DNS Enum: {e}{W}")

def run_snmp_enum(target, workspace_dir):
    """
    Usa snmpwalk para vazar informações inteiras sobre a máquina.
    """
    log_print(f"\n{B}[*] (AUTO-MODE) Entrada SNMP Detetada (Porta 161). A invocar snmpwalk...{W}")
    out_file = os.path.join(workspace_dir, "snmp_enum.txt")

    if shutil.which("snmpwalk"):
        try:
            log_print(f"{Y}[>] Walking com community 'public' (Isto é demorado, a correr)...{W}")
            # -c public, -v 1, -t 5 (timeout)
            res = subprocess.run(["snmpwalk", "-c", "public", "-v", "1", "-t", "5", target], capture_output=True, text=True)
            if "Timeout" not in res.stdout:
                with open(out_file, 'w') as f: f.write(res.stdout)
        except Exception as e:
            log_print(f"{R}[!] Erro de SNMP Enum: {e}{W}")
