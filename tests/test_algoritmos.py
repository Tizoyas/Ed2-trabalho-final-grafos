import math

from ed2grafos.algoritmos import bfs, dfs, dfs_recursivo, dijkstra
from ed2grafos.geradores import gerar_cadeia, gerar_estrela, gerar_malha
from ed2grafos.grafo import Grafo, ler_grafo
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]


def campus():
    return ler_grafo(RAIZ / "data" / "exemplo_campus.txt")


def direcionado():
    return ler_grafo(RAIZ / "data" / "exemplo_direcionado.txt")


def test_bfs_campus():
    resultado = bfs(campus(), "CampusCentral", "HospitalEscola")
    assert resultado.encontrado
    assert resultado.caminho == ("CampusCentral", "BlocoSaude", "HospitalEscola")
    assert resultado.custo == 2
    assert resultado.saltos == 2
    assert resultado.soma_pesos == 19
    assert resultado.tamanho_max_fronteira >= 1


def test_dijkstra_campus():
    resultado = dijkstra(campus(), "CampusCentral", "HospitalEscola")
    assert resultado.caminho == (
        "CampusCentral",
        "DataCenter",
        "ServidorBorda",
        "HospitalEscola",
    )
    assert resultado.custo == 14
    assert resultado.saltos == 3
    assert resultado.soma_pesos == 14


def test_direcionado():
    grafo = direcionado()
    menor_peso = dijkstra(grafo, "A", "D")
    menos_saltos = bfs(grafo, "A", "D")
    assert menor_peso.caminho == ("A", "B", "C", "D")
    assert menor_peso.custo == 3
    assert menos_saltos.caminho == ("A", "B", "D")
    assert menos_saltos.saltos == 2
    assert menos_saltos.soma_pesos == 6


def test_uniforme_bfs_igual_dijkstra():
    grafo = gerar_malha(30, cordas_caras=False)
    largura = bfs(grafo, 0, 29)
    minimo = dijkstra(grafo, 0, 29)
    assert largura.saltos == minimo.saltos == minimo.soma_pesos
    assert largura.saltos == math.ceil(29 / 2)


def test_variado_tradeoff():
    grafo = gerar_malha(30, cordas_caras=True)
    largura = bfs(grafo, 0, 29)
    minimo = dijkstra(grafo, 0, 29)
    assert largura.saltos == math.ceil(29 / 2)
    assert minimo.saltos == 29
    assert minimo.soma_pesos == 29
    assert minimo.soma_pesos < largura.soma_pesos
    assert largura.saltos < minimo.saltos


def test_dfs_igual_recursivo():
    grafo = direcionado()
    iterativa = dfs(grafo, "A", "D")
    recursiva = dfs_recursivo(grafo, "A", "D")
    assert iterativa.caminho == recursiva.caminho == ("A", "B", "C", "D")
    assert iterativa.saltos == 3
    assert not recursiva.estouro_pilha


def test_sem_caminho():
    grafo = Grafo(direcionado=True)
    grafo.adicionar_aresta("A", "B", 1)
    grafo.adicionar_vertice("C")
    for busca in (bfs, dfs, dfs_recursivo, dijkstra):
        resultado = busca(grafo, "A", "C")
        assert not resultado.encontrado
        assert resultado.caminho == ()
        assert resultado.custo is None


def test_origem_igual_destino():
    grafo = gerar_cadeia(4)
    resultado = dijkstra(grafo, 2, 2)
    assert resultado.encontrado
    assert resultado.caminho == (2,)
    assert resultado.custo == 0
    assert resultado.saltos == 0
    assert resultado.nos_visitados == 1


def test_cadeia_estoura_recursao():
    grafo = gerar_cadeia(2500)
    recursiva = dfs_recursivo(grafo, 0, 2499)
    iterativa = dfs(grafo, 0, 2499)
    assert recursiva.estouro_pilha
    assert not recursiva.encontrado
    assert iterativa.encontrado
    assert iterativa.caminho[0] == 0
    assert iterativa.caminho[-1] == 2499
    assert iterativa.saltos == 2499
    assert iterativa.tamanho_max_fronteira == 1


def test_estrela_fronteira():
    grafo = gerar_estrela(20)
    largura = bfs(grafo, 0, 19)
    profundidade = dfs(grafo, 0, 19)
    recursiva = dfs_recursivo(grafo, 0, 19)
    assert largura.tamanho_max_fronteira == 19
    assert profundidade.tamanho_max_fronteira == 19
    assert recursiva.encontrado
    assert recursiva.tamanho_max_fronteira <= 3
    assert largura.saltos == 1
