import os
import subprocess
import shutil
import tempfile
from core.utils import G, R, Y, B, W, log_print

def crack_hash(hash_data, wordlist=None, format=None, workspace_dir="."):
    """
    Função dedicada para crackar hashes oflline usando John the Ripper.
    'hash_data' pode ser um ficheiro ou a hash diretamente em string.
    """
    log_print(f"\n{B}[*] A Iniciar Módulo de Cracking (Offline)...{W}")

    if not shutil.which("john"):
        log_print(f"{R}[!] 'john' (John the Ripper) não está instalado ou não está no PATH.{W}")
        return

    # Se 'hash_data' não for um ficheiro existente, assumimos que é a hash em formato string
    if not os.path.exists(hash_data):
        log_print(f"{Y}[*] Hash providenciada como string. A criar ficheiro temporário...{W}")
        hash_file_path = os.path.join(workspace_dir, "target_hash.txt")
        with open(hash_file_path, "w") as f:
            f.write(hash_data + "\n")
    else:
        hash_file_path = hash_data

    # Configurar comando base
    cmd = ["john"]

    if format:
        cmd.append(f"--format={format}")
    
    if wordlist:
        if os.path.exists(wordlist):
            cmd.append(f"--wordlist={wordlist}")
        else:
            log_print(f"{R}[!] Wordlist não encontrada: {wordlist}. A usar modo base do John.{W}")

    cmd.append(hash_file_path)

    log_print(f"{B}[*] A executar: {' '.join(cmd)}{W}")

    try:
        # Primeiro, executamos o John para tentar crackar
        res = subprocess.run(cmd, capture_output=True, text=True)
        
        # Em seguida, extraímos o resultado com john --show
        show_cmd = ["john", "--show", hash_file_path]
        if format:
            show_cmd.insert(1, f"--format={format}")
            
        show_res = subprocess.run(show_cmd, capture_output=True, text=True)
        
        output_file = os.path.join(workspace_dir, "cracked_hashes.txt")
        with open(output_file, "w") as f:
            f.write(show_res.stdout)

        log_print(f"{G}[+] Resultados guardados em: {output_file}{W}\n")
        log_print(f"{G}{show_res.stdout.strip()}{W}")

    except Exception as e:
        log_print(f"{R}[!] Erro ao tentar crackar: {e}{W}")

def run_hydra_brute(target, port, service, users_file=None, pass_file=None, workspace_dir="."):
    """
    Kicks off a specific Hydra bruteforce against a service.
    """
    log_print(f"\n{B}[*] A Iniciar Hydra Brute-Force (Online) em {service.upper()} ({port})...{W}")
    if not shutil.which("hydra"):
        log_print(f"{R}[!] Hydra não instalado. Saltando brute-force...{W}")
        return

    out_file = os.path.join(workspace_dir, f"hydra_{service}_{port}_{target}.txt")
    
    # Defaults portáteis caso não se providenciem wordlists
    temp_u = False
    temp_p = False
    
    if not users_file or not os.path.exists(users_file):
        users_file = os.path.join(workspace_dir, "temp_users.txt")
        with open(users_file, "w") as uf: 
            uf.write("root\nadmin\nuser\nguest\npostgres\noracle\nubuntu\nadministrator\n")
        temp_u = True

    if not pass_file or not os.path.exists(pass_file):
        pass_file = os.path.join(workspace_dir, "temp_pass.txt")
        with open(pass_file, "w") as pf: 
            pf.write("root\nadmin\nguest\n123456\npassword\ntoortoor\npassword123\n")
        temp_p = True

    try:
        # hydra -L users.txt -P pass.txt ftp://192.168.1.5 -s 21
        cmd = ["hydra", "-L", users_file, "-P", pass_file, "-s", str(port), "-vV", "-t", "4", f"{service}://{target}"]
        log_print(f"{B}[*] Executando: {' '.join(cmd)}{W}")
        
        res = subprocess.run(cmd, capture_output=True, text=True)
        
        with open(out_file, "w") as f:
            f.write(res.stdout)
            
        if "login:" in res.stdout and "password:" in res.stdout:
            log_print(f"{G}[!!!] SUCESSO HYDRA: Credenciais encontradas!{W}")
        else:
            log_print(f"{Y}[-] Nenhuma credencial funcionou ou erro na execução.{W}")
            
    except Exception as e:
        log_print(f"{R}[!] Erro do Hydra: {e}{W}")
        
    finally:
        if temp_u and os.path.exists(users_file): os.remove(users_file)
        if temp_p and os.path.exists(pass_file): os.remove(pass_file)
