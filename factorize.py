"""Напишіть реалізацію функції factorize, яка приймає список чисел та повертає список чисел, на які числа з вхідного списку поділяються без залишку.
Реалізуйте синхронну версію та виміряйте час виконання.
Потім покращіть продуктивність вашої функції, реалізувавши використання кількох ядер процесора для паралельних обчислень і замірьте час виконання знову. 
Для визначення кількості ядер на машині використовуйте функцію cpu_count() з пакета multiprocessing"""

from multiprocessing import Process, RLock as PRLock
from multiprocessing.dummy import Pool  # Thread с оболонкою Process
from threading import Thread, RLock as TRlock
from time import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("factorize")


def factorize(num, filename, lock):
    divisors = [i for i in range(1, num + 1) if num % i == 0]
    logger.info(f"{num} == {divisors}")
    with lock:
        with open(filename, "a") as f:
            f.write(f"{num} == {divisors}\n")


# Синхронна версія, треди
def synchronous_version(numbers):
    th_filename = "th_factorize.txt"
    th_lock = TRlock()
    threads = []
    for num in numbers:
        thread = Thread(target=factorize, args=(num, th_filename, th_lock))
        threads.append(thread)

    timer = time()
    [thread.start() for thread in threads]
    [thread.join() for thread in threads]
    elapsed_time = round(time() - timer, 4)  # Обчислюємо час, що пройшов
    done_threads = [
        num + 1 for num in numbers if not thread.is_alive()
    ]  # Знаходимо завершені потоки
    print(f"Done by {len(done_threads)} threads: {elapsed_time} seconds")


# Процеси
def processs_version(numbers):
    pr_filename = "pr_factorize.txt"
    p_lock = PRLock()
    processes = []
    for num in numbers:
        process = Process(target=factorize, args=(num, pr_filename, p_lock))
        processes.append(process)

    timer = time()
    [process.start() for process in processes]
    [process.join() for process in processes]
    [process.close() for process in processes]
    elapsed_time = round(time() - timer, 4)  # Обчислюємо час, що пройшов
    done_process = [num + 1 for num in numbers]
    print(f"Done by {len(done_process)} processes: {elapsed_time} seconds")


# 1 процес
def one_process_version(numbers):
    lock = TRlock()
    timer = time()
    for num in numbers:
        factorize(num, "factorize.txt", lock)
    elapsed_time = round(time() - timer, 4)
    print(f"Done by 1 main processes: {elapsed_time} seconds")


# Пул - треди в оболонці процесів
def pool_version(numbers):
    pl_filename = "pl_factorize.txt"
    timer = time()
    th_lock = TRlock()
    args_list = [(num, pl_filename, th_lock) for num in numbers]
    with Pool(len(numbers)) as pool:
        results = pool.starmap(factorize, args_list)
    elapsed_time = round(time() - timer, 4)
    done_process = [num + 1 for num in numbers]
    print(f"Done by {len(done_process)} processes: {elapsed_time} seconds")


if __name__ == "__main__":
    numbers = [128, 255, 99999, 10651060]
    # Синхронна версія, треди
    synchronous_version(numbers)

    # Процеси
    processs_version(numbers)

    # 1 процес
    one_process_version(numbers)

    # Пул - треди в оболонці процесів
    pool_version(numbers)
