#!/usr/bin/env python3
"""
Скрипт для генерации тестовых сертификатов для TLS
"""
import os
import subprocess

def generate_certs_openssl():
    """Генерирует сертификаты используя OpenSSL"""
    os.makedirs("certs", exist_ok=True)
    
    print("Генерация приватного ключа сервера...")
    subprocess.run([
        "openssl", "genrsa", "-out", "certs/server.key", "2048"
    ], check=True)
    
    print("Генерация самоподписанного сертификата сервера...")
    subprocess.run([
        "openssl", "req", "-new", "-x509", "-sha256",
        "-key", "certs/server.key",
        "-out", "certs/server.crt",
        "-days", "365",
        "-subj", "/C=RU/ST=Moscow/L=Moscow/O=MIPT/CN=localhost"
    ], check=True)
    
    print("Сертификаты успешно сгенерированы в папке certs/")
    print("server.crt - сертификат сервера")
    print("server.key - приватный ключ сервера")

if __name__ == "__main__":
    try:
        generate_certs_openssl()
    except subprocess.CalledProcessError as e:
        print(f"Ошибка генерации сертификатов: {e}")
    except FileNotFoundError:
        print("OpenSSL не найден. Установите OpenSSL или используйте встроенную генерацию при запуске сервера")