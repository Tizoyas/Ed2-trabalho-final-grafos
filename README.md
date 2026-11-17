# BFS, DFS e Dijkstra

Trabalho final de Estrutura de Dados 2 (ESW416), Universidade de Rio Verde.
Prof. Me. Sandro Silva Moreira. Yasmim Tizo.

O programa lê um grafo ponderado em lista de adjacência, com aresta dirigida ou não e peso estritamente positivo, e compara quatro buscas:

- BFS, com fila FIFO. O custo é o número de saltos.
- DFS iterativa, com pilha explícita. O vértice é marcado ao sair da pilha, na mesma ordem da recursão. O custo também é o número de saltos, sem garantia de mínimo.
- DFS recursiva, para mostrar o estouro da pilha de chamadas.
- Dijkstra, com heap de mínimo e remoção preguiçosa. O custo é a soma dos pesos.

Cada busca devolve caminho, custo, nós visitados, tamanho máximo da fronteira e arestas examinadas.

## Formato do arquivo

```
# Metadados: V E TIPO
8 11 ND
# Arestas: u v peso
CampusCentral BlocoEngenharia 3
```

`TIPO` é `D` (dirigido) ou `ND` (não dirigido). Linhas com `#` são comentários. Peso não positivo, aresta repetida e cabeçalho incoerente são recusados. Há dois exemplos em `data/`.

## Como executar

Requer Python 3.11 ou superior.

```bash
pip install -r requirements.txt
python main.py data/exemplo_campus.txt CampusCentral HospitalEscola
python -m pytest
python benchmark.py
python gerar_relatorio.py
```

`benchmark.py` mede V = 1.000, 10.000 e 50.000, grava `benchmarks/resultados.json` e os quatro gráficos. `gerar_relatorio.py` monta `relatorio/Trabalho_Final_ED2.pdf` (no máximo quatro páginas). Os resultados já versionados foram produzidos por esses comandos.

Os cenários são:

1. Malha com todos os pesos iguais a 1. BFS e Dijkstra concordam no custo.
2. A mesma malha com o caminho de peso 1 e as cordas de peso 100. BFS reduz saltos e aumenta o peso; Dijkstra faz o contrário.
3. Cadeia, para estourar a DFS recursiva com fronteira constante, e estrela, para reter Θ(V) vértices na fila, na pilha explícita e no heap sem estourar a recursão.

## Layout

```
ed2grafos/          grafo, buscas, geradores, benchmark, gráficos e PDF
tests/              pytest
data/               exemplos
benchmarks/         medições e figuras
relatorio/          Trabalho_Final_ED2.pdf
main.py             comparação a partir de um arquivo
```
