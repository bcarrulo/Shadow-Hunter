import socket
from core.utils import G, R, Y, B, W, log_print

def grab_banner(ip, port):
    """
    Liga-se via socket puro a uma porta, lê os primeiros bytes recebidos e extrai o banner real.
    Isto é 100x mais limpo que usar Nmap apenas para descobrir se um serviço é SSH FTP ou HTTP.
    """
    banner = "N/A"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2.0)
        s.connect((ip, int(port)))
        
        # Algumas portas (como 80/HTTP) precisam que nós enviemos algo primeiro
        if int(port) in [80, 8080, 443]:
            s.send(b"HEAD / HTTP/1.0\r\n\r\n")
        
        resposta = s.recv(1024)
        if resposta:
            banner = resposta.decode('utf-8', errors='ignore').split('\n')[0].strip()
        s.close()
    except Exception:
        pass
    return banner

def fast_ping_sweep(network_range):
    """Pode ser implementado aqui no futuro para substituir o Nmap Ping Sweep inicial"""
    log_print(f"{Y}[*] Fast Ping Sweep via Socket pendente de implementação total.{W}")
    pass
