# RESUMO

Este relatório apresenta a simulação de três circuitos com amplificador operacional e uma pesquisa teórica sobre o transistor a efeito de campo (FET), desenvolvidas para a 2ª etapa da disciplina de Circuitos Eletrônicos. Na primeira parte, os circuitos foram projetados e simulados no LTspice com o amplificador operacional TL081 alimentado em ±15 V: um filtro passa-baixa Butterworth de 3ª ordem, com frequência de corte de 5 kHz, inclinação de 60 dB/década e ganho de 26 dB na faixa de passagem; um gerador de onda quadrada com frequência ajustável de 1 kHz a 10 kHz; e um oscilador senoidal em ponte de Wien de 15 kHz. Os dados acrescentados ao projeto, como o amplificador operacional, a alimentação e os valores comerciais de componentes, são justificados no texto. Os resultados simulados concordaram com os cálculos: o filtro apresentou ganho de 26,02 dB e frequência de −3 dB de 4.978,9 Hz; o gerador cobriu de 945,5 Hz a 11.047 Hz; e o oscilador operou em 14.952 Hz. Na segunda parte, caracterizam-se o JFET e o MOSFET e suas curvas características, apresentam-se formas de polarização e de amplificação e relacionam-se aplicações do componente.

# PALAVRAS-CHAVE

Amplificador operacional. Filtro Butterworth. Oscilador de Wien. Transistor a efeito de campo. Simulação.

# INTRODUÇÃO

Este relatório reúne os trabalhos propostos para a nota da 2ª etapa da disciplina de Circuitos Eletrônicos (semestre 2026.2): a simulação de três circuitos com amplificador operacional e uma pesquisa teórica sobre o transistor a efeito de campo (FET).

Na primeira parte, foram projetados e simulados um filtro passa-baixa Butterworth com frequência de corte de 5 kHz, inclinação de 60 dB/década e ganho de 26 dB na faixa de passagem; um gerador de onda quadrada com amplificador operacional, cuja frequência varia na década de 1 kHz a 10 kHz; e um oscilador senoidal em ponte de Wien com frequência de oscilação de 15 kHz. Conforme o enunciado, foram acrescentados dados ao desenvolvimento de cada projeto, e o motivo de cada acréscimo é explicado ao longo do texto. Na segunda parte, a pesquisa sobre o FET aborda a sua caracterização e curvas características, as formas de polarização e de amplificação e as aplicações do componente.

O trabalho está organizado em sete capítulos. O Capítulo 2 descreve a metodologia e os dados acrescentados; os Capítulos 3 a 5 apresentam os três projetos; o Capítulo 6 traz a pesquisa sobre o FET; e o Capítulo 7 reúne as considerações finais.

# CONCLUSÃO

Os três circuitos foram projetados e simulados no LTspice com o amplificador operacional TL081 e atenderam às especificações do enunciado: o filtro Butterworth de 3ª ordem tem frequência de corte de 5 kHz, inclinação de 60 dB/década e ganho de 26 dB na faixa de passagem; o gerador de onda quadrada cobre a década de 1 kHz a 10 kHz; e o oscilador de Wien oscila em 15 kHz (14,95 kHz na simulação). As limitações do amplificador operacional real, como a taxa de subida (*slew rate*) e o produto ganho-banda, foram consideradas no projeto. Os valores medidos estão nos Capítulos 3 a 5.

A pesquisa sobre o FET apresentou a caracterização do componente e suas curvas características, as formas de polarização e de amplificação e as aplicações, atendendo ao que foi solicitado para a segunda parte.

# REFERÊNCIAS

BOYLESTAD, R. L.; NASHELSKY, L. **Dispositivos eletrônicos e teoria de circuitos**. 11. ed. São Paulo: Pearson, 2013.

MALVINO, A.; BATES, D. J. **Eletrônica**. 8. ed. Porto Alegre: AMGH, 2016. v. 1.

SEDRA, A. S.; SMITH, K. C. **Microeletrônica**. 5. ed. São Paulo: Pearson, 2007.

TEXAS INSTRUMENTS. **TL08x JFET-Input Operational Amplifiers**: datasheet. Dallas: Texas Instruments, [s.d.].
