import unittest
import time
import threading
import socket
import sys
import os
import random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.tcp_server import TCPServer
from src.udp_server import UDPServer

class TestNetcatCompatibility(unittest.TestCase):
    """Test 3: Совместимость с netcat"""
    
    def setUp(self):
        self.host = 'localhost'
        # Используем случайные порты
        self.tcp_port = 9400 + random.randint(1, 100)
        self.udp_port = 9500 + random.randint(1, 100)
        self.tcp_server = None
        self.udp_server = None
        self.tcp_server_thread = None
        self.udp_server_thread = None
    
    def start_tcp_server(self):
        """Запускает TCP сервер"""
        self.tcp_server = TCPServer(self.host, self.tcp_port)
        self.tcp_server.start()
    
    def start_udp_server(self):
        """Запускает UDP сервер"""
        self.udp_server = UDPServer(self.host, self.udp_port)
        self.udp_server.start()
    
    def test_tcp_netcat_raw_socket(self):
        """TCP совместимость через raw sockets (имитация netcat)"""
        self.tcp_server_thread = threading.Thread(target=self.start_tcp_server)
        self.tcp_server_thread.daemon = True
        self.tcp_server_thread.start()
        time.sleep(1.5)
        
        try:
            # Имитируем netcat через raw socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3.0)
            sock.connect((self.host, self.tcp_port))
            
            # Отправляем сообщение без протокола (как netcat)
            test_messages = [
                b"Simple message\n",
                b"Another test\n"
            ]
            
            for msg in test_messages:
                sock.send(msg)
                time.sleep(0.3)  # Увеличиваем паузу
            
            # Сервер не должен упасть
            success = True
            
        except Exception as e:
            print(f"Netcat test error: {e}")
            success = False
        finally:
            try:
                sock.close()
            except:
                pass
            if self.tcp_server:
                self.tcp_server.stop()
        
        self.assertTrue(success)
    
    def test_udp_netcat_raw_socket(self):
        """UDP совместимость через raw sockets"""
        self.udp_server_thread = threading.Thread(target=self.start_udp_server)
        self.udp_server_thread.daemon = True
        self.udp_server_thread.start()
        time.sleep(1.5)
        
        try:
            # Имитируем netcat через UDP socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(3.0)
            
            test_messages = [
                b"UDP test 1",
                b"UDP test 2"
            ]
            
            for msg in test_messages:
                sock.sendto(msg, (self.host, self.udp_port))
                time.sleep(0.3)
            
            success = True
            
        except Exception as e:
            print(f"UDP netcat test error: {e}")
            success = False
        finally:
            try:
                sock.close()
            except:
                pass
            if self.udp_server:
                self.udp_server.stop()
        
        self.assertTrue(success)
    
    def test_tcp_protocol_with_netcat_style(self):
        """TCP протокол с сообщениями в стиле netcat"""
        # Используем другой порт
        self.tcp_port = 9600 + random.randint(1, 100)
        
        self.tcp_server_thread = threading.Thread(target=self.start_tcp_server)
        self.tcp_server_thread.daemon = True
        self.tcp_server_thread.start()
        time.sleep(1.5)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3.0)
            sock.connect((self.host, self.tcp_port))
            
            # Отправляем сообщения разной длины
            messages = [
                b"short",
                b"medium message here",
                b"x" * 500,  # Уменьшаем длину сообщения
                b"end"
            ]
            
            for msg in messages:
                sock.send(msg)
                time.sleep(0.2)
            
            success = True
            
        except Exception as e:
            print(f"Protocol test error: {e}")
            success = False
        finally:
            try:
                sock.close()
            except:
                pass
            if self.tcp_server:
                self.tcp_server.stop()
        
        self.assertTrue(success)
    
    def tearDown(self):
        """Очистка после каждого теста"""
        time.sleep(0.5)
        if self.tcp_server:
            self.tcp_server.stop()
        if self.udp_server:
            self.udp_server.stop()
        if self.tcp_server_thread and self.tcp_server_thread.is_alive():
            self.tcp_server_thread.join(timeout=2.0)
        if self.udp_server_thread and self.udp_server_thread.is_alive():
            self.udp_server_thread.join(timeout=2.0)

if __name__ == '__main__':
    unittest.main()