"""Monta o PDF a partir de benchmarks/resultados.json e das figuras."""

from pathlib import Path

from ed2grafos.graficos import gerar_graficos
from ed2grafos.relatorio_pdf import carregar_json, gerar_pdf


def main() -> None:
    resultado = carregar_json("benchmarks/resultados.json")
    gerar_graficos(resultado, "benchmarks/figuras")
    destino = gerar_pdf(resultado, Path("benchmarks/figuras"), "relatorio/Trabalho_Final_ED2.pdf")
    print(destino)


if __name__ == "__main__":
    main()
