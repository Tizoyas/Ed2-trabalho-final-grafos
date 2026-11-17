"""Gráficos de tempo, memória e fronteira."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

_CORES = {
    "bfs": "#0072B2",
    "dfs": "#E69F00",
    "dijkstra": "#009E73",
    "dfs_recursivo": "#D55E00",
}
_NOMES = {
    "bfs": "BFS",
    "dfs": "DFS iterativa",
    "dijkstra": "Dijkstra",
    "dfs_recursivo": "DFS recursiva",
}


def gerar_graficos(resultado: dict, pasta: str | Path) -> list[Path]:
    destino = Path(pasta)
    destino.mkdir(parents=True, exist_ok=True)
    plt.rcParams["font.family"] = "DejaVu Sans"
    saidas = [
        _serie(
            resultado,
            "uniforme",
            ("bfs", "dfs", "dijkstra"),
            "tempo_ms",
            "Tempo (ms)",
            "Tempo e vértices — pesos uniformes",
            destino / "tempo_vs_vertices.png",
        ),
        _serie(
            resultado,
            "uniforme",
            ("bfs", "dfs", "dijkstra"),
            "memoria_mib",
            "Memória de pico (MiB)",
            "Memória e vértices — pesos uniformes",
            destino / "memoria_vs_vertices.png",
        ),
        _serie(
            resultado,
            "uniforme",
            ("bfs", "dfs", "dijkstra"),
            "fronteira",
            "Fronteira máxima (vértices)",
            "Fronteira e vértices — pesos uniformes",
            destino / "fronteira_vs_vertices.png",
        ),
        _fronteira_estresse(resultado, destino / "fronteira_estresse.png"),
    ]
    plt.close("all")
    return saidas


def _pontos(resultado: dict, cenario: str, algoritmo: str, campo: str):
    xs = []
    ys = []
    for registro in resultado["cenarios"]:
        if registro["cenario"] != cenario:
            continue
        bloco = registro["algoritmos"][algoritmo]
        if bloco["resultado"]["estouro_pilha"] and campo != "fronteira":
            continue
        if campo == "fronteira":
            valor = bloco["resultado"]["tamanho_max_fronteira"]
        elif campo == "memoria_mib":
            valor = bloco["memoria_kib"] / 1024
        else:
            valor = bloco[campo]
        xs.append(registro["vertices"])
        ys.append(valor)
    return xs, ys


def _serie(resultado, cenario, algoritmos, campo, eixo_y, titulo, caminho: Path) -> Path:
    figura, eixo = plt.subplots(figsize=(6.4, 3.6), dpi=140)
    maior = 0.0
    for algoritmo in algoritmos:
        xs, ys = _pontos(resultado, cenario, algoritmo, campo)
        if not xs:
            continue
        maior = max(maior, max(ys))
        eixo.plot(xs, ys, marker="o", color=_CORES[algoritmo], label=_NOMES[algoritmo], linewidth=2)
    eixo.set_xlabel("Vértices")
    eixo.set_ylabel(eixo_y)
    eixo.set_title(titulo)
    eixo.set_xticks(_tamanhos(resultado, cenario))
    if campo == "fronteira":
        eixo.set_yscale("log")
    elif maior >= 10_000:
        eixo.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    else:
        eixo.ticklabel_format(axis="y", style="plain", useOffset=False)
    eixo.grid(True, alpha=0.3)
    eixo.legend(frameon=False)
    figura.tight_layout()
    figura.savefig(caminho)
    plt.close(figura)
    return caminho


def _fronteira_estresse(resultado: dict, caminho: Path) -> Path:
    figura, eixo = plt.subplots(figsize=(6.4, 3.6), dpi=140)
    series = (
        ("cadeia", "bfs", "#0072B2", "-", "BFS na cadeia"),
        ("estrela", "bfs", "#0072B2", "--", "BFS na estrela"),
        ("cadeia", "dfs_recursivo", "#D55E00", "-", "DFS recursiva na cadeia"),
        ("estrela", "dfs_recursivo", "#D55E00", "--", "DFS recursiva na estrela"),
    )
    for cenario, algoritmo, cor, estilo, rotulo in series:
        xs, ys = _pontos(resultado, cenario, algoritmo, "fronteira")
        eixo.plot(xs, ys, marker="o", linestyle=estilo, color=cor, label=rotulo, linewidth=2)
    eixo.set_xlabel("Vértices")
    eixo.set_ylabel("Fronteira ou profundidade máxima")
    eixo.set_title("Cadeia rasa na fila, funda na recursão")
    eixo.set_xticks(_tamanhos(resultado, "cadeia"))
    eixo.set_yscale("log")
    eixo.grid(True, alpha=0.3)
    eixo.legend(
        frameon=False,
        fontsize=8,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.22),
        ncol=2,
    )
    figura.tight_layout()
    figura.savefig(caminho, bbox_inches="tight")
    plt.close(figura)
    return caminho


def _tamanhos(resultado: dict, cenario: str) -> list[int]:
    return [registro["vertices"] for registro in resultado["cenarios"] if registro["cenario"] == cenario]
