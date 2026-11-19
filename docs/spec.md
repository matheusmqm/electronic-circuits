# Especificação do Projeto – Circuitos Eletrônicos (2ª Etapa, 2026.2)

> **Origem:** transcrição do PDF do enunciado do professor ("Material para compor a Nota da Etapa – Semestre 2026.2", arquivo `1978201-2 Etapa - Projeto da Circuitos Eletrônicos - Computação - 2026-2.pdf`).
> **Uso:** documento de contexto para o Claude Code. O texto do enunciado foi mantido fielmente; as seções "Resumo", "Checklist" e "Notas de interpretação" foram acrescentadas só para organizar o que o enunciado já diz, sem criar requisitos novos.
> **Ferramenta de simulação escolhida pela equipe:** PySpice (montagem das netlists) + LTspice (simulação). O enunciado permite "outro simulador de sua escolha" (ver item 4).
> **Documento complementar:** `calculos.md` (cálculos, valores dos componentes, plano e critérios de simulação).

---

## 1. Texto do enunciado (transcrição)

### Material para compor a Nota da Etapa — Semestre 2026.2

Caros alunos e alunas,

Apresentamos para vocês a proposta para compor a nota da 2ª etapa do semestre.
A nota da etapa será composta pela **simulação** e a **pesquisa bibliográfica sobre os Transistores a Efeito de Campo**.

O trabalho deverá ser entregue **até o dia 25 de novembro** sem a possibilidade de prorrogação.

Cada equipe deverá ser formada por, **no máximo, seis alunos**. Não haverá a possibilidade de acrescentar mais participantes à equipe. Formem uma nova equipe se for preciso. Não adianta insistir que não vou abrir mão disso.

O trabalho pode ser enviado para o meu e-mail até o dia 25 de novembro. Ou entregue pessoalmente no dia da entrega no laboratório às **13:30 h**. Irei ao laboratório nessa tarde só para receber os relatórios das equipes que decidiram entregar o relatório pessoalmente. **Trabalho via e-mail apenas em PDF.**
E-mail: `jbento@ifce.edu.br`

No dia 18 de novembro não teremos aula de laboratório. Não precisam aparecer no laboratório. Aproveitem e façam o trabalho.

A primeira parte é simulação e a segunda parte é uma pesquisa bibliográfica sobre os transistores a efeito de campo.

A simulação pode ser executada num simulador de circuitos eletrônicos (ORCAD, PROTEUS, MULTSIM, ou outro de sua escolha).

O relatório (um relatório por equipe) deverá ser entregue até o dia 25 de novembro, **digitado com os nomes de todos os membros da equipe**. Entregue pessoalmente ou por e-mail.

### 1ª Parte

1. **Filtro Passa Baixa, tipo Butterworth, frequência de corte de 5 kHz, com inclinação de 60 dB/década e ganho na faixa de passagem em 26 dB.**

2. **Gerador de Onda Quadrada usando amplificador operacional** com as seguintes características: o sinal deverá variar na seguinte década: de 1 kHz a 10 kHz.

3. **Oscilador Senoidal a ponte de Wien com frequência de oscilação de 15 kHz** usando amplificador operacional.

A equipe vai precisar acrescentar alguns dados ou informações no desenvolvimento de cada projeto. Deve ser feito e **explicar o porquê do acréscimo no relatório**.

**Cada equipe deverá entregar os três projetos propostos.**

### 2ª Parte

Desenvolver uma pesquisa teórica sobre o transistor a efeito de campo (FET).

Na pesquisa incluir os tópicos:

- Caracterização do componente FET e suas curvas características.
- Apresentar possibilidades de se polarizar e amplificar o componente FET.
- Apresentar aplicações para o componente.

**Data da entrega do trabalho: 25 de novembro (sem prorrogação).** Depois dessa data não teremos mais aulas.

Não haverá a possibilidade de se desenvolver o trabalho individualmente.

Após a correção dos relatórios a nota será publicada no Acadêmico.

Os alunos que precisarem fazer a avaliação final da disciplina deverão comparecer à sala de aula no dia **11/12** para fazerem a avaliação. Na avaliação constarão questões envolvendo os assuntos estudados ao longo de todo o semestre, inclusive os abordados no desenvolvimento do projeto.

---

## 2. Resumo dos requisitos

| Item | Requisito |
|---|---|
| Composição da nota | Simulação (1ª parte) + pesquisa bibliográfica sobre FET (2ª parte) |
| Prazo | **25 de novembro**, sem prorrogação |
| Equipe | Até 6 alunos; sem acréscimo de integrantes; sem trabalho individual |
| Entrega | Um relatório por equipe. Por e-mail (`jbento@ifce.edu.br`, **somente PDF**) ou pessoalmente no laboratório, às 13:30 h, no dia 25/11 |
| Conteúdo do relatório | Digitado, com o nome de todos os membros; os três projetos da 1ª parte; a pesquisa da 2ª parte; explicação do porquê de cada dado acrescentado |
| Simulador | ORCAD, PROTEUS, MULTISIM "ou outro de sua escolha" |
| Avaliação final | Quem precisar fazer: 11/12, em sala; inclui assuntos do semestre e dos projetos |

### Os três projetos da 1ª parte

| # | Projeto | Especificação do enunciado |
|---|---|---|
| 1 | Filtro passa-baixa Butterworth | fc = **5 kHz**; inclinação **60 dB/década**; ganho na faixa de passagem **26 dB** |
| 2 | Gerador de onda quadrada com amp-op | frequência variável na década de **1 kHz a 10 kHz** |
| 3 | Oscilador senoidal em ponte de Wien com amp-op | frequência de oscilação de **15 kHz** |

### Os tópicos da 2ª parte (pesquisa sobre FET)

1. Caracterização do componente FET e suas curvas características.
2. Possibilidades de polarizar e amplificar o FET.
3. Aplicações do componente.

---

## 3. Checklist de entregáveis

**Relatório (PDF)**
- [ ] Nomes de **todos** os membros da equipe (máximo 6).
- [ ] Projeto 1 (filtro): cálculo, circuito e resultado de simulação.
- [ ] Projeto 2 (onda quadrada 1–10 kHz): cálculo, circuito e resultado de simulação.
- [ ] Projeto 3 (Wien 15 kHz): cálculo, circuito e resultado de simulação.
- [ ] Em cada projeto, os **dados acrescentados** pela equipe, **com a explicação do porquê** de cada um.
- [ ] Pesquisa sobre FET com os três tópicos: caracterização e curvas; polarização e amplificação; aplicações.
- [ ] Texto digitado.
- [ ] Arquivo em PDF (obrigatório se enviado por e-mail).

**Prazos e logística**
- [ ] Entregar até 25/11 (e-mail para `jbento@ifce.edu.br`, ou pessoalmente no laboratório às 13:30 h).
- [ ] Sem prorrogação.

---

## 4. Notas de interpretação (para o agente)

Estas notas não fazem parte do enunciado. São leituras diretas do texto, registradas para evitar dúvidas:

1. **Simulador.** O enunciado cita ORCAD, PROTEUS e MULTISIM, mas admite "outro de sua escolha". A equipe escolheu **PySpice (montagem das netlists) + LTspice (simulação)**.
2. **"Acrescentar dados".** O enunciado deixa propositalmente em aberto parâmetros de projeto (amplificador operacional, tensão de alimentação, valores de componentes, topologia, ganho de cada seção etc.). O que a equipe definir deve aparecer **com justificativa** no relatório. Esses dados já estão definidos e justificados em `calculos.md` (seção 2).
3. **"Cada equipe deverá entregar os três projetos".** Nenhum dos três pode ficar de fora.
4. **Ganho de 26 dB.** É ganho **na faixa de passagem** (e não em fc, onde o ganho é 3 dB menor).
5. **Inclinação de 60 dB/década.** Equivale a um filtro de 3ª ordem (3 polos).
6. **Gerador de onda quadrada.** "Variar na década de 1 kHz a 10 kHz" exige frequência ajustável (por exemplo, por potenciômetro) cobrindo os dois extremos.
7. **Oscilador de Wien.** Frequência de oscilação de 15 kHz, senoidal, com amp-op.
8. **Prazo.** Hoje é 19/11/2026; a entrega é em 25/11/2026.