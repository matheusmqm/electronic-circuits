"""Desenha os esquematicos dos tres circuitos (schemdraw) a partir das tabelas de conexoes do memorial.
Convencao: amp-op com entrada + (in2) em cima e - (in1) embaixo; realimentacao por baixo."""
import matplotlib; matplotlib.use("Agg")
import schemdraw
import schemdraw.elements as e
from medidas import OUT

schemdraw.config(fontsize=10, unit=3)


def gnd(d, p):
    d += e.Ground().at(p)


def vert(d, el, texto, lado="r", at=None):
    """Adiciona elemento vertical (descendo) e coloca o rotulo ao lado do ponto medio."""
    e_ = d.add((el.at(at) if at is not None else el).down())
    mx, my = (e_.start.x + e_.end.x) / 2, (e_.start.y + e_.end.y) / 2
    dx = 0.25 if lado == "r" else -0.25
    d += e.Label().at((mx + dx, my)).label(texto, halign="left" if lado == "r" else "right")
    return e_


def opamp(d, x, y, nome):
    """Amp-op com a entrada + em (x, y) (em cima) e - 1,25 abaixo."""
    U = d.add(e.Opamp(leads=True).anchor("in2").at((x, y)).flip())
    d += e.Label().at((U.center.x - 0.15, U.center.y)).label(f"{nome} TL081", fontsize=8)
    return U


def secao_nao_inversora(d, U, rf, rg, nome_node, xo):
    """Divisor de realimentacao por baixo: no b em in1 -> desce -> (Rf ate a saida) e Rg ao terra."""
    d += e.Line().at(U.in1).left(0.8)
    d += e.Dot().label(nome_node, loc="left")
    d += e.Line().down(1.3)
    d += e.Dot()
    d.push()
    d += e.Resistor().right().tox(xo).label(rf, loc="bottom")
    d += e.Line().up().toy(U.out.y)
    d.pop()
    vert(d, e.Resistor(), rg, "r")
    gnd(d, d.here)


def filtro():
    with schemdraw.Drawing(show=False) as d:
        d += e.SourceSin().at((0, 0)).up().label("Vin AC 1 V", loc="left")
        d += e.Line().right(0.4)
        d += e.Resistor().right().label("R1a 6,8k")
        d += e.Dot().label("a", loc="top")
        d.push()
        vert(d, e.Capacitor(), "C1a 4,7n", "l")
        gnd(d, d.here)
        d.pop()
        d += e.Line().right(2.0)
        U1 = opamp(d, d.here.x, d.here.y, "U1")
        xo1 = U1.out.x + 1.2
        d += e.Line().at(U1.out).right(1.2)
        d += e.Dot().label("o1", loc="top")
        d.push()
        # a linha de realimentacao de U1 entra por baixo em xo1
        secao_nao_inversora(d, U1, "R1f 18k", "R1g 2k", "b", xo1)
        d.pop()
        # 2a secao (Sallen-Key)
        d += e.Resistor().right().label("R2a 6,8k")
        d += e.Dot().label("n3", loc="top")
        n3 = d.here
        d += e.Resistor().right().label("R2b 6,8k")
        d += e.Dot().label("n4", loc="top")
        d.push()
        vert(d, e.Capacitor(), "C2a 4,7n", "l")
        gnd(d, d.here)
        d.pop()
        d += e.Line().right(2.0)
        U2 = opamp(d, d.here.x, d.here.y, "U2")
        xo2 = U2.out.x + 1.2
        d += e.Line().at(U2.out).right(1.2)
        d += e.Dot().label("out", loc="top")
        d.push()
        d += e.Line().right(0.8)
        d.pop()
        d.push()
        # C2f: da saida, por cima, ate n3
        d += e.Line().up(1.8)
        d += e.Capacitor().left().tox(n3.x).label("C2f 4,7n", loc="top")
        d += e.Line().down().toy(n3.y)
        d.pop()
        secao_nao_inversora(d, U2, "R2f 10k", "R2g 10k", "n5", xo2)
        d.save(str(OUT / "projeto1_esquematico.png"), dpi=150)


def astavel():
    with schemdraw.Drawing(show=False) as d:
        U = opamp(d, 6, 0, "U1")
        xo = U.out.x + 1.2
        xvm = U.in1.x - 1.0           # no vm (mais proximo)
        xvp = xvm - 2.6               # no vp (mais afastado)
        # saida e positiva (RB por cima, ate vp)
        d += e.Line().at(U.out).right(1.2)
        d += e.Dot().label("out", loc="top")
        d.push()
        d += e.Line().right(0.8)
        d.pop()
        d.push()
        d += e.Line().up().toy(U.in2.y + 2.0)
        d += e.Resistor().left().tox(xvp).label("RB 10k", loc="top")
        d += e.Line().down().toy(U.in2.y)
        d += e.Dot().label("vp", loc="left")
        d.push()
        d += e.Line().right().tox(U.in2.x)
        d.pop()
        vert(d, e.Resistor(), "RA 10k", "l")
        gnd(d, d.here)
        d.pop()
        # realimentacao negativa por baixo: vm -> J -> P -> rt -> RF -> out
        d += e.Line().at(U.in1).left().tox(xvm)
        d += e.Dot().label("vm", loc="top")
        d += e.Line().down(1.6)
        d += e.Dot()
        d.push()
        xm = (xvm + xo) / 2
        d += e.Potentiometer().right().tox(xm).label("P 0-200k", loc="bottom")
        d += e.Dot().label("rt", loc="top")
        d += e.Resistor().right().tox(xo).label("RF 18k", loc="bottom")
        d += e.Line().up().toy(U.out.y)
        d.pop()
        vert(d, e.Capacitor(), "CT 2,2n", "r")
        gnd(d, d.here)
        d += e.Label().at((xvp, U.in2.y + 3.2)).label(
            "Partida (so na simulacao): pulso Ikick 2 uA / 1 us no no vp", fontsize=8, halign="left")
        d.save(str(OUT / "projeto2_esquematico.png"), dpi=150)


def wien():
    with schemdraw.Drawing(show=False) as d:
        U = opamp(d, 9, 0, "U1")
        xo = U.out.x + 1.2
        xvm = U.in1.x - 4.2
        xvp = xvm - 2.4
        d += e.Line().at(U.out).right(1.2)
        d += e.Dot().label("out", loc="top")
        d.push()
        d += e.Line().right(0.8)
        d.pop()
        # ramo serie por cima: out -> Rs -> ws -> Cs -> vp
        d.push()
        d += e.Line().up().toy(U.in2.y + 2.0)
        xm = (xo + xvp) / 2
        d += e.Resistor().left().tox(xm).label("Rs 12,68k", loc="top")
        d += e.Dot().label("ws", loc="top")
        d += e.Capacitor().left().tox(xvp).label("Cs 820p", loc="top")
        d += e.Line().down().toy(U.in2.y)
        d += e.Dot().label("vp", loc="top")
        d.push()
        d += e.Line().right().tox(U.in2.x)
        d.pop()
        d.push()
        vert(d, e.Resistor(), "Rp 12,68k", "r")
        gnd(d, d.here)
        d.pop()
        d += e.Line().left(2.0)
        vert(d, e.Capacitor(), "Cp 820p", "r")
        gnd(d, d.here)
        d.pop()
        # ganho: out -> R3 -> x -> (R4 || D1,D2) -> J -> vm ; Rg ao terra
        yJ = U.in1.y - 2.8
        d += e.Line().at(U.in1).left().tox(xvm)
        d += e.Dot().label("vm", loc="top")
        d += e.Line().down().toy(yJ)
        d += e.Dot()
        J = d.here
        d.push()
        vert(d, e.Resistor(), "Rg 10k", "r")
        gnd(d, d.here)
        d.pop()
        xx = xo - 3.6                      # no x
        xl = xx - 3.0                      # lado do vm do bloco R4 || diodos
        d += e.Line().at(J).right().tox(xl)
        d += e.Dot()
        d.push()
        d += e.Resistor().right().tox(xx).label("R4 3,3k", loc="bottom")
        d += e.Dot().label("x", loc="bottom")
        d.pop()
        d.push()
        d += e.Line().up(1.4)
        d += e.Diode().right().tox(xx).label("D2", loc="top")
        d += e.Line().down().toy(yJ)
        d.pop()
        d += e.Line().at((xx, yJ)).down(1.4)
        d += e.Diode().left().tox(xl).label("D1", loc="bottom")
        d += e.Line().up().toy(yJ)
        # do x ate a saida
        d += e.Resistor().at((xx, yJ)).right().tox(xo).label("R3 18k", loc="bottom")
        d += e.Line().up().toy(U.out.y)
        d.save(str(OUT / "projeto3_esquematico.png"), dpi=150)


if __name__ == "__main__":
    filtro(); astavel(); wien()
    print("esquematicos salvos em", OUT)
