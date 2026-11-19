# Memorial de Cálculo e Plano de Simulação – Circuitos Eletrônicos (2ª Etapa, 2026.2)

> **Finalidade:** documento de contexto para o Claude Code. Reúne (a) todos os cálculos **já revisados e corrigidos** dos três projetos, (b) os valores finais de cada componente, (c) o que é simulado (netlists montadas com **PySpice** e simuladas no **LTspice**) e (d) os critérios para dizer se a simulação confere com o cálculo.
> **Documento complementar:** `spec.md` (enunciado do professor) e `circuitos.md` (explicação de cada circuito).
> **Status dos cálculos:** todas as contas e fórmulas foram refeitas de forma independente e conferidas. **Estão corretas.** Os valores dos componentes da seção 4 são os valores finais do projeto: **não os altere** para "fazer a simulação bater".
> **Origem dos números de referência da seção 7:** simulação no **LTspice**, com o modelo comportamental do TL081 em `src/tl081_behav.lib` (portado do ngspice; mesma física). Os scripts estão em `src/` e as saídas em `output/`. Com outro modelo de amp-op (por exemplo, o macromodelo oficial da TI), diferenças pequenas são esperadas (ver seção 8).

---

## 0. O que o Claude Code deve fazer

1. Montar, com **PySpice**, os três circuitos (seções 3.2, 4.2 e 5.2) com **exatamente** os valores indicados.
2. Rodar as análises indicadas (AC para o filtro; transiente para o gerador e para a Wien).
3. Comparar cada resultado com o **valor teórico** e com os **critérios de aceitação** (seção 7).
4. Gerar os gráficos e tabelas pedidos (seção 9), nomeando os arquivos de forma clara.
5. Se algum resultado ficar fora do critério: **primeiro** verificar se a causa é o modelo do amp-op ou a montagem do circuito (nós trocados, entrada + e − invertidas, valor digitado errado); **só depois** questionar o cálculo. Relatar a causa encontrada em vez de ajustar valores sem explicar.
6. Não alterar os valores finais de componentes sem pedir confirmação. Se for necessário um ajuste (por exemplo, o resistor R da Wien por causa do GBW do modelo), usar a regra da seção 6.5 e registrar o motivo.

Contexto do projeto: três circuitos com amp-op para o enunciado da 2ª etapa. Cada circuito tem **dados acrescentados** (escolhas de projeto) que o relatório precisa **justificar** (seção 2).

---

## 1. Ambiente: PySpice + LTspice

Instalação (projeto gerenciado com `uv`; Python ≥ 3.14, ver `pyproject.toml`):

```bash
uv sync        # matplotlib, numpy, pyspice, schemdraw, spicelib
```

O **LTspice** precisa estar instalado (caminho padrão `%LOCALAPPDATA%/Programs/ADI/LTspice/LTspice.exe`, ou variável de ambiente `LTSPICE_EXE`).

**Fluxo adotado:**
- O **PySpice só monta o circuito** (`Circuit`, componentes, modelo de diodo; `str(circuit)` gera a netlist).
- `src/ltspice_runner.py` grava a netlist, acrescenta a análise, roda o LTspice em modo batch (`LTspice.exe -b`) e lê o `.raw` com **spicelib**. O backend nativo do PySpice não é usado (falha com ngspice ≥ 40 e NumPy ≥ 2).
- As netlists finais ficam em `output/netlists/` (`src/exportar_netlists.py`); os esquemáticos são gerados por `src/esquematicos.py`.

**Execução:**
```bash
cd src
python projeto1.py   # filtro (AC)        -> output/projeto1_*.png/.txt
python projeto2.py   # astável (transiente) -> output/projeto2_*.png/.txt
python projeto3.py   # Wien (transiente)  -> output/projeto3_*.png/.txt
```

Observações de uso:
- Não use `in` como nome de nó (palavra reservada do Python); os scripts usam `vin`.
- Parâmetros de `.subckt` **não podem** ter o mesmo nome de um elemento (`r1`, `c1`): no modelo usa-se `rr1` e `cc1`.
- No modelo portado para LTspice, os grampos usam fontes `B` (`Bp`, `Bn`, `V=...`) e a corrente do integrador usa `max(-imax, min(imax, ...))`, em vez de `limit()`.
- O modelo `tl081_behav.lib` é o `.include` de todas as netlists (o runner troca o caminho do `.include` pelo caminho absoluto).

---

## 2. Dados acrescentados ao projeto (exigidos pelo enunciado)

O enunciado diz que a equipe precisa acrescentar dados para desenvolver cada projeto e **explicar o porquê no relatório**. Estes são os dados acrescentados:

| Dado acrescentado | Valor adotado | Por quê |
|---|---|---|
| Amplificador operacional | **TL081** (entrada JFET) | Slew rate de 13 V/µs e produto ganho-banda (GBW) de 3 MHz (valores típicos, datasheet TI). O LM741 (0,5 V/µs) não consegue gerar onda quadrada limpa a 10 kHz com ±15 V: só a transição de −13,5 V a +13,5 V levaria 54 µs, mais que o semiperíodo de 50 µs. |
| Alimentação | **±15 V** simétrica | Tensão padrão de laboratório; o TL081 aceita até ±18 V. Saturação típica Vsat ≈ ±13,5 V (carga ≈ 10 kΩ; mínimo garantido ±12 V com 10 kΩ). |
| Séries de componentes | Resistores **E24** (5 %), capacitores **E12** | Valores encontrados no comércio; permitem montar e simular como seria na prática. As contas usam valores nominais (tolerâncias: seção 8). |
| Topologia do filtro | 1 polo (RC + não inversor) em cascata com 2 polos (Sallen-Key de componentes iguais) | Topologia do material da disciplina; a tabela de Butterworth fixa o ganho da seção de 2 polos em 2. |
| Ganho da 1ª seção do filtro | ≈ 10 V/V (20 dB) | O enunciado pede 26 dB no total; a 2ª seção já dá 6,02 dB fixos; os 20 dB restantes ficam na 1ª seção, onde o ganho é livre. |
| Variação de frequência do gerador | Resistor fixo + potenciômetro | Para varrer a década pedida é preciso um elemento variável; f é inversamente proporcional a R. |
| Realimentação positiva do gerador | β = 0,5 (RA = RB = 10 kΩ) | Define os limiares do comparador Schmitt (±6,75 V) e simplifica o período (ln 3). |
| Estabilização de amplitude da Wien | Diodos 1N4148 em antiparalelo com parte do resistor de realimentação | Sem isso a oscilação satura (onda ceifada) ou não parte. |

Parâmetros do TL081 usados em **todas** as contas (valores típicos, datasheet TI, família TL08x): GBW = 3 MHz, slew rate = 13 V/µs, saturação ±13,5 V com ±15 V e carga ≈ 10 kΩ, faixa de modo comum mínima ±11 V, tensão diferencial máxima ±30 V.

---

## 3. Projeto 1 – Filtro passa-baixa Butterworth (fc = 5 kHz, 60 dB/déc, 26 dB)

Notação: em cada seção do amp-op não inversor, **ACL = 1 + R1/R2** (R1 entre saída e entrada inversora; R2 da entrada inversora para o terra).

### 3.1 Cálculos (passo a passo)

**Ordem do filtro.** Cada polo faz o ganho cair 20 dB/década acima de fc. n = 60 ÷ 20 = **3 polos** (3ª ordem).

**Divisão em seções.** 3 polos = 1ª seção (1 polo) + 2ª seção (2 polos). Inclinação total = 20 + 40 = 60 dB/déc.

**Ganho total em V/V.**
```
Atotal = 10^(26/20) = 10^1,3 = 19,9526 V/V
```

**Ganho da 2ª seção (Sallen-Key, R e C iguais) – fixo em 2.**
```
H2(s) = A2·ω0² / ( s² + (3 − A2)·ω0·s + ω0² ),  ω0 = 1/(RC),   Q = 1/(3 − A2)
Butterworth 3ª ordem normalizado: (s + 1)(s² + s + 1)  ⇒ o par de polos tem Q = 1
1 = 1/(3 − A2) ⇒ A2 = 2 (= 6,02 dB)
A2 = 1 + R1/R2 = 2 ⇒ R1 = R2 = 10 kΩ
```

**Ganho da 1ª seção.**
```
A1 = Atotal / A2 = 19,9526 / 2 = 9,9763 V/V ⇒ R1/R2 = 8,9763
Adotando R2 = 2 kΩ: R1 = 17,953 kΩ (teórico) → comercial 18 kΩ ⇒ A1 = 1 + 18/2 = 10 V/V
Ganho total real = 10 × 2 = 20 V/V = 26,0206 dB  (erro 0,0206 dB; 0,24 % em V/V)
```

**Resistor e capacitor das redes RC.**
```
fc = 1/(2πRC);  C = 4,7 nF
R = 1/(2π × 5000 × 4,7e-9) = 6.772,6 Ω → comercial 6,8 kΩ
fc real = 1/(2π × 6800 × 4,7e-9) = 4.979,8 Hz  (erro −0,40 %)
```
(4,7 nF com 6,8 kΩ é, entre as combinações E24/E12 com R de 1 kΩ a 100 kΩ, a de menor erro; 4,7 kΩ com 6,8 nF dá o mesmo produto RC.) As três redes RC usam o mesmo R e C.

**Resposta teórica.**
```
|H1|² = 1/(1 + x²);   |H2|² = 1/(1 − x² + x⁴);   produto = 1/(1 + x⁶),   x = f/fc
|H(f)| = Atotal / √(1 + (f/fc)⁶)
Em f = fc: 1ª seção −3,01 dB; 2ª seção 0 dB (Q = 1); total −3,01 dB
```

**Verificações com o TL081.**
```
Banda da 1ª seção = GBW/A1 = 3 MHz/10 = 300 kHz (= 60·fc); da 2ª = 3 MHz/2 = 1,5 MHz
Slew rate exigido = 2π·fc·Vp = 2π × 5000 × 13,5 = 0,42 V/µs  < 13 V/µs
Entrada máxima sem saturar = 13,5/20 = 0,675 V de pico (usar até ~0,5 V no teste)
Nó intermediário: A1 × 0,675 = 6,75 V < Vsat
```

### 3.2 Topologia (tabela de conexões para montar com PySpice)

Alimentação ±15 V nos dois amp-ops. Entrada AC de 1 V (`dc 0 ac 1`) no nó `vin`.

| Componente | Valor | Nó A | Nó B | Observação |
|---|---|---|---|---|
| R1a | 6,8 kΩ | `vin` | `a` | rede RC da 1ª seção |
| C1a | 4,7 nF | `a` | `0` | |
| U1 (TL081) | — | `+`=`a`, `−`=`b` | saída `o1` | 1ª seção (não inversora) |
| R1f | 18 kΩ | `o1` | `b` | realimentação (R1 da notação) |
| R1g | 2 kΩ | `b` | `0` | R2 da notação |
| R2a | 6,8 kΩ | `o1` | `n3` | Sallen-Key |
| R2b | 6,8 kΩ | `n3` | `n4` | |
| C2a | 4,7 nF | `n4` | `0` | C do pino + para o terra |
| C2f | 4,7 nF | `n3` | `out` | C de realimentação positiva (saída → nó entre os R) |
| U2 (TL081) | — | `+`=`n4`, `−`=`n5` | saída `out` | 2ª seção |
| R2f | 10 kΩ | `out` | `n5` | R1 da notação |
| R2g | 10 kΩ | `n5` | `0` | R2 da notação |

### 3.3 O que simular

- **Análise AC**, 10 Hz a 1 MHz, 200 pontos por década (`.ac dec 200 10 1meg`), fonte `dc 0 ac 1`.
- Medir o ganho em dB (`20·log10|v(out)|`) em: 0,1·fc, 0,5·fc, fc, 2·fc, 10·fc (com fc real = 4.979,8 Hz); o ganho em banda passante; a frequência de −3 dB (ganho − 3,01 dB abaixo da banda passante); a inclinação entre 5·fc e 20·fc.
- (Opcional) transiente com senoide de 0,5 V de pico em 1 kHz: saída esperada ≈ 10 V de pico (20 V/V × 0,5 V), sem ceifamento.
- Gerar o **diagrama de Bode** (ganho × frequência, escala log em f, linha vertical em fc).

**Valores teóricos de referência (amp-op ideal):**

| f | Ganho (dB) |
|---|---:|
| 0,1·fc (498,0 Hz) | 26,021 |
| 0,5·fc (2.489,9 Hz) | 25,953 |
| 1,0·fc (4.979,8 Hz) | 23,010 |
| 2,0·fc (9.959,6 Hz) | 7,891 |
| 10·fc (49.798 Hz) | −33,979 |
| 100·fc (497.982 Hz) | −93,979 |

**Importante (não é erro):** com o TL081 real a resposta acima de ~10·fc cai **mais** que o ideal, porque a 1ª seção tem banda de 300 kHz (60·fc). Por isso a inclinação deve ser medida **entre 5·fc e 20·fc**, e não entre 10·fc e 100·fc.

---

## 4. Projeto 2 – Gerador de onda quadrada, 1 kHz a 10 kHz

Topologia: multivibrador astável. O amp-op é um comparador Schmitt (realimentação positiva por RA e RB); o capacitor C carrega e descarrega por RT = RF + P (realimentação negativa).

### 4.1 Cálculos (passo a passo)

**Limiares.**
```
β = RA/(RA + RB) = 10k/(10k + 10k) = 0,5
VUT = +β·Vsat = +6,75 V;  VLT = −6,75 V;  histerese = 13,5 V     (Vsat = 13,5 V)
```

**Período (dedução).**
```
vC(t) = Vsat − (Vsat + β·Vsat)·e^(−t/RT·C);  troca quando vC = +β·Vsat
t1 = RT·C·ln[(1 + β)/(1 − β)];  por simetria t2 = t1
T = 2·RT·C·ln 3 = 2,1972·RT·C;   f = 1/(2,1972·RT·C);   ciclo de trabalho = 50 %
```

**Faixa de resistência (valores teóricos, C = 2,2 nF).**
```
RTmín (10 kHz) = 1/(2,1972 × 10000 × 2,2e-9) = 20,687 kΩ
RTmáx (1 kHz)  = 1/(2,1972 × 1000 × 2,2e-9)  = 206,87 kΩ
P = RTmáx − RTmín = 186,19 kΩ;  RF = RTmín = 20,687 kΩ
```

**Efeito do slew rate do TL081 (por que RF = 18 kΩ e não 20 kΩ).**
```
ts = 2·Vsat/SR = 27 V / 13 V/µs = 2,077 µs  (cada transição)
Treal ≈ 2,1972·RT·C + 2·ts
RF = 20 kΩ: T = 96,68 + 4,15 = 100,83 µs ⇒ fmáx ≈ 9.918 Hz  < 10 kHz  ✗
RF = 18 kΩ: T = 87,01 + 4,15 =  91,16 µs ⇒ fmáx ≈ 10.969 Hz ≥ 10 kHz  ✓
```
Esta é uma **estimativa conservadora**: uma simulação numérica acrescenta ≈ 3,6 µs por período (não 4,15 µs). A conclusão (RF = 18 kΩ) não muda.

**Valores comerciais e faixa obtida (C = 2,2 nF, RA = RB = 10 kΩ, RF = 18 kΩ, P = 200 kΩ linear).**
```
fmáx (P = 0):      ideal 11.493 Hz;  com slew ≈ 10.969 Hz
fmín (P = 200 kΩ): ideal 949,0 Hz;   com slew ≈ 945,2 Hz
Faixa ≈ 945 Hz a 10.969 Hz  ⊃  1 kHz a 10 kHz
```

**Posição do potenciômetro para os extremos exatos (estimativa do memorial, com 2·ts).**
```
RT = (1/f − 2·ts)/(2,1972·C)
10 kHz: RT = 19,83 kΩ ⇒ P = 1,83 kΩ   (sem slew: 2,69 kΩ)
1 kHz:  RT = 206,01 kΩ ⇒ P = 188,01 kΩ (sem slew: 188,87 kΩ)
```
Observação: em 10 kHz o potenciômetro fica a menos de 1 % do curso; o ajuste é muito sensível.

**Verificações com o TL081.**
```
Saída ≈ ±13,5 V (27 Vpp);  tensão diferencial máx. na entrada = 2·β·Vsat = 13,5 V < 30 V
Modo comum máx. = ±6,75 V dentro de ±11 V
Pior carga na saída = (RA + RB) // RF = 20k // 18k = 9,47 kΩ (≈ 10 kΩ; diferença desprezível)
```

### 4.2 Topologia (tabela de conexões)

| Componente | Valor | Nó A | Nó B | Observação |
|---|---|---|---|---|
| U1 (TL081) | — | `+`=`vp`, `−`=`vm` | saída `out` | comparador |
| RB | 10 kΩ | `out` | `vp` | realimentação positiva |
| RA | 10 kΩ | `vp` | `0` | |
| RF | 18 kΩ | `out` | `rt` | parte fixa de RT |
| P | 0 a 200 kΩ (linear) | `rt` | `vm` | potenciômetro (na simulação, usar valor fixo por rodada; P = 0 → usar ≈ 1 mΩ) |
| C | 2,2 nF | `vm` | `0` | |

**Partida (importante):** o circuito tem um equilíbrio instável em v = 0 V. Para sair dele, injete um **pulso de corrente curto** (2 µA por 1 µs) no nó `vp`: `Ikick 0 vp pulse(0 2u 0 10n 10n 1u 1)`. Evite `.ic` + `uic` com o modelo deste projeto (os diodos de grampo do modelo podem dar "timestep too small").

### 4.3 O que simular

- **Análise transiente** por ≥ 12 ciclos (tempo = 14 / f estimada); passo máximo de 20 ns.
- Rodar para quatro posições do potenciômetro: **P = 0**, **P = 1,83 kΩ** (≈ 10 kHz), **P = 188,01 kΩ** (≈ 1 kHz), **P = 200 kΩ**.
- Medir: frequência (cruzamentos ascendentes por zero, ignorando os 2 primeiros ciclos), níveis alto e baixo, ciclo de trabalho. O **ciclo de trabalho** deve ser medido sobre um **número inteiro de períodos** (entre o primeiro e o último cruzamento ascendente); numa janela com número fracionário de períodos o valor sai deslocado em até ≈ 1 ponto percentual, sem relação com o circuito.
- Gerar: forma de onda de saída (e, opcionalmente, a tensão no capacitor `vm`, que deve ser uma exponencial entre ±6,75 V) e uma **varredura de P × frequência** cobrindo 1 kHz a 10 kHz.

---

## 5. Projeto 3 – Oscilador senoidal em ponte de Wien, 15 kHz

### 5.1 Cálculos (passo a passo)

**Condição de oscilação (Barkhausen).**
```
Zs = R + 1/(jωC);  Zp = R/(1 + jωRC)
β(jω) = Zp/(Zs + Zp) = 1/[3 + j(ωRC − 1/(ωRC))]
Fase nula em ω0 = 1/(RC) ⇒ f0 = 1/(2πRC);  em f0: β = 1/3
A·β = 1∠0° ⇒ A = 3 ⇒ 1 + Rf/Rg = 3 ⇒ Rf = 2·Rg
```

**R e C para 15 kHz (fórmula ideal).**
```
C = 820 pF:  R = 1/(2π × 15000 × 820e-12) = 12.939,4 Ω (teórico)
Comercial 13 kΩ:  f0 = 14.930,1 Hz (erro −0,47 %)
```
(820 pF com 13 kΩ é a combinação E24/E12 de menor erro; 8,2 nF com 1,3 kΩ dá o mesmo.)

**Efeito do amp-op real (GBW = 3 MHz) e compensação.**
```
A(f) = 3/(1 + j·3f/GBW);  atraso de fase em 15 kHz: φ = arctg(3 × 15000/3e6) = 0,859°
A rede de Wien precisa adiantar a mesma fase:
   arctg[(x − 1/x)/3] = −arctg(3f/GBW) ⇒ x − 1/x = −9·fosc/GBW,  x = fosc/f0
Com R = 13 kΩ: x = 0,97833 ⇒ fosc = 14.607 Hz
Erro total = −2,62 % em relação a 15 kHz  (−0,47 % do valor comercial; −2,17 % do atraso do amp-op)
```
**Compensação:**
```
Para fosc = 15 kHz: x = 0,97775 ⇒ f0 necessário = 15000/x = 15.341,3 Hz
R = 1/(2π × 15341,3 × 820e-12) = 12.651,6 Ω (teórico)
Comercial: 12 kΩ + 680 Ω em série = 12,68 kΩ (nos dois braços da ponte)
f0 = 15.306,9 Hz ⇒ fosc = 0,97780 × 15.306,9 = 14.967 Hz  (−0,22 %)
```

**Ganho, partida e estabilização de amplitude.**
```
Rg = 10 kΩ; Rf = R3 + R4, com D1 e D2 (1N4148) em antiparalelo sobre R4
Diodos cortados (sinal pequeno):  A = 1 + (18k + 3,3k)/10k = 3,13  > 3  → oscilação cresce
Diodos conduzindo (curto ideal):  A = 1 + 18k/10k = 2,80  < 3        → oscilação diminui
A amplitude se estabiliza onde o ganho médio vale 3. Folga de partida = 3,13/3 = +4,3 %.
```

**Estimativa da amplitude.**
```
Vout,p = 3·VD·Rg/(2·Rg − R3) = 3 × 0,6 × 10k/(20k − 18k) = 9,0 V de pico (≈ 18 Vpp)
Slew rate exigido = 2π × 15000 × 9 = 0,85 V/µs < 13 V/µs;   9 V < Vsat
```
Verificação por balanço harmônico (modelo exponencial do 1N4148): ≈ 9,06 V. A amplitude é **muito sensível** a R3 e Rg: com ±1 % varia de ≈ 7,1 V a ≈ 11,8 V.

**Carga na saída.**
```
|Zs + Zp| em 15 kHz = 27,2 kΩ (R = 12,68 kΩ, C = 820 pF)
R3 + R4 + Rg = 31,3 kΩ (28 kΩ com diodos conduzindo)
Carga total ≈ 14,5 kΩ (13,8 kΩ com diodos conduzindo) > 10 kΩ
```

### 5.2 Topologia (tabela de conexões)

| Componente | Valor | Nó A | Nó B | Observação |
|---|---|---|---|---|
| U1 (TL081) | — | `+`=`vp`, `−`=`vm` | saída `out` | |
| Rs | 12,68 kΩ (12 k + 680 Ω) | `out` | `ws` | ramo série da ponte |
| Cs | 820 pF | `ws` | `vp` | |
| Rp | 12,68 kΩ (12 k + 680 Ω) | `vp` | `0` | ramo paralelo da ponte |
| Cp | 820 pF | `vp` | `0` | |
| Rg | 10 kΩ | `vm` | `0` | |
| R3 | 18 kΩ | `out` | `x` | |
| R4 | 3,3 kΩ | `x` | `vm` | |
| D1 (1N4148) | — | anodo `x` | catodo `vm` | antiparalelo com D2, em paralelo com R4 |
| D2 (1N4148) | — | anodo `vm` | catodo `x` | |

Modelo do diodo 1N4148 (SPICE): `IS=2.682n N=1.836 RS=0.5664 CJO=4p M=0.333 TT=11.54n BV=100 IBV=100u`.

**Partida:** igual ao gerador (pulso de corrente de 2 µA por 1 µs em `vp`).

### 5.3 O que simular

- **Análise transiente** de ≥ 8 ms (passo máximo 0,1 µs). A partida leva ≈ 1 a 2 ms.
- Medir (janela final de 1,5 ms, estacionária): frequência de oscilação (cruzamentos por zero), amplitude de pico e a distorção harmônica (FFT, harmônicas 2 a 5).
- Rodar **duas vezes**: com **R = 12,68 kΩ** (projeto, compensado) e com **R = 13 kΩ** (sem compensação), para **demonstrar** o efeito do GBW descrito na teoria.
- Gerar: gráfico da partida e estabilização (tensão × tempo) e um zoom de poucos ciclos na região estacionária.

---

## 6. Regras de ajuste e verificação

### 6.1 Ordem de diagnóstico se algo não bater
1. Conferir nós e polaridade das entradas (`+` e `−`) do amp-op.
2. Conferir valores digitados (kΩ × Ω, nF × pF).
3. Conferir modelo do amp-op (GBW, slew rate, saturação).
4. Só então rever a teoria.

### 6.2 Efeitos esperados do amp-op real (não são erros)
- Filtro: acima de ~10·fc a atenuação é maior que a ideal (banda de 300 kHz da 1ª seção).
- Gerador: a frequência máxima fica abaixo da ideal (11.493 Hz) por causa do slew rate.
- Wien: a frequência cai ≈ 2,2 % em relação a f0 por causa do GBW.

### 6.3 Se o modelo do TL081 for outro
Os valores numéricos mudam um pouco (frequências do gerador e da Wien, amplitude da Wien). Registrar o modelo usado e comparar com os critérios da seção 7. Para a Wien, usar a regra da seção 6.5.

### 6.4 Tolerâncias (para análise opcional / montagem física)
- Gerador: potenciômetro 20 % menor (160 kΩ) → fmín ≈ 1.157 Hz (não alcança 1 kHz); C com +10 % → fmáx ≈ 10.014 Hz; C +5 % e RF +5 % → fmáx ≈ 9.992 Hz. Opcional: P = 250 kΩ (fmín ≈ 769 Hz). Recomendado: C de 5 % ou melhor e RF de 1 %.
- Wien: o ganho necessário passa a ser `A = 1 + Rs/Rp + Cp/Cs`. Pior caso: R 1 %/C 5 % → 3,126; R 5 %/C 5 % → 3,211; R 1 %/C 10 % → 3,242; R 5 %/C 10 % → 3,328. O ganho disponível (R3, R4, Rg de 1 %) é 3,09 a 3,17, logo, na montagem física, o circuito pode não partir no pior caso. Com valores nominais (simulação) parte sem problema. Para montagem física: R 1 %, C 5 % (C0G/filme) e trimpot de 5 kΩ no lugar de R4.
- Uma análise Monte Carlo (opcional) pode usar esses números como roteiro.

### 6.5 Reajuste do R da Wien se o GBW do modelo for diferente de 3 MHz
```
x ≈ 1 − 4,5 × (15000 / GBW)       (GBW em Hz)
R = x / (2π × 15000 × C)          (com C = 820 pF)
```
Exemplo (GBW = 3 MHz): x ≈ 0,9775 → R ≈ 12,65 kΩ (o projeto usa 12,68 kΩ). Registrar o novo R e o motivo no relatório.

---

## 7. Critérios de aceitação e resultados de referência

Resultados obtidos no **LTspice** com o modelo comportamental `src/tl081_behav.lib` (GBW = 3 MHz, SR = 13 V/µs, Vsat = ±13,5 V), componentes nominais. São os valores de `output/projeto*_tabela.txt`.

### 7.1 Projeto 1 – Filtro

| Grandeza | Teórico (ideal) | Referência simulada | Critério de aceitação |
|---|---:|---:|---|
| Ganho em banda passante | 26,02 dB | 26,020 dB | 26,02 ± 0,1 dB |
| Ganho em 0,5·fc | 25,953 dB | 25,966 dB | ± 0,1 dB do teórico |
| Ganho em fc real (4.979,8 Hz) | 23,010 dB | 23,007 dB | 23,01 ± 0,15 dB |
| Frequência de −3 dB | 4.979,8 Hz | 4.978,9 Hz | 4.980 Hz ± 2 % |
| Ganho em 2·fc | 7,891 dB | 7,833 dB | ± 0,3 dB do teórico |
| Ganho em 10·fc | −33,979 dB | −34,161 dB | ± 0,5 dB do teórico |
| Inclinação entre 5·fc e 20·fc | 60 dB/déc | 60,74 dB/déc | 60 ± 2 dB/déc |
| Ganho em 100·fc | −93,979 dB | −100,0 dB | só informativo (afetado pelo GBW) |

### 7.2 Projeto 2 – Gerador de onda quadrada

| Grandeza | Memorial | Referência simulada | Critério de aceitação |
|---|---:|---:|---|
| Níveis de saída | ±13,5 V | +13,51 / −13,51 V | ± 0,5 V |
| f com P = 0 (máxima) | 10.969 Hz (com slew) | 11.047 Hz | ≥ 10 kHz e dentro de 10.500 a 11.500 Hz |
| f com P = 1,83 kΩ | ≈ 10 kHz | 10.061 Hz | 10 kHz ± 2 % |
| P que dá 10 kHz exatos | 1,83 kΩ | ≈ 1,955 kΩ | entre 1,8 e 2,1 kΩ |
| f com P = 188,01 kΩ | ≈ 1 kHz | 1.000,3 Hz | 1 kHz ± 2 % |
| f com P = 200 kΩ (mínima) | 945,2 Hz | 945,5 Hz | ≤ 1 kHz e dentro de 930 a 960 Hz |
| Ciclo de trabalho | 50 % | 50,00 % (nos quatro casos) | 50 ± 2 % |

A faixa total obtida deve **conter** 1 kHz a 10 kHz.

### 7.3 Projeto 3 – Oscilador de Wien

| Grandeza | Memorial | Referência simulada | Critério de aceitação |
|---|---:|---:|---|
| fosc com R = 12,68 kΩ (compensado) | 14.967 Hz (−0,22 %) | 14.952 Hz (−0,32 %) | 15 kHz ± 1 % (14.850 a 15.150 Hz) |
| fosc com R = 13 kΩ (sem compensação) | 14.607 Hz (−2,62 %) | 14.592 Hz (−2,72 %) | 14.607 Hz ± 1 % (mostra o efeito do GBW) |
| Amplitude de pico | ≈ 9 V (7 a 11 V) | 8,94 V | entre 7 e 11 V, sem ceifar (< 13,5 V) |
| Partida | folga de 4,3 % | amplitude estabiliza em ≈ 2 ms | oscilação parte e estabiliza |
| THD (harmônicas 2 a 5) | — | 1,78 % | informativo (esperado: poucos %) |

---

## 8. Limitações conhecidas (para o relatório e para o agente)

- Os números de referência da seção 7 vêm de um **modelo comportamental** simulado no LTspice. O macromodelo oficial da TI (PSpice) pode dar GBW, slew rate e Vsat ligeiramente diferentes. Pequenas diferenças (décimos de %) em frequências e alguns % na amplitude da Wien são normais e **não** indicam erro de cálculo.
- A amplitude da Wien depende do modelo do 1N4148 e é sensível a R3 e Rg (seção 5.1).
- O modelo do slew rate do memorial para o gerador ("+2·ts") é conservador (≈ 0,5 µs acima da simulação). Isso explica por que, na simulação, os extremos saem ≈ 0,6 % acima do previsto (P = 1,83 kΩ dá 10.061 Hz).
- As tolerâncias de componentes (seção 6.4) não estão nas contas nominais.
- Usando o macromodelo oficial da TI: conferir a **ordem dos pinos** do `.subckt` (o modelo do projeto usa `inp inn vcc vee out`) e se o LTspice consegue ler o arquivo; modelos PSpice às vezes exigem ajustes.
- Efeitos de amp-op real vistos na simulação (não são erros): no astável a tensão no capacitor ultrapassa ligeiramente os limiares (≈ ±6,85 V em 10–11 kHz, ≈ ±6,77 V em 1 kHz) por causa do atraso da troca; na Wien a tensão sobre R4 chega a ≈ ±0,52 V (não 0,6 V); no filtro, a 1 kHz a fase é ≈ −23° (efeito do polo de 5 kHz).

---

## 9. Saídas esperadas da simulação (para o relatório)

Gerar, nomeando claramente os arquivos:

| Projeto | Saída |
|---|---|
| 1 | Diagrama de Bode (ganho × frequência) com fc marcada; tabela de ganhos por frequência (seção 7.1) |
| 2 | Forma de onda de saída em P = 0, 1,83 kΩ, 188,01 kΩ e 200 kΩ; gráfico P × frequência; tabela (seção 7.2) |
| 3 | Partida e estabilização; zoom da região estacionária; FFT; comparação R = 12,68 kΩ × 13 kΩ; tabela (seção 7.3) |

Cada projeto, no relatório, deve trazer: o circuito, os cálculos principais com o motivo de cada um, os dados acrescentados com a justificativa (seção 2), e a comparação **teórico × simulado**, com explicação de qualquer diferença (seção 6.2).

---

## 10. Resumo dos componentes

| Projeto | Componente | Valor teórico | Valor comercial/final | Resultado |
|---|---|---|---|---|
| 1 | R (3 redes RC) | 6.772,6 Ω | 6,8 kΩ | fc = 4.979,8 Hz (−0,40 %) |
| 1 | C (3 capacitores) | 4,7 nF | 4,7 nF | |
| 1 | 1ª seção R1 / R2 | 17,953 kΩ / 2 kΩ | 18 kΩ / 2 kΩ | A1 = 10 |
| 1 | 2ª seção R1 / R2 | R1 = R2 | 10 kΩ / 10 kΩ | A2 = 2 (Q = 1) |
| 1 | Ganho total | 19,9526 V/V (26 dB) | — | 20 V/V = 26,02 dB; 60 dB/déc |
| 1 | Amp-ops | | 2 × TL081, ±15 V | |
| 2 | RA, RB | β = 0,5 | 10 kΩ, 10 kΩ | limiares ±6,75 V |
| 2 | C | 2,2 nF | 2,2 nF | |
| 2 | RF (fixo) | 20,687 kΩ | 18 kΩ | folga para o slew rate |
| 2 | P (potenciômetro) | 186,19 kΩ | 200 kΩ linear | ≈ 945 Hz a 10.969 Hz |
| 2 | Amp-op | | TL081, ±15 V | ±13,5 V, 50 % |
| 3 | R (2 resistores) | 12.939,4 Ω (ideal) / 12.651,6 Ω (compensado) | 12 kΩ + 680 Ω | fosc ≈ 14.967 Hz (−0,22 %) |
| 3 | C (2 capacitores) | 820 pF | 820 pF | |
| 3 | Rg / R3 / R4 | Rg = 10 kΩ, Rf = 20 kΩ | 10 kΩ / 18 kΩ / 3,3 kΩ | A: 3,13 → 2,80 |
| 3 | D1, D2 | | 1N4148 | ≈ 9 V de pico |
| 3 | Amp-op | | TL081, ±15 V | |

---

---

# Apêndice – código de referência

O código de referência deixou de ser copiado neste documento: os arquivos em `src/` são a versão válida e testada.

| Arquivo | Função |
|---|---|
| `src/tl081_behav.lib` | Modelo comportamental do TL081 (GBW = 3 MHz, SR = 13 V/µs, saturação Vcc − 1,5 V / Vee + 1,5 V, `Rout` = 1 Ω; pinos `inp inn vcc vee out`) |
| `src/ltspice_runner.py` | Roda a netlist do PySpice no LTspice (batch) e lê o `.raw` com spicelib |
| `src/medidas.py` | Reamostragem, cruzamentos por zero e tabela de critérios |
| `src/projeto1.py` | Filtro Butterworth: análise AC, tabela e Bode |
| `src/projeto2.py` | Astável: transiente (4 posições de P), varredura P × f, ondas |
| `src/projeto3.py` | Wien: transiente, THD, FFT, comparação 12,68 kΩ × 13 kΩ |
| `src/exportar_netlists.py` / `src/esquematicos.py` | Netlists em `output/netlists/` e esquemáticos |
