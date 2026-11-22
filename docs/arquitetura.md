# Arquitetura do Relatório em PDF (ABNT)

Estrutura do PDF entregue, limitada ao que o `spec.md` exige e à NBR 14724. Nada além disso.

## 1. O que o spec exige e onde está no PDF

| Exigência do spec | Onde |
|---|---|
| Um relatório por equipe, digitado, com o nome de todos os integrantes (máx. 6) | Capa e folha de rosto |
| Entrega em PDF até 25/11 | `output/Relatorio_Circuitos_Eletronicos.pdf` |
| Projeto 1: filtro Butterworth, fc = 5 kHz, 60 dB/déc, ganho 26 dB | Cap. 3 |
| Projeto 2: gerador de onda quadrada, 1 kHz a 10 kHz, com amp-op | Cap. 4 |
| Projeto 3: oscilador de ponte de Wien, 15 kHz, com amp-op | Cap. 5 |
| Dados acrescentados a cada projeto, com o porquê | Seção 2.1 e cálculos de cada projeto |
| Simulador à escolha | Seção 2.2 (LTspice; netlists montadas com PySpice) |
| FET: caracterização e curvas características | Seções 6.1 e 6.2 |
| FET: polarização e amplificação | Seção 6.3 |
| FET: aplicações | Seção 6.4 |

## 2. Estrutura (NBR 14724)

**Pré-textuais:** capa, folha de rosto, resumo com palavras-chave (NBR 6028) e sumário (NBR 6027). Contadas, mas sem número visível.

**Textuais** (numeração visível a partir da Introdução, canto superior direito; numeração progressiva NBR 6024):

```
1 INTRODUÇÃO
2 METODOLOGIA E FERRAMENTAS DE SIMULAÇÃO   (2.1 dados acrescentados; 2.2 simulador; 2.3 alimentação e partida)
3 PROJETO 1 – FILTRO PASSA-BAIXA BUTTERWORTH   (3.1 a 3.6)
4 PROJETO 2 – GERADOR DE ONDA QUADRADA          (4.1 a 4.6)
5 PROJETO 3 – OSCILADOR SENOIDAL EM PONTE DE WIEN (5.1 a 5.6)
6 PESQUISA TEÓRICA: TRANSISTOR A EFEITO DE CAMPO (FET) (6.1 a 6.4)
7 CONSIDERAÇÕES FINAIS                          (conclusão e limitações, sem subseções)
```

Cada projeto: especificação, cálculos, componentes e conexões (com o esquemático), funcionamento, resultados da simulação e análise.

**Pós-textual:** referências (NBR 6023, ordem alfabética), citações no formato autor-data (NBR 10520).

## 3. Formatação

A4; margens 3 cm (superior e esquerda) e 2 cm (inferior e direita); Times New Roman 12; entrelinhas 1,5 (espaço simples em legendas, tabelas e resumo; fonte 10 nesses itens); recuo de 1,25 cm no parágrafo; texto justificado. Figuras e tabelas com título acima e "Fonte" abaixo, citadas no texto; tabelas no padrão IBGE (sem fechamento lateral); quadros fechados; equações centralizadas e numeradas à direita.

## 4. Origem do conteúdo

| Parte do PDF | Fonte |
|---|---|
| Capa e folha de rosto | constantes no início de `src/gerar_relatorio.py` |
| Resumo, introdução, conclusão, referências | `docs/elementos.md` |
| Caps. 2 a 5 e 7 | `docs/relatorio.md` (sem reescrita; só retirados os nomes de arquivos do repositório e ajustada a numeração) |
| Cap. 6 (FET) | `docs/fet.md`; figuras de `src/fet_curvas.py` |

## 5. Como gerar

```
uv run --no-project --with python-docx --with matplotlib python src/gerar_relatorio.py
```

Monta o `.docx` e o Word (via `src/exportar_pdf.ps1`) atualiza o sumário e exporta o PDF. Saída em `output/`.

## 6. Pendências que só a equipe pode preencher

- Nomes dos integrantes, nome do professor e cidade (capa e folha de rosto; constantes `EQUIPE`, `PROFESSOR`, `LOCAL` no script).
- Conferir instituição e curso (`INSTITUICAO`, `CURSO`).
- Conferir edição e ano dos livros e a revisão do datasheet do TL081 (hoje `[s.d.]`); acrescentar páginas nas citações.
