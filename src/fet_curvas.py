"""Parte 2 - FET: curvas caracteristicas (modelo ideal) e exemplos de polarizacao.

Gera figuras em output/fet_*.png e imprime os numeros dos exemplos usados em docs/fet.md.
Nao usa simulador: as curvas vem das equacoes quadraticas do JFET/MOSFET (Shockley e lei quadratica).
"""
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "output"
OUT.mkdir(exist_ok=True)

# ---- parametros didaticos (hipoteticos, nao de um componente especifico) ----
IDSS, VP = 8e-3, -4.0          # JFET canal n: Idss = 8 mA, Vp = -4 V
K, VTH = 0.5e-3, 2.0           # E-MOSFET canal n: k = 0,5 mA/V^2, Vth = 2 V


def jfet_id(vgs, vds):
    """Id do JFET canal n: corte, triodo e saturacao (sem modulacao de canal)."""
    vgs, vds = np.broadcast_arrays(np.asarray(vgs, float), np.asarray(vds, float))
    vov = vgs - VP
    sat = IDSS * (1 - vgs / VP) ** 2
    tri = (IDSS / VP**2) * (2 * vov * vds - vds**2)
    return np.where(vgs <= VP, 0.0, np.where(vds >= vov, sat, tri))


def emos_id(vgs, vds):
    vgs, vds = np.broadcast_arrays(np.asarray(vgs, float), np.asarray(vds, float))
    vov = vgs - VTH
    sat = K * vov**2
    tri = K * (2 * vov * vds - vds**2)
    return np.where(vov <= 0, 0.0, np.where(vds >= vov, sat, tri))


def estilo(ax, xl, yl, titulo):
    ax.set_xlabel(xl); ax.set_ylabel(yl); ax.set_title(titulo, fontsize=10)
    ax.grid(alpha=.3); ax.set_xlim(left=min(0, ax.get_xlim()[0])); ax.set_ylim(bottom=0)


# ---------------- Figura 1: curvas de dreno do JFET ----------------
vds = np.linspace(0, 15, 600)
fig, ax = plt.subplots(figsize=(7, 4.5))
for vgs in [0, -1, -2, -3, -3.5]:
    ax.plot(vds, jfet_id(vgs, vds) * 1e3, label=f"$V_{{GS}}$ = {vgs:g} V")
vb = np.linspace(0, 15, 300)
vgs_b = np.linspace(VP, 0, 200)
ax.plot(vgs_b - VP, IDSS * (1 - vgs_b / VP) ** 2 * 1e3, "k--", lw=1, label="$V_{DS}=V_{GS}-V_P$")
ax.axvline(0, color="k", lw=.5)
ax.text(0.5, 5.5, "região\nôhmica", fontsize=8); ax.text(8, 8.3, "região de saturação", fontsize=8)
ax.text(7, 1.0, "$V_{GS}\\leq V_P$ (−4 V): corte ($I_D$ = 0)", fontsize=8)
estilo(ax, "$V_{DS}$ (V)", "$I_D$ (mA)", "")
ax.set_ylim(0, 9); ax.legend(fontsize=8, loc="center left", bbox_to_anchor=(1.01, .5)); fig.tight_layout()
fig.savefig(OUT / "fet_jfet_dreno.png", dpi=200); plt.close(fig)

# ---------------- Figura 2: curvas de transferencia (3 tipos) ----------------
fig, axs = plt.subplots(1, 3, figsize=(11, 3.6))
v = np.linspace(-4, 0, 200)
axs[0].plot(v, IDSS * (1 - v / VP) ** 2 * 1e3)
axs[0].plot([0, VP / 2, VP], [8, 2, 0], "ro", ms=4)
axs[0].annotate("$I_{DSS}$", (0, 8), (-1.2, 7.2), fontsize=8)
axs[0].annotate("$I_{DSS}/4$ em $V_P/2$", (-2, 2), (-3.8, 3.5), fontsize=8)
estilo(axs[0], "$V_{GS}$ (V)", "$I_D$ (mA)", "JFET canal n")
v = np.linspace(-6, 3, 200)
axs[1].plot(v, np.where(v <= VP, 0, IDSS * (1 - v / VP) ** 2) * 1e3)
axs[1].axvline(0, color="k", lw=.5)
estilo(axs[1], "$V_{GS}$ (V)", "$I_D$ (mA)", "MOSFET de depleção canal n")
axs[1].set_xlim(-6, 3)
v = np.linspace(0, 6, 200)
axs[2].plot(v, K * np.clip(v - VTH, 0, None) ** 2 * 1e3)
axs[2].annotate("$V_{th}$ = 2 V", (2, 0), (2.3, 1.5), fontsize=8, arrowprops=dict(arrowstyle="->"))
estilo(axs[2], "$V_{GS}$ (V)", "$I_D$ (mA)", "MOSFET de enriquecimento canal n")
fig.tight_layout(); fig.savefig(OUT / "fet_transferencia.png", dpi=200); plt.close(fig)

# ---------------- Figura 3: curvas de dreno do E-MOSFET ----------------
vds = np.linspace(0, 10, 600)
fig, ax = plt.subplots(figsize=(7, 4.5))
for vgs in [2.5, 3, 3.5, 4, 4.5, 5]:
    ax.plot(vds, emos_id(vgs, vds) * 1e3, label=f"$V_{{GS}}$ = {vgs:g} V")
vg = np.linspace(VTH, 5, 200)
ax.plot(vg - VTH, K * (vg - VTH) ** 2 * 1e3, "k--", lw=1, label="$V_{DS}=V_{GS}-V_{th}$")
ax.text(0.2, 3.3, "ôhmica", fontsize=8); ax.text(6, 4.6, "saturação", fontsize=8)
estilo(ax, "$V_{DS}$ (V)", "$I_D$ (mA)", ""); ax.set_ylim(0, 5); ax.legend(fontsize=8, loc="center left", bbox_to_anchor=(1.01, .5))
fig.tight_layout(); fig.savefig(OUT / "fet_emosfet_dreno.png", dpi=200); plt.close(fig)

# ---------------- Exemplo 1: JFET autopolarizado ----------------
RS, RD, VDD = 500.0, 3300.0, 20.0
a = IDSS * RS**2 / VP**2
b = -(2 * IDSS * RS / abs(VP) + 1)
raizes = np.roots([a, b, IDSS])
id1 = [r for r in raizes if abs(r * RS) < abs(VP)][0].real
vgs1 = -id1 * RS
vds1 = VDD - id1 * (RD + RS)
gm1 = 2 * IDSS / abs(VP) * (1 - vgs1 / VP)
print(f"JFET auto: raizes={raizes*1e3} mA | Id={id1*1e3:.3f} mA Vgs={vgs1:.3f} V Vds={vds1:.3f} V "
      f"sat={vds1 >= vgs1 - VP} gm={gm1*1e3:.3f} mS")
print(f"  Av(CS bypass)={-gm1*RD:.2f}  Av(sem bypass)={-gm1*RD/(1+gm1*RS):.2f}")

# figura 4: reta de autopolarizacao
fig, ax = plt.subplots(figsize=(6, 4.2))
v = np.linspace(-4, 0, 200)
ax.plot(v, IDSS * (1 - v / VP) ** 2 * 1e3, label="Curva de transferência")
ax.plot(v, -v / RS * 1e3, label="Reta $V_{GS}=-I_D R_S$ ($R_S$ = 500 Ω)")
ax.plot(vgs1, id1 * 1e3, "ro"); ax.annotate(f"Q ({vgs1:.2f} V; {id1*1e3:.2f} mA)", (vgs1, id1 * 1e3), (-3.7, 5.6), fontsize=8, arrowprops=dict(arrowstyle="->"))
estilo(ax, "$V_{GS}$ (V)", "$I_D$ (mA)", ""); ax.legend(fontsize=8, loc="upper left")
fig.tight_layout(); fig.savefig(OUT / "fet_polarizacao.png", dpi=200); plt.close(fig)

# ---------------- Exemplo 2: E-MOSFET com realimentacao de dreno ----------------
RD2, VDD2 = 2000.0, 12.0
vov = (-1 + np.sqrt(1 + 4 * K * RD2 * (VDD2 - VTH))) / (2 * K * RD2)
id2 = K * vov**2
vgs2 = vov + VTH
print(f"E-MOSFET realim. dreno: Vov={vov:.3f} Vgs={vgs2:.3f} Id={id2*1e3:.3f} mA "
      f"Vds={VDD2-id2*RD2:.3f} gm={2*K*vov*1e3:.3f} mS Av={-2*K*vov*RD2:.2f}")
print("figuras em", OUT)
