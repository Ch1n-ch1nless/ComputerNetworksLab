# Сетевое приложение TCP/UDP

Моя реализация клиент-сервер приложение, реализующое общение через протоколы TCP и UDP.

## Структура проекта
```
my_dumps/
├── tcp_protocol_dump.pcap # Запись общения по протоколу TCP
├── udp_protocol_dump.pcap # Запись общения по протоколу UDP
src/
├── __init__.py         # Нужно для сборки проекта :)
├── protocols.py        # Протоколы для TCP/UDP сообщений
├── tcp_server.py       # TCP сервер
├── tcp_client.py       # TCP клиент
├── udp_server.py       # UDP сервер
└── udp_client.py       # UDP клиент
tests/
├── __init__.py         # Нужно для сборки проекта :)
├── test_1_basic.py     # Базовое подключение и обмен сообщениями
├── test_2_large_msg.py # Отправка больших сообщений (> MTU) 
├── test_3_netcat.py    # Совместимость с netcat
├── test_4_stability.py # Стабильность при долгой работе 
main.py                 # Основной скрипт для запуска
run_tests.py            # Скрипт для прогонки тестов
```

## Требования

* Python 3.6+
* Стандартные библиотеки (socket, threading, struct)
* Для тестирования pytest
* Для записи трафика Wireshark

## Установка и настройка
```bash
git clone https://github.com/Ch1n-ch1nless/ComputerNetworksLab.git
cd ComputerNetworksLab

python3 -m venv venv
source venv/bin/activate

pip install pytest

sudo apt update
sudo apt install wireshark
```

## Проверка установки
```bash
# Проверка Python
python3 --version

# Проверка установки в виртуальном окружении
pip list

# Проверка работы приложения
python3 main.py --mode tcp_server --port 8888
# Ожидаемый вывод:
# > TCP сервер запущен на localhost:8888
# >

```

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
python3 main.py --mode udp_server --host localhost --port 8888
```

### UDP клиент:
```bash
python3 main.py --mode udp_client --host localhost --port 8888
```

## Проведение эксперимента с записью трафика

1) Необходимо запустить 3 окна, в котром прописать следующие команды:
    * Первое окно (Запуск сервера):
    ```bash
    # Для TCP вводим такую команду
    python3 main.py --mode tcp_server --host localhost --port 8888
    # Для UDP нужно поменять аргумент флага --mode, на какой можно увидеть в примерах использований
    ```

    * Второе окно (Запуск клиента):
    ```bash
    # Для TCP вводим такую команду
    python3 main.py --mode tcp_client --host localhost --port 8888
    # Для UDP нужно поменять аргумент флага --mode, на какой можно увидеть в примерах использований
    ```

    * Третье окно (Wireshark для дампа трафика):
    ```bash
    wireshark # Запустить wireshark
    ```

2) Работа в wireshark.
    a) Как только `wireshark` был запущен, в открышемся меню выбираем интерфейс `Loopback: lo`.
    b) Ставим фильтры `tcp.port == 8888` для работы с TCP или `udp.port == 8888` для работы с UDP.
    c) Начинаем запись, в то же время со стороны клиента отправляем какие-нибудь сообщения.  P.S. сообщения надо писать на латинице, так как в записи wireshark кириллица не видна.
    d) Остановливаем запись.

Я провел аналогичный эксперимент и все сови записи положил в папку `my_dumps`.

## Тестирование кода

Прочитайте в [TESTS.md](TESTS.md)

## Описание протокола

Мини описание находится в [PROTOCOL.md](PROTOCOL.md)