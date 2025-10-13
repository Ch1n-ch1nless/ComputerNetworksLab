#!/usr/bin/env python3
import argparse
import sys
import os

# Добавляем текущую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(__file__))

from src.tcp_server import TCPServer
from src.tcp_client import TCPClient
from src.udp_server import UDPServer
from src.udp_client import UDPClient

def run_tcp_server(host: str, port: int):
    """Запускает TCP сервер"""
    server = TCPServer(host, port)
    server.start()

def run_tcp_client(host: str, port: int):
    """Запускает TCP клиент"""
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
    parser = argparse.ArgumentParser(description='Сетевое приложение TCP/UDP')
    parser.add_argument('--mode', choices=['tcp_server', 'tcp_client', 'udp_server', 'udp_client'],
                       required=True, help='Режим работы')
    parser.add_argument('--host', default='localhost', help='Хост для подключения')
    parser.add_argument('--port', type=int, default=8888, help='Порт для подключения')
    parser.add_argument('--udp-port', type=int, default=8889, help='Порт для UDP (по умолчанию 8889)')
    
    args = parser.parse_args()
    
    if args.mode == 'tcp_server':
        run_tcp_server(args.host, args.port)
    elif args.mode == 'tcp_client':
        run_tcp_client(args.host, args.port)
    elif args.mode == 'udp_server':
        run_udp_server(args.host, args.udp_port)
    elif args.mode == 'udp_client':
        run_udp_client(args.host, args.udp_port)

if __name__ == "__main__":
    main()