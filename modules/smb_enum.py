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

    # 2. Enum4Linux (A ferramenta de eleição clássica)
    if shutil.which("enum4linux"):
        log_print(f"{Y}[>] A lançar enum4linux em background...{W}")
        out_enum4linux = os.path.join(workspace_dir, "smb_enum4linux.txt")
        try:
            result = subprocess.run(["enum4linux", "-a", target], capture_output=True, text=True)
            with open(out_enum4linux, 'w') as f: f.write(result.stdout)
        except: pass
        
    # 3. NetExec (ou nxc/crackmapexec) - A fina flor do AD
    # Tenta detetar se o utilizador tem netexec ou a versão antiga crackmapexec instalada
    nxc_bin = "nxc" if shutil.which("nxc") else "crackmapexec" if shutil.which("crackmapexec") else None
    if nxc_bin:
        log_print(f"{Y}[>] NetExec Detetado. A testar login nulo a shares SMB...{W}")
        out_nxc = os.path.join(workspace_dir, f"smb_netexec.txt")
        try:
            # Testa contra shares de SMB usando sessão anónima
            res = subprocess.run([nxc_bin, "smb", target, "-u", "''", "-p", "''", "--shares"], capture_output=True, text=True)
            with open(out_nxc, 'w') as f: f.write(res.stdout)
        except Exception as e: log_print(f"{R}[!] Erro NetExec: {e}{W}")

    # 4. SMBMap - Fazer recursão às pastas que estejam abertas
    if shutil.which("smbmap"):
        log_print(f"{Y}[>] SMBMap (Listing recursivo de partilhas)...{W}")
        out_smbmap = os.path.join(workspace_dir, f"smb_smbmap.txt")
        try:
            # -H host, -u utilizador null, -R recursivo
            res = subprocess.run(["smbmap", "-H", target, "-u", "null", "-p", "", "-R"], capture_output=True, text=True)
            with open(out_smbmap, 'w') as f: f.write(res.stdout)
        except Exception as e: log_print(f"{R}[!] Erro SMBMap: {e}{W}")

