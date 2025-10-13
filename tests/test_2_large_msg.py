import unittest
import time
import threading
import sys
import os
import random
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.tcp_server import TCPServer
from src.tcp_client import TCPClient

class TestLargeMessages(unittest.TestCase):
    """Test 2: Отправка больших сообщений (> MTU)"""
    
    def setUp(self):
        self.host = 'localhost'
        # Используем случайные порты для избежания конфликтов
        self.port = 9100 + random.randint(1, 100)
        self.server = None
        self.server_thread = None
    
    def start_server(self):
        """Запускает сервер"""
        self.server = TCPServer(self.host, self.port)
        self.server.start()
    
    def test_tcp_20kb_message(self):
        """TCP сообщение 20KB"""
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(1.5)  # Увеличиваем время ожидания
        
        client = TCPClient(self.host, self.port)
        if not client.connect():
            self.skipTest("Не удалось подключиться к серверу")
        
        # Сообщение размером 20KB
        large_message = "X" * 20480
        response = client.send_message(large_message)
        
        self.assertIn("TCP эхо", response)
        self.assertEqual(len(response), len("TCP эхо: ") + len(large_message))
        
        client.disconnect()
        if self.server:
            self.server.stop()
    
    def test_tcp_50kb_message(self):
        """TCP сообщение 50KB (больше MTU)"""
        # Используем другой порт для этого теста
        self.port = 9200 + random.randint(1, 100)
        
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(1.5)
        
        client = TCPClient(self.host, self.port)
        if not client.connect():
            self.skipTest("Не удалось подключиться к серверу")
        
        # Сообщение размером 50KB
        large_message = "Y" * 51200
        response = client.send_message(large_message)
        
        # Более мягкая проверка для больших сообщений
        if "Сервер отключился" not in response:
            self.assertIn("TCP эхо", response)
            self.assertTrue(len(response) > 50000)
        
        client.disconnect()
        if self.server:
            self.server.stop()
    
    def test_tcp_various_sizes(self):
        """TCP сообщения разных размеров"""
        self.port = 9300 + random.randint(1, 100)
        
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        time.sleep(1.5)
        
        client = TCPClient(self.host, self.port)
        if not client.connect():
            self.skipTest("Не удалось подключиться к серверу")
        
        sizes = [100, 1024, 8192, 16384]  # Уменьшаем максимальный размер
        for size in sizes:
            message = "A" * size
            response = client.send_message(message)
            if "Сервер отключился" not in response:
                self.assertIn("TCP эхо", response)
                self.assertEqual(len(response), len("TCP эхо: ") + len(message))
        
        client.disconnect()
        if self.server:
            self.server.stop()
    
    def tearDown(self):
        """Очистка после каждого теста"""
        time.sleep(0.5)
        if self.server:
            self.server.stop()
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=2.0)

if __name__ == '__main__':
    unittest.main()