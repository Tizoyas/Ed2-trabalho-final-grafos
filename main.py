"""Compara BFS, DFS e Dijkstra num arquivo de grafo."""

from __future__ import annotations

import argparse
from pathlib import Path

from ed2grafos.algoritmos import bfs, dfs, dfs_recursivo, dijkstra
from ed2grafos.grafo import ler_grafo


def main() -> None:
    parser = argparse.ArgumentParser(description="Compara BFS, DFS e Dijkstra.")
    parser.add_argument("arquivo", type=Path, help="arquivo com cabeçalho V E TIPO")
    parser.add_argument("origem", help="vértice de origem")
    parser.add_argument("destino", help="vértice de destino")
    argumentos = parser.parse_args()
    grafo = ler_grafo(argumentos.arquivo)
    origem = _token(argumentos.origem)
    destino = _token(argumentos.destino)
    print(f"grafo: {grafo.ordem} vértices, {grafo.quantidade_arestas} arestas, "
          f"{'direcionado' if grafo.direcionado else 'não direcionado'}")
    print(f"consulta: {origem} -> {destino}")
    print()
    for busca in (bfs, dfs, dfs_recursivo, dijkstra):
        print(busca(grafo, origem, destino).texto())
        print()


def _token(texto: str):
    try:
        return int(texto)
    except ValueError:
        return texto


if __name__ == "__main__":
    main()
