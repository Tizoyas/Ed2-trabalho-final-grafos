"""Relatório técnico de no máximo quatro páginas."""

from __future__ import annotations

import json
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from PIL import Image

FONTE = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTE_NEGRITO = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
LARGURA_UTIL = 182


class Relatorio(FPDF):
    def header(self) -> None:
        if self.page_no() == 1:
            return
        self.set_font("DejaVu", "", 8)
        self.set_text_color(90, 90, 90)
        self.cell(
            0,
            5,
            "ED2 · BFS, DFS e Dijkstra · Yasmim Tizo",
            new_x=XPos.LMARGIN,
            new_y=YPos.NEXT,
        )
        self.set_draw_color(210, 210, 210)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(2)
        self.set_text_color(0, 0, 0)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("DejaVu", "", 8)
        self.set_text_color(90, 90, 90)
        self.cell(0, 6, f"{self.page_no()}/{{nb}}", align="R")
        self.set_text_color(0, 0, 0)


def gerar_pdf(resultado: dict, figuras: Path, destino: str | Path) -> Path:
    pdf = Relatorio(format="A4", unit="mm")
    pdf.set_auto_page_break(auto=True, margin=14)
    pdf.set_margins(14, 12, 14)
    pdf.alias_nb_pages()
    pdf.add_font("DejaVu", "", FONTE)
    pdf.add_font("DejaVu", "B", FONTE_NEGRITO)
    pdf.add_page()
    _capa(pdf)
    _secao(pdf, "1. Problema")
    _paragrafo(
        pdf,
        "O trabalho compara três buscas num grafo ponderado representado por lista de adjacência. "
        "A aresta pode ser dirigida ou não, e o peso é estritamente positivo. BFS e DFS foram "
        "tratadas em sala; Dijkstra entra como a busca que troca o critério de salto pelo critério "
        "de custo. As três devolvem o mesmo tipo de resultado: caminho, custo, nós visitados, "
        "tamanho máximo da fronteira e arestas examinadas.",
    )
    _secao(pdf, "2. Modelo e arquivo")
    _paragrafo(
        pdf,
        "O arquivo começa com o cabeçalho V E TIPO, em que TIPO é D ou ND, e segue com linhas "
        "u v peso. Comentários usam #. O leitor recusa peso não positivo, aresta duplicada e "
        "cabeçalho que não bate com o corpo. A lista de adjacência guarda, para cada vértice, "
        "os pares (vizinho, peso). Num grafo não dirigido a aresta é gravada nos dois sentidos.",
    )
    _secao(pdf, "3. As três buscas")
    _paragrafo(
        pdf,
        "BFS usa fila FIFO e marca o vértice ao entrar na fila. O primeiro caminho que alcança "
        "o destino é mínimo em saltos, com custo igual ao número de arestas. DFS iterativa usa "
        "pilha explícita e só marca o vértice quando ele sai da pilha; os vizinhos são empilhados "
        "em ordem inversa para repetir a ordem da versão recursiva. O custo também é contado em "
        "saltos, mas o caminho não é mínimo. A versão recursiva percorre a mesma regra e, se a "
        "pilha de chamadas estoura, devolve o erro em vez de derrubar o processo. Dijkstra usa "
        "heap binário de mínimo. Uma distância pior fica no heap até ser retirada e ignorada. "
        "O custo é a soma dos pesos. Com peso negativo o critério deixaria de valer; o programa "
        "não aceita esse caso.",
    )
    _secao(pdf, "4. O campus separa salto de custo")
    _paragrafo(
        pdf,
        "No grafo do campus, de CampusCentral até HospitalEscola, a BFS devolve "
        "CampusCentral, BlocoSaude, HospitalEscola: 2 saltos e peso 19. Dijkstra devolve "
        "CampusCentral, DataCenter, ServidorBorda, HospitalEscola: 3 saltos e peso 14. "
        "A rota mais curta em saltos é mais cara. DFS, nos dois exemplos pequenos, acompanha "
        "a recursão e no grafo dirigido A→D produz A, B, C, D (3 saltos), enquanto a BFS "
        "para em A, B, D (2 saltos, peso 6) e Dijkstra acha o peso 3.",
    )
    _secao(pdf, "5. Protocolo")
    limite = resultado["protocolo"]["limite_recursao"]
    _paragrafo(
        pdf,
        f"Os tamanhos são V = 1.000, 10.000 e 50.000. A malha é o caminho 0–1–…–(V−1) mais "
        f"a corda i—i+2. No cenário uniforme todo peso vale 1. No variado o caminho pesa 1 e "
        f"a corda pesa 100. A cadeia é só o caminho, para forçar profundidade. A estrela liga "
        f"o centro 0 a todas as folhas, para forçar largura. A consulta é sempre 0 → V−1. "
        f"O tempo é a mediana de time.perf_counter, com um aquecimento e cinco repetições "
        f"(três em V = 50.000), sem o traçador de memória. A memória é o pico de tracemalloc "
        f"numa execução à parte, com o grafo já montado. O limite de recursão deste "
        f"interpretador é {limite} quadros. Os invariantes do experimento são conferidos "
        f"pelo próprio benchmark e pelos testes automatizados.",
    )
    _secao(pdf, "6. Resultados")
    _paragrafo(pdf, _texto_resultados(resultado))
    _tabela_uniforme(pdf, resultado)
    pdf.ln(2)
    _tabela_variado(pdf, resultado)
    pdf.ln(2)
    _tabela_estresse(pdf, resultado)
    _secao(pdf, "7. Leitura")
    _paragrafo(pdf, _texto_leitura(resultado))
    _secao(pdf, "8. Gráficos")
    _grade(
        pdf,
        [
            (figuras / "tempo_vs_vertices.png", "Tempo na malha de pesos iguais a 1."),
            (figuras / "memoria_vs_vertices.png", "Pico de memória da busca, grafo já montado."),
            (figuras / "fronteira_vs_vertices.png", "Maior tamanho da fila, da pilha ou do heap."),
            (figuras / "fronteira_estresse.png", "Cadeia e estrela em escala logarítmica."),
        ],
    )
    _secao(pdf, "9. Onde isso aparece")
    _paragrafo(
        pdf,
        "No OSPF (RFC 2328) cada roteador monta a árvore de caminhos mínimos com Dijkstra. "
        "O peso é o custo administrativo do enlace. Se todos os custos fossem 1, a distância "
        "coincidiria com a BFS, como no primeiro cenário. O protocolo separa os dois critérios "
        "de propósito: saltos e custo não são a mesma grandeza, que é o que a malha de cordas "
        "caras mede.",
    )
    _paragrafo(
        pdf,
        "Um coletor web em largura segura na fila todas as URLs de um nível antes de descer. "
        "A fronteira cresce com a largura da teia, no mesmo formato da estrela. Uma descida "
        "recursiva segue um ramo até o limite da pilha de chamadas, no formato da cadeia. "
        "A pilha explícita permite cortar a profundidade e gravar a fronteira em disco.",
    )
    _paragrafo(
        pdf,
        "O coletor de Cheney (1970) copia o grafo de objetos vivos em largura e usa o próprio "
        "espaço de destino como fila. O custo de memória acompanha a largura da fronteira, "
        "não a profundidade. O gráfico da estrela é o caso ruim desse coletor; o da cadeia é "
        "o caso ruim da DFS recursiva. São limites diferentes.",
    )
    _paragrafo(
        pdf,
        "Numa rede social, “pessoas a dois saltos” é uma BFS com profundidade limitada. Quando "
        "a aresta passa a ter afinidade, o problema deixa de ser contagem de saltos e vira "
        "caminho mínimo ponderado. Usar BFS nesse grafo repete o erro do campus: a rota com "
        "menos pessoas no meio pode ser a de pior afinidade.",
    )
    _garantir_bloco(pdf, 36)
    _secao(pdf, "10. Conclusão")
    _paragrafo(
        pdf,
        "Com peso uniforme, BFS e Dijkstra concordam no custo e a fila é a estrutura mais "
        "simples. Com peso variado, minimizar saltos piora a soma, e o heap passa a ser "
        "necessário. A DFS não responde nenhuma das duas perguntas de otimalidade. A versão "
        "recursiva ainda depende da profundidade do ramo, não do número de vértices: a cadeia "
        "estoura com mil quadros e a estrela de 50.000 folhas não estoura. A fronteira que "
        "importa mudar de estrutura é a da BFS e a do heap, e ela acompanha a largura do grafo.",
    )
    _secao(pdf, "Referências")
    for cita in (
        "CORMEN, T. H. et al. Algoritmos: teoria e prática. 3. ed. Rio de Janeiro: Elsevier, 2012.",
        "DIJKSTRA, E. W. A note on two problems in connexion with graphs. Numerische Mathematik, v. 1, p. 269–271, 1959.",
        "MOY, J. OSPF Version 2. RFC 2328, 1998.",
        "CHENEY, C. J. A nonrecursive list compacting algorithm. Communications of the ACM, v. 13, n. 11, p. 677–678, 1970.",
        "NAJORK, M.; WIENER, J. L. Breadth-first crawling yields high-quality pages. In: WWW, 2001. p. 114–118.",
    ):
        _paragrafo(pdf, cita, tamanho=8, entrelinha=3.6)
    saida = Path(destino)
    saida.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(saida))
    if pdf.pages_count > 4:
        raise RuntimeError(f"relatório ficou com {pdf.pages_count} páginas; o limite é 4")
    return saida


def _capa(pdf: Relatorio) -> None:
    pdf.set_font("DejaVu", "", 9)
    pdf.set_text_color(70, 70, 70)
    pdf.cell(0, 4.5, "Universidade de Rio Verde · Estrutura de Dados 2 (ESW416)", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.cell(0, 4.5, "Prof. Me. Sandro Silva Moreira · Novembro de 2026", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)
    pdf.set_text_color(0, 0, 0)
    pdf.set_x(pdf.l_margin)
    pdf.set_font("DejaVu", "B", 14)
    pdf.multi_cell(
        0,
        6.2,
        "BFS, DFS e Dijkstra: salto, custo e tamanho da fronteira",
        new_x=XPos.LMARGIN,
        new_y=YPos.NEXT,
    )
    pdf.set_x(pdf.l_margin)
    pdf.set_font("DejaVu", "", 10)
    pdf.cell(0, 5, "Yasmim Tizo", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)


def _secao(pdf: Relatorio, titulo: str) -> None:
    pdf.ln(1.2)
    pdf.set_x(pdf.l_margin)
    pdf.set_font("DejaVu", "B", 11)
    pdf.multi_cell(0, 5, titulo, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(0.4)


def _paragrafo(pdf: Relatorio, texto: str, tamanho: float = 9, entrelinha: float = 4.15) -> None:
    pdf.set_x(pdf.l_margin)
    pdf.set_font("DejaVu", "", tamanho)
    pdf.multi_cell(0, entrelinha, texto, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(0.6)


def _texto_resultados(resultado: dict) -> str:
    uniforme = _do(resultado, "uniforme", 50_000)
    variado = _do(resultado, "variado", 50_000)
    cadeia = _do(resultado, "cadeia", 50_000)
    estrela = _do(resultado, "estrela", 50_000)
    saltos = _res(uniforme, "bfs")["saltos"]
    peso_bfs = _res(variado, "bfs")["soma_pesos"]
    return (
        f"Na malha uniforme o custo coincidiu em todos os tamanhos. Em V = 50.000, BFS e "
        f"Dijkstra gastam {saltos} saltos e a soma dos pesos é a mesma. "
        f"Na malha variada, Dijkstra segue o caminho e custa V−1; a BFS reduz os saltos e, "
        f"em V = 50.000, soma {_inteiro(peso_bfs)}. "
        f"Na cadeia de 50.000 vértices a fronteira da BFS fica em "
        f"{_res(cadeia, 'bfs')['tamanho_max_fronteira']} e a DFS recursiva estoura. "
        f"Na estrela, BFS e a pilha explícita retêm "
        f"{_inteiro(_res(estrela, 'bfs')['tamanho_max_fronteira'])} vértices, enquanto a "
        f"recursão desce no máximo {_res(estrela, 'dfs_recursivo')['tamanho_max_fronteira']} "
        f"quadros e termina."
    )


def _texto_leitura(resultado: dict) -> str:
    grande = _do(resultado, "uniforme", 50_000)
    variado = _do(resultado, "variado", 50_000)
    tempos = {nome: grande["algoritmos"][nome]["tempo_ms"] for nome in ("bfs", "dfs", "dijkstra")}
    fronteiras = {
        nome: grande["algoritmos"][nome]["resultado"]["tamanho_max_fronteira"]
        for nome in ("bfs", "dfs", "dijkstra")
    }
    return (
        f"Em V = 50.000, com pesos iguais a 1, a mediana foi {_ms(tempos['bfs'])} na BFS, "
        f"{_ms(tempos['dfs'])} na DFS iterativa e {_ms(tempos['dijkstra'])} em Dijkstra. "
        f"A BFS foi a mais rápida. A fronteira nessa malha foi {_inteiro(fronteiras['bfs'])} "
        f"na fila, {_inteiro(fronteiras['dfs'])} na pilha e {_inteiro(fronteiras['dijkstra'])} "
        f"no heap: a frente de busca é estreita, e a DFS segura quase todos os vértices porque "
        f"desce o caminho. A memória não segue essa proporção. O pico foi "
        f"{_kib(grande['algoritmos']['bfs']['memoria_kib'])} na BFS, "
        f"{_kib(grande['algoritmos']['dfs']['memoria_kib'])} na DFS e "
        f"{_kib(grande['algoritmos']['dijkstra']['memoria_kib'])} em Dijkstra. A pilha grande "
        f"pesa, e o mapa de distâncias também pesa quando a fronteira é pequena. "
        f"No cenário variado o heap chega a {_inteiro(_res(variado, 'dijkstra')['tamanho_max_fronteira'])} "
        f"entradas, contra {_inteiro(_res(variado, 'bfs')['tamanho_max_fronteira'])} da BFS, "
        f"porque distâncias já superadas continuam lá até serem retiradas. Ainda fica longe de V. "
        f"Na cadeia, DFS iterativa e Dijkstra completam o caminho com fronteira constante; a "
        f"recursiva não. Na estrela as três estruturas explícitas retêm V−1, e a recursão "
        f"continua com profundidade 2. Profundidade e largura cobram de estruturas diferentes, "
        f"e o pico de memória não é a mesma conta da fronteira."
    )


def _tabela_uniforme(pdf: Relatorio, resultado: dict) -> None:
    _garantir_bloco(pdf, 28)
    _legenda(pdf, "Malha uniforme: tempo mediano, saltos comuns e fronteira.")
    larguras = (22, 28, 32, 32, 22, 46)
    _linha(pdf, ("V", "saltos", "BFS (ms)", "Dijkstra (ms)", "DFS (ms)", "fronteira BFS / heap"), larguras, True)
    for vertices in (1000, 10_000, 50_000):
        item = _do(resultado, "uniforme", vertices)
        _linha(
            pdf,
            (
                _inteiro(vertices),
                str(_res(item, "bfs")["saltos"]),
                _ms(_alg(item, "bfs")["tempo_ms"], False),
                _ms(_alg(item, "dijkstra")["tempo_ms"], False),
                _ms(_alg(item, "dfs")["tempo_ms"], False),
                f"{_inteiro(_res(item, 'bfs')['tamanho_max_fronteira'])} / "
                f"{_inteiro(_res(item, 'dijkstra')['tamanho_max_fronteira'])}",
            ),
            larguras,
            False,
        )


def _tabela_variado(pdf: Relatorio, resultado: dict) -> None:
    _garantir_bloco(pdf, 28)
    _legenda(pdf, "Malha variada: a BFS economiza saltos e Dijkstra economiza peso.")
    larguras = (28, 38, 38, 39, 39)
    _linha(pdf, ("V", "saltos BFS", "saltos Dijkstra", "peso BFS", "peso Dijkstra"), larguras, True)
    for vertices in (1000, 10_000, 50_000):
        item = _do(resultado, "variado", vertices)
        _linha(
            pdf,
            (
                _inteiro(vertices),
                str(_res(item, "bfs")["saltos"]),
                str(_res(item, "dijkstra")["saltos"]),
                _inteiro(_res(item, "bfs")["soma_pesos"]),
                _inteiro(_res(item, "dijkstra")["soma_pesos"]),
            ),
            larguras,
            False,
        )


def _tabela_estresse(pdf: Relatorio, resultado: dict) -> None:
    _garantir_bloco(pdf, 28)
    _legenda(pdf, "Estresse: fronteira da BFS e profundidade da DFS recursiva.")
    larguras = (28, 36, 40, 40, 38)
    _linha(pdf, ("V", "fila na cadeia", "fila na estrela", "recursão cadeia", "recursão estrela"), larguras, True)
    for vertices in (1000, 10_000, 50_000):
        cadeia = _do(resultado, "cadeia", vertices)
        estrela = _do(resultado, "estrela", vertices)
        recursao_cadeia = "estouro" if _res(cadeia, "dfs_recursivo")["estouro_pilha"] else "ok"
        _linha(
            pdf,
            (
                _inteiro(vertices),
                str(_res(cadeia, "bfs")["tamanho_max_fronteira"]),
                _inteiro(_res(estrela, "bfs")["tamanho_max_fronteira"]),
                f"{recursao_cadeia} ({_res(cadeia, 'dfs_recursivo')['tamanho_max_fronteira']})",
                str(_res(estrela, "dfs_recursivo")["tamanho_max_fronteira"]),
            ),
            larguras,
            False,
        )


def _garantir_bloco(pdf: Relatorio, altura: float) -> None:
    if pdf.get_y() + altura > pdf.h - 16:
        pdf.add_page()


def _legenda(pdf: Relatorio, texto: str) -> None:
    pdf.set_x(pdf.l_margin)
    pdf.set_font("DejaVu", "B", 8)
    pdf.multi_cell(0, 3.8, texto, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(0.4)


def _linha(pdf: Relatorio, colunas: tuple[str, ...], larguras: tuple[int, ...], cabecalho: bool) -> None:
    pdf.set_x(pdf.l_margin)
    pdf.set_font("DejaVu", "B" if cabecalho else "", 7.5)
    if cabecalho:
        pdf.set_fill_color(236, 236, 236)
    for texto, largura in zip(colunas, larguras):
        pdf.cell(largura, 4.6, texto, border=1, fill=cabecalho, align="C")
    pdf.ln()


def _grade(pdf: Relatorio, itens: list[tuple[Path, str]]) -> None:
    largura = 88
    for indice in range(0, len(itens), 2):
        par = itens[indice : indice + 2]
        alturas = [_altura(caminho, largura) for caminho, _ in par]
        bloco = max(alturas) + 8
        if pdf.get_y() + bloco > pdf.h - 16:
            pdf.add_page()
        y = pdf.get_y()
        x = pdf.l_margin
        for (caminho, legenda), altura in zip(par, alturas):
            pdf.image(str(caminho), x=x, y=y, w=largura, h=altura)
            pdf.set_xy(x, y + altura + 0.6)
            pdf.set_font("DejaVu", "", 7.5)
            pdf.multi_cell(largura, 3.3, legenda)
            x += largura + 6
        pdf.set_y(y + bloco)


def _altura(caminho: Path, largura: float) -> float:
    with Image.open(caminho) as imagem:
        return largura * imagem.size[1] / imagem.size[0]


def _do(resultado: dict, cenario: str, vertices: int) -> dict:
    for item in resultado["cenarios"]:
        if item["cenario"] == cenario and item["vertices"] == vertices:
            return item
    raise KeyError(f"{cenario} {vertices}")


def _alg(item: dict, nome: str) -> dict:
    return item["algoritmos"][nome]


def _res(item: dict, nome: str) -> dict:
    return item["algoritmos"][nome]["resultado"]


def _inteiro(valor) -> str:
    return f"{int(valor):,}".replace(",", ".")


def _ms(valor: float, unidade: bool = True) -> str:
    texto = f"{valor:.1f}".replace(".", ",")
    return f"{texto} ms" if unidade else texto


def _kib(valor: float) -> str:
    if valor >= 1024:
        return f"{valor / 1024:.1f} MiB".replace(".", ",")
    return f"{valor:.0f} KiB".replace(".", ",")


def carregar_json(caminho: str | Path) -> dict:
    return json.loads(Path(caminho).read_text(encoding="utf-8"))
