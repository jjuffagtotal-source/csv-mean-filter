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


def calcular_media(
    caminho_csv: str, coluna: str, filtro: tuple[str, str] | None = None
) -> float:
    """Retorna a média dos valores numéricos da coluna informada.

    Células vazias são ignoradas. Com filtro (coluna, valor), considera só as
    linhas cuja coluna do filtro é igual ao valor (após strip). Levanta
    FileNotFoundError se o arquivo não existir e ValueError para coluna
    ausente, valor não numérico ou ausência de valores numéricos.
    """
    if not os.path.isfile(caminho_csv):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_csv}")

    with open(caminho_csv, encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        cabecalho = leitor.fieldnames or []
        for nome in [coluna] + ([filtro[0]] if filtro else []):
            if nome not in cabecalho:
                raise ValueError(f"Coluna '{nome}' não encontrada no cabeçalho")

        soma = 0.0
        quantidade = 0
        for linha in leitor:
            if filtro and (linha.get(filtro[0]) or "").strip() != filtro[1].strip():
                continue
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

    if quantidade == 0:
        sufixo = f" com o filtro {filtro[0]}={filtro[1]}" if filtro else ""
        raise ValueError(f"Nenhum valor numérico na coluna '{coluna}'{sufixo}")
    return soma / quantidade


def main(argv=None) -> int:
    """Ponto de entrada da CLI; retorna o código de saída."""
    parser = argparse.ArgumentParser(description="Média de uma coluna de um CSV.")
    parser.add_argument("arquivo", help="caminho do arquivo CSV")
    parser.add_argument("coluna", help="nome da coluna")
    parser.add_argument(
        "--filtrar-coluna", type=_filtro_argparse, metavar="COLUNA=VALOR",
        help="considera só as linhas em que COLUNA é igual a VALOR",
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
