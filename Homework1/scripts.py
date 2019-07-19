"""
1. Написать функцию host_ping(), в которой с помощью утилиты ping будет
проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел должен
быть представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять их доступность
с выводом соответствующего сообщения («Узел доступен»,
«Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться
с помощью функции ip_address().

2. Написать функцию host_range_ping() для перебора ip-адресов из
заданного диапазона.
Меняться должен только последний октет каждого адреса. По результатам
проверки должно выводиться соответствующее сообщение.

3. Написать функцию host_range_ping_tab(), возможности которой основаны
на функции из примера 2.
Но в данном случае результат должен быть итоговым по всем ip-адресам,
представленным в табличном формате
(использовать модуль tabulate). Таблица должна состоять из двух колонок
и выглядеть примерно так:

Reachable
10.0.0.1
10.0.0.2

Unreachable
10.0.0.3
10.0.0.4
"""

import subprocess
import ipaddress
import socket
import os
from tabulate import tabulate


def ip_address(host):
    try:
        if type(host) in (str, int):
            check = str(ipaddress.ip_address(host))
        else:
            return False
    except ValueError:
        try:
            check = socket.gethostbyname(host)
        except socket.gaierror:
            return False
    return check


def host_ping(lst):
    result = []
    for host in lst:
        verified_ip = ip_address(host)
        if verified_ip:
            with open(os.devnull, 'w') as DNULL:
                response = subprocess.call(
                    ["ping", "-n", "2", "-w", "2", verified_ip], stdout=DNULL
                )
            if response == 0:
                result.append(('Доступен', str(host), f'[{verified_ip}]'))
                # print(f'Доступен    {host} [{verified_ip}]')
                continue
        result.append(('Не доступен', str(host),
                       f'[{verified_ip if verified_ip else "Не определён"}]'))
        # print(f'Не доступен {host} '
        #       f'[{verified_ip if verified_ip else "Не определён"}]')
    return result


def host_range_ping(network):
    try:
        hosts = list(map(str, ipaddress.ip_network(network).hosts()))
    except ValueError as e:
        print(e)
    else:
        count = 255
        for host in host_ping(hosts):
            if not count:
                break
            count -= 1
            print(f'{host[0].ljust(11)} {host[1].ljust(15)} {host[2]}')


def host_range_ping_tab(network):
    table = [('Доступные', 'Недоступные')]
    sort = [[], []]
    try:
        hosts = list(map(str, ipaddress.ip_network(network).hosts()))
    except ValueError as e:
        print(e)
    else:
        result = host_ping(hosts)
        for host in result:
            if len(host[0]) == 8:
                sort[0].append(f'{host[1].ljust(15)} {host[2]}')
            else:
                sort[1].append(f'{host[1].ljust(15)} {host[2]}')
        table.extend(list(zip(*sort)))
        if len(sort[0]) > len(sort[1]):
            for item in sort[0][len(sort[1]):]:
                table.append((item, None))
        elif len(sort[0]) < len(sort[1]):
            for item in sort[1][len(sort[0]):]:
                table.append((None, item))
        print(tabulate(table, headers='firstrow', stralign='center',
                       tablefmt='pipe'))


ip_addresses = ['127.0.0.1', 'yandex.ru', 'yandex.hru', 2130706433]

print('Задание №1', end='\n\n')
for i in host_ping(ip_addresses):
    print(f'{i[0].ljust(11)} {i[1].ljust(15)} {i[2]}')

print('\nЗадание №2', end='\n\n')
host_range_ping('173.194.222.0/28')

print('\nЗадание №3', end='\n\n')
host_range_ping_tab('173.194.222.0/28')
