# analise

Script de linha de comando em Python que lê um arquivo CSV e calcula a média de uma coluna numérica, com filtro opcional por valor de outra coluna.

## Funcionalidades

- Calcula a média de qualquer coluna numérica de um CSV com cabeçalho.
- Filtro opcional `--filtrar-coluna COLUNA=VALOR` para considerar só as linhas que batem com o valor.
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

## Uso

```bash
python src/analise.py ARQUIVO COLUNA [--filtrar-coluna COLUNA=VALOR]
```

### Exemplos

Dado o arquivo `dados.csv`:

```csv
nome,idade,salario
Ana,30,1000
Bia,25,3000
Caio,30,2000
```

Média de uma coluna:

```bash
$ python src/analise.py dados.csv salario
2000.0
```

Média só das linhas em que `idade` é `30`:

```bash
$ python src/analise.py dados.csv salario --filtrar-coluna idade=30
1500.0
```

### Regras do filtro

- O formato é `coluna=valor`. A divisão acontece no primeiro `=`, então `obs=a=b` filtra a coluna `obs` pelo valor `a=b`.
- A comparação é exata e diferencia maiúsculas de minúsculas, após remover espaços nas pontas. `30` não bate com `30.0`.
- `coluna=` (valor vazio) seleciona as linhas em que a coluna está vazia.
- Valores não numéricos em linhas que não batem com o filtro são ignorados.

### Códigos de saída

| Código | Situação |
|--------|----------|
| `0` | Sucesso: a média é impressa na saída padrão. |
| `1` | Arquivo inexistente, coluna inexistente, valor não numérico ou nenhum valor numérico (mensagem `Erro: ...` na saída de erro). |
| `2` | Argumentos inválidos, como um filtro sem `=` (`use o formato coluna=valor`). |

### Uso como módulo

Com a pasta `src/` no `PYTHONPATH` (ou executando a partir dela):

```python
from analise import calcular_media, interpretar_filtro

calcular_media("dados.csv", "salario")                     # 2000.0
calcular_media("dados.csv", "salario", ("idade", "30"))    # 1500.0
calcular_media("dados.csv", "salario", interpretar_filtro("idade=30"))
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
