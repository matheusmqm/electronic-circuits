"""Salva em output/netlists/ a netlist de cada circuito (a mesma que o LTspice recebe), para inspecao."""
import re
from pathlib import Path
import projeto1, projeto2, projeto3
from medidas import OUT

d = OUT / "netlists"; d.mkdir(exist_ok=True)
casos = {
    "projeto1.cir": (projeto1.build(), ".ac dec 200 10 1meg"),
    "projeto2_P1k83.cir": (projeto2.build(1830), ".tran 0 140u 0 20n"),
    "projeto3_R12k68.cir": (projeto3.build(R=12.68e3), ".tran 0 8m 0 0.1u"),
    "projeto3_R13k.cir": (projeto3.build(R=13e3), ".tran 0 8m 0 0.1u"),
}
for nome, (c, an) in casos.items():
    txt = str(c).replace("\n.end", "")
    txt = re.sub(r"(?im)^\.include .*$", ".include ../../src/tl081_behav.lib", txt)
    (d / nome).write_text(f"{txt}\n{an}\n.end\n", encoding="utf-8")
    print("salvo", d / nome)
