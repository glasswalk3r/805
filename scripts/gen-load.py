#!/usr/bin/env python

import os
import random
import string
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from time import sleep

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
from tqdm import tqdm

ALPHABET = string.ascii_letters + string.digits
print("Carregando credenciais do arquivo .env")
load_dotenv(".env")

parser = ArgumentParser(
    description="Insere dados randômicos na tabela seed do banco de dados curso para simular carga",
    formatter_class=ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "--repeat", help="Quantas vezes a operação deve ser repetida", default=5000
)
parser.add_argument(
    "--sleep",
    help="Tempo de espera entre uma inserção e outra, em segundos",
    default=0.3,
    type=int,
)
args = parser.parse_args()

try:
    connection = mysql.connector.connect(
        host="localhost",
        user=os.environ["USERNAME"],
        password=os.environ["PASSWORD"],
        database="curso",
    )

    if connection.is_connected():
        cursor = connection.cursor()

        insert_query = "INSERT INTO seed (random) VALUES (%s)"

        for i in tqdm(range(args.repeat)):
            cursor.execute(insert_query, [("".join(random.choices(ALPHABET, k=16)))])
            connection.commit()

            if args.sleep > 0:
                sleep(args.sleep)

except Error as e:
    print(f"Ocorreu um erro ao tentar conectar no MySQL: {e}")

finally:
    if "cursor" in locals() and cursor is not None:
        cursor.close()
    if "connection" in locals() and connection.is_connected():
        connection.close()
        print("\nA conexão com o MySQL foi encerrada")
