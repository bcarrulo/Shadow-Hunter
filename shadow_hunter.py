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

def interactive_menu():
    """Modo Clássico Interativo: Corre se o tool for iniciado sem argumentos."""
    banner()
    print(f"\n{B}[?] S E L E C I O N E   O   S E U   A L V O :{W}")
    print(f"{B}[0]{W} AUTO-RECON (Detectar minha rede local)")
    print(f"{B}[1]{W} Escanear Range de Rede (Ex: 192.168.1.0/24)")
    print(f"{B}[2]{W} Escanear IP Único (Targeted)")
    print(f"{B}[99]{W} Sair")
    
    choice = input(f"\n{G}[?] Opção: {W}")
    
    target = None
    if choice == '0':
        net = get_local_ip()
        if net:
            conf = input(f"{Y}[?] Confirmar alvo {net}? (S/n): {W}")
            if conf.lower() != 'n': target = net
    elif choice == '1':
        target = input(f"{Y}[>] Digite a rede: {W}")
    elif choice == '2':
        target = input(f"{Y}[>] Digite o IP: {W}")
    elif choice == '99':
        sys.exit(0)
        
    if not target:
        log_print(f"{R}[!] Alvo Inválido. A encerrar.{W}")
        sys.exit(1)
        
    print(f"\n{B}[?] P E R F I L   D E   A T A Q U E :{W}")
    print(f"{B}[1]{W} FAST")
    print(f"{B}[2]{W} DEEP (Mais Demorado)")
    
    p_choice = input(f"\n{G}[?] Opção: {W}")
    profile = 'deep' if p_choice == '2' else 'fast'
    
    return target, profile, False # interactive nunca chuta o automode hard sozinho por default

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
    
    args = parser.parse_args()

    # MODO HÍBRIDO
    if len(sys.argv) == 1:
        # Modo Interativo Menus Antigo
        target, profile, auto = interactive_menu()
        is_auto_mode = True # No menu vamos assumir que queremos o automode todo a disparar para ter piada no interativo
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

    if len(sys.argv) > 1:
        banner()
    
    pre_flight_check()
    workspace = setup_workspace(target)
    
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
