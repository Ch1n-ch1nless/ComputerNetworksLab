import socket
import threading
import time
from src.protocols import TCPProtocol

class TCPServer:
    def __init__(self, host: str = 'localhost', port: int = 8888, buffer_size: int = 4096, max_retries: int = 3):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.max_retries = max_retries
        self.running = False
        self.server_socket = None
        self.client_threads = []
        
    def start(self):
        """Запускает TCP сервер"""
        for attempt in range(self.max_retries):
            try:
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server_socket.bind((self.host, self.port))
                self.server_socket.settimeout(1.0)
                self.server_socket.listen(5)
                
                self.running = True
                print(f"TCP сервер запущен на {self.host}:{self.port}")
                break
                
            except OSError as e:
                if attempt < self.max_retries - 1:
                    print(f"Попытка {attempt + 1} не удалась: {e}. Пробуем снова...")
                    time.sleep(1)
                    self.port += 1  # Пробуем следующий порт
                else:
                    print(f"Ошибка запуска сервера после {self.max_retries} попыток: {e}")
                    return
        
        if not self.running:
            return
            
        try:
            while self.running:
                try:
                    client_socket, addr = self.server_socket.accept()
                    print(f"Подключен клиент: {addr}")
                    
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, addr)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    self.client_threads.append(client_thread)
                    
                except socket.timeout:
                    continue
                except OSError as e:
                    if self.running:
                        print(f"Ошибка accept: {e}")
                    break
                except Exception as e:
                    print(f"Неожиданная ошибка: {e}")
                    break
                    
        except KeyboardInterrupt:
            print("\nОстановка сервера...")
        except Exception as e:
            print(f"Ошибка в основном цикле сервера: {e}")
        finally:
            self.stop()
    
    def _handle_client(self, client_socket: socket.socket, addr: tuple):
        """Обрабатывает подключение TCP клиента"""
        try:
            while self.running:
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
            if self.running:
                print(f"Ошибка с клиентом {addr}: {e}")
        finally:
            try:
                client_socket.close()
                print(f"Соединение с {addr} закрыто")
            except:
                pass
    
    def stop(self):
        """Останавливает сервер"""
        self.running = False
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass