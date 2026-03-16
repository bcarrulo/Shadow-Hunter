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

        # Secção 0: Subdomínios (Apenas Se Domain Enum correu)
        sub_alive_file = os.path.join(workspace_dir, "subdomains_alive.txt")
        sub_all_file = os.path.join(workspace_dir, "subdomains_all.txt")
        if os.path.exists(sub_alive_file) or os.path.exists(sub_all_file):
            f.write("## 0. 🌍 Enumeração de Subdomínios\n\n")
            if os.path.exists(sub_alive_file):
                with open(sub_alive_file, 'r') as sf:
                    subs = sf.readlines()
                f.write(f"**Subdomínios VIVOS ({len(subs)}):**\n```text\n")
                f.writelines(subs[:50])
                if len(subs) > 50: f.write("... (truncado)\n")
                f.write("```\n\n")
            elif os.path.exists(sub_all_file):
                with open(sub_all_file, 'r') as sf:
                    subs = sf.readlines()
                f.write(f"**Subdomínios Apanhados (Sem confirmação de vida) ({len(subs)}):**\n```text\n")
                f.writelines(subs[:50])
                if len(subs) > 50: f.write("... (truncado)\n")
                f.write("```\n\n")
            f.write("---\n\n")
        
        # Secção 1: Portas Abertas (Tabela)
        f.write("## 1. 🚪 Superfície de Ataque (Network Enum)\n\n")
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
        f.write("## 2. 🕸️ Mapeamento Web\n")
        web_files = [x for x in os.listdir(workspace_dir) if x.startswith("web_") and x.endswith(".txt")]
        if web_files:
            for web_file in web_files:
                f.write(f"### Descobertas em `{web_file}` (Feroxbuster, Nuclei, WPScan, Nmap)\n")
                f.write("```text\n")
                with open(os.path.join(workspace_dir, web_file), 'r', errors='ignore') as wf:
                    lines = wf.readlines()[:50]
                    f.writelines(lines)
                if len(lines) == 50: f.write("\n... (Resultados truncados, ver ficheiro original) ...\n")
                f.write("```\n\n")
        else:
            f.write("*Sem enumeração web registada.*\n\n")

        # Secção 3: Enumeração de Serviços
        f.write("---\n\n## 3. ⚙️ Ferramentas de Infraestrutura (SMB, AD, DNS, etc)\n")
        
        serv_files = [x for x in os.listdir(workspace_dir) if x.endswith(".txt") and any(k in x for k in ["smb_", "ftp_", "dns_", "snmp_"])]
        if serv_files:
            f.write("Resultados de ferramentas como NetExec, SMBMap, Enum4linux e axfr:\n\n")
            for s_file in serv_files:
                f.write(f"### `{s_file}`\n")
                f.write("```text\n")
                with open(os.path.join(workspace_dir, s_file), 'r', errors='ignore') as sf:
                    lines = sf.readlines()[:50]
                    f.writelines(lines)
                if len(lines) == 50: f.write("\n... (Resultados truncados, ver original) ...\n")
                f.write("```\n\n")
        else:
            f.write("*Sem leaks de serviços específicos encontrados.*\n\n")

        # Secção 4: Exploits Guardados
        f.write("---\n\n## 4. 🗡️ Ofensiva e Credenciais\n")
        
        # Hydra e Cracking
        brute_files = [x for x in os.listdir(workspace_dir) if (x.startswith("hydra_") or x.startswith("cracked_")) and x.endswith(".txt")]
        if brute_files:
            f.write("### 🔑 Credenciais (Brute-Force & Hashes)\n\n")
            for b_file in brute_files:
                f.write(f"#### Origem: `{b_file}`\n")
                f.write("```text\n")
                with open(os.path.join(workspace_dir, b_file), 'r', errors='ignore') as bf:
                    lines = bf.readlines()
                    f.writelines(lines[:50])
                if len(lines) > 50: f.write("\n... (truncado)\n")
                f.write("```\n\n")

        # Searchsploit
        exp_file = os.path.join(workspace_dir, "searchsploit_findings.txt")
        if os.path.exists(exp_file):
            f.write("### 📜 CVEs Potenciais e Exploits Encontrados\n\n")
            f.write("```text\n")
            with open(exp_file, 'r', errors='ignore') as ef:
                lines = ef.readlines()
                f.writelines(lines[:100])
            if len(lines) > 100: f.write("\n... (truncado)\n")
            f.write("```\n\n")
        elif not brute_files and not os.path.exists(exp_file):
            f.write("*Sem vetor ofensivo direto automatizado apanhado nesta run.*\n\n")

        # Footer
        f.write("---\n")
        f.write("> **Gerado com 🖤 pelo ShadowHunter Framework**\n")

    log_print(f"{G}[!!!] R E L A T Ó R I O   C O N C L U Í D O [!!!]{W}")
    log_print(f"{G}[>] Ficheiro Master gerado em: {report_path}{W}")