# Scripts

Eu criei (ou reescrevi o código em Perl) os scripts dentro do diretório `scripts`.

### Requisitos

- uv
- Python versão 3.12 ou superior

### Como usar

As dependências de todos os scripts são gerenciadas em um só local (`pyproject.yaml`) usando o uv.

Para instalar essas dependências, o recomendado é criar um virtualenv e instalar ali:

```bash
uv venv .venv
uv sync
. .venv/bin/activate
```

Os scripts devem funcionar depois disso. Essas configurações foram testadas no Linux.

Se você estiver usando outro sistema operacional que não seja Linux, se vire porque eu não ligo!

## `gen-load.py`

```bash
./scripts/gen-load.py --help
Carregando credenciais do arquivo .env
usage: gen-load.py [-h] [--repeat REPEAT] [--sleep SLEEP]

Insere dados randômicos na tabela seed do banco de dados curso para simular carga

options:
  -h, --help       show this help message and exit
  --repeat REPEAT  Quantas vezes a operação deve ser repetida (default: 5000)
  --sleep SLEEP    Tempo de espera entre uma inserção e outra, em segundos (default: 0.3)
```

Este programa é mais eficiente do que usar um loop no shell porque você se autentica somente uma vez no banco.

Isso significa que você vai gerar carga no MySQL inserindo dados, não fazendo login/logoff N vezes.

Você também vai ganhar uma barra de progresso na faixa.

## `gen-users.py`

```bash
./scripts/gen-users.py --help
usage: gen-users.py [-h] [--repeat REPEAT] [--host HOST] [--port PORT]
                    [--user USER]

Insere N registros de dados gerados automaticamente na tabela curso.usuarios

options:
  -h, --help       show this help message and exit
  --repeat REPEAT  Quantas vezes a operação deve ser repetida (default: 100)
  --host HOST      Qual o host que deve conectar (default: localhost)
  --port PORT      Qual a porta do servidor usar para conexão (default: 3306)
  --user USER      Nome do usuário para conexão no MySQL (default: app)
```

Este programa insere registros fake (nome, email, data de nascimento, profissão e status) na tabela
`curso.usuarios`, usando a biblioteca [Faker](https://faker.readthedocs.io/) com a localidade `pt_BR`.

A profissão de cada registro é sorteada por um `DynamicProvider` do próprio Faker, carregado a partir da lista de
30 profissões em `files/profissoes.csv`.

Diferente do `gen-load.py`, a senha não vem do `.env`: ela é pedida interativamente (via `getpass`), então o
usuário informado em `--user` precisa ter permissão de `INSERT` na tabela `curso.usuarios`.
