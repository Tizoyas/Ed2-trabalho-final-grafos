"""Fila, pilha e heap de mínimo usados pelas buscas."""

from __future__ import annotations

import heapq
from collections import deque
from typing import Any


class Fila:
    """Fila FIFO. Registra o maior tamanho atingido."""

    def __init__(self) -> None:
        self._dados: deque[Any] = deque()
        self.tamanho_maximo = 0

    def enfileirar(self, item: Any) -> None:
        self._dados.append(item)
        if len(self._dados) > self.tamanho_maximo:
            self.tamanho_maximo = len(self._dados)

    def desenfileirar(self) -> Any:
        return self._dados.popleft()

    def vazia(self) -> bool:
        return not self._dados

    def __len__(self) -> int:
        return len(self._dados)


class Pilha:
    """Pilha LIFO explícita. Registra o maior tamanho atingido."""

    def __init__(self) -> None:
        self._dados: list[Any] = []
        self.tamanho_maximo = 0

    def empilhar(self, item: Any) -> None:
        self._dados.append(item)
        if len(self._dados) > self.tamanho_maximo:
            self.tamanho_maximo = len(self._dados)

    def desempilhar(self) -> Any:
        return self._dados.pop()

    def vazia(self) -> bool:
        return not self._dados

    def __len__(self) -> int:
        return len(self._dados)


class FilaDePrioridadeMinima:
    """Heap binário de mínimo. Empate pela ordem de inserção.

    A remoção é preguiçosa: uma chave superada permanece no heap até
    chegar ao topo. ``tamanho_maximo`` inclui essas entradas obsoletas.
    """

    def __init__(self) -> None:
        self._dados: list[tuple[float, int, Any]] = []
        self._sequencia = 0
        self.tamanho_maximo = 0

    def inserir(self, prioridade: float, item: Any) -> None:
        heapq.heappush(self._dados, (prioridade, self._sequencia, item))
        self._sequencia += 1
        if len(self._dados) > self.tamanho_maximo:
            self.tamanho_maximo = len(self._dados)

    def remover(self) -> tuple[float, Any]:
        prioridade, _, item = heapq.heappop(self._dados)
        return prioridade, item

    def vazia(self) -> bool:
        return not self._dados

    def __len__(self) -> int:
        return len(self._dados)
