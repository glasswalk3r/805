#!/usr/bin/env python

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from getpass import getpass
from time import sleep

import mysql.connector
from mysql.connector import Error

parser = ArgumentParser(
    description="Mede a taxa de escrita do redo log do InnoDB (innodb_os_log_written) e projeta o total em uma hora",
    formatter_class=ArgumentDefaultsHelpFormatter,
)
parser.add_argument("--host", help="Qual o host que deve conectar", default="localhost")
parser.add_argument("--port", help="Qual a porta do servidor usar para conexão", default=3306, type=int)
parser.add_argument("--database", help="Qual o banco de dados usar para conexão", default="mysql")
parser.add_argument("--user", help="Nome do usuário para conexão no MySQL", default="root")
parser.add_argument("--sleep", help="Tempo de espera entre as duas leituras, em segundos", default=60, type=int)
args = parser.parse_args()

password = getpass(prompt=f"Digite a senha para o usuário {args.user}: ")

try:
    connection = mysql.connector.connect(
        host=args.host,
        port=args.port,
        user=args.user,
        password=password,
        database=args.database,
    )

    if connection.is_connected():
        cursor = connection.cursor()

        cursor.execute("SHOW STATUS LIKE 'innodb_os_log_written'")
        _, first = cursor.fetchone()

        sleep(args.sleep)

        cursor.execute("SHOW STATUS LIKE 'innodb_os_log_written'")
        _, second = cursor.fetchone()

        total = int(second) - int(first)
        total_hour = total * (3600 // args.sleep)

        print(f"{total} bytes, ou {total // 1024 // 1024} mb em {args.sleep} segundos")
        print(f"{total_hour} bytes, ou {total_hour // 1024 // 1024} mb em 1 hora")

except Error as e:
    print(f"Ocorreu um erro ao tentar conectar no MySQL: {e}")

finally:
    if "cursor" in locals() and cursor is not None:
        cursor.close()
    if "connection" in locals() and connection.is_connected():
        connection.close()
