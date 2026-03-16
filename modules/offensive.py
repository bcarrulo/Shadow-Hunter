import os
import subprocess
import shutil
import tempfile
from core.utils import G, R, Y, B, W, log_print

def run_hydra_brute(target, port, service, workspace_dir):
    """
    Kicks off a quick Hydra bruteforce against SSH or FTP using common small wordlists.
    This acts on the "low hanging fruit" method.
    """
    log_print(f"\n{R}[*] (AUTO-MODE) A Iniciar Hydra Brute-Force Ligeiro em {service.upper()} ({port})...{W}")
    if not shutil.which("hydra"):
        log_print(f"{Y}[!] Hydra não instalado. Saltando brute-force...{W}")
        return

    out_file = os.path.join(workspace_dir, f"hydra_{service}_{port}.txt")
    
    # Criamos ficheiros temporários para login/passwords para não precisar de ficheiros grandes externos
    # (Ou podíamos usar o /usr/share/wordlists, mas isto torna a tool portátil)
    default_users = "root\nadmin\nuser\nguest\npostgres\noracle\nubuntu\nadministrator\n"
    default_pass = "root\nadmin\nguest\n123456\npassword\ntoortoor\npassword123\n"
    
    users_file = os.path.join(workspace_dir, "temp_users.txt")
    pass_file = os.path.join(workspace_dir, "temp_pass.txt")
    
    with open(users_file, "w") as uf: uf.write(default_users)
    with open(pass_file, "w") as pf: pf.write(default_pass)

    try:
        # hydra -L temp_users.txt -P temp_pass.txt ftp://192.168.1.5 -s 21 -o result.txt -t 4
        cmd = ["hydra", "-L", users_file, "-P", pass_file, "-s", str(port), "-vV", "-t", "4", "-I", f"{service}://{target}"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        
        with open(out_file, "w") as f:
            f.write(res.stdout)
            
        if "login:" in res.stdout and "password:" in res.stdout:
            log_print(f"{G}[!!!] SUCESSO HYDRA: Credenciais encontradas! Ver relatório.{W}")
        else:
            log_print(f"[-] Nenhuma credencial básica funcionou em {service}.")
            
    except Exception as e:
        log_print(f"{R}[!] Erro do Hydra: {e}{W}")
        
    finally:
        # Cleanup dos ficheiros temporários
        if os.path.exists(users_file): os.remove(users_file)
        if os.path.exists(pass_file): os.remove(pass_file)


def run_searchsploit(target, open_ports, workspace_dir):
    """
    Recebe o dicionário de portas abertas e tenta procurar exploits locais para as versões dos serviços.
    """
    log_print(f"\n{B}[*] (AUTO-MODE) A iniciar Auto-Searchsploit em background...{W}")
    
    if not shutil.which("searchsploit"):
        log_print(f"{Y}[!] 'searchsploit' não encontrado no sistema. A saltar módulo de Exploits.{W}")
        return

    out_file = os.path.join(workspace_dir, "searchsploit_findings.txt")
    found_exploits = False

    with open(out_file, 'w') as f:
        f.write("=== RESULTADOS AUTOMÁTICOS DO SEARCHSPLOIT ===\n\n")
        
        for port, service_info in open_ports.items():
            # Filtra serviços desconhecidos ou vazios
            if not service_info or service_info.lower() in ['unknown', 'http', 'tcp', 'udp', 'ssh']:
                continue
            
            # Limpa ruído típico do Nmap para melhorar a query do searchsploit
            search_query = service_info.replace("?", "").replace("httpd", "").strip()
            
            if len(search_query) < 3: # Ignora queries muito pequenas
                continue

            log_print(f"{Y}[>] A pesquisar CVEs para: {search_query} (Porta {port}){W}")
            
            cmd = ["searchsploit", search_query]
            try:
                # Correr searchsploit sem cores para não quebrar o ficheiro TXT
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                # Se encontrou alguma coisa e não é erro
                if "No Results" not in result.stdout and "No match" not in result.stdout and len(result.stdout) > 20:
                    found_exploits = True
                    f.write(f"\n[+] PORTA {port}: {service_info}\n")
                    f.write("-" * 50 + "\n")
                    f.write(result.stdout)
                    f.write("-" * 50 + "\n")
                    log_print(f"{G}    [!] Encontrados potenciais exploits para a porta {port}!{W}")
                else:
                    log_print(f"    [-] Nada de relevante encontrado.")
            except Exception as e:
                log_print(f"{R}[!] Erro ao pesquisar {search_query}: {e}{W}")

    if found_exploits:
        log_print(f"{G}[+] Relatório de exploits guardado em: {out_file}{W}")
    else:
        # Limpa o ficheiro se não encontrou nada
        os.remove(out_file)
