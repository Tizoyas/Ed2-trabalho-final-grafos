"""Grafos determinísticos usados no benchmark e nos testes."""

from __future__ import annotations

from ed2grafos.grafo import Grafo


def gerar_malha(n: int, cordas_caras: bool = False) -> Grafo:
    """Caminho 0-1-...-(n-1) mais a corda i — i+2 em todo vértice.

    Com ``cordas_caras=False`` todo peso vale 1. Com ``cordas_caras=True``
    o caminho pesa 1 e cada corda pesa 100. A distância em saltos passa a
    discordar da distância ponderada.
    """

    if n < 1:
        raise ValueError("n deve ser positivo")
    grafo = Grafo(direcionado=False)
    for vertice in range(n):
        grafo.adicionar_vertice(vertice)
    for vertice in range(n - 1):
        grafo.adicionar_aresta(vertice, vertice + 1, 1)
    for vertice in range(n - 2):
        grafo.adicionar_aresta(vertice, vertice + 2, 100 if cordas_caras else 1)
    return grafo


def gerar_cadeia(n: int, peso: float = 1) -> Grafo:
    """Único caminho 0-1-...-(n-1). A fronteira das buscas fica constante."""

    if n < 1:
        raise ValueError("n deve ser positivo")
    if peso <= 0:
        raise ValueError("peso deve ser maior que zero")
    grafo = Grafo(direcionado=False)
    for vertice in range(n):
        grafo.adicionar_vertice(vertice)
    for vertice in range(n - 1):
        grafo.adicionar_aresta(vertice, vertice + 1, peso)
    return grafo


def gerar_estrela(n: int, peso: float = 1) -> Grafo:
    """Centro 0 ligado a todas as folhas. A fronteira retém Θ(V) vértices."""

    if n < 1:
        raise ValueError("n deve ser positivo")
    if peso <= 0:
        raise ValueError("peso deve ser maior que zero")
    grafo = Grafo(direcionado=False)
    for vertice in range(n):
        grafo.adicionar_vertice(vertice)
    for folha in range(1, n):
        grafo.adicionar_aresta(0, folha, peso)
    return grafo
