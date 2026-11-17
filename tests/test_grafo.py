from pathlib import Path

import pytest

from ed2grafos.grafo import Grafo, ler_grafo, salvar_grafo

RAIZ = Path(__file__).resolve().parents[1]
CAMPUS = RAIZ / "data" / "exemplo_campus.txt"
DIRECIONADO = RAIZ / "data" / "exemplo_direcionado.txt"


def test_le_campus():
    grafo = ler_grafo(CAMPUS)
    assert not grafo.direcionado
    assert grafo.ordem == 8
    assert grafo.quantidade_arestas == 11
    assert grafo.peso_aresta("CampusCentral", "DataCenter") == 5
    assert grafo.tem_aresta("DataCenter", "CampusCentral")


def test_le_direcionado():
    grafo = ler_grafo(DIRECIONADO)
    assert grafo.direcionado
    assert grafo.ordem == 4
    assert grafo.quantidade_arestas == 5
    assert grafo.tem_aresta("A", "B")
    assert not grafo.tem_aresta("B", "A")


def test_rejeita_peso_nao_positivo():
    grafo = Grafo()
    with pytest.raises(ValueError):
        grafo.adicionar_aresta("A", "B", 0)
    with pytest.raises(ValueError):
        grafo.adicionar_aresta("A", "B", -3)


def test_rejeita_aresta_duplicada():
    grafo = Grafo(direcionado=True)
    grafo.adicionar_aresta("A", "B", 1)
    with pytest.raises(ValueError):
        grafo.adicionar_aresta("A", "B", 2)


def test_rejeita_cabecalho_inconsistente(tmp_path: Path):
    arquivo = tmp_path / "quebrado.txt"
    arquivo.write_text("# Metadados: V E TIPO\n3 1 ND\nA B 1\n", encoding="utf-8")
    with pytest.raises(ValueError):
        ler_grafo(arquivo)


def test_roundtrip(tmp_path: Path):
    original = ler_grafo(CAMPUS)
    destino = tmp_path / "copia.txt"
    salvar_grafo(original, destino)
    copia = ler_grafo(destino)
    assert copia.ordem == original.ordem
    assert copia.quantidade_arestas == original.quantidade_arestas
    assert copia.peso_aresta("LabIA", "DataCenter") == 2


def test_validar_caminho():
    grafo = ler_grafo(CAMPUS)
    valido, soma = grafo.validar_caminho(
        ("CampusCentral", "DataCenter", "ServidorBorda", "HospitalEscola")
    )
    assert valido
    assert soma == 14
    invalido, _ = grafo.validar_caminho(("CampusCentral", "HospitalEscola"))
    assert not invalido
