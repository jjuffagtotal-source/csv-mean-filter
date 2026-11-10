"""Calcula a média de uma coluna numérica de um arquivo CSV."""

import argparse
import csv
import os
import sys


def interpretar_filtro(texto: str) -> tuple[str, str]:
    """Converte "coluna=valor" em (coluna, valor), dividindo no primeiro "="."""
    if "=" not in texto:
        raise ValueError(f"Filtro sem '=': {texto!r}")
    nome, valor = (parte.strip() for parte in texto.split("=", 1))
    if not nome:
        raise ValueError(f"Filtro sem nome de coluna: {texto!r}")
    return nome, valor


def _filtro_argparse(texto: str) -> tuple[str, str]:
    """Adapta interpretar_filtro para o type= do argparse."""
    try:
        return interpretar_filtro(texto)
    except ValueError:
        raise argparse.ArgumentTypeError("use o formato coluna=valor") from None


Filtro = tuple[str, str]


def _normalizar_filtros(filtro) -> list[Filtro]:
    """Aceita None, um filtro (coluna, valor) ou uma lista de filtros."""
    if not filtro:
        return []
    if isinstance(filtro, tuple) and len(filtro) == 2 and isinstance(filtro[0], str):
        return [filtro]
    return list(filtro)


def _descrever_filtros(filtros: list[Filtro]) -> str:
    """Monta o sufixo das mensagens de erro, ex.: " com os filtros a=1, b=2"."""
    if not filtros:
        return ""
    termos = ", ".join(f"{nome}={valor}" for nome, valor in filtros)
    return f" com o filtro {termos}" if len(filtros) == 1 else f" com os filtros {termos}"


def calcular_media(
    caminho_csv: str, coluna: str, filtro: Filtro | list[Filtro] | None = None
) -> float:
    """Retorna a média dos valores numéricos da coluna informada.

    Células vazias são ignoradas. filtro pode ser um par (coluna, valor) ou uma
    lista de pares; só são consideradas as linhas que satisfazem TODOS eles
    (comparação exata após strip). Levanta FileNotFoundError se o arquivo não
    existir e ValueError para coluna ausente, valor não numérico, nenhuma linha
    restante após os filtros ou ausência de valores numéricos.
    """
    filtros = _normalizar_filtros(filtro)
    if not os.path.isfile(caminho_csv):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_csv}")

    with open(caminho_csv, encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        cabecalho = leitor.fieldnames or []
        for nome in [coluna] + [nome for nome, _ in filtros]:
            if nome not in cabecalho:
                raise ValueError(f"Coluna '{nome}' não encontrada no cabeçalho")

        soma = 0.0
        quantidade = 0
        linhas_aceitas = 0
        for linha in leitor:
            if any(
                (linha.get(nome) or "").strip() != valor.strip()
                for nome, valor in filtros
            ):
                continue
            linhas_aceitas += 1
            bruto = (linha.get(coluna) or "").strip()
            if not bruto:
                continue
            try:
                soma += float(bruto)
            except ValueError:
                raise ValueError(
                    f"Valor não numérico '{bruto}' na linha {leitor.line_num}"
                ) from None
            quantidade += 1

    sufixo = _descrever_filtros(filtros)
    if filtros and linhas_aceitas == 0:
        raise ValueError(f"Nenhuma linha restante{sufixo}")
    if quantidade == 0:
        raise ValueError(f"Nenhum valor numérico na coluna '{coluna}'{sufixo}")
    return soma / quantidade


def main(argv=None) -> int:
    """Ponto de entrada da CLI; retorna o código de saída."""
    parser = argparse.ArgumentParser(description="Média de uma coluna de um CSV.")
    parser.add_argument("arquivo", help="caminho do arquivo CSV")
    parser.add_argument("coluna", help="nome da coluna")
    parser.add_argument(
        "--filtrar-coluna", type=_filtro_argparse, metavar="COLUNA=VALOR",
        action="append",
        help="considera só as linhas em que COLUNA é igual a VALOR; pode ser "
        "repetido, e a linha precisa satisfazer todos os filtros (AND)",
    )
    args = parser.parse_args(argv)

    try:
        media = calcular_media(args.arquivo, args.coluna, args.filtrar_coluna)
    except (FileNotFoundError, ValueError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1
    print(media)
    return 0


if __name__ == "__main__":
    sys.exit(main())
