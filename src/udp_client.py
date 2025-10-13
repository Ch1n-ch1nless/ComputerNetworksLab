import socket
from src.protocols import UDPProtocol  # Абсолютный импорт

class UDPClient:
    def __init__(self, host: str = 'localhost', port: int = 8889, buffer_size: int = 4096, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.timeout = timeout
        self.socket = None
        
    def connect(self):
        """Создает UDP сокет"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(self.timeout)
            print(f"UDP клиент готов к отправке на {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Ошибка создания сокета: {e}")
            return False
    
    def send_message(self, message: str) -> str:
        """Отправляет сообщение и возвращает ответ"""
        if not self.socket:
            return "Сокет не создан"
        
        try:
            # Отправка сообщения
            self.socket.sendto(UDPProtocol.create_message(message), (self.host, self.port))
            
            # Получение ответа
            data, addr = self.socket.recvfrom(self.buffer_size)
            return UDPProtocol.parse_message(data)
            
        except socket.timeout:
            return "Таймаут ожидания ответа"
        except Exception as e:
            return f"Ошибка отправки: {e}"
    
    def disconnect(self):
        """Закрывает сокет"""
        if self.socket:
            self.socket.close()
            self.socket = None