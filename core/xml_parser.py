import xml.etree.ElementTree as ET
import os
from core.utils import G, R, Y, B, W, log_print

def parse_nmap_xml(xml_file):
    """Lê o relatório XML do Nmap e devolve as portas abertas e serviços num dicionário."""
    open_ports = {}
    
    if not os.path.exists(xml_file):
        log_print(f"{R}[!] Erro: Ficheiro XML {xml_file} não encontrado! O scan falhou?{W}")
        return open_ports
        
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        
        for host in root.findall('host'):
            # Ignora hosts que não estão 'up'
            status = host.find('status')
            if status is not None and status.get('state') != 'up':
                continue
                
            ports = host.find('ports')
            if ports is None:
                continue
                
            for port in ports.findall('port'):
                state = port.find('state')
                if state is not None and state.get('state') == 'open':
                    port_id = int(port.get('portid'))
                    service = port.find('service')
                    
                    # Extrai informações do serviço se existirem
                    svc_name = service.get('name') if service is not None else 'unknown'
                    svc_product = service.get('product') if service is not None else ''
                    svc_version = service.get('version') if service is not None else ''
                    
                    details = f"{svc_name} {svc_product} {svc_version}".strip()
                    open_ports[port_id] = details
                    
    except Exception as e:
        log_print(f"{R}[!] Erro ao dar parse no XML do Nmap: {e}{W}")
        
    return open_ports
