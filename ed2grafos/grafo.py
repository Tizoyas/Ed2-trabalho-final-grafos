"""Grafo ponderado com lista de adjacência e leitura de arquivo."""

from __future__ import annotations

from pathlib import Path

from ed2grafos.resultado import Vertice


class Grafo:
    """Lista de adjacência. Toda aresta tem peso estritamente positivo."""

    def __init__(self, direcionado: bool = False) -> None:
        self.direcionado = direcionado
        self._adj: dict[Vertice, list[tuple[Vertice, float]]] = {}

    def adicionar_vertice(self, vertice: Vertice) -> None:
        self._adj.setdefault(vertice, [])

    def adicionar_aresta(self, origem: Vertice, destino: Vertice, peso: float) -> None:
        if peso <= 0:
            raise ValueError(f"peso deve ser maior que zero, recebido {peso}")
        if self.tem_aresta(origem, destino):
            raise ValueError(f"aresta duplicada: {origem} -> {destino}")
        self.adicionar_vertice(origem)
        self.adicionar_vertice(destino)
        self._adj[origem].append((destino, float(peso)))
        if not self.direcionado and origem != destino:
            self._adj[destino].append((origem, float(peso)))

    def definir_peso(self, origem: Vertice, destino: Vertice, peso: float) -> None:
        if peso <= 0:
            raise ValueError(f"peso deve ser maior que zero, recebido {peso}")
        self._substituir(origem, destino, float(peso))
        if not self.direcionado and origem != destino:
            self._substituir(destino, origem, float(peso))

    def _substituir(self, origem: Vertice, destino: Vertice, peso: float) -> None:
        lista = self._adj[origem]
        for indice, (vizinho, _) in enumerate(lista):
            if vizinho == destino:
                lista[indice] = (destino, peso)
                return
        raise KeyError(f"aresta inexistente: {origem} -> {destino}")

    def vizinhos(self, vertice: Vertice) -> tuple[tuple[Vertice, float], ...]:
        if vertice not in self._adj:
            raise KeyError(f"vértice inexistente: {vertice}")
        return tuple(self._adj[vertice])

    def tem_aresta(self, origem: Vertice, destino: Vertice) -> bool:
        return any(vizinho == destino for vizinho, _ in self._adj.get(origem, []))

    def peso_aresta(self, origem: Vertice, destino: Vertice) -> float:
        for vizinho, peso in self._adj[origem]:
            if vizinho == destino:
                return peso
        raise KeyError(f"aresta inexistente: {origem} -> {destino}")

    def contem(self, vertice: Vertice) -> bool:
        return vertice in self._adj

    @property
    def ordem(self) -> int:
        return len(self._adj)

    @property
    def quantidade_arestas(self) -> int:
        total = sum(len(lista) for lista in self._adj.values())
        if self.direcionado:
            return total
        return total // 2

    def vertices(self) -> list[Vertice]:
        return list(self._adj)

    def arestas(self) -> list[tuple[Vertice, Vertice, float]]:
        vistas: set[object] = set()
        saida: list[tuple[Vertice, Vertice, float]] = []
        for origem, lista in self._adj.items():
            for destino, peso in lista:
                chave: object = (origem, destino) if self.direcionado else frozenset((origem, destino))
                if chave in vistas:
                    continue
                vistas.add(chave)
                saida.append((origem, destino, peso))
        return saida

    def validar_caminho(self, caminho: tuple[Vertice, ...] | list[Vertice]) -> tuple[bool, float | None]:
        if not caminho:
            return False, None
        for vertice in caminho:
            if vertice not in self._adj:
                return False, None
        soma = 0.0
        for origem, destino in zip(caminho, caminho[1:]):
            if not self.tem_aresta(origem, destino):
                return False, None
            soma += self.peso_aresta(origem, destino)
        return True, soma


def ler_grafo(caminho: str | Path) -> Grafo:
    """Lê ``# Metadados: V E TIPO`` seguido de linhas ``u v peso``."""

    texto = Path(caminho).read_text(encoding="utf-8")
    linhas = []
    for bruta in texto.splitlines():
        linha = bruta.split("#", 1)[0].strip()
        if linha:
            linhas.append(linha)
    if not linhas:
        raise ValueError("arquivo vazio")

    cabecalho = linhas[0].split()
    if len(cabecalho) != 3:
        raise ValueError("cabeçalho deve ser: V E TIPO")
    try:
        vertices_esperados = int(cabecalho[0])
        arestas_esperadas = int(cabecalho[1])
    except ValueError as erro:
        raise ValueError("V e E devem ser inteiros") from erro

    tipo = cabecalho[2].upper()
    if tipo in {"D", "DIRECIONADO"}:
        direcionado = True
    elif tipo in {"ND", "NAO_DIRECIONADO", "NÃO_DIRECIONADO"}:
        direcionado = False
    else:
        raise ValueError("TIPO deve ser D ou ND")

    if len(linhas) - 1 != arestas_esperadas:
        raise ValueError(
            f"o cabeçalho declara {arestas_esperadas} arestas, o arquivo tem {len(linhas) - 1}"
        )

    grafo = Grafo(direcionado)
    for linha in linhas[1:]:
        partes = linha.split()
        if len(partes) != 3:
            raise ValueError(f"aresta mal formada: {linha}")
        origem, destino, peso_texto = partes
        try:
            peso = float(peso_texto)
        except ValueError as erro:
            raise ValueError(f"peso inválido: {peso_texto}") from erro
        grafo.adicionar_aresta(_token(origem), _token(destino), peso)

    if grafo.ordem != vertices_esperados:
        raise ValueError(
            f"o cabeçalho declara {vertices_esperados} vértices, a leitura encontrou {grafo.ordem}"
        )
    if grafo.quantidade_arestas != arestas_esperadas:
        raise ValueError(
            f"o cabeçalho declara {arestas_esperadas} arestas, a leitura encontrou {grafo.quantidade_arestas}"
        )
    return grafo


def salvar_grafo(grafo: Grafo, caminho: str | Path) -> None:
    tipo = "D" if grafo.direcionado else "ND"
    arestas = grafo.arestas()
    linhas = [
        "# Metadados: V E TIPO",
        f"{grafo.ordem} {len(arestas)} {tipo}",
        "# Arestas: u v peso",
    ]
    for origem, destino, peso in arestas:
        linhas.append(f"{origem} {destino} {_formatar_peso(peso)}")
    Path(caminho).write_text("\n".join(linhas) + "\n", encoding="utf-8")


def _token(texto: str) -> Vertice:
    try:
        return int(texto)
    except ValueError:
        return texto


def _formatar_peso(peso: float) -> str:
    if float(peso).is_integer():
        return str(int(peso))
    return f"{peso:.6f}".rstrip("0").rstrip(".")
