#!/usr/bin/env python3
import argparse
import sys
import os
import ssl

sys.path.insert(0, os.path.dirname(__file__))

from src.tcp_server import TCPServer
from src.tcp_client import TCPClient
from src.tls_tcp_server import TLSTCPServer
from src.tls_tcp_client import TLSTCPClient
from src.udp_server import UDPServer
from src.udp_client import UDPClient

def generate_self_signed_cert():
    """Генерирует самоподписанный сертификат для тестирования"""
    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        import datetime
        
        # Создаем приватный ключ
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
        )
        
        # Создаем сертификат
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "RU"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Moscow"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "MIPT"),
            x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
        ])
        
        cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName("localhost")]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Создаем папку certs если ее нет
        os.makedirs("certs", exist_ok=True)
        
        # Сохраняем приватный ключ
        with open("certs/server.key", "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption(),
            ))
        
        # Сохраняем сертификат
        with open("certs/server.crt", "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
            
        print("Сгенерированы самоподписанные сертификаты в папке certs/")
        return "certs/server.crt", "certs/server.key"
        
    except ImportError:
        print("Для генерации сертификатов установите: pip install cryptography")
        return None, None

def run_tcp_server(host: str, port: int):
    """Запускает обычный TCP сервер"""
    server = TCPServer(host, port)
    server.start()

def run_tcp_client(host: str, port: int):
    """Запускает обычный TCP клиент"""
    client = TCPClient(host, port)
    
    if not client.connect():
        return
    
    try:
        while True:
            message = input("Введите сообщение (или 'quit' для выхода): ")
            if message.lower() == 'quit':
                break
            
            response = client.send_message(message)
            print(f"Ответ сервера: {response}")
            
    except KeyboardInterrupt:
        print("\nОтключение...")
    finally:
        client.disconnect()

def run_tls_tcp_server(host: str, port: int, certfile: str, keyfile: str, ca_certs: str):
    """Запускает TLS TCP сервер"""
    if not certfile or not keyfile:
        print("Генерация самоподписанных сертификатов...")
        certfile, keyfile = generate_self_signed_cert()
        if not certfile or not keyfile:
            print("Не удалось сгенерировать сертификаты")
            return
    
    server = TLSTCPServer(host, port, certfile=certfile, keyfile=keyfile, ca_certs=ca_certs)
    server.start()

def run_tls_tcp_client(host: str, port: int, ca_certs: str, certfile: str, keyfile: str):
    """Запускает TLS TCP клиент"""
    client = TLSTCPClient(host, port, ca_certs=ca_certs, certfile=certfile, keyfile=keyfile)
    
    if not client.connect():
        return
    
    try:
        while True:
            message = input("Введите сообщение (или 'quit' для выхода): ")
            if message.lower() == 'quit':
                break
            
            response = client.send_message(message)
            print(f"Ответ сервера: {response}")
            
    except KeyboardInterrupt:
        print("\nОтключение...")
    finally:
        client.disconnect()

def run_udp_server(host: str, port: int):
    """Запускает UDP сервер"""
    server = UDPServer(host, port)
    server.start()

def run_udp_client(host: str, port: int):
    """Запускает UDP клиент"""
    client = UDPClient(host, port)
    
    if not client.connect():
        return
    
    try:
        while True:
            message = input("Введите сообщение (или 'quit' для выхода): ")
            if message.lower() == 'quit':
                break
            
            response = client.send_message(message)
            print(f"Ответ сервера: {response}")
            
    except KeyboardInterrupt:
        print("\nОтключение...")
    finally:
        client.disconnect()

def main():
    parser = argparse.ArgumentParser(description='Сетевое приложение TCP/UDP с поддержкой TLS')
    parser.add_argument('--mode', 
                       choices=['tcp_server', 'tcp_client', 'tls_tcp_server', 'tls_tcp_client', 'udp_server', 'udp_client'],
                       required=True, help='Режим работы')
    parser.add_argument('--host', default='localhost', help='Хост для подключения')
    parser.add_argument('--port', type=int, default=8888, help='Порт для подключения')
    parser.add_argument('--certfile', help='Путь к сертификату сервера (для TLS)')
    parser.add_argument('--keyfile', help='Путь к приватному ключу сервера (для TLS)')
    parser.add_argument('--ca-certs', help='Путь к корневому сертификату CA (для TLS)')
    
    args = parser.parse_args()
    
    # Проверяем SSLKEYLOGFILE для TLS режимов
    if args.mode in ['tls_tcp_server', 'tls_tcp_client']:
        sslkeylog = os.environ.get('SSLKEYLOGFILE')
        if sslkeylog:
            print(f"SSLKEYLOGFILE установлен: {sslkeylog}")
        else:
            print("Предупреждение: SSLKEYLOGFILE не установлен. Wireshark не сможет расшифровать TLS трафик.")
    
    if args.mode == 'tcp_server':
        run_tcp_server(args.host, args.port)
    elif args.mode == 'tcp_client':
        run_tcp_client(args.host, args.port)
    elif args.mode == 'tls_tcp_server':
        run_tls_tcp_server(args.host, args.port, args.certfile, args.keyfile, args.ca_certs)
    elif args.mode == 'tls_tcp_client':
        run_tls_tcp_client(args.host, args.port, args.ca_certs, args.certfile, args.keyfile)
    elif args.mode == 'udp_server':
        run_udp_server(args.host, args.port)
    elif args.mode == 'udp_client':
        run_udp_client(args.host, args.port)

if __name__ == "__main__":
    main()