"""Gera o relatorio final em ABNT (NBR 14724) a partir de docs/relatorio.md, docs/fet.md e docs/elementos.md.

Saida: output/Relatorio_Circuitos_Eletronicos.docx (+ .pdf, exportado pelo Word via src/exportar_pdf.ps1).

Uso:  uv run --no-project --with python-docx --with matplotlib python src/gerar_relatorio.py
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

matplotlib.rcParams["mathtext.fontset"] = "stix"

ROOT = Path(__file__).resolve().parent.parent
DOCS, OUT = ROOT / "docs", ROOT / "output"
NOME = "Relatorio_Circuitos_Eletronicos"

# ============================ DADOS DA CAPA (conferir) ============================
INSTITUICAO = "INSTITUTO FEDERAL DE EDUCAÇÃO, CIÊNCIA E TECNOLOGIA DO CEARÁ"
CURSO = "Curso de Computação"
DISCIPLINA = "Circuitos Eletrônicos"
EQUIPE = ["[NOMES DE TODOS OS INTEGRANTES DA EQUIPE]"]       # máx. 6, um por linha
PROFESSOR = "[Nome do professor]"
LOCAL, ANO = "[Cidade]", "2026"
TITULO = "SIMULAÇÃO DE CIRCUITOS COM AMPLIFICADOR OPERACIONAL E PESQUISA SOBRE TRANSISTORES A EFEITO DE CAMPO"
NATUREZA = (f"Relatório da 2ª etapa da disciplina de {DISCIPLINA}, semestre 2026.2, "
            f"composto pela simulação de três circuitos com amplificador operacional e por "
            f"pesquisa teórica sobre o transistor a efeito de campo (FET).")

# ================= ajustes sobre o texto de docs/relatorio.md =====================
# (trechos que citam arquivos/jargão do repositório, ou cuja numeração muda no PDF)
SUBST = [
    ("(valores típicos do datasheet TI)", "(valores típicos do datasheet da Texas Instruments; TEXAS INSTRUMENTS, [s.d.])"),
    (" Não se usa `.ic` + `uic`.", ""),
    # projeto 1
    ("![Esquemático do filtro](img/circ_filtro.jpg)\n\n### 2.1 Especificação", "### 2.1 Especificação"),
    ("### 2.3 Componentes e conexões\n", "### 2.3 Componentes e conexões\n\n![Esquemático do filtro passa-baixa Butterworth](img/circ_filtro.jpg)\n"),
    ("| Vin | `dc 0 ac 1` | `vin` | `0` | Fonte AC de 1 V (|Vout| = ganho em V/V) |",
     "| Vin | `dc 0 ac 1` | `vin` | `0` | Fonte AC de 1 V (\\|Vout\\| = ganho em V/V) |"),
    ("Netlist exata: `output/netlists/projeto1.cir`. Análise: `.ac dec 200 10 1meg`.", "Análise: `.ac dec 200 10 1meg`."),
    ("Fonte: `output/projeto1_tabela.txt`.\n\n", ""),
    ("**Gráfico:** `output/projeto1_bode.png` — curva simulada", "A {fig:projeto1_bode} mostra a curva simulada"),
    ("**Ganho total.** Atotal = 10^(26/20) = 19,9526 V/V.",
     "**Ganho total.**\n\n" + r"$$[_gt] A_{\mathrm{total}}=10^{26/20}=19{,}9526\ \mathrm{V/V}"),
    ("Regra geral (se o GBW for outro): x ≈ 1 − 4,5·(15000/GBW); R = x/(2π·15000·C).",
     "Regra geral (se o GBW for outro):\n\n" + r"$$[_rg] x\approx1-4{,}5\,\frac{15000}{GBW},\qquad R=\frac{x}{2\pi\cdot15000\cdot C}"),
    ("- A inclinação medida entre 5·fc e 20·fc é 60,74 dB/déc, dentro de ±2 dB/déc de 60.",
     "- A inclinação medida entre 5·fc e 20·fc é 60,74 dB/déc, próxima dos 60 dB/déc especificados."),
    ("**Resultado do Projeto 1:** todos os critérios atendidos.", "**Resultado do Projeto 1:** o filtro atende à especificação."),
    # projeto 2
    ("![Esquemático do gerador](img/circ_astavel.jpg)\n\n### 3.1 Especificação", "### 3.1 Especificação"),
    ("### 3.3 Componentes e conexões\n", "### 3.3 Componentes e conexões\n\n![Esquemático do gerador de onda quadrada (multivibrador astável)](img/circ_astavel.jpg)\n"),
    ("Netlist de exemplo: `output/netlists/projeto2_P1k83.cir` (`.tran 0 140u 0 20n`).", "Análise de exemplo: `.tran 0 140u 0 20n`."),
    ("Fonte: `output/projeto2_tabela.txt`. Quatro posições", "Quatro posições"),
    ("Teórico (memorial)", "Teórico"),
    ("O memorial estimava 1.830 Ω (critério: 1.800–2.100 Ω, OK)", "O cálculo teórico estimava 1.830 Ω"),
    ("pelo método da secante (6 iterações, partindo de 1 kΩ e 3 kΩ) →", "obtido por ajuste na simulação →"),
    ("⇒ a faixa **contém** 1–10 kHz (OK).", "⇒ a faixa **contém** 1–10 kHz."),
    ("**Resultado do Projeto 2:** todos os critérios atendidos. Ciclo de trabalho = 50,00 % em todas as posições.",
     "**Resultado do Projeto 2:** a faixa de 1 kHz a 10 kHz é coberta, com ciclo de trabalho de 50 % em todas as posições."),
    ("estimativa do memorial", "estimativa teórica"),
    ("**Varredura P × frequência** (`output/projeto2_p_vs_f.png`; ciclo de trabalho", "**Varredura P × frequência** (ciclo de trabalho"),
    ("**Gráficos:**\n- `output/projeto2_ondas.png`: grade 2×2 com 4 períodos finais de V(out) e da tensão no capacitor V(vm) para P = 0, 1,83 kΩ, 188,01 kΩ e 200 kΩ (título de cada painel traz a frequência medida).\n- `output/projeto2_p_vs_f.png`: P (kΩ) × f (Hz), eixo f em escala log, com linhas em 1 kHz e 10 kHz.",
     "A {fig:projeto2_ondas} mostra, em grade 2×2, os 4 períodos finais de V(out) e da tensão no capacitor V(vm) para P = 0, 1,83 kΩ, 188,01 kΩ e 200 kΩ (o título de cada painel traz a frequência medida). A {fig:projeto2_p_vs_f} relaciona P (kΩ) e f (Hz), com f em escala logarítmica e marcações em 1 kHz e 10 kHz."),
    # projeto 3
    ("![Esquemático do oscilador de Wien](img/circ_wien.jpg)\n\n### 4.1 Especificação", "### 4.1 Especificação"),
    ("### 4.3 Componentes e conexões\n", "### 4.3 Componentes e conexões\n\n![Esquemático do oscilador de Wien](img/circ_wien.jpg)\n"),
    ("Netlists: `output/netlists/projeto3_R12k68.cir` e `projeto3_R13k.cir` (`.tran 0 8m 0 0.1u`).", "Análise: `.tran 0 8m 0 0.1u`."),
    ("Fonte: `output/projeto3_tabela.txt`. Duas rodadas", "Duas rodadas"),
    ("**Gráficos:**\n- `output/projeto3_partida.png`: V(out) × t (0–8 ms), partida e estabilização (R = 12,68 kΩ).\n- `output/projeto3_zoom.png`: 4 ciclos na região estacionária.\n- `output/projeto3_fft.png`: espectro de 0 a 6·f (amplitude em dBV com a THD no título).\n- `output/projeto3_comparacao_R.png`: 4 ciclos finais com R = 12,68 kΩ × R = 13 kΩ, lado a lado, com fosc e erro em cada título.",
     "A {fig:projeto3_partida} mostra V(out) × t (0–8 ms), com a partida e a estabilização (R = 12,68 kΩ); a {fig:projeto3_zoom}, 4 ciclos na região estacionária; e a {fig:projeto3_comparacao_R}, os 4 ciclos finais com R = 12,68 kΩ e R = 13 kΩ, lado a lado, com fosc e erro em cada título."),
    ("![Espectro](../output/projeto3_fft.png)\n\n", ""),
    ("prevista no memorial", "prevista no cálculo teórico"),
    ("**Resultado do Projeto 3:** todos os critérios atendidos.", "**Resultado do Projeto 3:** o oscilador atende à especificação, oscilando em 14.952 Hz."),
]

# trechos removidos do texto de docs/relatorio.md (do marcador inicial até o marcador final, que é mantido)
CORTES = [
    ("**Tolerâncias (para montagem física).**", "### 4.3 Componentes e conexões"),                       # análise de tolerâncias
    ("**Espectro (R = 12,68 kΩ, FFT sobre número inteiro de ciclos):**", "**Outras grandezas observadas (R = 12,68 kΩ, regime):**"),  # THD, espectro e partida
]
# linhas removidas (início da linha)
CORTAR_LINHAS = ["- THD de 1,78 %", "- **Tolerâncias** (componentes reais)", "- Se o GBW do modelo for outro",
                 "- A medição do ciclo de trabalho foi corrigida"]
# colunas de critério de aceitação e linhas de THD saem das tabelas
COLUNAS_FORA = ("Critério", "Resultado")
LINHAS_FORA = ("THD",)

# títulos das tabelas/quadros de docs/relatorio.md, na ordem em que aparecem no PDF
# (Q = quadro, conteúdo descritivo; T = tabela, dados numéricos)
TITULOS_REL = [
    ("Q", "Dados acrescentados ao projeto e justificativas"),
    ("Q", "Componentes e conexões do filtro passa-baixa"),
    ("T", "Resultados da simulação AC do filtro passa-baixa"),
    ("T", "Ganho e fase do filtro em frequências adicionais"),
    ("Q", "Componentes e conexões do gerador de onda quadrada"),
    ("T", "Frequência de saída do gerador para quatro posições do potenciômetro"),
    ("T", "Níveis de saída e ciclo de trabalho do gerador"),
    ("T", "Frequência simulada do gerador em função de P"),
    ("Q", "Componentes e conexões do oscilador de Wien"),
    ("T", "Resultados da simulação do oscilador de Wien"),
]

# legendas e frase de citação das figuras que ainda não são citadas no texto
FIG_LEAD = {
    "circ_filtro": "O esquemático do filtro é apresentado na {ref}.",
    "projeto1_bode": None,
    "circ_astavel": "O esquemático do gerador é apresentado na {ref}.",
    "projeto2_ondas": None,
    "projeto2_p_vs_f": None,
    "circ_wien": "O esquemático do oscilador é apresentado na {ref}.",
    "projeto3_partida": None,
    "projeto3_zoom": None,
    "projeto3_fft": None,
    "projeto3_comparacao_R": None,
}
FIG_TITULO = {
    "projeto1_bode": "Resposta em frequência do filtro: simulada e teórica",
    "projeto2_ondas": "Formas de onda do gerador para quatro posições do potenciômetro",
    "projeto2_p_vs_f": "Frequência do gerador em função do potenciômetro P",
    "projeto3_partida": "Partida e estabilização do oscilador de Wien",
    "projeto3_zoom": "Oscilador de Wien em regime estacionário",
    "projeto3_fft": "Espectro do oscilador de Wien",
    "projeto3_comparacao_R": "Oscilador de Wien com R = 12,68 kΩ e R = 13 kΩ",
}
FONTE_FIG = "Fonte: Elaborada pelos autores (2026)."
FONTE_TAB = "Fonte: Elaborada pelos autores (2026)."


# =============================== PARSER DO MARKDOWN ===============================
def split_cells(line):
    inner = line.strip()
    inner = inner[1:-1] if inner.endswith("|") else inner[1:]
    cells = re.split(r"(?<!\\)\|", inner)
    return [c.strip().replace("\\|", "|") for c in cells]


def parse(text, shift=0, titulos=None):
    """Converte markdown em lista de blocos. `titulos`: lista (kind, titulo) consumida pelas tabelas sem <!--Q:-->."""
    lines = text.split("\n")
    blocks, i, n = [], 0, len(lines)
    pending = None
    starters = ("|", "```", "![", "$$", "#", "- ", "  - ", "<!--")
    while i < n:
        ln = lines[i]
        s = ln.strip()
        if not s or s == "---":
            i += 1
        elif s.startswith("```"):
            j = i + 1
            while not lines[j].strip().startswith("```"):
                j += 1
            blocks.append(("code", "\n".join(lines[i + 1:j])))
            i = j + 1
        elif s.startswith("<!--"):
            m = re.match(r"<!--([QT]):\s*(.*?)\s*-->", s)
            pending = (m.group(1), m.group(2))
            i += 1
        elif s.startswith("|"):
            j = i
            while j < n and lines[j].strip().startswith("|"):
                j += 1
            hdr = split_cells(lines[i])
            aligns = ["r" if c.endswith(":") and not c.startswith(":") else "l" for c in split_cells(lines[i + 1])]
            rows = [split_cells(r) for r in lines[i + 2:j]]
            if any(h in COLUNAS_FORA for h in hdr):          # sem colunas de critério de aceitação nem linhas de THD
                manter = [k for k, h in enumerate(hdr) if h not in COLUNAS_FORA]
                rows = [[r[k] for k in manter] for r in rows if not r[0].startswith(LINHAS_FORA)]
                hdr = [hdr[k] for k in manter]
                aligns = [aligns[k] for k in manter]
            for r in rows:
                assert len(r) == len(hdr), f"tabela com colunas inconsistentes: {r} vs {hdr}"
            kind, title = pending if pending else titulos.pop(0)
            pending = None
            fonte = FONTE_TAB
            if j < n and lines[j].startswith("Fonte:"):
                fonte, j = lines[j].strip(), j + 1
            blocks.append(("table", dict(header=hdr, rows=rows, aligns=aligns, kind=kind, title=title, fonte=fonte)))
            i = j
        elif s.startswith("!["):
            m = re.match(r"!\[(.*?)\]\((.*?)\)", s)
            key = Path(m.group(2)).stem
            title = FIG_TITULO.get(key, m.group(1))
            fonte, j = FONTE_FIG, i + 1
            if j < n and lines[j].startswith("Fonte:"):
                fonte, j = lines[j].strip(), j + 1
            blocks.append(("fig", dict(path=(DOCS / m.group(2)).resolve(), key=key, title=title, fonte=fonte)))
            i = j
        elif s.startswith("$$"):
            m = re.match(r"\$\$\[(\w+)\]\s*(.*?)(\$\$)?$", s)
            blocks.append(("eq", m.group(1), m.group(2)))
            i += 1
        elif s.startswith("#"):
            m = re.match(r"(#+)\s+(.*)", s)
            lvl = len(m.group(1)) + shift
            title = re.sub(r"^\d+(\.\d+)*\.?\s+", "", m.group(2)).strip()
            blocks.append(("h", lvl, title))
            i += 1
        elif re.match(r"^\s*- ", ln):
            lvl = 2 if ln.startswith("  ") else 1
            txt = [s[2:]]
            i += 1
            while i < n and lines[i].strip() and not re.match(r"^\s*- ", lines[i]) and not lines[i].strip().startswith(starters):
                txt.append(lines[i].strip()); i += 1
            blocks.append(("bullet", lvl, " ".join(txt)))
        elif re.match(r"^\d+\.\s", s):
            m = re.match(r"^(\d+)\.\s+(.*)", s)
            txt = [m.group(2)]
            i += 1
            while i < n and lines[i].strip() and not lines[i].strip().startswith(starters) and not re.match(r"^\d+\.\s", lines[i].strip()):
                txt.append(lines[i].strip()); i += 1
            blocks.append(("num", m.group(1), " ".join(txt)))
        else:
            txt = [s]
            i += 1
            while i < n and lines[i].strip() and not lines[i].strip().startswith(starters) and lines[i].strip() != "---" \
                    and not re.match(r"^\d+\.\s", lines[i].strip()):
                txt.append(lines[i].strip()); i += 1
            blocks.append(("p", " ".join(txt)))
    return blocks


def sections_of(text):
    """Divide docs/relatorio.md pelos '## N.' -> {N: corpo}."""
    out, cur = {}, None
    for ln in text.split("\n"):
        m = re.match(r"## (\d+)\.\s", ln)
        if m:
            cur = int(m.group(1)); out[cur] = []
        elif ln.startswith("## "):
            cur = None
        elif cur is not None:
            out[cur].append(ln)
    return {k: "\n".join(v) for k, v in out.items()}


def elementos(text):
    out, cur = {}, None
    for ln in text.split("\n"):
        if ln.startswith("# "):
            cur = ln[2:].strip(); out[cur] = []
        elif cur:
            out[cur].append(ln)
    return {k: "\n".join(v) for k, v in out.items()}


TEXTO_SIMULADOR = (
    "A simulação foi feita no LTspice, simulador de escolha da equipe, como o enunciado permite. "
    "As netlists foram montadas em Python com o PySpice. O amplificador operacional foi representado por um "
    "modelo comportamental do TL081, com produto ganho-banda (GBW), taxa de subida (*slew rate*) e saturação "
    "conforme a Seção 2.1."
)

# blocos de cálculo de docs/relatorio.md -> equações (LaTeX/mathtext). Chave: início da 1ª linha do bloco.
# ("eq", latex) = equação centralizada; ("p", texto) = frase de ligação.
CALCS = [
    # ---- Projeto 1 ----
    ("H2(s) = A2", [
        ("eq", r"H_2(s)=\frac{A_2\,\omega_0^2}{s^2+(3-A_2)\,\omega_0\,s+\omega_0^2},\qquad \omega_0=\frac{1}{RC},\qquad Q=\frac{1}{3-A_2}"),
        ("p", "Butterworth de 3ª ordem: (s + 1)(s² + s + 1), ou seja, um par de polos com Q = 1. Logo:"),
        ("eq", r"1=\frac{1}{3-A_2}\ \Rightarrow\ A_2=2\ (=6{,}02\ \mathrm{dB})\ \Rightarrow\ R_1=R_2=10\ \mathrm{k}\Omega"),
    ]),
    ("A1 = Atotal/A2", [
        ("eq", r"A_1=\frac{A_{\mathrm{total}}}{A_2}=\frac{19{,}9526}{2}=9{,}9763\ \Rightarrow\ \frac{R_1}{R_2}=8{,}9763"),
        ("eq", r"R_2=2\ \mathrm{k}\Omega\ \Rightarrow\ R_1=17{,}953\ \mathrm{k}\Omega\ \ \mathrm{(teórico)}"),
        ("p", "Valor comercial R1 = 18 kΩ:"),
        ("eq", r"A_1=1+\frac{18}{2}=10"),
        ("eq", r"A_{\mathrm{total,real}}=10\times2=20\ \mathrm{V/V}=26{,}0206\ \mathrm{dB}"),
        ("p", "Erro de 0,0206 dB (0,24 % em V/V)."),
    ]),
    ("fc = 1/(2πRC); C = 4,7 nF", [
        ("eq", r"f_c=\frac{1}{2\pi RC},\qquad C=4{,}7\ \mathrm{nF}\ \Rightarrow\ R=\frac{1}{2\pi\,(5000)\,(4{,}7\cdot10^{-9})}=6.772{,}6\ \Omega"),
        ("p", "Valor comercial R = 6,8 kΩ:"),
        ("eq", r"f_c=\frac{1}{2\pi\,(6800)\,(4{,}7\cdot10^{-9})}=4.979{,}8\ \mathrm{Hz}\qquad(\mathrm{erro}\ {-}0{,}40\ \%)"),
    ]),
    ("|H1|² = 1/(1 + x²)", [
        ("eq", r"|H_1|^2=\frac{1}{1+x^2},\qquad |H_2|^2=\frac{1}{1-x^2+x^4},\qquad |H_1|^2\,|H_2|^2=\frac{1}{1+x^6},\qquad x=\frac{f}{f_c}"),
        ("eq", r"|H(f)|=\frac{A_{\mathrm{total}}}{\sqrt{1+\left(f/f_c\right)^6}},\qquad A_{\mathrm{total}}=20\ \mathrm{V/V}"),
        ("p", "Em f = fc: 1ª seção −3,01 dB; 2ª seção 0 dB (Q = 1); total −3,01 dB. A fase em fc é:"),
        ("eq", r"\varphi(f_c)=-45^\circ-90^\circ=-135^\circ"),
        ("p", "e tende a −270° em alta frequência."),
    ]),
    # ---- Projeto 2 ----
    ("β = RA/(RA + RB)", [
        ("eq", r"\beta=\frac{R_A}{R_A+R_B}=\frac{10\ \mathrm{k}}{10\ \mathrm{k}+10\ \mathrm{k}}=0{,}5"),
        ("eq", r"V_{UT}=+\beta V_{\mathrm{sat}}=+6{,}75\ \mathrm{V},\qquad V_{LT}=-6{,}75\ \mathrm{V},\qquad V_{H}=13{,}5\ \mathrm{V}\qquad(V_{\mathrm{sat}}=13{,}5\ \mathrm{V})"),
    ]),
    ("vC(t) = Vsat", [
        ("eq", r"v_C(t)=V_{\mathrm{sat}}-(1+\beta)\,V_{\mathrm{sat}}\,e^{-t/(R_T C)}"),
        ("p", "A comutação ocorre quando vC = +β·Vsat. Por simetria, t2 = t1:"),
        ("eq", r"t_1=R_T C\,\ln\left[\frac{1+\beta}{1-\beta}\right]"),
        ("eq", r"T=2R_T C\,\ln 3=2{,}1972\,R_T C,\qquad f=\frac{1}{2{,}1972\,R_T C}"),
        ("p", "O ciclo de trabalho é de 50 %."),
    ]),
    ("RTmín (10 kHz)", [
        ("eq", r"R_{T,\mathrm{min}}\ (10\ \mathrm{kHz})=\frac{1}{2{,}1972\times10000\times2{,}2\cdot10^{-9}}=20{,}687\ \mathrm{k}\Omega"),
        ("eq", r"R_{T,\mathrm{max}}\ (1\ \mathrm{kHz})=\frac{1}{2{,}1972\times1000\times2{,}2\cdot10^{-9}}=206{,}87\ \mathrm{k}\Omega"),
        ("eq", r"P=R_{T,\mathrm{max}}-R_{T,\mathrm{min}}=186{,}19\ \mathrm{k}\Omega,\qquad R_F=R_{T,\mathrm{min}}=20{,}687\ \mathrm{k}\Omega"),
    ]),
    ("ts = 2·Vsat/SR", [
        ("eq", r"t_s=\frac{2V_{\mathrm{sat}}}{SR}=\frac{27\ \mathrm{V}}{13\ \mathrm{V/\mu s}}=2{,}077\ \mu\mathrm{s}\qquad(\mathrm{por\ transição})"),
        ("eq", r"T_{\mathrm{real}}\approx2{,}1972\,R_T C+2t_s"),
        ("p", "Com RF = 20 kΩ a frequência máxima não alcança 10 kHz; com RF = 18 kΩ alcança:"),
        ("eq", r"R_F=20\ \mathrm{k}\Omega:\quad T=96{,}68+4{,}15=100{,}83\ \mu\mathrm{s}\ \Rightarrow\ f_{\mathrm{max}}\approx9.918\ \mathrm{Hz}<10\ \mathrm{kHz}"),
        ("eq", r"R_F=18\ \mathrm{k}\Omega:\quad T=87{,}01+4{,}15=91{,}16\ \mu\mathrm{s}\ \Rightarrow\ f_{\mathrm{max}}\approx10.969\ \mathrm{Hz}\geq10\ \mathrm{kHz}"),
    ]),
    ("fmáx (P = 0):", [
        ("eq", r"f_{\mathrm{max}}\ (P=0):\quad f_{\mathrm{ideal}}=11.493\ \mathrm{Hz};\quad f_{\mathrm{slew}}\approx10.969\ \mathrm{Hz}"),
        ("eq", r"f_{\mathrm{min}}\ (P=200\ \mathrm{k}\Omega):\quad f_{\mathrm{ideal}}=949{,}0\ \mathrm{Hz};\quad f_{\mathrm{slew}}\approx945{,}2\ \mathrm{Hz}"),
        ("eq", r"f\in[945;\ 10.969]\ \mathrm{Hz}\ \supset\ [1000;\ 10000]\ \mathrm{Hz}"),
    ]),
    ("RT = (1/f − 2·ts)", [
        ("eq", r"R_T=\frac{1/f-2t_s}{2{,}1972\,C}"),
        ("eq", r"f=10\ \mathrm{kHz}:\quad R_T=19{,}83\ \mathrm{k}\Omega\ \Rightarrow\ P=1{,}83\ \mathrm{k}\Omega\qquad(\mathrm{sem\ slew}:\ 2{,}69\ \mathrm{k}\Omega)"),
        ("eq", r"f=1\ \mathrm{kHz}:\quad R_T=206{,}01\ \mathrm{k}\Omega\ \Rightarrow\ P=188{,}01\ \mathrm{k}\Omega\qquad(\mathrm{sem\ slew}:\ 188{,}87\ \mathrm{k}\Omega)"),
    ]),
    # ---- Projeto 3 ----
    ("Zs = R + 1/(jωC)", [
        ("eq", r"Z_s=R+\frac{1}{j\omega C},\qquad Z_p=\frac{R}{1+j\omega RC}"),
        ("eq", r"\beta(j\omega)=\frac{Z_p}{Z_s+Z_p}=\frac{1}{3+j\left(\omega RC-\frac{1}{\omega RC}\right)}"),
        ("p", "A fase é nula em ω0 e, nessa frequência, β = 1/3:"),
        ("eq", r"\omega_0=\frac{1}{RC}\ \Rightarrow\ f_0=\frac{1}{2\pi RC},\qquad \beta(f_0)=\frac{1}{3}"),
        ("eq", r"A\beta=1\angle0^\circ\ \Rightarrow\ A=3\ \Rightarrow\ 1+\frac{R_f}{R_g}=3\ \Rightarrow\ R_f=2R_g"),
    ]),
    ("C = 820 pF: R = 1/(2π", [
        ("eq", r"R=\frac{1}{2\pi\times15000\times820\cdot10^{-12}}=12.939{,}4\ \Omega\qquad(C=820\ \mathrm{pF})"),
        ("p", "Valor comercial R = 13 kΩ:"),
        ("eq", r"f_0=14.930{,}1\ \mathrm{Hz}\qquad(\mathrm{erro}\ {-}0{,}47\ \%)"),
    ]),
    ("A(f) = 3/(1 + j·3f/GBW)", [
        ("eq", r"A(f)=\frac{3}{1+j\,3f/GBW},\qquad \varphi=\arctan\left(\frac{3\times15000}{3\cdot10^{6}}\right)=0{,}859^\circ\qquad(f=15\ \mathrm{kHz})"),
        ("p", "A rede de Wien precisa adiantar a mesma fase:"),
        ("eq", r"\arctan\left[\frac{x-1/x}{3}\right]=-\arctan\left(\frac{3f}{GBW}\right)\ \Rightarrow\ x-\frac{1}{x}=-\frac{9f_{\mathrm{osc}}}{GBW},\qquad x=\frac{f_{\mathrm{osc}}}{f_0}"),
        ("eq", r"R=13\ \mathrm{k}\Omega:\quad x=0{,}97833\ \Rightarrow\ f_{\mathrm{osc}}=14.607\ \mathrm{Hz}"),
        ("p", "Erro total de −2,62 %: −0,47 % do valor comercial e −2,17 % do atraso do amp-op."),
    ]),
    ("Para fosc = 15 kHz", [
        ("eq", r"f_{\mathrm{osc}}=15\ \mathrm{kHz}:\quad x=0{,}97775\ \Rightarrow\ f_0=\frac{15000}{x}=15.341{,}3\ \mathrm{Hz}"),
        ("eq", r"R=\frac{1}{2\pi\times15341{,}3\times820\cdot10^{-12}}=12.651{,}6\ \Omega"),
        ("p", "Valor comercial: 12 kΩ + 680 Ω em série = 12,68 kΩ (nos dois braços):"),
        ("eq", r"f_0=15.306{,}9\ \mathrm{Hz}\ \Rightarrow\ f_{\mathrm{osc}}=0{,}97780\times15.306{,}9=14.967\ \mathrm{Hz}\qquad(-0{,}22\ \%)"),
    ]),
    ("Rg = 10 kΩ; Rf = R3 + R4", [
        ("p", "Rg = 10 kΩ e Rf = R3 + R4, com D1 e D2 (1N4148) em antiparalelo sobre R4. Com os diodos cortados (sinal pequeno), o ganho é maior que 3 e a oscilação cresce:"),
        ("eq", r"A=1+\frac{18\ \mathrm{k}+3{,}3\ \mathrm{k}}{10\ \mathrm{k}}=3{,}13>3"),
        ("p", "Com os diodos conduzindo (curto ideal), o ganho é menor que 3 e a oscilação diminui:"),
        ("eq", r"A=1+\frac{18\ \mathrm{k}}{10\ \mathrm{k}}=2{,}80<3"),
        ("p", "A amplitude se estabiliza onde o ganho médio vale 3. A folga de partida é:"),
        ("eq", r"\frac{3{,}13}{3}=1{,}043\qquad(+4{,}3\ \%)"),
    ]),
    ("Vout,p = 3·VD·Rg", [
        ("eq", r"V_{out,p}=\frac{3V_D R_g}{2R_g-R_3}=\frac{3\times0{,}6\times10\ \mathrm{k}}{20\ \mathrm{k}-18\ \mathrm{k}}=9{,}0\ \mathrm{V}\qquad(\approx18\ \mathrm{Vpp})"),
        ("eq", r"SR_{\mathrm{exigido}}=2\pi\times15000\times9=0{,}85\ \mathrm{V/\mu s}<13\ \mathrm{V/\mu s},\qquad 9\ \mathrm{V}<V_{\mathrm{sat}}"),
    ]),
    ("|Zs + Zp| em 15 kHz", [
        ("eq", r"|Z_s+Z_p|=27{,}2\ \mathrm{k}\Omega\qquad(15\ \mathrm{kHz},\ R=12{,}68\ \mathrm{k}\Omega,\ C=820\ \mathrm{pF})"),
        ("eq", r"R_3+R_4+R_g=31{,}3\ \mathrm{k}\Omega\qquad(28\ \mathrm{k}\Omega\ \mathrm{com\ diodos\ conduzindo})"),
        ("eq", r"R_{\mathrm{carga}}\approx14{,}5\ \mathrm{k}\Omega\ \ (13{,}8\ \mathrm{k}\Omega)\ >\ 10\ \mathrm{k}\Omega"),
    ]),
]


def converter_codigo(blocks):
    """Troca cada bloco de cálculo (texto monoespaçado) por equações tipográficas (CALCS)."""
    out, usados = [], set()
    for b in blocks:
        if b[0] != "code":
            out.append(b)
            continue
        primeira = b[1].split("\n")[0]
        for pref, itens in CALCS:
            if primeira.startswith(pref):
                usados.add(pref)
                out += [("eq", "_c", t) if k == "eq" else ("p", t) for k, t in itens]
                break
        else:
            raise AssertionError(f"bloco de código sem tradução: {primeira!r}")
    assert usados == {p for p, _ in CALCS}, {p for p, _ in CALCS} - usados
    return out


def montar():
    rel = (DOCS / "relatorio.md").read_text(encoding="utf-8")
    for old, new in SUBST:
        assert old in rel, f"trecho não encontrado em relatorio.md: {old[:70]!r}"
        rel = rel.replace(old, new)
    for ini, fim in CORTES:
        i, j = rel.index(ini), rel.index(fim)
        assert i < j, ini
        rel = rel[:i] + rel[j:]
    rel = "\n".join(ln for ln in rel.split("\n") if not ln.startswith(tuple(CORTAR_LINHAS)))
    sec = sections_of(rel)
    el = elementos((DOCS / "elementos.md").read_text(encoding="utf-8"))
    fet = (DOCS / "fet.md").read_text(encoding="utf-8")
    titulos = list(TITULOS_REL)
    b = []
    H = lambda lvl, t: [("h", lvl, t)]
    # 1 Introdução
    b += H(1, "INTRODUÇÃO") + parse(el["INTRODUÇÃO"])
    # 2 Metodologia
    b += H(1, "METODOLOGIA E FERRAMENTAS DE SIMULAÇÃO")
    b += H(2, "Dados acrescentados ao projeto e justificativas") + parse(sec[0], 0, titulos)
    b += H(2, "Simulador utilizado") + parse(TEXTO_SIMULADOR)
    partida = sec[1].split("### 1.3 Alimentação e partida")[1].split("### 1.4")[0]
    b += H(2, "Alimentação e partida dos osciladores") + parse(partida)
    # 3-5 Projetos
    for num, tit in ((2, "PROJETO 1 – FILTRO PASSA-BAIXA BUTTERWORTH"),
                     (3, "PROJETO 2 – GERADOR DE ONDA QUADRADA"),
                     (4, "PROJETO 3 – OSCILADOR SENOIDAL EM PONTE DE WIEN")):
        b += H(1, tit) + parse(sec[num], -1, titulos)
    # 6 FET
    b += parse(fet, 0, titulos)
    # 7 Considerações finais
    b += H(1, "CONSIDERAÇÕES FINAIS") + parse(el["CONCLUSÃO"])
    b += parse("Os resultados devem ser lidos com as seguintes observações:\n\n" + sec[6], 0, titulos)
    assert not titulos, f"tabelas sem uso: {titulos}"
    b = converter_codigo(b)
    b += [("h0", "REFERÊNCIAS")] + parse(el["REFERÊNCIAS"])
    return b, el


# ============================== NUMERAÇÃO E REFERÊNCIAS ==============================
def numerar(blocks):
    cont = {"q": 0, "t": 0, "f": 0, "e": 0}
    h = [0, 0, 0, 0]
    refs = {}
    out = []
    for blk in blocks:
        if blk[0] == "h":
            lvl = blk[1]
            h[lvl - 1] += 1
            for k in range(lvl, 4):
                h[k] = 0
            blk = ("h", lvl, blk[2], ".".join(str(x) for x in h[:lvl]))
        elif blk[0] == "table":
            d = blk[1]
            c = "q" if d["kind"] == "Q" else "t"
            cont[c] += 1
            d["num"] = cont[c]
            d["rotulo"] = ("Quadro" if c == "q" else "Tabela") + f" {cont[c]}"
        elif blk[0] == "fig":
            cont["f"] += 1
            blk[1]["num"] = cont["f"]
            refs["fig:" + blk[1]["key"]] = f"Figura {cont['f']}"
        elif blk[0] == "eq":
            if blk[1].startswith("_"):          # linha de cálculo: sem número
                blk = ("eq", blk[1], blk[2], None)
            else:
                cont["e"] += 1
                refs["eq:" + blk[1]] = f"({cont['e']})"
                blk = ("eq", blk[1], blk[2], cont["e"])
        out.append(blk)
    return out, refs


def resolver(txt, refs):
    def sub(m):
        k = m.group(1)
        assert k in refs, f"referência inexistente: {k}"
        return refs[k]
    return re.sub(r"\{((?:fig|eq):\w+)\}", sub, txt)


# ================================== DOCX ==================================
def fonte(style_or_font, name="Times New Roman", size=None, bold=None, italic=None):
    f = style_or_font.font if hasattr(style_or_font, "font") else style_or_font
    f.name = name
    if size: f.size = Pt(size)
    if bold is not None: f.bold = bold
    if italic is not None: f.italic = italic
    f.color.rgb = RGBColor(0, 0, 0)
    if hasattr(style_or_font, "element"):
        rpr = style_or_font.element.get_or_add_rPr()
        rf = rpr.get_or_add_rFonts()
        for a in ("w:ascii", "w:hAnsi", "w:eastAsia", "w:cs"):
            rf.set(qn(a), name)
        for a in ("w:asciiTheme", "w:hAnsiTheme", "w:eastAsiaTheme", "w:cstheme"):
            if rf.get(qn(a)) is not None:      # o tema do Word se sobrepõe à fonte escolhida
                del rf.attrib[qn(a)]


def novo_estilo(doc, nome, base="Normal"):
    st = doc.styles.add_style(nome, WD_STYLE_TYPE.PARAGRAPH)
    st.base_style = doc.styles[base]
    return st


def criar_estilos(doc):
    st = doc.styles
    n = st["Normal"]
    fonte(n, size=12)
    pf = n.paragraph_format
    pf.space_before = pf.space_after = Pt(0)
    pf.line_spacing = 1.0
    texto = novo_estilo(doc, "Texto ABNT")
    texto.paragraph_format.line_spacing = 1.5
    texto.paragraph_format.first_line_indent = Cm(1.25)
    texto.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    texto.paragraph_format.widow_control = True
    item = novo_estilo(doc, "Item ABNT")
    item.paragraph_format.line_spacing = 1.5
    item.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    # títulos (numeração literal no texto): 1 CAIXA ALTA negrito; 2 negrito; 3 normal; 4 itálico
    for lvl, (b, it) in {1: (True, False), 2: (True, False), 3: (False, False), 4: (False, True)}.items():
        h = st[f"Heading {lvl}"]
        fonte(h, size=12, bold=b, italic=it)
        h.paragraph_format.space_before = Pt(0 if lvl == 1 else 18)
        h.paragraph_format.space_after = Pt(12)
        h.paragraph_format.line_spacing = 1.0
        h.paragraph_format.keep_with_next = True
        h.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
        h.paragraph_format.page_break_before = (lvl == 1)
    sn = novo_estilo(doc, "Titulo sem numero")
    fonte(sn, size=12, bold=True)
    sn.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    sn.paragraph_format.space_after = Pt(18)
    sn.paragraph_format.keep_with_next = True
    leg = novo_estilo(doc, "Legenda ABNT")
    fonte(leg, size=10)
    leg.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    leg.paragraph_format.space_before = Pt(12)
    leg.paragraph_format.space_after = Pt(4)
    leg.paragraph_format.keep_with_next = True
    fon = novo_estilo(doc, "Fonte ABNT")
    fonte(fon, size=10)
    fon.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    fon.paragraph_format.space_before = Pt(4)
    fon.paragraph_format.space_after = Pt(14)
    cod = novo_estilo(doc, "Codigo ABNT")
    fonte(cod, name="Courier New", size=9.5)
    cod.paragraph_format.left_indent = Cm(0.5)
    cod.paragraph_format.space_before = Pt(4)
    cod.paragraph_format.space_after = Pt(10)
    tab = novo_estilo(doc, "Tabela ABNT")
    fonte(tab, size=10)
    tab.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
    res = novo_estilo(doc, "Resumo ABNT")
    res.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    ref = novo_estilo(doc, "Referencia ABNT")
    ref.paragraph_format.space_after = Pt(12)
    ref.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT


SUBSUP = re.compile(r"([A-Za-zμΩ])_(\{[^}]+\}|[A-Za-z0-9]+)|\^\(([^)]*)\)|\^(\{[^}]+\}|[0-9+\-−]+)")


def runs_texto(p, txt, size=None, bold=False, italic=False):
    """Escreve texto com **negrito**, *itálico*, `código` e sub/sobrescrito."""
    txt = txt.replace("\|", "|")
    for tok in re.split(r"(`[^`]+`)", txt):
        if not tok:
            continue
        if tok.startswith("`") and tok.endswith("`"):
            r = p.add_run(tok[1:-1])
            fonte(r, name="Courier New", size=(size - 1.5 if size else 10), bold=bold, italic=italic)
            continue
        for seg in re.split(r"(\*\*.+?\*\*)", tok):
            if seg.startswith("**") and seg.endswith("**") and len(seg) > 4:
                _italico(p, seg[2:-2], size, True, italic)
            else:
                _italico(p, seg, size, bold, italic)


def _italico(p, txt, size, bold, italic):
    for seg in re.split(r"(?<![\w*])(\*[^*\s][^*]*?\*)(?![\w*])", txt):
        if seg.startswith("*") and seg.endswith("*") and len(seg) > 2:
            _subsup(p, seg[1:-1], size, bold, True)
        else:
            _subsup(p, seg, size, bold, italic)


def _subsup(p, txt, size, bold, italic):
    pos = 0
    for m in SUBSUP.finditer(txt):
        _run(p, txt[pos:m.start()], size, bold, italic)
        if m.group(1):
            _run(p, m.group(1), size, bold, italic)
            _run(p, m.group(2).strip("{}"), size, bold, italic, sub=True)
        else:
            sup = m.group(3) if m.group(3) is not None else m.group(4).strip("{}")
            _run(p, sup, size, bold, italic, sup=True)
        pos = m.end()
    _run(p, txt[pos:], size, bold, italic)


def _run(p, txt, size, bold, italic, sub=False, sup=False):
    if not txt:
        return
    r = p.add_run(txt)
    if size: r.font.size = Pt(size)
    if bold: r.bold = True
    if italic: r.italic = True
    if sub: r.font.subscript = True
    if sup: r.font.superscript = True


def borda(cell_or_tbl_pr, **lados):
    b = OxmlElement("w:tblBorders" if cell_or_tbl_pr.tag.endswith("tblPr") else "w:tcBorders")
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        if lado in lados:
            e = OxmlElement(f"w:{lado}")
            e.set(qn("w:val"), lados[lado][0]); e.set(qn("w:sz"), str(lados[lado][1]))
            e.set(qn("w:space"), "0"); e.set(qn("w:color"), "000000")
            b.append(e)
    cell_or_tbl_pr.append(b)


def add_tabela(doc, d, refs):
    cap = doc.add_paragraph(style="Legenda ABNT")
    runs_texto(cap, f"{d['rotulo']} – {d['title']}", size=10)
    ncol = len(d["header"])
    t = doc.add_table(rows=1 + len(d["rows"]), cols=ncol)
    t.autofit = True
    tblPr = t._tbl.tblPr
    w = OxmlElement("w:tblW"); w.set(qn("w:type"), "pct"); w.set(qn("w:w"), "5000")
    for old in tblPr.findall(qn("w:tblW")):
        tblPr.remove(old)
    tblPr.append(w)
    mar = OxmlElement("w:tblCellMar")
    for lado, v in (("top", 25), ("left", 70), ("bottom", 25), ("right", 70)):
        e = OxmlElement(f"w:{lado}"); e.set(qn("w:w"), str(v)); e.set(qn("w:type"), "dxa"); mar.append(e)
    tblPr.append(mar)
    if d["kind"] == "Q":   # quadro: fechado
        borda(tblPr, top=("single", 8), left=("single", 8), bottom=("single", 8), right=("single", 8),
              insideH=("single", 4), insideV=("single", 4))
    else:                  # tabela (IBGE): só horizontais, sem fechamento lateral
        borda(tblPr, top=("single", 8), bottom=("single", 8))
    for ri, linha in enumerate([d["header"]] + d["rows"]):
        row = t.rows[ri]
        trPr = row._tr.get_or_add_trPr()
        trPr.append(OxmlElement("w:cantSplit"))
        if ri == 0:
            trPr.append(OxmlElement("w:tblHeader"))
        for ci, txt in enumerate(linha):
            c = row.cells[ci]
            p = c.paragraphs[0]
            p.style = doc.styles["Tabela ABNT"]
            if d["aligns"][ci] == "r" and ri > 0:
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            if ri == 0:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            runs_texto(p, resolver(txt, refs), size=10, bold=(ri == 0))
            p.paragraph_format.keep_with_next = True   # mantém tabela e "Fonte" na mesma página
            if ri == 0 and d["kind"] == "T":
                borda(c._tc.get_or_add_tcPr(), bottom=("single", 6))
    f = doc.add_paragraph(style="Fonte ABNT")
    runs_texto(f, resolver(d["fonte"], refs), size=10)


def add_figura(doc, d, refs):
    cap = doc.add_paragraph(style="Legenda ABNT")
    runs_texto(cap, f"Figura {d['num']} – {d['title']}", size=10)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_with_next = True
    from PIL import Image
    with Image.open(d["path"]) as im:
        w, h = im.size
    larg = min(16.0, 11.5 * w / h)
    p.add_run().add_picture(str(d["path"]), width=Cm(larg))
    f = doc.add_paragraph(style="Fonte ABNT")
    runs_texto(f, resolver(d["fonte"], refs), size=10)


def add_equacao(doc, key, latex, num, tmp):
    png = tmp / f"eq_{abs(hash((key, latex)))}.png"
    fig = plt.figure(figsize=(0.1, 0.1))
    fig.text(0, 0, f"${latex}$", fontsize=13.5)
    fig.savefig(png, dpi=300, bbox_inches="tight", pad_inches=0.04, transparent=True)
    plt.close(fig)
    from PIL import Image
    with Image.open(png) as im:
        w, h = im.size
    p = doc.add_paragraph()
    p.paragraph_format.line_spacing = 1.5 if num else 1.15
    p.paragraph_format.space_before = Pt(6 if num else 3)
    p.paragraph_format.space_after = Pt(6 if num else 3)
    p.paragraph_format.keep_together = True
    larg = min(w / 300 * 2.54, 15.0 if num else 16.0)
    if num:
        ts = p.paragraph_format.tab_stops
        ts.add_tab_stop(Cm(8), WD_TAB_ALIGNMENT.CENTER)
        ts.add_tab_stop(Cm(16), WD_TAB_ALIGNMENT.RIGHT)
        p.add_run("\t")
        p.add_run().add_picture(str(png), width=Cm(larg))
        p.add_run(f"\t({num})")
    else:                                   # linha de cálculo: centralizada, sem número
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.add_run().add_picture(str(png), width=Cm(larg))


def campo(par, instr, texto_cache=""):
    """Insere um campo complexo do Word (TOC, PAGE...)."""
    for tipo, extra in (("begin", None), (None, instr), ("separate", None), (None, texto_cache), ("end", None)):
        r = par.add_run()
        if tipo:
            fc = OxmlElement("w:fldChar"); fc.set(qn("w:fldCharType"), tipo); r._r.append(fc)
        elif extra is instr:
            it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = instr; r._r.append(it)
        else:
            r.text = texto_cache


def par(doc, txt="", style=None, align=None, size=None, bold=None, before=None, after=None, indent=None):
    p = doc.add_paragraph(style=style)
    if align is not None: p.alignment = align
    if before is not None: p.paragraph_format.space_before = Pt(before)
    if after is not None: p.paragraph_format.space_after = Pt(after)
    if indent is not None: p.paragraph_format.left_indent = Cm(indent)
    if txt:
        r = p.add_run(txt)
        if size: r.font.size = Pt(size)
        if bold is not None: r.bold = bold
    return p


def pre_textuais(doc, el):
    C, J = WD_ALIGN_PARAGRAPH.CENTER, WD_ALIGN_PARAGRAPH.JUSTIFY
    # --- capa ---
    par(doc, INSTITUICAO, align=C, bold=True)
    par(doc, CURSO, align=C, before=6)
    par(doc, f"Disciplina: {DISCIPLINA}", align=C, before=6)
    par(doc, "", before=130)
    for nome in EQUIPE:
        par(doc, nome, align=C, before=0)
    par(doc, "", before=110)
    par(doc, TITULO, align=C, bold=True)
    par(doc, "", before=150)
    par(doc, LOCAL, align=C)
    par(doc, ANO, align=C)
    doc.add_page_break()
    # --- folha de rosto ---
    for nome in EQUIPE:
        par(doc, nome, align=C)
    par(doc, "", before=120)
    par(doc, TITULO, align=C, bold=True)
    par(doc, "", before=60)
    p = par(doc, NATUREZA, align=J, size=11, indent=7.5)
    par(doc, f"Professor: {PROFESSOR}", align=J, size=11, indent=7.5, before=8)
    par(doc, "", before=90)
    par(doc, LOCAL, align=C)
    par(doc, ANO, align=C)
    doc.add_page_break()
    # --- resumo ---
    par(doc, "RESUMO", style="Titulo sem numero")
    p = doc.add_paragraph(style="Resumo ABNT")
    runs_texto(p, el["RESUMO"].strip())
    p = doc.add_paragraph(style="Resumo ABNT")
    p.paragraph_format.space_before = Pt(12)
    r = p.add_run("Palavras-chave: "); r.bold = True
    runs_texto(p, el["PALAVRAS-CHAVE"].strip())
    doc.add_page_break()
    # --- sumário ---
    par(doc, "SUMÁRIO", style="Titulo sem numero")
    p = doc.add_paragraph()
    campo(p, 'TOC \\o "1-3" \\h \\z \\u', "Atualize o campo (F9) para gerar o sumário.")


def cabecalho_numeracao(section):
    section.header.is_linked_to_previous = False
    p = section.header.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    campo(p, "PAGE", "1")
    for r in p.runs:
        fonte(r.font, size=10)
        r.font.size = Pt(10)


def construir():
    blocks, el = montar()
    blocks, refs = numerar(blocks)
    tmp = Path(tempfile.mkdtemp(prefix="relatorio_eq_"))
    doc = Document()
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21), Cm(29.7)
    sec.top_margin, sec.left_margin, sec.bottom_margin, sec.right_margin = Cm(3), Cm(3), Cm(2), Cm(2)
    sec.header_distance = Cm(2)
    criar_estilos(doc)
    pre_textuais(doc, el)
    # seção textual: numeração visível a partir da Introdução (as páginas anteriores são contadas)
    s2 = doc.add_section(WD_SECTION.NEW_PAGE)
    cabecalho_numeracao(s2)
    vistas_fig = set()
    for blk in blocks:
        k = blk[0]
        if k == "h":
            _, lvl, titulo, num = blk
            p = doc.add_paragraph(style=f"Heading {min(lvl, 4)}")
            runs_texto(p, f"{num} {titulo}")
        elif k == "h0":
            p = doc.add_paragraph(style="Heading 1")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            runs_texto(p, blk[1])
        elif k == "p":
            txt = resolver(blk[1], refs)
            for key in re.findall(r"\{fig:(\w+)\}", blk[1]):
                vistas_fig.add(key)
            ref_style = "Referencia ABNT" if "TEXAS" in txt[:10] or re.match(r"^[A-ZÇÃ ]{4,},", txt) else "Texto ABNT"
            p = doc.add_paragraph(style=ref_style)
            runs_texto(p, txt)
        elif k == "bullet":
            _, lvl, txt = blk
            for key in re.findall(r"\{fig:(\w+)\}", txt):
                vistas_fig.add(key)
            p = doc.add_paragraph(style="Item ABNT")
            esq = 1.9 if lvl == 1 else 2.9
            p.paragraph_format.left_indent = Cm(esq)
            p.paragraph_format.first_line_indent = Cm(-0.6)
            p.add_run("•\t" if lvl == 1 else "–\t")
            runs_texto(p, resolver(txt, refs))
        elif k == "num":
            p = doc.add_paragraph(style="Item ABNT")
            p.paragraph_format.left_indent = Cm(1.9)
            p.paragraph_format.first_line_indent = Cm(-0.7)
            p.add_run(f"{blk[1]}.\t")
            runs_texto(p, resolver(blk[2], refs))
        elif k == "code":
            p = doc.add_paragraph(style="Codigo ABNT")
            p.paragraph_format.keep_together = True
            linhas = blk[1].split("\n")
            for i, ln in enumerate(linhas):
                r = p.add_run(ln)
                if i < len(linhas) - 1:
                    r.add_break()
        elif k == "table":
            d = blk[1]
            lead = f"{'O' if d['kind'] == 'Q' else 'A'} {d['rotulo']} apresenta {d['title'][0].lower() + d['title'][1:]}."
            p = doc.add_paragraph(style="Texto ABNT")
            runs_texto(p, lead)
            add_tabela(doc, d, refs)
        elif k == "fig":
            d = blk[1]
            if d["key"] not in vistas_fig:
                lead = FIG_LEAD.get(d["key"])
                assert lead, f"figura {d['key']} não é citada no texto antes de aparecer"
                p = doc.add_paragraph(style="Texto ABNT")
                runs_texto(p, lead.replace("{ref}", f"Figura {d['num']}"))
            add_figura(doc, d, refs)
        elif k == "eq":
            add_equacao(doc, blk[1], blk[2], blk[3], tmp)
    # figuras citadas só depois de aparecerem seriam erro de ABNT: checagem
    for blk in blocks:
        if blk[0] == "fig":
            assert blk[1]["key"] in vistas_fig or FIG_LEAD.get(blk[1]["key"]), blk[1]["key"]
    doc.core_properties.title = TITULO.capitalize()
    doc.core_properties.author = "Equipe"
    OUT.mkdir(exist_ok=True)
    docx = OUT / f"{NOME}.docx"
    doc.save(docx)
    print("docx:", docx)
    # índice de títulos, para conferência
    for blk in blocks:
        if blk[0] == "h":
            print("  " * (blk[1] - 1) + f"{blk[3]} {blk[2]}")
    return docx


def exportar_pdf(docx):
    pdf = docx.with_suffix(".pdf")
    r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                        str(ROOT / "src" / "exportar_pdf.ps1"), "-Docx", str(docx), "-Pdf", str(pdf)],
                       capture_output=True, text=True)
    print(r.stdout.strip()); print(r.stderr.strip(), file=sys.stderr)
    return pdf


if __name__ == "__main__":
    d = construir()
    if "--sem-pdf" not in sys.argv:
        exportar_pdf(d)
