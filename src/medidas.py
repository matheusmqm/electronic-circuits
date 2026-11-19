"""Utilitarios comuns: medidas em formas de onda e tabela de criterios."""
import numpy as np
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "output"
OUT.mkdir(exist_ok=True)


def uniforme(t, v, n=None, t0=None, t1=None):
    """Reamostra (t, v) (passo variavel do LTspice) numa grade uniforme."""
    t0 = t[0] if t0 is None else t0
    t1 = t[-1] if t1 is None else t1
    n = n or int((t1 - t0) / 5e-9)
    tt = np.linspace(t0, t1, n, endpoint=False)
    return tt, np.interp(tt, t, v)


def cruzamentos_asc(t, v):
    """Instantes de cruzamento ascendente por zero (interpolacao linear)."""
    idx = np.where((v[:-1] < 0) & (v[1:] >= 0))[0]
    return t[idx] - v[idx] * (t[idx + 1] - t[idx]) / (v[idx + 1] - v[idx])


class Tabela:
    """Acumula linhas (grandeza, teorico, simulado, criterio, ok) e imprime/salva."""
    def __init__(self, titulo):
        self.titulo, self.linhas = titulo, []

    def add(self, nome, teorico, simulado, criterio, ok, unid=""):
        ok = None if ok is None else bool(ok)
        self.linhas.append((nome, teorico, simulado, criterio, ok, unid))

    def texto(self):
        w = max(len(l[0]) for l in self.linhas)
        s = [f"== {self.titulo} ==",
             f"{'Grandeza':{w}s} | {'Teorico':>12s} | {'Simulado':>12s} | Criterio | Resultado"]
        for nome, te, si, cr, ok, u in self.linhas:
            fte = "-" if te is None else f"{te:.4g}"
            r = "OK" if ok is True else ("FALHOU" if ok is False else "info")
            s.append(f"{nome:{w}s} | {fte:>12s} | {si:12.5g} | {cr} {u} | {r}")
        return "\n".join(s)

    def salvar(self, nome):
        txt = self.texto()
        (OUT / nome).write_text(txt, encoding="utf-8")
        print(txt)
