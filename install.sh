#!/bin/bash

# =========================================================================
# INSTALLER: Shadow-Hunter Recon Framework
# OS: Kali Linux, Parrot OS, Ubuntu, Debian
# =========================================================================

# Cores para o output
GREEN="\033[1;32m"
BLUE="\033[1;34m"
RED="\033[1;31m"
RESET="\033[0m"

echo -e "${BLUE}"
echo "    __  __               __                 "
echo "   / / / /_  ______  ___/ /____  _____      "
echo "  / /_/ / / / / __ \/ __  / __ \/ ___/      "
echo " / __  / /_/ / / / / /_/ / /_/ / /        "
echo "/_/ /_/\__,_/_/ /_/\__,_/\____/_/         "
echo "==========================================="
echo -e "${GREEN}[*] Shadow-Hunter Auto-Installer Started${RESET}\n"

# Verifica se o script está a ser executado como root
if [ "$EUID" -ne 0 ]; then
  echo -e "${RED}[!] Por favor, execute como root (sudo ./install.sh)${RESET}"
  exit 1
fi

echo -e "${BLUE}[+] Atualizando repositórios base...${RESET}"
apt-get update -y > /dev/null

echo -e "${BLUE}[+] Instalando pacotes e ferramentas de sistema...${RESET}"
apt-get install -y nmap whatweb enum4linux dnsutils snmp util-linux python3 python3-pip wget curl git > /dev/null

# Instalando FFUF (Caso não esteja nos repos da distro)
if ! command -v ffuf &> /dev/null; then
    echo -e "${BLUE}[+] Instalando FFUF (Web Fuzzer)...${RESET}"
    apt-get install -y ffuf > /dev/null
    if [ $? -ne 0 ]; then
        echo -e "${RED}[-] Erro ao instalar FFUF via apt. Tente instalar via Go depois.${RESET}"
    fi
else
    echo -e "${GREEN}[+] FFUF já está instalado.${RESET}"
fi

# Descarregando wordlist common.txt (Se não existir)
WORDLIST_DIR="/usr/share/wordlists/dirb"
if [ ! -f "$WORDLIST_DIR/common.txt" ]; then
    echo -e "${BLUE}[+] Descarregando wordlists iniciais (common.txt)...${RESET}"
    mkdir -p $WORDLIST_DIR
    wget -q https://raw.githubusercontent.com/v0re/dirb/master/wordlists/common.txt -O $WORDLIST_DIR/common.txt
fi

# Instalando Nuclei (Scanner de Vulnerabilidades Web)
if ! command -v nuclei &> /dev/null; then
    echo -e "${BLUE}[+] Instalando Nuclei (via repositório oficial)...${RESET}"
    # Depende de Go. No Kali às vezes tem apt install nuclei, vamos tentar esse:
    apt-get install -y nuclei > /dev/null
    if ! command -v nuclei &> /dev/null; then
        echo -e "${RED}[-] Nuclei requer Go para instalar manualmente se o apt falhar.${RESET}"
    fi
else
    echo -e "${GREEN}[+] Nuclei já está instalado.${RESET}"
    echo -e "${BLUE}[+] Atualizando templates do Nuclei...${RESET}"
    su - $SUDO_USER -c "nuclei -update-templates > /dev/null 2>&1"
fi

# Instalando dependências de Python locais (Se existirem, apesar de que usamos libs default)
echo -e "${BLUE}[+] A verificar dependências de Python...${RESET}"
# O script atualmente usa bibliotecas nativas de Python (os, sys, subprocess, xml, argparse)
# Mas deixamos aqui o pip caso queiras adicionar requirements no futuro
# pip3 install -r requirements.txt --break-system-packages > /dev/null 2>&1

echo -e "\n${GREEN}======================================================${RESET}"
echo -e "${GREEN}[!!!] Instalação Concluída com Sucesso! [!!!]${RESET}"
echo -e "${GREEN}======================================================${RESET}"
echo -e "Agora você pode executar no seu Linux:"
echo -e "  ${BLUE}python3 shadow_hunter.py${RESET}"
echo -e "  ou"
echo -e "  ${BLUE}sudo python3 shadow_hunter.py -t <IP_ALVO> -p fast --auto${RESET}"
