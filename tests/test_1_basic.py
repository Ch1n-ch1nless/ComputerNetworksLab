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

class TestBasicConnection(unittest.TestCase):
    """Test 1: Базовое подключение и обмен сообщениями"""
    
    def setUp(self):
        self.tcp_host = 'localhost'
        self.tcp_port = 9001
        self.udp_host = 'localhost'
        self.udp_port = 9002
        
    def test_tcp_basic_echo(self):
        """TCP базовый эхо-тест"""
        server = TCPServer(self.tcp_host, self.tcp_port)
        server_thread = threading.Thread(target=server.start)
        server_thread.daemon = True
        server_thread.start()
        time.sleep(0.5)
        
        client = TCPClient(self.tcp_host, self.tcp_port)
        self.assertTrue(client.connect())
        
        test_messages = ["Hello", "Test message", "Another message"]
        for msg in test_messages:
            response = client.send_message(msg)
            self.assertIn("TCP эхо", response)
            self.assertIn(msg, response)
        
        client.disconnect()
        server.stop()
    
    def test_udp_basic_echo(self):
        """UDP базовый эхо-тест"""
        server = UDPServer(self.udp_host, self.udp_port)
        server_thread = threading.Thread(target=server.start)
        server_thread.daemon = True
        server_thread.start()
        time.sleep(0.5)
        
        client = UDPClient(self.udp_host, self.udp_port, timeout=2.0)
        self.assertTrue(client.connect())
        
        test_messages = ["UDP test", "Quick brown fox", "Final message"]
        for msg in test_messages:
            response = client.send_message(msg)
            self.assertIn("UDP эхо", response)
            self.assertIn(msg, response)
        
        client.disconnect()
        server.stop()
    
    def test_tcp_connection_refused(self):
        """TCP подключение к несуществующему серверу"""
        client = TCPClient(self.tcp_host, 9999)  # Несуществующий порт
        self.assertFalse(client.connect())

if __name__ == '__main__':
    unittest.main()