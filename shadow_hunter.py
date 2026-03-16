import argparse
import sys
import os
import time

from core.utils import banner, setup_workspace, log_print, get_local_ip, R, G, Y, B, W
from core.pre_flight import pre_flight_check
from core.xml_parser import parse_nmap_xml
from core.report_gen import generate_markdown_report

# Modulos
from modules.network_enum import run_network_scan
from modules.ftp_enum import run_ftp_anon_check
from modules.smb_enum import run_smb_enum
from modules.web_enum import run_web_fuzz
from modules.offensive import run_searchsploit
from modules.infra_enum import run_dns_enum, run_snmp_enum
from modules.cracker import crack_hash
from modules.domain_enum import run_subdomain_enum, is_ip

def interactive_menu():
    """Modo Clássico Interativo: Corre se o tool for iniciado sem argumentos."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        banner()
        print(f"\n{B}===================================================={W}")
        print(f"{Y}   M E N U   P R I N C I P A L   S H A D O W - H U N T E R{W}")
        print(f"{B}===================================================={W}")
        
        print(f"\n{B}[?] S E L E C I O N E   O   S E U   M Ó D U L O :{W}")
        print(f" {G}[1]{W} Escanear Range de Rede (Ex: 192.168.1.0/24)")
        print(f" {G}[2]{W} Escanear Alvo Específico (IP / Domínio)")
        print(f" {G}[3]{W} Auto-Recon (Detectar a minha rede local)")
        print(f" {G}[4]{W} Crackar Hash Offline (John the Ripper)")
        print(f" {R}[99]{W} Sair do Shadow Hunter")
        print(f"{B}----------------------------------------------------{W}")
        
        choice = input(f"\n{Y}[>] O que pretende fazer? {W}")
        
        if choice == '99':
            log_print(f"{R}[!] A Encerrar o Shadow Hunter. Happy Hacking!{W}")
            sys.exit(0)
            
        elif choice == '4':
            os.system('cls' if os.name == 'nt' else 'clear')
            banner()
            print(f"\n{B}--- MODO CRACKER (OFFLINE) ---{W}")
            h_data = input(f"{Y}[>] Introduza a Hash ou Ficheiro c/ Hashes: {W}")
            w_list = input(f"{Y}[>] Introduza a Wordlist (Deixe vazio para fallback em base): {W}")
            f_type = input(f"{Y}[>] Introduza o Formato da Hash (Deixe vazio para detecção auto, ex: raw-md5, nt): {W}")
            crack_hash(
                h_data.strip(), 
                w_list.strip() if w_list.strip() else None, 
                f_type.strip() if f_type.strip() else None, 
                os.getcwd()
            )
            input(f"\n{B}[Pressione ENTER para voltar ao Menu Principal]{W}")
            continue

        target = None
        if choice == '1':
            target = input(f"{Y}[>] Digite a rede (Ex: 192.168.1.0/24): {W}")
        elif choice == '2':
            target = input(f"{Y}[>] Digite o IP ou Domínio (Ex: 10.10.10.5 ou example.com): {W}")
        elif choice == '3':
            net = get_local_ip()
            if net:
                conf = input(f"{Y}[?] Confirmar auto-recon na rede detectada ({net})? (S/n): {W}")
                if conf.lower() != 'n': target = net
            else:
                log_print(f"{R}[!] Não foi possível detectar automaticamente a rede local.{W}")
                time.sleep(2)
                continue

        if not target:
            log_print(f"{R}[!] Alvo Inválido ou cancelado.{W}")
            time.sleep(1)
            continue
            
        print(f"\n{B}----------------------------------------------------{W}")
        print(f"{B}[?] P E R F I L   D E   A T A Q U E   N M A P :{W}")
        print(f" {G}[1]{W} FAST (Apenas Portas Comuns - Rápido)")
        print(f" {G}[2]{W} DEEP (Todas as Portas, Scripts Vuln - Demorado)")
        print(f"{B}----------------------------------------------------{W}")
        
        p_choice = input(f"\n{Y}[>] Selecione o Perfil: {W}")
        profile = 'deep' if p_choice == '2' else 'fast'
        
        print(f"\n{B}----------------------------------------------------{W}")
        print(f"{B}[?] D E S E J A   A T I V A R   O   A U T O - M O D E  ?{W}")
        print(f" {Y}Se ativado, irá lançar módulos automaticamente (Web, SMB, DNS){W}")
        print(f" {Y}consoante as portas detetadas pelo scan inicial.{W}")
        print(f"{B}----------------------------------------------------{W}")
        
        a_choice = input(f"\n{Y}[>] Ativar Auto-Mode? (S/n): {W}")
        auto_mode = True if a_choice.lower() != 'n' else False

        # Return to main to continue execution
        return target, profile, auto_mode

def hunter_automode(target, workspace_dir, profile):
    """
    O Cerebro do Auto-Recon: Analisa o .xml depois do nmap correr.
    E lança modulos em catadupa conforme as portas abertas.
    """
    xml_file = os.path.join(workspace_dir, f"nmap_{profile}.xml")
    
    log_print(f"\n{Y}[!] A EXTRAIR DADOS ({xml_file})...{W}")
    portas = parse_nmap_xml(xml_file)
    
    if not portas:
         log_print(f"{R}[!] Nenhuma porta aberta detetada ou XML inválido.{W}")
         return

    log_print(f"{G}[+] Portas Abertas Detetadas pelo Automode:{W}")
    for p, details in portas.items():
        log_print(f"    - Porta {p}: {details}")
        
    # --- A DECISÃO TÁTICA ---
    # HTTP/HTTPS Web Enum
    for p in portas.keys():
        if p in [80, 443, 8080, 8000, 8443]:
             run_web_fuzz(target, p, workspace_dir)

    # SMB Enum
    if 139 in portas or 445 in portas:
         run_smb_enum(target, workspace_dir)

    # FTP Enum
    if 21 in portas:
         run_ftp_anon_check(target, 21, workspace_dir)

    # Infra e Outros (DNS, SNMP) Note: O Nmap TCP apanha 53 tcp, o SNMP precisaria do Nmap UDP para apanhar na perfeição, mas deixamos as duas
    if 53 in portas:
         run_dns_enum(target, workspace_dir)
    if 161 in portas:
         run_snmp_enum(target, workspace_dir)

    # Searchsploit (Ofensivo)
    run_searchsploit(target, portas, workspace_dir)

    # Geração do Relatório Final (Sempre corre no final do Automode)
    generate_markdown_report(target, workspace_dir, portas)

def main():
    parser = argparse.ArgumentParser(
        description="ShadowHunter Recon Framework (CTF/Pentest)",
        epilog="Exemplo: python3 shadow_hunter.py -t 10.10.10.5 -p fast --auto"
    )
    
    parser.add_argument("-t", "--target", help="IP do alvo ou Domínio (Ex: 10.10.10.5)")
    parser.add_argument("-p", "--profile", choices=['fast', 'deep', 'vuln', 'stealth'], default="fast", 
                        help="Perfil de scan do Nmap")
    parser.add_argument("-a", "--auto", action="store_true", 
                        help="Ativar 'Hunter Mode' - Análise e Scripts consoante portas abertas.")
    parser.add_argument("--crack", help="Ficheiro contendo hashes ou string da hash para crackar offline (John)")
    parser.add_argument("--wordlist", help="Caminho para wordlist opcional (para o módulo crack)")
    parser.add_argument("--format", help="Formato da hash para o John (Ex: raw-md5, bcrypt)")
    
    args = parser.parse_args()

    # MODO CLI CRACKING DIRECIONAL
    if args.crack:
        banner()
        crack_hash(args.crack, args.wordlist, args.format, os.getcwd())
        sys.exit(0)

    # MODO HÍBRIDO
    if len(sys.argv) == 1:
        # Loop Principal do Menu Wizard
        while True:
            target, profile, is_auto_mode = interactive_menu()
            
            if os.geteuid() != 0 and profile in ['stealth']:
                log_print(f"{R}[!] Scans stealth precisam de root (sudo)!{W}")
                sys.exit(1)

            pre_flight_check()
            workspace = setup_workspace(target)
            
            # 0. RESOLUÇÃO DE DOMÍNIOS (Subdomains)
            if not is_ip(target):
                run_subdomain_enum(target, workspace)
            
            # 1. NETWORK RECON BASE
            run_network_scan(target, profile, workspace)
            
            # 2. HUNTER AUTOMODE
            if is_auto_mode:
                log_print(f"\n{G}==================================================={W}")
                log_print(f"{G}    [!] ATIVANDO HUNTER AUTOMODE (CASCATA) [!]{W}")
                log_print(f"{G}==================================================={W}")
                time.sleep(1)
                hunter_automode(target, workspace, profile)
            else:
                log_print(f"\n{Y}[*] Modo Auto não ativado. Scan de mapa base terminado.{W}")

            print(f"\n{G}[!] Scan em {target} concluído com Sucesso!{W}")
            print(f"{G}[!] Os resultados estão na pasta {workspace}.{W}")
            
            _ret = input(f"\n{Y}[>] Deseja voltar ao Menu Principal? (S/n): {W}")
            if _ret.lower() == 'n':
                log_print(f"{B}[!] A terminar o Shadow Hunter...{W}")
                sys.exit(0)
            else:
                continue
    else:
        # Modo CLI Rápido
        if not args.target:
             parser.print_help(sys.stderr)
             sys.exit(1)
        target = args.target
        profile = args.profile
        is_auto_mode = args.auto

        if os.geteuid() != 0 and profile in ['stealth']:
            log_print(f"{R}[!] Scans stealth precisam de root (sudo)!{W}")
            sys.exit(1)

        banner()
        
        pre_flight_check()
        workspace = setup_workspace(target)
        
        # 0. RESOLUÇÃO DE DOMÍNIOS (Subdomains)
        if not is_ip(target):
            run_subdomain_enum(target, workspace)
            
        # 1. NETWORK RECON BASE
        run_network_scan(target, profile, workspace)
        
        # 2. HUNTER AUTOMODE
        if is_auto_mode:
            log_print(f"\n{G}==================================================={W}")
            log_print(f"{G}    [!] ATIVANDO HUNTER AUTOMODE (CASCATA) [!]{W}")
            log_print(f"{G}==================================================={W}")
            time.sleep(1)
            hunter_automode(target, workspace, profile)
        else:
            log_print(f"\n{Y}[*] Modo Auto desativado. Scan de mapa base terminado.{W}")

if __name__ == "__main__":
    main()
