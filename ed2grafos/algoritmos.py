"""BFS, DFS iterativa, DFS recursiva e Dijkstra."""

from __future__ import annotations

from ed2grafos.estruturas import Fila, FilaDePrioridadeMinima, Pilha
from ed2grafos.grafo import Grafo
from ed2grafos.resultado import ResultadoCaminho, Vertice


def bfs(grafo: Grafo, origem: Vertice, destino: Vertice) -> ResultadoCaminho:
    """Caminho mínimo em número de saltos. A fronteira é uma fila FIFO."""

    _exigir_vertices(grafo, origem, destino)
    fila = Fila()
    visitados = {origem}
    pai: dict[Vertice, Vertice | None] = {origem: None}
    fila.enfileirar(origem)
    nos = 0
    arestas = 0
    while not fila.vazia():
        atual = fila.desenfileirar()
        nos += 1
        if atual == destino:
            break
        for vizinho, _peso in grafo.vizinhos(atual):
            arestas += 1
            if vizinho not in visitados:
                visitados.add(vizinho)
                pai[vizinho] = atual
                fila.enfileirar(vizinho)
    return _montar("bfs", grafo, origem, destino, pai, nos, fila.tamanho_maximo, arestas)


def dfs(grafo: Grafo, origem: Vertice, destino: Vertice) -> ResultadoCaminho:
    """DFS com pilha explícita. O vértice é marcado ao sair da pilha.

    A ordem de descoberta acompanha a DFS recursiva: os vizinhos são
    empilhados de trás para a frente e o pai é o da primeira retirada.
    """

    _exigir_vertices(grafo, origem, destino)
    pilha = Pilha()
    pilha.empilhar((origem, None))
    visitados: set[Vertice] = set()
    pai: dict[Vertice, Vertice | None] = {}
    nos = 0
    arestas = 0
    while not pilha.vazia():
        atual, anterior = pilha.desempilhar()
        if atual in visitados:
            continue
        visitados.add(atual)
        pai[atual] = anterior
        nos += 1
        if atual == destino:
            break
        for vizinho, _peso in reversed(grafo.vizinhos(atual)):
            arestas += 1
            if vizinho not in visitados:
                pilha.empilhar((vizinho, atual))
    return _montar("dfs", grafo, origem, destino, pai, nos, pilha.tamanho_maximo, arestas)


def dfs_recursivo(grafo: Grafo, origem: Vertice, destino: Vertice) -> ResultadoCaminho:
    """DFS pela pilha de chamadas. ``RecursionError`` vira estouro de pilha."""

    _exigir_vertices(grafo, origem, destino)
    visitados: set[Vertice] = set()
    pai: dict[Vertice, Vertice | None] = {}
    estado = {"nos": 0, "arestas": 0, "profundidade": 0, "maximo": 0, "encontrado": False}

    def visitar(atual: Vertice, anterior: Vertice | None) -> None:
        visitados.add(atual)
        pai[atual] = anterior
        estado["nos"] += 1
        estado["profundidade"] += 1
        if estado["profundidade"] > estado["maximo"]:
            estado["maximo"] = estado["profundidade"]
        if atual == destino:
            estado["encontrado"] = True
            estado["profundidade"] -= 1
            return
        for vizinho, _peso in grafo.vizinhos(atual):
            estado["arestas"] += 1
            if vizinho not in visitados and not estado["encontrado"]:
                visitar(vizinho, atual)
        estado["profundidade"] -= 1

    try:
        visitar(origem, None)
    except RecursionError:
        return _montar(
            "dfs_recursivo",
            grafo,
            origem,
            destino,
            {},
            estado["nos"],
            estado["maximo"],
            estado["arestas"],
            estouro=True,
            detalhe="RecursionError: a pilha de chamadas do interpretador encheu",
        )
    return _montar(
        "dfs_recursivo",
        grafo,
        origem,
        destino,
        pai,
        estado["nos"],
        estado["maximo"],
        estado["arestas"],
    )


def dijkstra(grafo: Grafo, origem: Vertice, destino: Vertice) -> ResultadoCaminho:
    """Caminho mínimo pela soma dos pesos. Exige peso estritamente positivo.

    O heap guarda entradas obsoletas e só consolida um vértice na primeira
    vez em que ele sai com a menor distância conhecida.
    """

    _exigir_vertices(grafo, origem, destino)
    fila = FilaDePrioridadeMinima()
    distancia: dict[Vertice, float] = {origem: 0.0}
    pai: dict[Vertice, Vertice | None] = {origem: None}
    consolidados: set[Vertice] = set()
    fila.inserir(0.0, origem)
    nos = 0
    arestas = 0
    while not fila.vazia():
        custo, atual = fila.remover()
        if atual in consolidados or custo > distancia.get(atual, float("inf")):
            continue
        consolidados.add(atual)
        pai.setdefault(atual, None)
        nos += 1
        if atual == destino:
            break
        for vizinho, peso in grafo.vizinhos(atual):
            arestas += 1
            if vizinho in consolidados:
                continue
            proposta = custo + peso
            if proposta < distancia.get(vizinho, float("inf")):
                distancia[vizinho] = proposta
                pai[vizinho] = atual
                fila.inserir(proposta, vizinho)
    return _montar(
        "dijkstra",
        grafo,
        origem,
        destino,
        pai,
        nos,
        fila.tamanho_maximo,
        arestas,
    )


def _exigir_vertices(grafo: Grafo, origem: Vertice, destino: Vertice) -> None:
    if not grafo.contem(origem):
        raise KeyError(f"vértice inexistente: {origem}")
    if not grafo.contem(destino):
        raise KeyError(f"vértice inexistente: {destino}")


def _reconstruir(
    pai: dict[Vertice, Vertice | None], origem: Vertice, destino: Vertice
) -> tuple[Vertice, ...] | None:
    if destino not in pai:
        return None
    caminho: list[Vertice] = []
    atual: Vertice | None = destino
    vistos: set[Vertice] = set()
    while atual is not None:
        if atual in vistos:
            return None
        vistos.add(atual)
        caminho.append(atual)
        if atual == origem:
            caminho.reverse()
            return tuple(caminho)
        atual = pai.get(atual)
    return None


def _montar(
    algoritmo: str,
    grafo: Grafo,
    origem: Vertice,
    destino: Vertice,
    pai: dict[Vertice, Vertice | None],
    nos: int,
    fronteira: int,
    arestas: int,
    estouro: bool = False,
    detalhe: str = "",
) -> ResultadoCaminho:
    if estouro:
        return ResultadoCaminho(
            algoritmo=algoritmo,
            origem=origem,
            destino=destino,
            encontrado=False,
            caminho=(),
            custo=None,
            nos_visitados=nos,
            tamanho_max_fronteira=fronteira,
            saltos=None,
            soma_pesos=None,
            arestas_examinadas=arestas,
            estouro_pilha=True,
            detalhe=detalhe,
        )
    caminho = _reconstruir(pai, origem, destino)
    if caminho is None:
        return ResultadoCaminho(
            algoritmo=algoritmo,
            origem=origem,
            destino=destino,
            encontrado=False,
            caminho=(),
            custo=None,
            nos_visitados=nos,
            tamanho_max_fronteira=fronteira,
            saltos=None,
            soma_pesos=None,
            arestas_examinadas=arestas,
        )
    valido, soma = grafo.validar_caminho(caminho)
    if not valido or soma is None:
        raise RuntimeError(f"{algoritmo} devolveu um caminho que não existe no grafo")
    saltos = len(caminho) - 1
    custo: float | int = soma if algoritmo == "dijkstra" else saltos
    return ResultadoCaminho(
        algoritmo=algoritmo,
        origem=origem,
        destino=destino,
        encontrado=True,
        caminho=caminho,
        custo=custo,
        nos_visitados=nos,
        tamanho_max_fronteira=fronteira,
        saltos=saltos,
        soma_pesos=soma,
        arestas_examinadas=arestas,
    )
