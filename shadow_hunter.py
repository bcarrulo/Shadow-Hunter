import nmap
import sys
import os
import time
from datetime import datetime

import socket

# Cores para o terminal (Estética Hacker)
R = '\033[31m' # Red
G = '\033[32m' # Green
Y = '\033[33m' # Yellow
B = '\033[34m' # Blue
W = '\033[0m'  # White (Reset)

# Inicializa o Scanner
nm = nmap.PortScanner()
LOG_FILE = f"scan_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"

def get_vendor(mac_address):
    """Tenta obter o fabricante (Vendor) pelo MAC Address usando API ou DB local do Nmap"""
    try:
        # Nota: O nmap já retorna 'vendor' no scan, vamos usar isso primeiro
        return "Desconhecido"
    except:
        return "VendorNotFound"

def get_local_ip():
    """Tenta descobrir o IP local e sugere a rede /24"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        # Assume /24
        return f"{ip.rsplit('.', 1)[0]}.0/24"
    except:
        return None

def banner():
    # Limpa a tela (Windows ou Linux)
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{G}")
    print(r"""
   _____ _               _                 
  / ____| |             | |                
 | (___ | |__   __ _  __| | _____      __  
  \___ \| '_ \ / _` |/ _` |/ _ \ \ /\ / /  
  ____) | | | | (_| | (_| | (_) \ V  V /   
 |_____/|_| |_|\__,_|\__,_|\___/ \_/\_/    
    HU N T E R   E D I T I O N  v1.0
    """)
    print(f"{W}--------------------------------------------------")
    print(f"{Y}[*] Log Output: {LOG_FILE}{W}")
    print(f"{Y}[*] Operator: {os.getlogin() if os.name == 'nt' else os.getenv('USER')}{W}")
    print(f"{W}--------------------------------------------------\n")

def log_print(text):
    print(text)
    try:
        with open(LOG_FILE, 'a') as f:
            # Remove códigos de cor para o arquivo de texto
            clean_text = text.replace(R, '').replace(G, '').replace(Y, '').replace(B, '').replace(W, '')
            f.write(clean_text + "\n")
    except:
        pass

def get_targets():
    """Menu para seleção de alvos"""
    print(f"{B}[0]{W} AUTO-RECON (Detectar minha rede local e atacar)")
    print(f"{B}[1]{W} Escanear uma única rede (ex: 192.168.1.0/24)")
    print(f"{B}[2]{W} Escanear Range de Subnets (ex: 192.168.0.x até 192.168.5.x)")
    print(f"{B}[3]{W} Escanear IP Único (Targeted)")
    print(f"{B}[99]{W} Sair")
    
    choice = input(f"\n{G}[?] Selecione uma opção: {W}")
    
    targets = []
    
    if choice == '0':
        detected_net = get_local_ip()
        if detected_net:
            print(f"{G}[+] Rede detectada: {detected_net}{W}")
            confirm = input(f"{Y}[?] Confirmar alvo? (S/n): {W}")
            if confirm.lower() != 'n':
                targets.append(detected_net)
        else:
            print(f"{R}[!] Não foi possível detectar a rede local.{W}")

    elif choice == '1':
        net = input(f"{Y}[>] Digite a rede (ex: 192.168.1.0/24): {W}")
        targets.append(net)
        
    elif choice == '2':
        base = input(f"{Y}[>] Digite os 2 primeiros octetos (ex: 192.168): {W}")
        start = int(input(f"{Y}[>] Começar na subnet (ex: 0): {W}"))
        end = int(input(f"{Y}[>] Terminar na subnet (ex: 5): {W}"))
        
        for i in range(start, end + 1):
            targets.append(f"{base}.{i}.0/24")
            
    elif choice == '3':
        ip = input(f"{Y}[>] Digite o IP Alvo: {W}")
        targets.append(ip)
        
    elif choice == '99':
        sys.exit()
        
    else:
        print(f"{R}[!] Opção inválida!{W}")
        time.sleep(1)
        return get_targets()
        
    return targets

def get_scan_profile():
    """Menu para seleção de Perfil de Scan"""
    print(f"\n{B}[?] S E L E C I O N E   O   P E R F I L   D E   A T A Q U E :{W}")
    print(f"{B}[1]{W} FAST SCAN (Top 1000 ports, -T4) -> Rápido e Furtivo")
    print(f"{B}[2]{W} DEEP SCAN (All 65535 ports, -A, Vuln Scripts) -> Lento e Barulhento")
    print(f"{B}[3]{W} VULN SCAN (Scripts de vulnerabilidade focados, -sV --script vuln)")
    print(f"{B}[4]{W} STEALTH SCAN (TCP SYN, -sS -T4 -p-)")
    print(f"{B}[5]{W} AGGRESSIVE (Intense Scan, -T5 -A -v)")
    print(f"{B}[6]{W} LEVE (Ping Only -sn)")
    print(f"{B}[9]{W} CUSTOM (Digite seus próprios argumentos)")
    
    choice = input(f"\n{G}[?] Escolha o perfil: {W}")
    
    # Adicionando Timeouts e Retries para evitar travamentos
    if choice == '1':
        return '-p 1-1000 -T4 --open --max-retries 2 --host-timeout 5m'
    elif choice == '2':
        return '-p- -A --script vuln -T4 --host-timeout 30m'
    elif choice == '3':
        return '-sV --script vuln -T4 --max-retries 3 --host-timeout 20m'
    elif choice == '4':
        return '-sS -p- -T4 --max-retries 2'
    elif choice == '5':
        return '-T5 -A -v --host-timeout 10m'
    elif choice == '6':
        return '-sn'
    elif choice == '9':
        return input(f"{Y}[>] Digite os argumentos do Nmap (ex: -sS -p 80,443): {W}")
    else:
        print(f"{R}[!] Opção inválida! Usando Default (Fast Scan).{W}")
        time.sleep(1)
        return '-p 1-1000 -T4 --open'

def targeted_port_scan(host, port):
    """Realiza scans específicos em uma porta selecionada (Loop persistente)"""
    while True:
        print(f"\n{B}[?] S E L E C I O N E   O   T I P O   D E   A T A Q U E   N A   P O R T A   {port}:{W}")
        print(f"{B}[1]{W} VERSION DETECTION (-sV) -> Tentar descobrir versão exata")
        print(f"{B}[2]{W} UDP SCAN (-sU) -> Verificar se responde em UDP (Lento)")
        print(f"{B}[3]{W} XMAS SCAN (-sX) -> Evasão de Firewall (Fin, Psh, Urg)")
        print(f"{B}[4]{W} FIN SCAN (-sF) -> Evasão (Apenas flag FIN)")
        print(f"{B}[5]{W} NULL SCAN (-sN) -> Evasão (Sem flags)")
        print(f"{B}[6]{W} WINDOW SCAN (-sW) -> Analyse TCP Window")
        print(f"{B}[7]{W} NSE VULN SCAN -> Scripts de Vulnerabilidade (CVEs)")
        print(f"{B}[8]{W} NSE AUTH/CREDS -> Tenta senhas padrão e Auth Bypass")
        print(f"{B}[9]{W} NSE EXPLOIT -> Tenta rodar Exploits (PERIGOSO!)")
        print(f"{B}[A]{W} RODAR TUDO (Sequencial: Version -> Vuln -> Auth)")
        print(f"{B}[0]{W} VOLTAR para seleção de porta")

        choice = input(f"\n{G}[?] Escolha o ataque: {W}")
        
        if choice == '0':
            break

        queue = []
        if choice == 'A':
            queue = [
                ('Version', '-sV --version-intensity 9'),
                ('Vuln', '-sV --script vuln'),
                ('Auth', '-sV --script auth,default')
            ]
        else:
            args = ''
            label = 'Custom'
            if choice == '1': args, label = '-sV --version-intensity 9', 'Version'
            elif choice == '2': args, label = '-sU', 'UDP'
            elif choice == '3': args, label = '-sX', 'Xmas'
            elif choice == '4': args, label = '-sF', 'Fin'
            elif choice == '5': args, label = '-sN', 'Null'
            elif choice == '6': args, label = '-sW', 'Window'
            elif choice == '7': args, label = '-sV --script vuln', 'Vuln'
            elif choice == '8': args, label = '-sV --script auth,default', 'Auth'
            elif choice == '9': args, label = '-sV --script exploit', 'Exploit'
            
            if args:
                queue.append((label, args))

        if not queue:
            continue

        for label, args in queue:
            log_print(f"\n{Y}[*] Executing {label} Scan on {host}:{port}...{W}")
            try:
                nm.scan(host, ports=str(port), arguments=args)
                
                if host in nm.all_hosts():
                     # Verifica TCP
                     if 'tcp' in nm[host] and int(port) in nm[host]['tcp']:
                         svc = nm[host]['tcp'][int(port)]
                         state = svc['state']
                         reason = svc['reason']
                         log_print(f"    {G}[RESULT]{W} Port {port}: {state} (Reason: {reason})")
                         
                         # Detalhes de Versão
                         if 'product' in svc and svc['product']:
                             log_print(f"    Product: {svc.get('product')} | Version: {svc.get('version')}")
                         
                         # Detalhes de Scripts (NSE)
                         if 'script' in svc:
                             for sname, out in svc['script'].items():
                                 lines = out.strip().split('\n')
                                 log_print(f"        {R}[SCRIPT: {sname}]{W}")
                                 for line in lines:
                                     log_print(f"            {line}")
                         else:
                             # Feedback explícito se não houver output de script
                             if 'script' in args:
                                 log_print(f"        {G}[OK]{W} Nenhum problema/script output retornado (Clean?)")
                                     
            except Exception as e:
                log_print(f"{R}[ERROR] Falha no scan da porta: {e}{W}")

def run_scan(target_list, scan_args):
    total_found = 0
    
    for network in target_list:
        log_print(f"\n{B}[*] INICIANDO RECONHECIMENTO EM: {network}{W}")
        
        try:
            # FASE 1: Ping Sweep (Rápido)
            nm.scan(hosts=network, arguments='-sn -PE -n')
            hosts = [x for x in nm.all_hosts() if nm[x].state() == 'up']
            
            log_print(f"{G}[+] Hosts vivos encontrados: {len(hosts)}{W}")
            
            if len(hosts) == 0:
                continue

            # FASE 2: Deep Scan
            for host in hosts:
                total_found += 1
                log_print(f"\n{Y}[*] Atacando Alvo: {host} ... Aguarde...{W}")
                
                # Scan com argumentos do perfil selecionado
                log_print(f"{Y}[*] Executing: nmap {scan_args} {host}{W}")
                nm.scan(host, arguments=scan_args)
                
                if host not in nm.all_hosts(): continue

                # OS Detection
                if 'osclass' in nm[host]:
                    for os_info in nm[host]['osclass']:
                        log_print(f"    {B}[OS]{W} {os_info['osfamily']} ({os_info['accuracy']}%)")

                # Hostname & MAC
                log_print(f"{B}   [+] INFO GERAL:{W}")
                
                # Tenta pegar Hostname
                hostname = "Desconhecido"
                if 'hostnames' in nm[host] and len(nm[host]['hostnames']) > 0:
                     hostname = nm[host]['hostnames'][0]['name']
                log_print(f"       Hostname: {hostname}")

                # Tenta pegar MAC e Vendor
                if 'addresses' in nm[host] and 'mac' in nm[host]['addresses']:
                    mac = nm[host]['addresses']['mac']
                    vendor = nm[host]['vendor'].get(mac, 'N/A')
                    log_print(f"       MAC Addr: {mac} ({vendor})")
                
                log_print(f"{B}   [+] SERVIÇOS & VULNERABILIDADES:{W}")
                
                open_ports = []
                for proto in nm[host].all_protocols():
                    ports = sorted(nm[host][proto].keys())
                    for port in ports:
                        svc = nm[host][proto][port]
                        state = svc['state']
                        if state == 'open':
                            open_ports.append(port)
                            prod = svc.get('product', 'Unknown')
                            ver = svc.get('version', '')
                            extrainfo = svc.get('extrainfo', '')
                            
                            log_print(f"       {G}[OPEN]{W} {port}/{proto} -> {prod} {ver} {extrainfo}".strip())
                            
                            if 'script' in svc:
                                for sname, out in svc['script'].items():
                                    # Formata output multi-linha para ficar bonito
                                    lines = out.strip().split('\n')
                                    log_print(f"           {R}[VULN?]{W} {sname}:")
                                    for line in lines:
                                        log_print(f"               {line}")
                
                # --- MENU DE ATAQUE ESPECÍFICO DE PORTA ---
                if open_ports:
                    while True:
                        print(f"\n{Y}[?] Portas abertas neste host: {open_ports}{W}")
                        ask = input(f"{G}[?] Quer lançar um ataque específico em alguma porta? (Porta/N): {W}")
                        
                        if ask.lower() in ['n', 'no', 'nao', '']:
                            break
                        
                        try:
                            target_port = int(ask)
                            if target_port in open_ports:
                                targeted_port_scan(host, target_port)
                            else:
                                print(f"{R}[!] Porta {target_port} não estava aberta no scan inicial.{W}")
                        except ValueError:
                            print(f"{R}[!] Entrada inválida.{W}")

        except KeyboardInterrupt:
            print("\n[!] Abortado pelo operador.")
            sys.exit()
        except Exception as e:
            log_print(f"{R}[ERROR] Falha ao scanear {network}: {e}{W}")

    log_print(f"\n{G}[*] MISSÃO CUMPRIDA. Total de alvos processados: {total_found}{W}")

# --- MAIN LOOP ---
if __name__ == "__main__":
    # Verifica root (Nmap precisa de root para OS fingerprinting)
    if os.geteuid() != 0:
        print(f"{R}[!] Execute como root (sudo)!{W}")
        sys.exit()

    try:
        while True:
            banner()
            alvos = get_targets()
            
            if alvos:
                profile_args = get_scan_profile()
                run_scan(alvos, profile_args)
                
            input(f"\n{Y}[ENTER] para voltar ao menu...{W}")
            
    except KeyboardInterrupt:
        print("\n[!] Encerrando...")