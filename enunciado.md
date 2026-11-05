# T3 (TPP3) — MPI Divisão e Conquista (D&C)

> Transcrito do Moodle em 03/11/2026.
>
> - Enunciado: https://moodle.pucrs.br/mod/page/view.php?id=3803750 (atualizado 29/10/2026)
> - Pseudocódigo D&C: https://moodle.pucrs.br/mod/page/view.php?id=3803753
> - Artigo da versão balanceada: [docs/refs/mergesort-pdpta11.pdf](docs/refs/mergesort-pdpta11.pdf)
>   (Radenski, *Shared Memory, Message Passing, and Hybrid Merge Sorts for Standalone and
>   Clustered SMPs*, PDPTA'11)
> - Código da versão balanceada: https://github.com/gary-funck/parallel-merge-sort
>   (clonado em [docs/refs/parallel-merge-sort/](docs/refs/parallel-merge-sort/), arquivo `mpi_mergesort.c`)
> - Vídeo de apresentação do enunciado (16 min): https://moodle.pucrs.br/mod/url/view.php?id=3803751
> - Sala de entrega: https://moodle.pucrs.br/mod/assign/view.php?id=3803761
> - **Prazo: terça-feira, 10/11/2026, 19:15** — Grupo 12, apresentação em aula no mesmo dia

## Objetivo

Implementar com MPI uma versão paralela no modelo **divisão e conquista** de uma ordenação
quadrática (**bubble sort**). Executar no cluster atlântica com até 2 nós, variando **1, 3, 7,
15 e 31 processos** (31 com HT). Medir também uma versão em que o trabalho é **balanceado na
árvore** (código do artigo no git).

## Funcionamento (Figura 1, `docs/figura-dc.gif`)

- A raiz verifica se o vetor será **dividido** ou **conquistado**. A condição de conquista é
  uma comparação com um valor fixo (`delta`). Exemplo: vetor de 40 elementos com `delta = 10`
  desce 2 níveis da árvore binária e usa 7 processos.
- Se dividir, cada filho recebe uma metade e repete a decisão.
- As folhas ordenam com bubble sort e devolvem ao pai. O pai intercala os dois vetores
  recebidos e devolve ao seu pai, até a raiz ter o vetor original ordenado.
- Numeração da figura: filhos de `p` são `2p+1` e `2p+2` (p0 → p1, p2; p1 → p3, p4; p2 → p5, p6).

Referência de tempo dada no enunciado: **1.000.000 de elementos** com 1 processo levou
**74 min** na atlântica; com 3 processos (raiz + 2 filhos) em 3 núcleos, **18 min**.

## Itens de avaliação (enunciado)

- execução da versão sequencial da ordenação;
- implementação da versão paralela SPMD do BS em MPI no modelo divisão e conquista;
- medição da sequencial em um core e da paralela (2 nós exclusivos da atlântica, 15
  processadores; cada nó tem 8 processadores físicos);
- speed-up e eficiência para 1, 3, 7, 15 e 31 processos (31 com HT);
- análise do balanceamento de carga nos diferentes níveis da árvore;
- análise do ganho com HT;
- análise do ganho com um mecanismo de balanceamento de carga (aumentando o número de
  processos **e** com a versão do artigo);
- executar com mais processos (63, 127, 255, 511, 1023) e analisar o desempenho;
- clareza do código (comentários e nomes de variáveis).

## Rubrica (11 critérios, 0–10 cada)

1. O relatório está bem escrito e no formato solicitado.
2. Implementou o algoritmo **sem balanceamento** corretamente e ordenou vetores de **1.000.000**
   de elementos.
3. Enviou o código da versão sem balanceamento em anexo, de forma que foi possível reproduzir os
   resultados.
4. Explicou como funciona o código sem balanceamento e, **especialmente, a versão com
   balanceamento do artigo**, detalhando as mensagens enviadas e como funciona a **condição de
   parada**.
5. Abordou o **balanceamento de carga** (foco do trabalho): problemas da versão sem
   balanceamento e como podem ser mitigados **com e sem alteração no código** (versão do artigo).
6. Executou as duas versões com um número grande de processos (63, 127, 255, 512, 1023) e
   explicou o que aconteceu com o desempenho.
7. Avaliou o desempenho da versão sem balanceamento, com balanceamento por aumento do número de
   processos e com balanceamento por alteração do código (versão do artigo).
8. Plotou a **escalabilidade forte e a eficiência para as duas versões**, com tabelas, e os
   valores são compatíveis com o esperado.
9. Deixou claro se usou ferramenta de IA, qual e como (instrumentação do código e relatório).
10. Dedicou boa parte do relatório a uma análise aprofundada dos resultados.
11. Apresentou os resultados em aula com participação ativa de todos os integrantes.

## Código fornecido

Bubble sort (`bs`) e intercalação (`interleaving`): ver o enunciado no Moodle. O vetor de teste
é inicializado no pior caso (ordem decrescente: `vetor[i] = ARRAY_SIZE - i`). Tamanhos citados
no código: 10.000, 100.000 e 1.000.000.

## Pseudocódigo D&C do professor

```c
MPI_Init();
my_rank = MPI_Comm_rank();
if (my_rank != 0) {                               // não sou a raiz, tenho pai
    MPI_Recv(vetor, pai);
    MPI_Get_count(&Status, MPI_INT, &tam_vetor);  // tamanho da mensagem recebida
} else {
    tam_vetor = VETOR_SIZE;
    Inicializa(vetor, tam_vetor);                 // raiz gera o vetor (ordem reversa)
}
if (tam_vetor <= delta)
    BubbleSort(vetor);                            // conquisto
else {                                            // divido
    MPI_Send(&vetor[0], filho_esquerda, tam_vetor/2);
    MPI_Send(&vetor[tam_vetor/2], filho_direita, tam_vetor/2);
    MPI_Recv(&vetor[0], filho_esquerda);
    MPI_Recv(&vetor[tam_vetor/2], filho_direita);
    Intercala(vetor);
}
if (my_rank != 0) MPI_Send(vetor, pai, tam_vetor); // devolvo ao pai
else Mostra(vetor);
MPI_Finalize();
```

## Versão balanceada (artigo, `mpi_mergesort.c`)

- O processo **fica com uma metade** e envia a outra a um ajudante, em vez de mandar as duas
  metades e ficar parado esperando: `helper_rank = my_rank + 2^level`.
- Cada ajudante calcula o seu nível mais alto na árvore (`my_topmost_level`) e repete o
  procedimento com a parte que recebeu.
- **Condição de parada:** quando `helper_rank > max_rank` (não há mais processos), o processo
  ordena sozinho a parte que tem. Não há `delta` fixo: a profundidade sai do número de processos.
- Envio assíncrono (`MPI_Isend`) da metade, ordenação da própria metade, `MPI_Recv` da metade
  ordenada do ajudante e intercalação.
