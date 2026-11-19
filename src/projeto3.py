"""Projeto 3 - Oscilador em ponte de Wien (15 kHz). Transiente; mede fosc, amplitude e THD."""
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import ltspice_runner
from medidas import Tabela, OUT, uniforme, cruzamentos_asc
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *


def build(R=12.68e3, C=820e-12, Rg=10e3, R3=18e3, R4=3.3e3):
    c = Circuit("Oscilador Wien 15 kHz")
    c.include("tl081_behav.lib")
    c.model("D1N4148", "D", IS=2.682e-9, N=1.836, RS=0.5664, CJO=4e-12, M=0.333, TT=11.54e-9, BV=100, IBV=100e-6)
    c.V("cc", "vcc", c.gnd, 15@u_V)
    c.V("ee", "vee", c.gnd, -15@u_V)
    c.X("U1", "TL081B", "vp", "vm", "vcc", "vee", "out")
    c.R("s", "out", "ws", R@u_Ω)
    c.C("s", "ws", "vp", C@u_F)
    c.R("p", "vp", c.gnd, R@u_Ω)
    c.C("p", "vp", c.gnd, C@u_F)
    c.R("g", "vm", c.gnd, Rg@u_Ω)
    c.R("3", "out", "x", R3@u_Ω)
    c.R("4", "x", "vm", R4@u_Ω)
    c.D("1", "x", "vm", model="D1N4148")
    c.D("2", "vm", "x", model="D1N4148")
    c.I("kick", c.gnd, "vp", "pulse(0 2u 0 10n 10n 1u 1)")
    return c


def medir(c, tmax=8e-3, janela=1.5e-3):
    an = ltspice_runner.run(c, f".tran 0 {tmax} 0 0.1u")
    t, v = an["time"], an["v(out)"]
    tu, vu = uniforme(t, v, t0=tmax - janela, t1=t[-1])
    tc = cruzamentos_asc(tu, vu)
    f = 1 / np.mean(np.diff(tc))
    # THD: FFT sobre numero inteiro de ciclos (harmonicas caem exatamente nos bins)
    tt = np.linspace(tc[0], tc[-1], 20000, endpoint=False)
    vv = np.interp(tt, tu, vu)
    sp = np.abs(np.fft.rfft(vv)) / len(vv) * 2
    k1 = len(tc) - 1                       # numero de ciclos = bin da fundamental
    thd = np.sqrt(sum(sp[k * k1] ** 2 for k in range(2, 6))) / sp[k1]
    # estabilizacao: pico nos ultimos 1,5 ms vs. 1,5 ms anteriores
    p_fin = np.max(np.abs(v[t > tmax - janela]))
    p_ant = np.max(np.abs(v[(t > tmax - 2 * janela) & (t <= tmax - janela)]))
    return dict(f=f, vmax=vu.max(), vmin=vu.min(), thd=thd, estab=abs(p_fin / p_ant - 1),
                t=t, v=v, tt=tt, vv=vv, sp=sp, k1=k1)


def main():
    rc = medir(build(R=12.68e3))
    rn = medir(build(R=13e3))
    tb = Tabela("Projeto 3 - Oscilador de Wien (LTspice, modelo TL081 comportamental)")
    tb.add("fosc R = 12,68 kOhm (compensado)", 14967, rc["f"], "14850..15150", 14850 <= rc["f"] <= 15150, "Hz")
    tb.add("erro vs 15 kHz (compensado)", -0.22, (rc["f"] / 15000 - 1) * 100, "info", None, "%")
    tb.add("fosc R = 13 kOhm (sem compensacao)", 14607, rn["f"], "14607 +-1 %", abs(rn["f"] / 14607 - 1) <= .01, "Hz")
    tb.add("erro vs 15 kHz (sem compensacao)", -2.62, (rn["f"] / 15000 - 1) * 100, "info", None, "%")
    for lab, r in (("12,68 kOhm", rc), ("13 kOhm", rn)):
        pk = max(r["vmax"], -r["vmin"])
        tb.add(f"Amplitude de pico (R = {lab})", 9.0, pk, "7..11 e <13,5", 7 <= pk <= 11 and pk < 13.5, "V")
        tb.add(f"Estabilizacao (R = {lab})", None, r["estab"] * 100, "variacao < 5 %", r["estab"] < .05, "%")
        tb.add(f"THD 2-5 (R = {lab})", None, r["thd"] * 100, "informativo (poucos %)", None, "%")
    tb.salvar("projeto3_tabela.txt")

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(rc["t"] * 1e3, rc["v"], lw=.6, label="R = 12,68 kOhm"); ax.set_xlabel("t (ms)"); ax.set_ylabel("Vout (V)")
    ax.grid(alpha=.4); ax.set_title("Wien: partida e estabilizacao"); ax.legend()
    fig.tight_layout(); fig.savefig(OUT / "projeto3_partida.png", dpi=150)

    fig, ax = plt.subplots(figsize=(9, 4))
    T = 1 / rc["f"]; m = rc["t"] > rc["t"][-1] - 4 * T
    ax.plot((rc["t"][m] - rc["t"][m][0]) * 1e6, rc["v"][m]); ax.grid(alpha=.4)
    ax.set_xlabel("t (us)"); ax.set_ylabel("Vout (V)"); ax.set_title("Wien: regiao estacionaria (zoom, 4 ciclos)")
    fig.tight_layout(); fig.savefig(OUT / "projeto3_zoom.png", dpi=150)

    fig, ax = plt.subplots(figsize=(8, 4))
    fh = rc["f"] * np.arange(0, 7); ks = rc["k1"] * np.arange(0, 7)
    amp = rc["sp"][ks]
    ax.stem(fh / 1e3, 20 * np.log10(np.maximum(amp, 1e-9)), bottom=-100)
    ax.set_ylim(-100, 30); ax.set_xlabel("f (kHz)"); ax.set_ylabel("Amplitude (dBV)"); ax.grid(alpha=.4)
    ax.set_title(f"Wien: espectro (THD 2-5 = {rc['thd']*100:.2f} %)")
    fig.tight_layout(); fig.savefig(OUT / "projeto3_fft.png", dpi=150)

    fig, axs = plt.subplots(1, 2, figsize=(11, 4), sharey=True)
    for ax, (lab, r) in zip(axs, (("R = 12,68 kOhm (compensado)", rc), ("R = 13 kOhm (sem compensacao)", rn))):
        T = 1 / r["f"]; m = r["t"] > r["t"][-1] - 4 * T
        ax.plot((r["t"][m] - r["t"][m][0]) * 1e6, r["v"][m]); ax.grid(alpha=.4)
        ax.set_title(f"{lab}\nfosc = {r['f']:.0f} Hz ({(r['f']/15000-1)*100:+.2f} %)"); ax.set_xlabel("t (us)")
    axs[0].set_ylabel("Vout (V)")
    fig.tight_layout(); fig.savefig(OUT / "projeto3_comparacao_R.png", dpi=150)


if __name__ == "__main__":
    main()
