import socket
import ssl
import os
from typing import Optional
from src.protocols import TCPProtocol

class TLSTCPClient:
    def __init__(
        self, 
        host: str = 'localhost', 
        port: int = 8888, 
        buffer_size: int = 4096,
        ca_certs: Optional[str] = None,
        certfile: Optional[str] = None,
        keyfile: Optional[str] = None
    ):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.ca_certs = ca_certs
        self.certfile = certfile
        self.keyfile = keyfile
        self.socket = None
        self.ssl_socket = None
        
    def _setup_ssl_context(self) -> ssl.SSLContext:
        """Настраивает SSL контекст для клиента"""
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        
        if self.ca_certs:
            context.load_verify_locations(cafile=self.ca_certs)
            context.verify_mode = ssl.CERT_REQUIRED
        else:
            # Для самоподписанных сертификатов отключаем проверку
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
        if self.certfile and self.keyfile:
            context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
            
        return context
    
    def connect(self) -> bool:
        """Подключается к TLS TCP серверу"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            ssl_context = self._setup_ssl_context()
            self.ssl_socket = ssl_context.wrap_socket(
                self.socket, 
                server_hostname=self.host
            )
            
            self.ssl_socket.connect((self.host, self.port))
            print(f"Подключен к TLS TCP серверу {self.host}:{self.port}")
            print(f"SSL версия: {self.ssl_socket.version()}")
            print(f"SSL Key Log File: {os.environ.get('SSLKEYLOGFILE', 'Не установлен')}")
            return True
            
        except ssl.SSLError as e:
            print(f"SSL ошибка подключения: {e}")
            return False
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            return False
    
    def send_message(self, message: str) -> str:
        """Отправляет сообщение и возвращает ответ"""
        if not self.ssl_socket:
            return "Не подключен к серверу"
        
        try:
            # Отправка сообщения
            message_data = TCPProtocol.prepare_message(message.encode('utf-8'))
            self.ssl_socket.sendall(message_data)
            
            # Получение ответа
            success, response_data = TCPProtocol.receive_message(self.ssl_socket, self.buffer_size)
            if success and response_data:
                return response_data.decode('utf-8')
            else:
                return "Сервер отключился"
                
        except ssl.SSLError as e:
            return f"SSL ошибка отправки: {e}"
        except Exception as e:
            return f"Ошибка отправки: {e}"
    
    def disconnect(self):
        """Отключается от сервера"""
        if self.ssl_socket:
            self.ssl_socket.close()
            self.ssl_socket = None
        if self.socket:
            self.socket.close()
            self.socket = None