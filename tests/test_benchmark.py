from ed2grafos.benchmark import executar
from ed2grafos.geradores import gerar_cadeia, gerar_estrela, gerar_malha
from ed2grafos.algoritmos import bfs
from ed2grafos.resultado import ResultadoCaminho


def test_malha_conectada_e_deterministica():
    primeira = gerar_malha(25, cordas_caras=True)
    segunda = gerar_malha(25, cordas_caras=True)
    assert primeira.ordem == 25
    assert primeira.quantidade_arestas == segunda.quantidade_arestas == 24 + 23
    assert primeira.peso_aresta(0, 1) == 1
    assert primeira.peso_aresta(0, 2) == 100
    assert bfs(primeira, 0, 24).encontrado


def test_cadeia_e_estrela():
    cadeia = gerar_cadeia(8)
    estrela = gerar_estrela(8)
    assert cadeia.quantidade_arestas == 7
    assert estrela.quantidade_arestas == 7
    assert bfs(cadeia, 0, 7).tamanho_max_fronteira == 1
    assert bfs(estrela, 0, 7).tamanho_max_fronteira == 7


def test_benchmark_mini_invariantes():
    resultado = executar(tamanhos=(40,), repeticoes=1, aquecimento=0)
    assert resultado["protocolo"]["par"]
    assert len(resultado["cenarios"]) == 4
    for cenario in resultado["cenarios"]:
        assert cenario["vertices"] == 40
        assert all(cenario["invariantes"].values())


def test_texto_resultado():
    texto = ResultadoCaminho(
        algoritmo="dijkstra",
        origem=0,
        destino=2,
        encontrado=True,
        caminho=(0, 1, 2),
        custo=5,
        nos_visitados=3,
        tamanho_max_fronteira=2,
        saltos=2,
        soma_pesos=5,
        arestas_examinadas=4,
    ).texto()
    assert "Dijkstra" in texto
    assert "soma dos pesos" in texto
    assert "fronteira máxima" in texto
    assert "arestas examinadas" in texto
