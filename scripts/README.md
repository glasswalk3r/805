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

## `galera-wsrep.py`

```bash
./scripts/galera-wsrep.py --help
usage: galera-wsrep.py [-h] [--host HOST] [--port PORT] [--database DATABASE]
                       [--user USER]

Verifica se o nó Galera está pronto (wsrep_ready = ON)

options:
  -h, --help           show this help message and exit
  --host HOST          Qual o host que deve conectar (default: localhost)
  --port PORT          Qual a porta do servidor usar para conexão (default:
                       3306)
  --database DATABASE  Qual o banco de dados usar para conexão (default:
                       curso)
  --user USER          Nome do usuário para conexão no MySQL (default: hector)
```

Este programa é usado para checar se um nó do cluster Galera está pronto para receber conexões (`wsrep_ready = ON`).

A senha também é pedida interativamente (via `getpass`), então o usuário informado em `--user` precisa ter
permissão para rodar `SHOW STATUS` no banco.

O programa termina com o código de saída `0` quando o nó está pronto e `1` caso contrário (ou se ocorrer algum
erro de conexão), o que permite usá-lo como *health check* em scripts de shell ou em ferramentas de
monitoramento, como o próprio HAProxy fazia com o script original.

## `innodb-file-size.py`

```bash
./scripts/innodb-file-size.py --help
usage: innodb-file-size.py [-h] [--host HOST] [--port PORT]
                           [--database DATABASE] [--user USER] [--sleep SLEEP]

Mede a taxa de escrita do redo log do InnoDB (innodb_os_log_written) e projeta
o total em uma hora

options:
  -h, --help           show this help message and exit
  --host HOST          Qual o host que deve conectar (default: localhost)
  --port PORT          Qual a porta do servidor usar para conexão (default:
                       3306)
  --database DATABASE  Qual o banco de dados usar para conexão (default:
                       mysql)
  --user USER          Nome do usuário para conexão no MySQL (default: root)
  --sleep SLEEP        Tempo de espera entre as duas leituras, em segundos
                       (default: 60)
```

Este programa é usado para estimar o tamanho ideal do `innodb_log_file_size` a partir da taxa de escrita real do *redo*
log do InnoDB.

Ele lê o valor de `innodb_os_log_written`, espera `--sleep` segundos (o script original sempre esperava 60
segundos, aqui esse valor virou configurável) e lê o valor novamente, calculando quantos bytes foram escritos
no intervalo e projetando esse total para uma hora.

A senha também é pedida interativamente (via `getpass`) e o usuário informado em `--user` precisa ter
permissão para rodar `SHOW STATUS` no banco.

## `pitr-chunks.py`

```bash
./scripts/pitr-chunks.py --help
usage: pitr-chunks.py [-h] [--host HOST] [--port PORT] [--user USER]
                      [--file FILE] [--batch-size BATCH_SIZE] [--sleep SLEEP]

Recria o banco pitr e cadastra aos poucos os registros de um CSV, para treinar
PITR

options:
  -h, --help            show this help message and exit
  --host HOST           Qual o host que deve conectar (default: localhost)
  --port PORT           Qual a porta do servidor usar para conexão (default:
                        3306)
  --user USER           Nome do usuário para conexão no MySQL (default: root)
  --file FILE           Caminho do arquivo CSV com os registros a inserir
                        (default: files/chunks.csv)
  --batch-size BATCH_SIZE
                        Quantos registros inserir antes de aguardar (default:
                        10)
  --sleep SLEEP         Tempo de espera entre um lote e outro, em segundos
                        (default: 60)
```

Este programa é usado para praticar recuperação PITR (*Point in Time Recovery*) no MySQL. O banco `pitr` e a tabela
`pitr.chunks` (antes definidos em `files/chunks.sql`) são criados automaticamente na primeira execução.

Os registros são lidos com o módulo `csv` a partir de `files/chunks.csv` (caminho configurável via `--file`) e
inseridos em lotes de `--batch-size` registros. A cada lote, o programa aguarda `--sleep` segundos e escreve na
tela o horário e a região usada, para facilitar anotar as faixas de tempo e cortar os logs binários com
exatidão — a mesma lógica do script original, que sorteava a região entre 10 cidades brasileiras a cada 10
inserções, ignorando o valor de região já presente no CSV.

A senha também é pedida interativamente (via `getpass`) e o usuário informado em `--user` precisa ter
permissão de `CREATE` e `INSERT` no banco.

## `galera-cache.py`

```bash
./scripts/galera-cache.py --help
usage: galera-cache.py [-h] [--host HOST] [--port PORT] [--database DATABASE]
                       [--user USER] [--sleep SLEEP]

Mede a taxa de tráfego de replicação do Galera (wsrep_received_bytes +
wsrep_replicated_bytes) e projeta o total em uma hora, para dimensionar o
gcache.size

options:
  -h, --help           show this help message and exit
  --host HOST          Qual o host que deve conectar (default: localhost)
  --port PORT          Qual a porta do servidor usar para conexão (default:
                       3306)
  --database DATABASE  Qual o banco de dados usar para conexão (default:
                       mysql)
  --user USER          Nome do usuário para conexão no MySQL (default: root)
  --sleep SLEEP        Tempo de espera entre as duas leituras, em segundos
                       (default: 60)
```

Este programa é usado para estimar o tamanho ideal do `gcache.size` do Galera a partir do tráfego real de replicação do
cluster.

Ele lê os valores de `wsrep_received_bytes` e `wsrep_replicated_bytes`, espera `--sleep` segundos (o script
original sempre esperava 60 segundos, aqui esse valor virou configurável) e lê os valores novamente, somando
quantos bytes trafegaram no intervalo e projetando esse total para uma hora.

A senha também é pedida interativamente (via `getpass`) e o usuário informado em `--user` precisa ter
permissão para rodar `SHOW STATUS` no banco.
