import os
from datetime import datetime
from core.utils import G, R, Y, B, W, log_print

def generate_markdown_report(target, workspace_dir, open_ports):
    """
    Consolida todos os dados extraídos de várias tools e compila num REPORT.md
    """
    log_print(f"\n{B}[*] A G E R A R   R E L A T Ó R I O   F I N A L ...{W}")
    
    report_path = os.path.join(workspace_dir, "REPORT.md")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        # Cabeçalho
        f.write(f"# 🎯 Shadow Hunter Report: `{target}`\n")
        f.write(f"**Data do Scan:** {now}\n")
        f.write("---\n\n")
        
        # Secção 1: Portas Abertas (Tabela)
        f.write("## 1. 🌐 Superfície de Ataque (Network Enum)\n\n")
        if open_ports:
            f.write("| Porta | Serviço & Versão |\n")
            f.write("|-------|-----------------|\n")
            for port, details in open_ports.items():
                clean_details = details if details else "Desconhecido"
                f.write(f"| **{port}** | {clean_details} |\n")
        else:
            f.write("*Nenhuma porta detetada.* 🤔\n")
        f.write("\n---\n\n")

        # Secção 2: Web Enum
        f.write("## 2. 🕸️ Mapeamento Web (Web Enum)\n")
        web_files = [f for f in os.listdir(workspace_dir) if f.startswith("web_enum") and f.endswith(".txt")]
        if web_files:
            for web_file in web_files:
                f.write(f"### Descobertas em `{web_file}`\n")
                f.write("```text\n")
                with open(os.path.join(workspace_dir, web_file), 'r', errors='ignore') as wf:
                    # Lê só as primeiras 30 linhas para não inundar o report
                    lines = wf.readlines()[:30]
                    f.writelines(lines)
                if len(lines) == 30: f.write("... (Resultados truncados, ver ficheiro original) ...\n")
                f.write("```\n\n")
        else:
            f.write("*Sem enumeração web registada.*\n\n")

        # Secção 3: Enumeração de Serviços (SMB, FTP, etc)
        f.write("## 3. ⚙️ Serviços Específicos (SMB, FTP, DNS, SNMP)\n")
        
        # Pega em todos os txts de serviços e infra que não sejam web nem o do searchsploit ou o do nmap global
        serv_files = [x for x in os.listdir(workspace_dir) if x.endswith(".txt") and ("smb" in x or "ftp" in x or "dns" in x or "snmp" in x)]
        if serv_files:
            for s_file in serv_files:
                f.write(f"### Serviço: `{s_file}`\n")
                f.write("```text\n")
                with open(os.path.join(workspace_dir, s_file), 'r', errors='ignore') as sf:
                    # Traz as primeiras 50 linhas para não entupir
                    f.writelines(sf.readlines()[:50])
                f.write("```\n\n")
        else:
            f.write("*Sem leaks de serviços específicos encontrados.* 🔒\n\n")

        # Secção 4: Exploits Guardados
        f.write("---\n\n")
        f.write("## 4. 🗡️ Auto-Exploit e CVEs Sugeridos\n")
        exp_file = os.path.join(workspace_dir, "searchsploit_findings.txt")
        if os.path.exists(exp_file):
            f.write("A ferramenta tentou mapear as versões detetadas contra a base de dados de Exploits locais:\n\n")
            f.write("```text\n")
            with open(exp_file, 'r', errors='ignore') as ef:
                # Limite de 100 linhas no MD
                f.writelines(ef.readlines()[:100])
            f.write("```\n\n")
        else:
            f.write("*O Searchsploit não detetou CVEs óbvios para as versões dadas.*\n\n")

        # Footer
        f.write("---\n")
        f.write("> **Gerado com 🖤 pelo ShadowHunter Framework**\n")

    log_print(f"{G}[!!!] R E L A T Ó R I O   C O N C L U Í D O [!!!]{W}")
    log_print(f"{G}[>] Ficheiro Master gerado em: {report_path}{W}")