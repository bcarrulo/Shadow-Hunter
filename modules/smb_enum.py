import subprocess
import os
import shutil
from core.utils import G, R, Y, B, W, log_print

def run_smb_enum(target, workspace_dir):
    log_print(f"\n{B}[*] (AUTO-MODE) A enumerar SMB agressivamente em {target}...{W}")
    out_file = os.path.join(workspace_dir, "smb_enum_nmap.txt")
    
    # 1. Nmap Base
    cmd_nmap = ["nmap", "-p", "139,445", "--script=smb-vuln*,smb-enum-shares", target]
    try:
        log_print(f"{Y}[>] A correr nmap SMB scripts...{W}")
        result = subprocess.run(cmd_nmap, capture_output=True, text=True, check=False)
        with open(out_file, 'w') as f: f.write(result.stdout)
    except Exception as e: log_print(f"{R}[!] Erro no nmap SMB: {e}{W}")

    # 2. Enum4Linux (A ferramenta de eleição em CTFs)
    if shutil.which("enum4linux"):
        log_print(f"{Y}[>] A lançar enum4linux em background...{W}")
        out_enum4linux = os.path.join(workspace_dir, "smb_enum4linux.txt")
        try:
            # -a corre todos os módulos (users, shares, password policies, groups)
            result = subprocess.run(["enum4linux", "-a", target], capture_output=True, text=True)
            with open(out_enum4linux, 'w') as f: f.write(result.stdout)
        except: pass

