[![Tests](https://github.com/jjuffagtotal-source/csv-mean-filter/actions/workflows/ci.yml/badge.svg)](https://github.com/jjuffagtotal-source/csv-mean-filter/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/csv-mean-filter.svg)](https://pypi.org/project/csv-mean-filter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
# analise

Script de linha de comando em Python que lê um arquivo CSV e calcula a média de uma coluna numérica, com filtros opcionais por valor de outras colunas.

## Funcionalidades

- Calcula a média de qualquer coluna numérica de um CSV com cabeçalho.
- Filtro opcional `--filtrar-coluna COLUNA=VALOR` para considerar só as linhas que batem com o valor.
- Múltiplos filtros: repita `--filtrar-coluna` e só as linhas que satisfazem **todos** eles (lógica AND) entram na média.
- Ignora células vazias.
- Lê CSVs gravados pelo Excel (UTF-8 com BOM).
- Mensagens de erro claras e códigos de saída previsíveis.
- Usa apenas a biblioteca padrão: nenhuma dependência externa.

## Requisitos

- Python 3.10 ou superior.

## Instalação

Não há pacotes para instalar. Basta clonar o repositório:

```bash
git clone <url-do-repositorio>
cd <pasta-do-repositorio>
```

## Instalação via pip

O projeto também pode ser instalado como pacote, o que disponibiliza o comando `csv-mean` no terminal. Na raiz do repositório:

```bash
pip install .
```

Futuramente, quando o pacote estiver publicado no PyPI:

```bash
pip install csv-mean-filter
```

Depois de instalado, use `csv-mean` no lugar de `python src/analise.py`:

```bash
$ csv-mean dados.csv salario --filtrar-coluna idade=30 --filtrar-coluna cidade=SP
1500.0
```

Recomenda-se instalar dentro de um ambiente virtual (`python -m venv .venv`).

## Uso

```bash
python src/analise.py ARQUIVO COLUNA [--filtrar-coluna COLUNA=VALOR ...]
```

### Exemplos

Dado o arquivo `dados.csv`:

```csv
nome,idade,cidade,salario
Ana,30,SP,1000
Bia,25,SP,3000
Caio,30,SP,2000
Duda,30,RJ,6000
```

Média de uma coluna:

```bash
$ python src/analise.py dados.csv salario
3000.0
```

Média só das linhas em que `idade` é `30`:

```bash
$ python src/analise.py dados.csv salario --filtrar-coluna idade=30
3000.0
```

Média só das linhas em que `idade` é `30` **e** `cidade` é `SP`:

```bash
$ python src/analise.py dados.csv salario --filtrar-coluna idade=30 --filtrar-coluna cidade=SP
1500.0
```

Se nenhuma linha satisfizer todos os filtros, o script sai com código `1`:

```bash
$ python src/analise.py dados.csv salario --filtrar-coluna idade=25 --filtrar-coluna cidade=RJ
Erro: Nenhuma linha restante com os filtros idade=25, cidade=RJ
```

### Regras do filtro

- O formato é `coluna=valor`. A divisão acontece no primeiro `=`, então `obs=a=b` filtra a coluna `obs` pelo valor `a=b`.
- A comparação é exata e diferencia maiúsculas de minúsculas, após remover espaços nas pontas. `30` não bate com `30.0`.
- `coluna=` (valor vazio) seleciona as linhas em que a coluna está vazia.
- Valores não numéricos em linhas que não batem com o filtro são ignorados.
- `--filtrar-coluna` pode ser repetido; os filtros são combinados com AND. Uma linha que falha em qualquer filtro é descartada, e a ordem dos filtros não importa.
- Repetir a mesma coluna com valores diferentes (`cidade=SP` e `cidade=RJ`) não deixa nenhuma linha e resulta em erro.

### Códigos de saída

| Código | Situação |
|--------|----------|
| `0` | Sucesso: a média é impressa na saída padrão. |
| `1` | Arquivo inexistente, coluna inexistente, valor não numérico, nenhuma linha restante após os filtros ou nenhum valor numérico (mensagem `Erro: ...` na saída de erro). |
| `2` | Argumentos inválidos, como um filtro sem `=` (`use o formato coluna=valor`). |

### Uso como módulo

Com a pasta `src/` no `PYTHONPATH` (ou executando a partir dela):

```python
from analise import calcular_media, interpretar_filtro

calcular_media("dados.csv", "salario")                     # 3000.0
calcular_media("dados.csv", "salario", ("idade", "30"))    # 3000.0
calcular_media("dados.csv", "salario", interpretar_filtro("idade=30"))
calcular_media("dados.csv", "salario", [("idade", "30"), ("cidade", "SP")])  # 1500.0
```

## Testes

Os testes usam apenas o `unittest` da biblioteca padrão. Na raiz do projeto:

```bash
python -m unittest discover -s tests -v
```

## Estrutura

```
src/analise.py           # script e funções
tests/test_analise.py    # testes unitários
```

## Licença

Distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE).


