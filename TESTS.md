# Тестирование моего приложения

## Структура тестов
```
tests/
├── __init__.py         # Нужно для сборки проекта :)
├── test_1_basic.py     # Базовое подключение и обмен сообщениями
├── test_2_large_msg.py # Отправка больших сообщений (> MTU) 
├── test_3_netcat.py    # Совместимость с netcat
├── test_4_stability.py # Стабильность при долгой работе 
```

## Запуск тестов
```bash
python3 run_tests.py
```

## Запуск тестов с pytest
```bash
# Все тесты
python3 -m pytest tests/ -v

# Конкретный тест
python3 -m pytest tests/test_1_basic.py -v
```

## Описание каждого теста

1) `test_1_basic.py`

    Запуск:
    ```bash
    python3 -m pytest tests/test_1_basic.py -v
    ```


    Данный тест проверяет:
    * Установка TCP соединения
    * Обмен сообщениями TCP
    * Обмен сообщениями UDP
    * Обработка ошибок подключения

2) `test_2_large_msg.py`

    Запуск:
    ```bash
    python3 -m pytest tests/test_2_large_msg.py -v
    ```

    Данный тест проверяет:
    * Отправка сообщений 20KB через TCP
    * Отправка сообщений 50KB через TCP (больше MTU)
    * Отправка сообщений разных размеров

3) Совместимость с netcat

    Запуск:
    ```bash
    python3 -m pytest tests/test_3_netcat.py -v
    ```

    Данный тест проверяет:
    * Работа TCP сервера с raw sockets (имитация netcat)
    * Работа UDP сервера с raw sockets
    * Обработка сообщений без протокола

4) Стабильность при долгой работе

    Запуск:
    ```bash
    python3 -m pytest tests/test_4_stability.py -v
    ```

    Данный тест проверяет:
    * Длительная работа TCP соединения
    * Длительная работа UDP соединения
    * Многократные переподключения TCP
    * Непрерывная отправка UDP сообщений

## Тестирование с `netcat`

```bash
# Запуск сервера
python3 main.py --mode tcp_server --port 8888

# В другом терминале - подключение через netcat
nc localhost 8888

# Отправка большого сообщения
dd if=/dev/zero bs=1024 count=20 | tr '\0' 'A' | nc localhost 8888
```