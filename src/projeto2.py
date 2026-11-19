"""Projeto 2 - Gerador de onda quadrada (astavel). Transiente; mede f, niveis e ciclo de trabalho."""
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import ltspice_runner
from medidas import Tabela, OUT, uniforme, cruzamentos_asc
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

RF = 18e3


def build(p_ohm):
    c = Circuit("Astavel 1-10 kHz")
    c.include("tl081_behav.lib")
    c.V("cc", "vcc", c.gnd, 15@u_V)
    c.V("ee", "vee", c.gnd, -15@u_V)
    c.X("U1", "TL081B", "vp", "vm", "vcc", "vee", "out")
    c.R("B", "out", "vp", 10@u_kΩ)
    c.R("A", "vp", c.gnd, 10@u_kΩ)
    c.R("F", "out", "rt", 18@u_kΩ)
    c.R("P", "rt", "vm", max(p_ohm, 1e-3)@u_Ω)
    c.C("T", "vm", c.gnd, 2.2@u_nF)
    c.I("kick", c.gnd, "vp", "pulse(0 2u 0 10n 10n 1u 1)")   # tira do equilibrio instavel
    return c


def medir(p_ohm, ciclos=12):
    f_est = 1 / (2.1972 * (RF + p_ohm) * 2.2e-9)
    tmax = (ciclos + 2) / f_est
    an = ltspice_runner.run(build(p_ohm), f".tran 0 {tmax:.6e} 0 20n")
    t, v, vm = an["time"], an["v(out)"], an["v(vm)"]
    tu, vu = uniforme(t, v, t0=2 / f_est, t1=t[-1])
    tc = cruzamentos_asc(tu, vu)
    f = 1 / np.mean(np.diff(tc))
    return dict(f=f, vmax=vu.max(), vmin=vu.min(), duty=np.mean(vu > 0), t=t, v=v, vm=vm)


def main():
    tb = Tabela("Projeto 2 - Gerador de onda quadrada (LTspice, modelo TL081 comportamental)")
    casos = [("P = 0 (fmax)", 0), ("P = 1,83 kOhm", 1830), ("P = 188,01 kOhm", 188010), ("P = 200 kOhm (fmin)", 200e3)]
    res = {}
    for lab, p in casos:
        res[p] = r = medir(p)
        print(f"{lab}: f = {r['f']:.1f} Hz")
    r0, r1, r2, r3 = (res[p] for p in (0, 1830, 188010, 200e3))
    tb.add("f com P = 0 (max)", 10969, r0["f"], "10500..11500", 10500 <= r0["f"] <= 11500 and r0["f"] >= 1e4, "Hz")
    tb.add("f com P = 1,83 kOhm", 1e4, r1["f"], "10 kHz +-2 %", abs(r1["f"] / 1e4 - 1) <= .02, "Hz")
    tb.add("f com P = 188,01 kOhm", 1e3, r2["f"], "1 kHz +-2 %", abs(r2["f"] / 1e3 - 1) <= .02, "Hz")
    tb.add("f com P = 200 kOhm (min)", 945.2, r3["f"], "930..960 e <=1 kHz", 930 <= r3["f"] <= 960 and r3["f"] <= 1e3, "Hz")
    for lab, p in casos:
        r = res[p]
        tb.add(f"Nivel alto ({lab})", 13.5, r["vmax"], "+-0,5", abs(r["vmax"] - 13.5) <= .5, "V")
        tb.add(f"Nivel baixo ({lab})", -13.5, r["vmin"], "+-0,5", abs(r["vmin"] + 13.5) <= .5, "V")
        tb.add(f"Ciclo de trabalho ({lab})", 50, r["duty"] * 100, "50 +-2", abs(r["duty"] * 100 - 50) <= 2, "%")

    # varredura P x f (inclui pontos proximos dos extremos) e P que da 10 kHz exatos
    ps = np.array([0, 500, 1000, 1830, 3000, 5000, 10e3, 20e3, 40e3, 70e3, 100e3, 140e3, 188010, 200e3])
    fs = np.array([res[p]["f"] if p in res else medir(p, 8)["f"] for p in ps])
    # secante em torno de 10 kHz
    a, b = 1000.0, 3000.0
    fa, fb = medir(a, 8)["f"], medir(b, 8)["f"]
    for _ in range(5):
        c_ = b - (fb - 1e4) * (b - a) / (fb - fa)
        a, fa, b = b, fb, c_
        fb = medir(b, 8)["f"]
    tb.add("P que da 10 kHz exatos", 1830, b, "1800..2100", 1800 <= b <= 2100, "Ohm")
    tb.add("Faixa contem 1-10 kHz", None, 1.0, "fmin<=1k e fmax>=10k", (r3["f"] <= 1e3) and (r0["f"] >= 1e4))
    tb.salvar("projeto2_tabela.txt")

    # graficos
    fig, axs = plt.subplots(2, 2, figsize=(11, 7))
    for ax, (lab, p) in zip(axs.flat, casos):
        r = res[p]; T = 1 / r["f"]
        m = (r["t"] >= r["t"][-1] - 4 * T)
        ax.plot((r["t"][m] - r["t"][m][0]) * 1e6, r["v"][m], label="Vout")
        ax.plot((r["t"][m] - r["t"][m][0]) * 1e6, r["vm"][m], label="Vcap (vm)", alpha=.7)
        ax.set_title(f"{lab} - f = {r['f']:.0f} Hz"); ax.grid(alpha=.4)
        ax.set_xlabel("t (us)"); ax.set_ylabel("V"); ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout(); fig.savefig(OUT / "projeto2_ondas.png", dpi=150)

    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.semilogy(ps / 1e3, fs, "o-")
    ax.axhline(1e3, ls="--", c="gray"); ax.axhline(1e4, ls="--", c="gray")
    ax.set_xlabel("P (kOhm)"); ax.set_ylabel("f (Hz)"); ax.grid(True, which="both", alpha=.4)
    ax.set_title("Astavel: P x frequencia (linhas: 1 kHz e 10 kHz)")
    fig.tight_layout(); fig.savefig(OUT / "projeto2_p_vs_f.png", dpi=150)


if __name__ == "__main__":
    main()
