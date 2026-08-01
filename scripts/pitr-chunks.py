#!/usr/bin/env python

import csv
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from datetime import datetime
from getpass import getpass
from time import sleep

import mysql.connector
from mysql.connector import Error

REGIONS = [
    "Osasco",
    "Acre",
    "Amazonas",
    "Barretos",
    "Belo Horizonte",
    "Distrito Federal",
    "Porto Velho",
    "Sorocaba",
    "Araras",
    "Limeira",
]

CREATE_DATABASE = "CREATE DATABASE IF NOT EXISTS pitr"

CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS pitr.chunks (
        id int(11) NOT NULL AUTO_INCREMENT,
        region varchar(255) DEFAULT NULL,
        country varchar(255) DEFAULT NULL,
        type varchar(255) DEFAULT NULL,
        channel varchar(255) DEFAULT NULL,
        priority varchar(255) DEFAULT NULL,
        order_date varchar(255) DEFAULT NULL,
        oid varchar(255) DEFAULT NULL,
        ship_date varchar(255) DEFAULT NULL,
        sold varchar(255) DEFAULT NULL,
        price varchar(255) DEFAULT NULL,
        cost varchar(255) DEFAULT NULL,
        total_revenue varchar(255) DEFAULT NULL,
        total_cost varchar(255) DEFAULT NULL,
        total_profit varchar(255) DEFAULT NULL,
        PRIMARY KEY (id)
    )
"""

INSERT_CHUNK = """
    INSERT INTO pitr.chunks (region, country, type, channel, priority, order_date, oid, ship_date, sold, price,
    cost, total_revenue, total_cost, total_profit)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

parser = ArgumentParser(
    description="Recria o banco pitr e cadastra aos poucos os registros de um CSV, para treinar PITR",
    formatter_class=ArgumentDefaultsHelpFormatter,
)
parser.add_argument("--host", help="Qual o host que deve conectar", default="localhost")
parser.add_argument("--port", help="Qual a porta do servidor usar para conexão", default=3306, type=int)
parser.add_argument("--user", help="Nome do usuário para conexão no MySQL", default="root")
parser.add_argument("--file", help="Caminho do arquivo CSV com os registros a inserir", default="files/chunks.csv")
parser.add_argument("--batch-size", help="Quantos registros inserir antes de aguardar", default=10, type=int)
parser.add_argument("--sleep", help="Tempo de espera entre um lote e outro, em segundos", default=60, type=int)
args = parser.parse_args()

password = getpass(prompt=f"Digite a senha para o usuário {args.user}: ")

try:
    connection = mysql.connector.connect(
        host=args.host,
        port=args.port,
        user=args.user,
        password=password,
    )

    if connection.is_connected():
        cursor = connection.cursor()

        cursor.execute(CREATE_DATABASE)
        cursor.execute(CREATE_TABLE)
        connection.commit()

        with open(args.file, encoding="utf-8", newline="") as f:
            reader = csv.reader(f)

            region_index = 0
            batch_count = 0

            for row in reader:
                if not row:
                    continue

                _region, *rest = row
                region = REGIONS[region_index]

                cursor.execute(INSERT_CHUNK, (region, *rest))
                connection.commit()

                batch_count += 1

                if batch_count == args.batch_size:
                    print(f"{datetime.now():%Y-%m-%d %H:%M:%S} -> {region}")
                    sleep(args.sleep)
                    region_index += 1
                    batch_count = 0

except Error as e:
    print(f"Ocorreu um erro ao tentar conectar no MySQL: {e}")

finally:
    if "cursor" in locals() and cursor is not None:
        cursor.close()
    if "connection" in locals() and connection.is_connected():
        connection.close()
