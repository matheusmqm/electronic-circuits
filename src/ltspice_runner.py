"""Executa uma netlist (gerada pelo PySpice) no LTspice em modo batch e le o .raw com spicelib.
Substitui o ngspice_runner.py do memorial (o projeto usa LTspice em vez de ngspice)."""
import os
import re
import subprocess
import tempfile
from pathlib import Path

import numpy as np
from spicelib import RawRead

LTSPICE = os.environ.get(
    "LTSPICE_EXE", str(Path.home() / "AppData/Local/Programs/ADI/LTspice/LTspice.exe"))
LIB = str(Path(__file__).with_name("tl081_behav.lib")).replace("\\", "/")


def run(circuit, analysis, workdir=None):
    """circuit: PySpice Circuit; analysis: ex. '.tran 0 2m 0 20n' ou '.ac dec 200 10 1meg'.
    Retorna dict {'time'|'frequency', 'v(no)': array}. Nos em minusculas."""
    workdir = Path(workdir or tempfile.mkdtemp(prefix="lts_"))
    workdir.mkdir(parents=True, exist_ok=True)
    cir = workdir / "c.cir"
    txt = str(circuit).replace("\n.end", "")
    txt = re.sub(r"(?im)^\.include .*$", f".include {LIB}", txt)
    txt += f"\n{analysis}\n.end\n"
    cir.write_text(txt)
    for f in workdir.glob("c.raw"):
        f.unlink()
    r = subprocess.run([LTSPICE, "-b", str(cir)], capture_output=True, text=True, cwd=workdir)
    raw = workdir / "c.raw"
    if not raw.exists():
        log = (workdir / "c.log").read_text(errors="replace") if (workdir / "c.log").exists() else ""
        raise RuntimeError(r.stdout + r.stderr + log)
    rd = RawRead(str(raw), verbose=False)
    out = {}
    for name in rd.get_trace_names():
        out[name.lower()] = np.array(rd.get_trace(name).get_wave(0))
    axis = rd.get_axis(0)
    key = "time" if "time" in out else "frequency"
    out[key] = np.abs(np.array(axis)) if key == "time" else np.real(np.array(axis))
    return out
