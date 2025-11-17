import socket
import ssl
import threading
import time
import os
from typing import Optional
from src.protocols import TCPProtocol

class TLSTCPServer:
    def __init__(
        self, 
        host: str = 'localhost', 
        port: int = 8888, 
        buffer_size: int = 4096, 
        max_retries: int = 3,
        certfile: Optional[str] = None,
        keyfile: Optional[str] = None,
        ca_certs: Optional[str] = None
    ):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.max_retries = max_retries
        self.certfile = certfile
        self.keyfile = keyfile
        self.ca_certs = ca_certs
        self.running = False
        self.server_socket = None
        self.ssl_context = None
        self.client_threads = []
        
    def _setup_ssl_context(self):
        """Настраивает SSL контекст для сервера"""
        self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        
        if self.certfile and self.keyfile:
            self.ssl_context.load_cert_chain(certfile=self.certfile, keyfile=self.keyfile)
            print(f"Загружены сертификаты: {self.certfile}, {self.keyfile}")
        else:
            # Генерируем самоподписанный сертификат (для тестирования)
            print("Предупреждение: используются самоподписанные сертификаты")
            self.ssl_context.check_hostname = False
            self.ssl_context.verify_mode = ssl.CERT_NONE
            
        if self.ca_certs:
            self.ssl_context.load_verify_locations(cafile=self.ca_certs)
            self.ssl_context.verify_mode = ssl.CERT_REQUIRED
        
    def start(self):
        """Запускает TLS TCP сервер"""
        self._setup_ssl_context()
        
        for attempt in range(self.max_retries):
            try:
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server_socket.bind((self.host, self.port))
                self.server_socket.settimeout(1.0)
                self.server_socket.listen(5)
                
                self.running = True
                print(f"TLS TCP сервер запущен на {self.host}:{self.port}")
                print(f"SSL Key Log File: {os.environ.get('SSLKEYLOGFILE', 'Не установлен')}")
                break
                
            except OSError as e:
                if attempt < self.max_retries - 1:
                    print(f"Попытка {attempt + 1} не удалась: {e}. Пробуем снова...")
                    time.sleep(1)
                    self.port += 1
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
                    
                    # Обертываем сокет в SSL
                    try:
                        ssl_client_socket = self.ssl_context.wrap_socket(
                            client_socket, 
                            server_side=True
                        )
                        print(f"TLS соединение установлено с {addr}")
                    except ssl.SSLError as e:
                        print(f"Ошибка SSL handshake с {addr}: {e}")
                        client_socket.close()
                        continue
                    
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(ssl_client_socket, addr)
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
    
    def _handle_client(self, client_socket: ssl.SSLSocket, addr: tuple):
        """Обрабатывает подключение TLS TCP клиента"""
        try:
            while self.running:
                success, data = TCPProtocol.receive_message(client_socket, self.buffer_size)
                if not success or not data:
                    break
                
                message = data.decode('utf-8')
                print(f"TLS TCP от {addr}: {message[:100]}..." if len(message) > 100 else f"TLS TCP от {addr}: {message}")
                
                response = f"TLS TCP эхо: {message}"
                response_data = TCPProtocol.prepare_message(response.encode('utf-8'))
                client_socket.sendall(response_data)
                
        except ssl.SSLError as e:
            print(f"SSL ошибка с клиентом {addr}: {e}")
        except ConnectionResetError:
            print(f"Клиент {addr} отключился")
        except Exception as e:
            if self.running:
                print(f"Ошибка с клиентом {addr}: {e}")
        finally:
            try:
                client_socket.close()
                print(f"TLS соединение с {addr} закрыто")
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