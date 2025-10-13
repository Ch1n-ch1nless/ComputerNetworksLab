import socket
import time
from src.protocols import UDPProtocol

class UDPServer:
    def __init__(self, host: str = 'localhost', port: int = 8889, buffer_size: int = 4096):
        self.host = host
        self.port = port
        self.buffer_size = buffer_size
        self.running = False
        self.socket = None
        
    def start(self):
        """Запускает UDP сервер"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.settimeout(1.0)  # Таймаут для recvfrom
            self.socket.bind((self.host, self.port))
            
            self.running = True
            print(f"UDP сервер запущен на {self.host}:{self.port}")
            
            while self.running:
                try:
                    data, addr = self.socket.recvfrom(self.buffer_size)
                    message = UDPProtocol.parse_message(data)
                    print(f"UDP от {addr}: {message}")
                    
                    # Эхо-ответ
                    response = f"UDP эхо: {message}"
                    self.socket.sendto(UDPProtocol.create_message(response), addr)
                    
                except socket.timeout:
                    continue  # Таймаут - проверяем running
                except OSError as e:
                    if self.running:
                        print(f"Ошибка UDP: {e}")
                    break
                except Exception as e:
                    print(f"Неожиданная ошибка UDP: {e}")
                    break
                    
        except KeyboardInterrupt:
            print("\nОстановка сервера...")
        except Exception as e:
            print(f"Ошибка запуска UDP сервера: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """Останавливает сервер"""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass