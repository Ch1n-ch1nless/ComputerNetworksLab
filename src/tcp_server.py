import socket
import threading
from protocols import TCPProtocol

class TCPServer:
    def __init__(self, host: str = 'localhost', port: int = 8888, buffer_size: int = 4096):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.running = False
        self.server_socket = None
        
    def start(self):
        """Запускает TCP сервер"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        self.running = True
        print(f"TCP сервер запущен на {self.host}:{self.port}")
        
        try:
            while self.running:
                client_socket, addr = self.server_socket.accept()
                print(f"Подключен клиент: {addr}")

                client_thread = threading.Thread(
                    target=self._handle_client,
                    args=(client_socket, addr)
                )
                client_thread.daemon = True
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\nОстановка сервера...")
        finally:
            self.stop()
    
    def _handle_client(self, client_socket: socket.socket, addr: tuple):
        """Обрабатывает подключение TCP клиента"""
        try:
            while True:
                success, data = TCPProtocol.receive_message(client_socket, self.buffer_size)
                if not success or not data:
                    break
                
                message = data.decode('utf-8')
                print(f"TCP от {addr}: {message[:100]}..." if len(message) > 100 else f"TCP от {addr}: {message}")

                response = f"TCP эхо: {message}"
                response_data = TCPProtocol.prepare_message(response.encode('utf-8'))
                client_socket.sendall(response_data)
                
        except ConnectionResetError:
            print(f"Клиент {addr} отключился")
        except Exception as e:
            print(f"Ошибка с клиентом {addr}: {e}")
        finally:
            client_socket.close()
            print(f"Соединение с {addr} закрыто")
    
    def stop(self):
        """Останавливает сервер"""
        self.running = False
        if self.server_socket:
            self.server_socket.close()