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
