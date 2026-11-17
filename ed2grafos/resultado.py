"""Resultado comum de BFS, DFS e Dijkstra."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Hashable

Vertice = Hashable

_NOMES = {
    "bfs": "BFS",
    "dfs": "DFS",
    "dfs_recursivo": "DFS recursivo",
    "dijkstra": "Dijkstra",
}


@dataclass(frozen=True)
class ResultadoCaminho:
    algoritmo: str
    origem: Vertice
    destino: Vertice
    encontrado: bool
    caminho: tuple[Any, ...]
    custo: float | int | None
    nos_visitados: int
    tamanho_max_fronteira: int
    saltos: int | None
    soma_pesos: float | None
    arestas_examinadas: int
    estouro_pilha: bool = False
    detalhe: str = ""

    def texto(self, limite_caminho: int = 12) -> str:
        nome = _NOMES.get(self.algoritmo, self.algoritmo)
        linhas = [nome]
        if self.estouro_pilha:
            linhas.append("  resultado: estouro da pilha de recursão")
            if self.detalhe:
                linhas.append(f"  detalhe: {self.detalhe}")
        elif not self.encontrado:
            linhas.append("  resultado: caminho inexistente")
        else:
            linhas.append(f"  caminho: {_formatar_caminho(self.caminho, limite_caminho)}")
            if self.algoritmo == "dijkstra":
                linhas.append(f"  custo (soma dos pesos): {_formatar_numero(self.custo)}")
            else:
                linhas.append(f"  custo (saltos): {self.custo}")
            linhas.append(f"  saltos: {self.saltos}")
            linhas.append(f"  soma dos pesos: {_formatar_numero(self.soma_pesos)}")
        linhas.append(f"  nós visitados: {self.nos_visitados}")
        linhas.append(f"  fronteira máxima: {self.tamanho_max_fronteira}")
        linhas.append(f"  arestas examinadas: {self.arestas_examinadas}")
        return "\n".join(linhas)


def _formatar_caminho(caminho: tuple[Any, ...], limite: int) -> str:
    if len(caminho) <= limite:
        return " -> ".join(str(vertice) for vertice in caminho)
    cabeca = " -> ".join(str(vertice) for vertice in caminho[:4])
    cauda = " -> ".join(str(vertice) for vertice in caminho[-3:])
    return f"{cabeca} -> ... ({len(caminho)} vértices) -> {cauda}"


def _formatar_numero(valor: float | int | None) -> str:
    if valor is None:
        return "-"
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    if isinstance(valor, float):
        return f"{valor:.4f}".rstrip("0").rstrip(".")
    return str(valor)
