import socket
from src.protocols import TCPProtocol  # Абсолютный импорт

class TCPClient:
    def __init__(self, host: str = 'localhost', port: int = 8888, buffer_size: int = 4096):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.socket = None
        
    def connect(self):
        """Подключается к TCP серверу"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            print(f"Подключен к TCP серверу {self.host}:{self.port}")
            return True
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False
    
    def send_message(self, message: str) -> str:
        """Отправляет сообщение и возвращает ответ"""
        if not self.socket:
            return "Не подключен к серверу"
        
        try:
            # Отправка сообщения
            message_data = TCPProtocol.prepare_message(message.encode('utf-8'))
            self.socket.sendall(message_data)
            
            # Получение ответа
            success, response_data = TCPProtocol.receive_message(self.socket, self.buffer_size)
            if success and response_data:
                return response_data.decode('utf-8')
            else:
                return "Сервер отключился"
                
        except Exception as e:
            return f"Ошибка отправки: {e}"
    
    def disconnect(self):
        """Отключается от сервера"""
        if self.socket:
            self.socket.close()
            self.socket = None