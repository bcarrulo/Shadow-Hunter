import subprocess
import os
import shutil
from core.utils import G, R, Y, B, W, log_print

def run_dns_enum(target, workspace_dir):
    """
    Tenta Zone Transfer e queries DNS, usando preferencialmente dns.resolver puro (dnspython), 
    se não instalado, faz fallback seguro para o bash (dig).
    """
    log_print(f"\n{B}[*] (AUTO-MODE) Entrada DNS Detetada (Porta 53). A tentar Axis/Enumeração...{W}")
    out_file = os.path.join(workspace_dir, "dns_enum.txt")

    try:
        import dns.zone
        import dns.resolver
        import dns.query
        
        log_print(f"{Y}[>] A iniciar AXFR Zone Transfer via native python (dnspython)...{W}")
        with open(out_file, 'w') as f:
            f.write("=== [NATIVE DNS ENUM] ===\n")
            try:
                # Se tu tiveres o domínio alvo podes tentar a query, assumindo que target pode ser nome
                # Tenta pedir o registo NS se der
                ns_answers = dns.resolver.resolve(target, 'NS')
                for server in ns_answers:
                     f.write(f"NS Encontrado: {server.target}\n")
                     # Tentativa Zone Transfer
                     z = dns.zone.from_xfr(dns.query.xfr(str(server.target), target))
                     names = z.nodes.keys()
                     for n in names:
                          f.write(f"Subdomínio: {z[n].to_text(n)}\n")
                log_print(f"{G}[+] Native AXFR efetuado. {W}")
            except Exception as e:
                f.write(f"Sem resposta limpa de AXFR: {e}\n")
                
    except ImportError:
        # Fallback caso a biblioteca dnspython falhe ou falte
        log_print(f"{R}[-] dnspython não instalada. A alternar para dig (fallback bash)...{W}")
        if shutil.which("dig"):
            try:
                res = subprocess.run(["dig", "axfr", f"@{target}"], capture_output=True, text=True)
                with open(out_file, 'w') as f: f.write(res.stdout)
            except Exception as e: log_print(f"{R}[!] Erro de dig: {e}{W}")

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
