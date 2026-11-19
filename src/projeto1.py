"""Projeto 1 - Filtro passa-baixa Butterworth 3a ordem (fc = 5 kHz, 26 dB, 60 dB/dec). Analise AC."""
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import ltspice_runner
from medidas import Tabela, OUT
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

FC = 4979.8          # fc real (R = 6,8 kOhm, C = 4,7 nF)
ATOT = 20.0          # ganho total real (V/V)


def build():
    c = Circuit("Filtro Butterworth 3a ordem")
    c.include("tl081_behav.lib")
    c.V("cc", "vcc", c.gnd, 15@u_V)
    c.V("ee", "vee", c.gnd, -15@u_V)
    c.V("in", "vin", c.gnd, "dc 0 ac 1")
    # 1a secao: RC + nao inversor, A1 = 1 + 18k/2k = 10
    c.R("1a", "vin", "a", 6.8@u_kΩ)
    c.C("1a", "a", c.gnd, 4.7@u_nF)
    c.X("U1", "TL081B", "a", "b", "vcc", "vee", "o1")
    c.R("1f", "o1", "b", 18@u_kΩ)
    c.R("1g", "b", c.gnd, 2@u_kΩ)
    # 2a secao: Sallen-Key, A2 = 1 + 10k/10k = 2
    c.R("2a", "o1", "n3", 6.8@u_kΩ)
    c.R("2b", "n3", "n4", 6.8@u_kΩ)
    c.C("2a", "n4", c.gnd, 4.7@u_nF)
    c.C("2f", "n3", "out", 4.7@u_nF)
    c.X("U2", "TL081B", "n4", "n5", "vcc", "vee", "out")
    c.R("2f", "out", "n5", 10@u_kΩ)
    c.R("2g", "n5", c.gnd, 10@u_kΩ)
    return c


def teorico(f):
    return 20 * np.log10(ATOT / np.sqrt(1 + (f / FC) ** 6))


def main():
    an = ltspice_runner.run(build(), ".ac dec 200 10 1meg")
    f = an["frequency"]; g = 20 * np.log10(np.abs(an["v(out)"]))
    at = lambda fr: float(np.interp(np.log10(fr), np.log10(f), g))

    tb = Tabela("Projeto 1 - Filtro Butterworth (LTspice, modelo TL081 comportamental)")
    g0 = at(100.0)
    tb.add("Ganho banda passante", 26.0206, g0, "26,02 +-0,1", abs(g0 - 26.0206) <= 0.1, "dB")
    for lab, k, tol in [("Ganho 0,1 fc", .1, None), ("Ganho 0,5 fc", .5, .1), ("Ganho fc", 1, .15),
                        ("Ganho 2 fc", 2, .3), ("Ganho 10 fc", 10, .5), ("Ganho 100 fc", 100, None)]:
        s = at(k * FC); te = float(teorico(k * FC))
        tb.add(f"{lab} ({k*FC:.1f} Hz)", te, s, "informativo" if tol is None else f"+-{tol} do teor.",
               None if tol is None else abs(s - te) <= tol, "dB")
    alvo = g0 - 3.0103
    i3 = np.where(g <= alvo)[0][0]
    f3 = float(np.exp(np.interp(alvo, g[i3-1:i3+1][::-1], np.log(f[i3-1:i3+1][::-1]))))
    tb.add("Frequencia de -3 dB", FC, f3, "4980 +-2 %", abs(f3 / FC - 1) <= .02, "Hz")
    sl = (at(5 * FC) - at(20 * FC)) / np.log10(4)
    tb.add("Inclinacao 5fc-20fc", 60, sl, "60 +-2", abs(sl - 60) <= 2, "dB/dec")
    tb.salvar("projeto1_tabela.txt")

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.semilogx(f, g, label="Simulado (LTspice, TL081)")
    ax.semilogx(f, teorico(f), "--", label="Teorico (amp-op ideal)")
    ax.axvline(FC, ls=":", c="gray", label=f"fc = {FC:.1f} Hz")
    ax.set_xlim(10, 1e6); ax.set_ylim(-120, 35)
    ax.grid(True, which="both", alpha=.4); ax.legend()
    ax.set_xlabel("f (Hz)"); ax.set_ylabel("Ganho (dB)"); ax.set_title("Filtro Butterworth 3a ordem - Bode")
    fig.tight_layout(); fig.savefig(OUT / "projeto1_bode.png", dpi=150)


if __name__ == "__main__":
    main()
