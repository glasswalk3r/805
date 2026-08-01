#!/usr/bin/env python

import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from getpass import getpass

import mysql.connector
from mysql.connector import Error

parser = ArgumentParser(
    description="Verifica se o nó Galera está pronto (wsrep_ready = ON)",
    formatter_class=ArgumentDefaultsHelpFormatter,
)
parser.add_argument("--host", help="Qual o host que deve conectar", default="localhost")
parser.add_argument("--port", help="Qual a porta do servidor usar para conexão", default=3306, type=int)
parser.add_argument("--database", help="Qual o banco de dados usar para conexão", default="curso")
parser.add_argument("--user", help="Nome do usuário para conexão no MySQL", default="hector")
args = parser.parse_args()

password = getpass(prompt=f"Digite a senha para o usuário {args.user}: ")

exit_code = 1

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
        cursor.execute("SHOW STATUS LIKE 'wsrep_ready'")
        _, value = cursor.fetchone()

        exit_code = 0 if value == "ON" else 1

except Error as e:
    print(f"Ocorreu um erro ao tentar conectar no MySQL: {e}")

finally:
    if "cursor" in locals() and cursor is not None:
        cursor.close()
    if "connection" in locals() and connection.is_connected():
        connection.close()

sys.exit(exit_code)
