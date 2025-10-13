#!/usr/bin/env python3
"""
Скрипт запуска всех тестов
"""

import subprocess
import sys
import os
import time
import random

def run_test(test_file, test_name):
    """Запускает отдельный тест"""
    print(f"\n{'='*60}")
    print(f"Запуск теста: {test_name}")
    print(f"{'='*60}")
    
    start_time = time.time()
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            test_file, '-v', '--tb=short', '--disable-warnings'
        ], cwd=os.path.dirname(__file__), timeout=60, capture_output=True, text=True)
        
        duration = time.time() - start_time
        
        # Выводим вывод теста
        if result.stdout:
            print("Вывод теста:")
            print(result.stdout)
        
        if result.stderr:
            print("Ошибки теста:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"[PASS] {test_name} - пройден ({duration:.2f}с)")
            return True
        else:
            print(f"[FAIL] {test_name} - не пройден ({duration:.2f}с)")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"[TIME] {test_name} - таймаут")
        return False
    except Exception as e:
        print(f"[ERROR] {test_name} - ошибка: {e}")
        return False

def main():
    """Запускает все тесты последовательно"""
    print("Запуск тестов сетевого приложения")
    print("Тестирование TCP/UDP клиент-серверного приложения")
    
    test_suite = [
        ('tests/test_1_basic.py', 'Базовое подключение и обмен сообщениями'),
        ('tests/test_2_large_msg.py', 'Отправка больших сообщений (> MTU)'),
        ('tests/test_3_netcat.py', 'Совместимость с netcat'),
        ('tests/test_4_stability.py', 'Стабильность при долгой работе')
    ]
    
    results = []
    for test_file, test_name in test_suite:
        success = run_test(test_file, test_name)
        results.append((test_name, success))
        time.sleep(3)  # Увеличиваем паузу между тестами до 3 секунд
    
    # Сводка результатов
    print(f"\n{'='*60}")
    print("СВОДКА РЕЗУЛЬТАТОВ")
    print(f"{'='*60}")
    
    passed = 0
    for test_name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\nИтого: {passed}/{len(results)} тестов пройдено")
    
    if passed == len(results):
        print("Все тесты успешно пройдены!")
        return 0
    else:
        print("Некоторые тесты не пройдены")
        return 1

if __name__ == '__main__':
    # Добавляем случайный seed для портов
    random.seed()
    sys.exit(main())