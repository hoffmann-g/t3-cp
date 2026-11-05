/*
 * Ordenacao por troca simples (bubble sort) -- versao sequencial (T3)
 *
 * Dois modos, ambos em um unico processo:
 *
 *   --delta 0 (padrao): bubble sort no vetor inteiro. E a linha de base pedida
 *       no enunciado ("versao sequencial em um core").
 *   --delta D > 0: a mesma divisao e conquista da versao MPI, executada em um
 *       core so. O vetor e dividido ao meio ate o pedaco ter no maximo D
 *       elementos; cada pedaco e ordenado com bubble sort e os pares sao
 *       intercalados de volta. Serve de referencia justa: como o bubble sort e
 *       O(n^2), dividir o vetor ja reduz o trabalho total, e esta versao separa
 *       esse ganho algoritmico do ganho do paralelismo.
 *
 * O vetor e inicializado no pior caso (ordem decrescente), como no codigo do
 * enunciado. Depois de ordenado ele deve conter 1, 2, ..., n.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define DEFAULT_TAM 1000000

/* Bubble sort do enunciado: para quando uma passada nao faz troca. */
static void bs(int n, int *vetor) {
    int c = 0, d, troca, trocou = 1;

    while (c < (n - 1) && trocou) {
        trocou = 0;
        for (d = 0; d < n - c - 1; d++) {
            if (vetor[d] > vetor[d + 1]) {
                troca = vetor[d];
                vetor[d] = vetor[d + 1];
                vetor[d + 1] = troca;
                trocou = 1;
            }
        }
        c++;
    }
}

/* Rotina de intercalacao do enunciado: as duas metades de "vetor" ja estao
   ordenadas; devolve um novo vetor com o resultado intercalado. */
static int *interleaving(int vetor[], int tam) {
    int *vetor_auxiliar;
    int i1, i2, i_aux;

    vetor_auxiliar = (int *)malloc(sizeof(int) * tam);

    i1 = 0;
    i2 = tam / 2;

    for (i_aux = 0; i_aux < tam; i_aux++) {
        if (((vetor[i1] <= vetor[i2]) && (i1 < (tam / 2))) || (i2 == tam))
            vetor_auxiliar[i_aux] = vetor[i1++];
        else
            vetor_auxiliar[i_aux] = vetor[i2++];
    }

    return vetor_auxiliar;
}

/* Divisao e conquista em um unico processo: mesmo criterio de parada da versao
   MPI (pedaco com no maximo "delta" elementos). */
static void dc_sequencial(int *vetor, int tam, int delta) {
    if (tam <= delta) {
        bs(tam, vetor);
        return;
    }
    int metade = tam / 2;
    dc_sequencial(vetor, metade, delta);
    dc_sequencial(vetor + metade, tam - metade, delta);
    int *intercalado = interleaving(vetor, tam);
    memcpy(vetor, intercalado, sizeof(int) * tam);
    free(intercalado);
}

static double get_time(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
}

int main(int argc, char *argv[]) {
    int tam = DEFAULT_TAM;
    int delta = 0;

    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--tam") == 0 && i + 1 < argc) {
            tam = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--delta") == 0 && i + 1 < argc) {
            delta = atoi(argv[++i]);
        }
    }

    int *vetor = malloc(sizeof(int) * tam);
    if (vetor == NULL) {
        fprintf(stderr, "Erro ao alocar o vetor.\n");
        return 1;
    }
    for (int i = 0; i < tam; i++) {
        vetor[i] = tam - i; /* pior caso: ordem decrescente */
    }

    double inicio = get_time();
    if (delta > 0) {
        dc_sequencial(vetor, tam, delta);
    } else {
        bs(tam, vetor);
    }
    double fim = get_time();

    int ok = 1;
    for (int i = 0; i < tam; i++) {
        if (vetor[i] != i + 1) {
            ok = 0;
            break;
        }
    }
    free(vetor);

    printf("%.6f %s\n", fim - inicio, ok ? "ok" : "ERRO");
    return ok ? 0 : 1;
}
