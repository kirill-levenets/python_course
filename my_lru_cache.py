'''
https://github.com/python/cpython/blob/3.6/Lib/functools.py#L485

LRU (least recently used) — это алгоритм, при котором вытесняются значения, которые 
дольше всего не запрашивались. Соответственно, необходимо хранить время 
последнего запроса к значению. И как только число закэшированных значений превосходит N 
необходимо вытеснить из кеша значение, которое дольше всего не запрашивалось.

Задача - 1
Создать декоратор lru_cache (подобный тому который реализован в Python).

Задача - 2
Ваш lru_cache декоратор должен иметь служебный метод cache_info  - статистика использования 
вашего кеша (например: сколько раз вычислялась ваша функция, а сколько раз значение 
было взято из кеша, сколько места свободно в кэше, время жизни кэша)

Задача - 3
Ваш lru_cache декоратор должен иметь служебный метод cache_clear - очищает кэш


Пример обращения к служебному методу декоратора


def decorator(my_func):
     def wrapper():
           my_func()
     def cache_clear():
           pass
     wrapper.cache_clear = cache_clear
     return wrapper
@decorator
def my_func():
      pass
my_func.cache_clear()

{
 'count_used': 3,
 'time_created': datetime.datetime('2019-05-30 12:34:00+000'),
 'time_used': datetime.datetime('2019-05-30 12:35:11+000'),
 'func_value': func(*args, **kwargs)
}

'''

import datetime
from collections import OrderedDict
import pprint
import time


def make_key(*args, **kwargs):
    key = args
    for item in sorted(kwargs.items()):
        key += item
    return key


def my_lru_cache(max_size, max_ttl):
    def extended_cache(func):
        cache = OrderedDict()

        def wrapper(*args, **kwargs):
            current_time = datetime.datetime.now()

            def get_new():
                return {
                    'func_value': func(*args, **kwargs),
                    'count_used': 0,
                    'time_created': current_time,
                    'time_used': current_time
                }

            cache_key = make_key(*args, **kwargs)
            val = None
            if cache_key in cache:
                val = cache.pop(cache_key)
                tdelta = current_time - val['time_created']
                if tdelta.total_seconds() > max_ttl:
                    val = get_new()
                else:
                    val['time_used'] = current_time
                    val['count_used'] += 1
            else:
                val = get_new()
                if len(cache) + 1 > max_size:
                    cache.popitem(last=False)  # find oldest

            cache[cache_key] = val
            return val['func_value']

        def cache_clear():
            cache.clear()

        def cache_info():
            print('cache free places: {]'.format(max_size - len(cache)))
            pprint.pprint(cache)

        wrapper.cache_clear = cache_clear
        wrapper.cache_info = cache_info

        return wrapper
    return extended_cache


@my_lru_cache(2, 1)
def calc_sum(n, step=1):
    sm = 0
    for i in range(1, n + 1, step):
        sm += i
    return sm


for i in [10, 20] * 4:
    print('calc_sum for {} is:\n{}'.format(i, calc_sum(i, step=2)))
    calc_sum.cache_info()
    time.sleep(0.1)

