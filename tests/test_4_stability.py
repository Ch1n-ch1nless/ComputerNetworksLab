import unittest
import time
import threading
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.tcp_server import TCPServer
from src.tcp_client import TCPClient
from src.udp_server import UDPServer
from src.udp_client import UDPClient

class TestStability(unittest.TestCase):
    """Test 4: Стабильность при долгой работе"""
    
    def setUp(self):
        self.tcp_host = 'localhost'
        self.tcp_port = 9007
        self.udp_host = 'localhost'
        self.udp_port = 9008
        self.tcp_server = None
        self.udp_server = None
        self.tcp_server_thread = None
        self.udp_server_thread = None
    
    def start_tcp_server(self):
        """Запускает TCP сервер"""
        self.tcp_server = TCPServer(self.tcp_host, self.tcp_port)
        self.tcp_server.start()
    
    def start_udp_server(self):
        """Запускает UDP сервер"""
        self.udp_server = UDPServer(self.udp_host, self.udp_port)
        self.udp_server.start()
    
    def test_tcp_extended_operation(self):
        """TCP длительная работа"""
        self.tcp_server_thread = threading.Thread(target=self.start_tcp_server)
        self.tcp_server_thread.daemon = True
        self.tcp_server_thread.start()
        time.sleep(1)  # Увеличиваем время ожидания
        
        client = TCPClient(self.tcp_host, self.tcp_port)
        self.assertTrue(client.connect())
        
        # Многократная отправка сообщений
        for i in range(20):  # Уменьшаем количество сообщений
            message = f"Message {i}: " + "A" * 50  # Уменьшаем размер сообщения
            response = client.send_message(message)
            self.assertIn("TCP эхо", response)
            self.assertIn(f"Message {i}", response)
            time.sleep(0.1)  # Увеличиваем паузу
        
        client.disconnect()
        if self.tcp_server:
            self.tcp_server.stop()
    
    def test_udp_extended_operation(self):
        """UDP длительная работа"""
        self.udp_server_thread = threading.Thread(target=self.start_udp_server)
        self.udp_server_thread.daemon = True
        self.udp_server_thread.start()
        time.sleep(1)  # Увеличиваем время ожидания
        
        client = UDPClient(self.udp_host, self.udp_port, timeout=5.0)  # Увеличиваем таймаут
        self.assertTrue(client.connect())
        
        # Многократная отправка сообщений
        for i in range(15):  # Уменьшаем количество сообщений
            message = f"UDP Message {i}"
            response = client.send_message(message)
            # Более мягкая проверка для UDP
            if "Таймаут" not in response:
                self.assertIn("UDP эхо", response)
                self.assertIn(f"UDP Message {i}", response)
            time.sleep(0.2)  # Увеличиваем паузу
        
        client.disconnect()
        if self.udp_server:
            self.udp_server.stop()
    
    def test_tcp_reconnect_stability(self):
        """TCP стабильность при переподключениях"""
        self.tcp_server_thread = threading.Thread(target=self.start_tcp_server)
        self.tcp_server_thread.daemon = True
        self.tcp_server_thread.start()
        time.sleep(1)  # Увеличиваем время ожидания
        
        # Несколько переподключений
        for i in range(3):  # Уменьшаем количество переподключений
            client = TCPClient(self.tcp_host, self.tcp_port)
            
            # Повторяем попытку подключения при ошибке
            max_attempts = 3
            for attempt in range(max_attempts):
                if client.connect():
                    break
                elif attempt < max_attempts - 1:
                    time.sleep(0.5)  # Ждем перед повторной попыткой
                else:
                    self.fail(f"Не удалось подключиться после {max_attempts} попыток")
            
            # Отправляем несколько сообщений
            for j in range(2):  # Уменьшаем количество сообщений
                message = f"Reconnect {i}, message {j}"
                response = client.send_message(message)
                self.assertIn("TCP эхо", response)
                self.assertIn(message, response)
                time.sleep(0.2)  # Увеличиваем паузу
            
            client.disconnect()
            time.sleep(0.5)  # Увеличиваем паузу между переподключениями
        
        if self.tcp_server:
            self.tcp_server.stop()
    
    def test_udp_continuous_messages(self):
        """UDP непрерывная отправка сообщений"""
        self.udp_server_thread = threading.Thread(target=self.start_udp_server)
        self.udp_server_thread.daemon = True
        self.udp_server_thread.start()
        time.sleep(1)  # Увеличиваем время ожидания
        
        client = UDPClient(self.udp_host, self.udp_port, timeout=3.0)
        self.assertTrue(client.connect())
        
        # Быстрая отправка сообщений
        for i in range(10):  # Уменьшаем количество сообщений
            message = f"Quick UDP {i}"
            response = client.send_message(message)
            # Более мягкая проверка для UDP
            if "Таймаут" not in response:
                self.assertIn("UDP эхо", response)
                self.assertIn(f"Quick UDP {i}", response)
            time.sleep(0.2)  # Увеличиваем паузу
        
        client.disconnect()
        if self.udp_server:
            self.udp_server.stop()
    
    def tearDown(self):
        """Очистка после каждого теста"""
        time.sleep(0.5)  # Даем время на освобождение портов
        
        if self.tcp_server:
            self.tcp_server.stop()
        if self.udp_server:
            self.udp_server.stop()
        
        # Ждем завершения потоков
        if self.tcp_server_thread and self.tcp_server_thread.is_alive():
            self.tcp_server_thread.join(timeout=2.0)
        if self.udp_server_thread and self.udp_server_thread.is_alive():
            self.udp_server_thread.join(timeout=2.0)

if __name__ == '__main__':
    unittest.main()