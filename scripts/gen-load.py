#!/usr/bin/env python

import os
import random
import string
import sys
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from time import sleep

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error
from tqdm import tqdm


def connect(host: str, port: int, database: str):
    return mysql.connector.connect(
        host=host,
        port=port,
        user=os.environ["USERNAME"],
        password=os.environ["PASSWORD"],
        database=database,
    )


ALPHABET = string.ascii_letters + string.digits
print("Carregando credenciais do arquivo .env")
load_dotenv(".env")

parser = ArgumentParser(
    description="Insere dados randômicos na tabela curso.seed para simular carga enquanto executando um cluster InnoDB",
    formatter_class=ArgumentDefaultsHelpFormatter,
    epilog="Quando você exercitar derrubar o nó primário, o programa tentará reconectar via MySQL Router",
)
parser.add_argument("--host", help="Qual o host que deve conectar", default="localhost")
parser.add_argument("--port", help="Qual a porta do MySQL Router usar para conexão", default=6446, type=int)
parser.add_argument("--repeat", help="Quantas vezes a operação deve ser repetida", default=5000)
parser.add_argument("--database", help="Qual o banco de dados no servidor utilizar", default="curso")
parser.add_argument(
    "--sleep",
    help="Tempo de espera entre uma inserção e outra, em segundos",
    default=0.3,
    type=int,
)
args = parser.parse_args()
exit_code = 0

try:
    connection = connect(host=args.host, port=args.port, database=args.database)

    if connection.is_connected():
        cursor = connection.cursor()
        insert_query = "INSERT INTO seed (random) VALUES (%s)"

        for i in tqdm(range(args.repeat)):
            value = "".join(random.choices(ALPHABET, k=16))

            while True:
                try:
                    cursor.execute(insert_query, [value])
                    connection.commit()
                    break
                except Error as e:
                    print(f"\nFalha ao inserir, tentando reconectar: {e}")
                    try:
                        connection.close()
                    except Error:
                        pass
                    sleep(1)
                    connection = connect(host=args.host, port=args.port, database=args.database)
                    cursor = connection.cursor()

            if args.sleep > 0:
                sleep(args.sleep)

except Error as e:
    print(f"Ocorreu um erro ao tentar conectar no MySQL: {e}. Corrija o problema e reexecute o programa")
    exit_code = 1
except Exception as e:
    print(f"Um erro insperado ocorreu: {e}. Abortando a execução")
    exit_code = 1
finally:
    if "cursor" in locals() and cursor is not None:
        cursor.close()
    if "connection" in locals() and connection.is_connected():
        connection.close()
        print("\nA conexão com o MySQL foi encerrada")

sys.exit(exit_code)
