import os
import subprocess
import shutil
from core.utils import G, R, Y, B, W, log_print

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
