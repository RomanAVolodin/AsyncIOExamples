import asyncio
import concurrent.futures
import multiprocessing
import random
import threading
import time
from asyncio import Future

import requests


async def one(title: str = ''):
    for i in range(4):
        print(f'create one {title=} {i=}')
        await asyncio.sleep(1)
        print(f'stop one {title=} {i=}')


async def two():
    print('create two')
    await asyncio.sleep(2)
    print('stop two')


async def three():
    print('create three')
    await asyncio.sleep(3)
    print('stop three')


async def main():
    asyncio.create_task(one('not_awaited'))
    t1 = asyncio.create_task(one())
    t2 = asyncio.create_task(two())
    t3 = asyncio.create_task(three())

    pending_tasks = asyncio.all_tasks()
    print(pending_tasks)

    await asyncio.gather(t1, t2, t3, return_exceptions=True)

    # pending_tasks = asyncio.all_tasks()
    # print('again', pending_tasks)
    # await asyncio.gather(*pending_tasks, return_exceptions=True)  # в том числе и себя же зацикливает async def main()


def show_identities(name: str):
    print(
        f'Функция: {name} работает в процессе с id: {multiprocessing.current_process().ident}, '
        f'в потоке с id: {threading.current_thread().ident}'
    )


def fetch_data():
    show_identities('fetch_data')
    response = requests.get('https://yandex.ru/')
    data = response.content
    print(f'{time.ctime()} Получены данные с сайта yandex.ru: ', len(data))


def calculate():
    show_identities('calculate')
    print(f'{time.ctime()} Произведен сложный расчет', sum(i * i for i in range(10 ** 7)))


async def main_next():
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, fetch_data)
        print('custom thread pool', result)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        result = await loop.run_in_executor(executor, calculate)
        print('custom process pool', result)

    thread_executor = concurrent.futures.ThreadPoolExecutor()
    t1 = loop.run_in_executor(thread_executor, fetch_data)

    proc_executor = concurrent.futures.ProcessPoolExecutor()
    t2 = loop.run_in_executor(proc_executor, fetch_data)

    await asyncio.gather(t1, t2)

    thread_executor.shutdown()
    proc_executor.shutdown()


async def delay():
    rand_delay = random.uniform(0.3, 1.9)
    print(f'Сгенерировано число {rand_delay}...')
    await asyncio.sleep(rand_delay)
    print(f'Завершилась корутина {rand_delay}...')
    return rand_delay


async def main_next_next_next():
    tasks = [asyncio.create_task(delay()) for _ in range(5)]
    print('Начало работы...')
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    # done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)

    for task in pending:
        task.cancel()

    completed_task = done.pop()
    print('Результат работы приложения:', completed_task.result())


async def main_next_next():
    my_future = Future()
    print(my_future.done())  # Результат ещё не получен, поэтому Future счиатется невыполненной
    my_future.set_result('Результат')
    print(my_future.done())  # Теперь Future завершена
    print(my_future.result())


if __name__ == '__main__':
    start = time.time()
    asyncio.run(main())
    print(time.time() - start)

    start = time.time()
    asyncio.run(main_next())
    print(time.time() - start)

    print('=======================')
    asyncio.run(main_next_next())

    print('=======================')
    asyncio.run(main_next_next_next())

