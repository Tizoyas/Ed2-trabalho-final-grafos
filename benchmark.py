"""Gera benchmarks/resultados.json e os gráficos."""

from ed2grafos.benchmark import executar, salvar
from ed2grafos.graficos import gerar_graficos


def main() -> None:
    resultado = executar(verboso=True)
    salvar(resultado, "benchmarks/resultados.json")
    figuras = gerar_graficos(resultado, "benchmarks/figuras")
    print("benchmarks/resultados.json")
    for figura in figuras:
        print(figura)


if __name__ == "__main__":
    main()
