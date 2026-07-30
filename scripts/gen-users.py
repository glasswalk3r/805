#!/usr/bin/env python

from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from getpass import getpass

import mysql.connector
from faker import Faker
from faker.providers import DynamicProvider
from mysql.connector import Error
from tqdm import tqdm


def profession_provider():
    with open("files/profissoes.csv", encoding="utf-8") as f:
        professions = [line.strip() for line in f if line.strip()][:30]

    return DynamicProvider(provider_name="profession", elements=professions)


parser = ArgumentParser(
    description="Insere N registros de dados gerados automaticamente na tabela curso.usuarios",
    formatter_class=ArgumentDefaultsHelpFormatter,
)
parser.add_argument(
    "--repeat",
    help="Quantas vezes a operação deve ser repetida",
    default=100,
    type=int,
)
parser.add_argument("--host", help="Qual o host que deve conectar", default="localhost")
parser.add_argument("--port", help="Qual a porta do servidor usar para conexão", default=3306, type=int)
parser.add_argument("--user", help="Nome do usuário para conexão no MySQL", default="app")
args = parser.parse_args()

password = getpass(prompt=f"Digite a senha para o usuário {args.user}: ")

fake = Faker("pt_BR")
fake.add_provider(profession_provider())

try:
    connection = mysql.connector.connect(
        host="localhost",
        user=args.user,
        password=password,
        database="curso",
    )

    if connection.is_connected():
        print("Successfully connected to MySQL database")
        cursor = connection.cursor()

        insert_query = "INSERT INTO usuarios (nome, email, nascimento, profissao, status) VALUES (%s, %s, %s, %s, %s)"

        for _ in tqdm(range(args.repeat)):
            user_data = (fake.name(), fake.email(), fake.date_of_birth(), fake.profession(), 1)
            cursor.execute(insert_query, user_data)
            connection.commit()

        print(f"Inseridos {args.repeat} registros")

except Error as e:
    print(f"Error while connecting to MySQL: {e}")

finally:
    if "connection" in locals() and connection.is_connected():
        cursor.close()
        connection.close()
        print("\nMySQL connection is safely closed")
