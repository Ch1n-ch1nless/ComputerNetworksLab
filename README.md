# Сетевое приложение TCP/UDP

Простое сетевое приложение, реализующее клиент и сервер для протоколов TCP и UDP.

## Структура проекта
```
src/
├── protocols.py  #Протоколы для TCP/UDP сообщений
├── tcp_server.py  #TCP сервер
├── tcp_client.py  #TCP клиент
├── udp_server.py  #UDP сервер
└── udp_client.py  #UDP клиент
main.py  #Основной скрипт для запуска
```

## Требования

* Python 3.6+
* Стандартные библиотеки (socket, threading, struct)

## Использование

### TCP сервер:
```bash
python3 main.py --mode tcp_server --host localhost --port 8888
```

### TCP клиент:
```bash
python3 main.py --mode tcp_client --host localhost --port 8888
```

### UDP сервер:
```bash
python3 main.py --mode udp_server --host localhost --udp-port 8889
```

### UDP клиент:
```bash
python3 main.py --mode udp_client --host localhost --udp-port 8889
```

## Проведение эксперимента с записью трафика
```

```

## Тестирование кода

### TCP
```
# Сервер
python3 main.py --mode tcp_server --port 8888

# Клиент через netcat  
dd if=/dev/zero bs=1024 count=20 | tr '\0' 'A' > large_msg.txt
nc localhost 8888 < large_msg.txt
```

### UDP
```
# Сервер
python3 main.py --mode udp_server --udp-port 8889

# Клиент через netcat
nc -u localhost 8889
```

## Описание протокола

#### TCP Protocol:
* Сообщения предваряются 4-байтовым заголовком с длиной
* Поддержка сообщений больше MTU
* Гарантированная доставка

#### UDP Protocol:
* Простые датаграммы
* Быстрая доставка
* Ответ на каждое сообщение

