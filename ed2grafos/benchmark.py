"""Mede tempo, memória e fronteira de BFS, DFS e Dijkstra."""

from __future__ import annotations

import json
import sys
import time
import tracemalloc
from pathlib import Path
from typing import Callable

from ed2grafos.algoritmos import bfs, dfs, dfs_recursivo, dijkstra
from ed2grafos.geradores import gerar_cadeia, gerar_estrela, gerar_malha
from ed2grafos.grafo import Grafo
from ed2grafos.resultado import ResultadoCaminho

TAMANHOS_PADRAO = (1000, 10_000, 50_000)
SEMENTE_RELATORIO = 20261117

ALGORITMOS: dict[str, Callable[[Grafo, int, int], ResultadoCaminho]] = {
    "bfs": bfs,
    "dfs": dfs,
    "dfs_recursivo": dfs_recursivo,
    "dijkstra": dijkstra,
}


def executar(
    tamanhos: tuple[int, ...] = TAMANHOS_PADRAO,
    repeticoes: int | None = None,
    aquecimento: int = 1,
    verboso: bool = False,
) -> dict:
    registros = []
    for tamanho in tamanhos:
        reps = repeticoes if repeticoes is not None else (3 if tamanho >= 50_000 else 5)
        malha = gerar_malha(tamanho, cordas_caras=False)
        malha_cara = gerar_malha(tamanho, cordas_caras=True)
        cadeia = gerar_cadeia(tamanho)
        estrela = gerar_estrela(tamanho)
        planos = (
            ("uniforme", malha, "pesos iguais a 1 na malha caminho+corda"),
            ("variado", malha_cara, "caminho com peso 1 e cordas com peso 100"),
            ("cadeia", cadeia, "caminho único, fronteira constante"),
            ("estrela", estrela, "controle de retenção de fronteira"),
        )
        for nome, grafo, descricao in planos:
            if verboso:
                print(f"medindo {nome} V={tamanho}", file=sys.stderr)
            algoritmos = {}
            brutos: dict[str, ResultadoCaminho] = {}
            for chave, funcao in ALGORITMOS.items():
                tempo_ms, resultado = _medir_tempo(
                    lambda funcao=funcao, grafo=grafo: funcao(grafo, 0, tamanho - 1),
                    reps,
                    aquecimento,
                )
                memoria = _medir_memoria(lambda funcao=funcao, grafo=grafo: funcao(grafo, 0, tamanho - 1))
                brutos[chave] = resultado
                algoritmos[chave] = {
                    "tempo_ms": tempo_ms,
                    "memoria_kib": memoria / 1024,
                    "resultado": _serializar(resultado),
                }
            invariantes = _invariantes(nome, tamanho, brutos)
            falhas = [chave for chave, ok in invariantes.items() if not ok]
            if falhas:
                raise AssertionError(f"invariante violada em {nome} V={tamanho}: {falhas}")
            registros.append(
                {
                    "cenario": nome,
                    "descricao": descricao,
                    "vertices": tamanho,
                    "arestas": grafo.quantidade_arestas,
                    "origem": 0,
                    "destino": tamanho - 1,
                    "repeticoes": reps,
                    "aquecimento": aquecimento,
                    "algoritmos": algoritmos,
                    "invariantes": invariantes,
                }
            )
    return {
        "protocolo": {
            "tamanhos": list(tamanhos),
            "semente_documental": SEMENTE_RELATORIO,
            "tempo": "mediana de time.perf_counter, sem tracemalloc",
            "memoria": "pico do tracemalloc numa execução separada, grafo já construído",
            "par": "origem 0 e destino V-1",
            "limite_recursao": sys.getrecursionlimit(),
        },
        "cenarios": registros,
    }


def salvar(resultado: dict, caminho: str | Path) -> None:
    destino = Path(caminho)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _medir_tempo(funcao: Callable[[], ResultadoCaminho], repeticoes: int, aquecimento: int):
    for _ in range(aquecimento):
        funcao()
    amostras = []
    ultimo = None
    for _ in range(repeticoes):
        inicio = time.perf_counter()
        ultimo = funcao()
        amostras.append((time.perf_counter() - inicio) * 1000)
    amostras.sort()
    return amostras[len(amostras) // 2], ultimo


def _medir_memoria(funcao: Callable[[], ResultadoCaminho]) -> int:
    tracemalloc.start()
    try:
        funcao()
        _, pico = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return pico


def _serializar(resultado: ResultadoCaminho) -> dict:
    caminho = [str(vertice) for vertice in resultado.caminho]
    if len(caminho) > 12:
        caminho = caminho[:4] + ["..."] + caminho[-3:]
    custo = resultado.custo
    soma = resultado.soma_pesos
    return {
        "algoritmo": resultado.algoritmo,
        "encontrado": resultado.encontrado,
        "estouro_pilha": resultado.estouro_pilha,
        "custo": _numero(custo),
        "saltos": resultado.saltos,
        "soma_pesos": _numero(soma),
        "nos_visitados": resultado.nos_visitados,
        "tamanho_max_fronteira": resultado.tamanho_max_fronteira,
        "arestas_examinadas": resultado.arestas_examinadas,
        "vertices_no_caminho": len(resultado.caminho),
        "caminho": caminho,
        "detalhe": resultado.detalhe,
    }


def _numero(valor: float | int | None):
    if isinstance(valor, float) and valor.is_integer():
        return int(valor)
    return valor


def _invariantes(cenario: str, n: int, resultados: dict[str, ResultadoCaminho]) -> dict[str, bool]:
    busca_largura = resultados["bfs"]
    busca_profundidade = resultados["dfs"]
    recursiva = resultados["dfs_recursivo"]
    caminho_minimo = resultados["dijkstra"]
    checagens = {
        "bfs_encontrou": busca_largura.encontrado,
        "dfs_encontrou": busca_profundidade.encontrado,
        "dijkstra_encontrou": caminho_minimo.encontrado,
    }
    if cenario == "uniforme":
        checagens["bfs_igual_dijkstra"] = (
            busca_largura.saltos == caminho_minimo.saltos == caminho_minimo.soma_pesos
        )
    elif cenario == "variado":
        checagens["dijkstra_mais_barato"] = (
            caminho_minimo.soma_pesos is not None
            and busca_largura.soma_pesos is not None
            and caminho_minimo.soma_pesos < busca_largura.soma_pesos
        )
        checagens["bfs_menos_saltos"] = (
            busca_largura.saltos is not None
            and caminho_minimo.saltos is not None
            and busca_largura.saltos < caminho_minimo.saltos
        )
        checagens["dijkstra_segue_o_caminho"] = (
            caminho_minimo.saltos == n - 1 and caminho_minimo.soma_pesos == n - 1
        )
    elif cenario == "cadeia":
        checagens["caminho_unico"] = (
            busca_largura.saltos == busca_profundidade.saltos == caminho_minimo.saltos == n - 1
        )
        checagens["fronteira_bfs_constante"] = busca_largura.tamanho_max_fronteira == 1
        if n >= sys.getrecursionlimit() - 20:
            checagens["dfs_recursiva_estourou"] = recursiva.estouro_pilha and not recursiva.encontrado
        else:
            checagens["dfs_recursiva_encontrou"] = recursiva.encontrado and not recursiva.estouro_pilha
    elif cenario == "estrela":
        checagens["fronteira_bfs_linear"] = busca_largura.tamanho_max_fronteira == n - 1
        checagens["fronteira_dfs_linear"] = busca_profundidade.tamanho_max_fronteira == n - 1
        checagens["dfs_recursiva_nao_estoura"] = recursiva.encontrado and not recursiva.estouro_pilha
        checagens["profundidade_recursiva_pequena"] = recursiva.tamanho_max_fronteira <= 3
    return checagens
