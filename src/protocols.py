import struct
from typing import Tuple

class TCPProtocol:
    """Протокол для работы с TCP сообщениями"""
    
    @staticmethod
    def prepare_message(data: bytes) -> bytes:
        """Подготавливает сообщение с заголовком длины"""
        length = len(data)
        header = struct.pack('!I', length)  # 4-байтовый заголовок с длиной
        return header + data
    
    @staticmethod
    def receive_message(sock, buffer_size: int = 4096) -> Tuple[bool, bytes]:
        """Принимает сообщение с заголовком длины"""
        try:
            # Получаем заголовок с длиной
            header = sock.recv(4)
            if not header:
                return False, b""
            
            message_length = struct.unpack('!I', header)[0]
            
            # Получаем данные
            received_data = b""
            while len(received_data) < message_length:
                remaining = message_length - len(received_data)
                chunk = sock.recv(min(buffer_size, remaining))
                if not chunk:
                    return False, b""
                received_data += chunk
            
            return True, received_data
            
        except (ConnectionResetError, struct.error):
            return False, b""

class UDPProtocol:
    """Протокол для работы с UDP сообщениями"""
    
    @staticmethod
    def create_message(data: str) -> bytes:
        """Создает UDP сообщение"""
        return data.encode('utf-8')
    
    @staticmethod
    def parse_message(data: bytes) -> str:
        """Парсит UDP сообщение"""
        return data.decode('utf-8')