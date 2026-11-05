/*
 * Bubble sort por divisao e conquista com MPI -- versao SEM balanceamento
 *
 * Segue o pseudocodigo do enunciado. Os processos formam uma arvore binaria com
 * a numeracao da Figura 1: os filhos de r sao 2r+1 e 2r+2 e o pai e (r-1)/2.
 *
 *   - Cada processo recebe um vetor do pai (a raiz gera o vetor inicial).
 *   - Se o vetor tem mais que "delta" elementos e o processo tem filhos, ele
 *     DIVIDE: manda a primeira metade ao filho da esquerda e a segunda ao da
 *     direita, espera os dois de volta e INTERCALA.
 *   - Senao ele CONQUISTA: ordena o vetor com bubble sort.
 *   - Por fim devolve o vetor ordenado ao pai.
 *
 * Desbalanceamento inerente: so as folhas executam o bubble sort. Os nos
 * internos passam a ordenacao inteira parados em MPI_Recv, esperando os
 * filhos, e so trabalham na intercalacao. Com 2^k - 1 processos, apenas
 * 2^(k-1) (pouco mais da metade) ordenam.
 *
 * delta padrao = ceil(tam / folhas), em que "folhas" e o numero de folhas da
 * maior arvore binaria cheia que cabe nos processos disponiveis. Assim a
 * arvore desce exatamente ate usar todos os processos (com 7 processos e
 * vetor de 40, delta = 10, como no exemplo do enunciado).
 */

#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DEFAULT_TAM 1000000
#define TAG_VETOR 1

/* Papel do processo na execucao, para a analise de balanceamento. */
#define OCIOSO 0  /* nenhum ancestral dividiu ate ele */
#define FOLHA 1   /* conquistou: executou o bubble sort */
#define INTERNO 2 /* dividiu: so esperou e intercalou */

/* Estatisticas de um processo, reunidas na raiz ao final (fora da medicao). */
#define NUM_ESTAT 6
enum { E_NIVEL, E_PAPEL, E_TAM, E_ORDENA, E_ESPERA, E_INTERCALA };

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

/* Um no divide se o vetor e maior que delta e se o filho da direita existe. */
static int divide(int rank, int tam_vetor, int delta, int num_procs) {
    return tam_vetor > delta && 2 * rank + 2 < num_procs;
}

/*
 * Descobre, sem trocar mensagens, se o processo vai receber trabalho e de que
 * tamanho: refaz o caminho da raiz ate ele aplicando a mesma regra de divisao.
 * Processos que nunca recebem nada (por exemplo, quando o numero de processos
 * nao forma uma arvore cheia) nao podem ficar bloqueados esperando o pai.
 */
static int tamanho_do_no(int rank, int tam, int delta, int num_procs) {
    int caminho[64], profundidade = 0;
    for (int r = rank; r > 0; r = (r - 1) / 2) {
        caminho[profundidade++] = r;
    }
    int no = 0, tam_no = tam;
    for (int i = profundidade - 1; i >= 0; i--) {
        if (!divide(no, tam_no, delta, num_procs)) {
            return 0; /* o ancestral conquistou: este processo fica ocioso */
        }
        int filho = caminho[i];
        tam_no = (filho == 2 * no + 1) ? tam_no / 2 : tam_no - tam_no / 2;
        no = filho;
    }
    return tam_no;
}

static int nivel_do_no(int rank) {
    int nivel = 0;
    for (int r = rank; r > 0; r = (r - 1) / 2) nivel++;
    return nivel;
}

int main(int argc, char *argv[]) {
    int my_rank, num_procs;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &num_procs);

    int tam = DEFAULT_TAM, delta = 0, estatisticas = 0;
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--tam") == 0 && i + 1 < argc) {
            tam = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--delta") == 0 && i + 1 < argc) {
            delta = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--estatisticas") == 0) {
            estatisticas = 1;
        }
    }
    if (delta <= 0) {
        /* folhas da maior arvore cheia com num_procs processos */
        int folhas = 1;
        while (4 * folhas - 1 <= num_procs) folhas *= 2;
        delta = (tam + folhas - 1) / folhas;
    }

    int pai = (my_rank - 1) / 2;
    int filho_esq = 2 * my_rank + 1, filho_dir = 2 * my_rank + 2;
    double estat[NUM_ESTAT] = {0};
    estat[E_NIVEL] = nivel_do_no(my_rank);

    int *vetor = NULL;
    int tam_vetor = (my_rank == 0) ? tam : tamanho_do_no(my_rank, tam, delta,
                                                         num_procs);
    if (my_rank == 0) {
        vetor = malloc(sizeof(int) * tam);
        for (int i = 0; i < tam; i++) vetor[i] = tam - i; /* pior caso */
    }

    MPI_Barrier(MPI_COMM_WORLD);
    double inicio = MPI_Wtime();

    if (tam_vetor > 0) {
        if (my_rank != 0) {
            /* nao sou a raiz: recebo do pai e descubro o tamanho */
            MPI_Status status;
            MPI_Probe(pai, TAG_VETOR, MPI_COMM_WORLD, &status);
            MPI_Get_count(&status, MPI_INT, &tam_vetor);
            vetor = malloc(sizeof(int) * tam_vetor);
            MPI_Recv(vetor, tam_vetor, MPI_INT, pai, TAG_VETOR, MPI_COMM_WORLD,
                     MPI_STATUS_IGNORE);
        }
        estat[E_TAM] = tam_vetor;

        if (!divide(my_rank, tam_vetor, delta, num_procs)) {
            /* conquisto */
            estat[E_PAPEL] = FOLHA;
            double t = MPI_Wtime();
            bs(tam_vetor, vetor);
            estat[E_ORDENA] = MPI_Wtime() - t;
        } else {
            /* divido: uma metade para cada filho */
            estat[E_PAPEL] = INTERNO;
            int metade = tam_vetor / 2;
            MPI_Send(&vetor[0], metade, MPI_INT, filho_esq, TAG_VETOR,
                     MPI_COMM_WORLD);
            MPI_Send(&vetor[metade], tam_vetor - metade, MPI_INT, filho_dir,
                     TAG_VETOR, MPI_COMM_WORLD);

            /* espero os filhos devolverem as metades ordenadas */
            double t = MPI_Wtime();
            MPI_Recv(&vetor[0], metade, MPI_INT, filho_esq, TAG_VETOR,
                     MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            MPI_Recv(&vetor[metade], tam_vetor - metade, MPI_INT, filho_dir,
                     TAG_VETOR, MPI_COMM_WORLD, MPI_STATUS_IGNORE);
            estat[E_ESPERA] = MPI_Wtime() - t;

            /* intercalo o vetor inteiro */
            t = MPI_Wtime();
            int *intercalado = interleaving(vetor, tam_vetor);
            free(vetor);
            vetor = intercalado;
            estat[E_INTERCALA] = MPI_Wtime() - t;
        }

        if (my_rank != 0) {
            MPI_Send(vetor, tam_vetor, MPI_INT, pai, TAG_VETOR, MPI_COMM_WORLD);
        }
    }

    double fim = MPI_Wtime();

    /* Fora da medicao: estatisticas de todos os processos na raiz. */
    double *todas = NULL;
    if (my_rank == 0) todas = malloc(sizeof(double) * NUM_ESTAT * num_procs);
    MPI_Gather(estat, NUM_ESTAT, MPI_DOUBLE, todas, NUM_ESTAT, MPI_DOUBLE, 0,
               MPI_COMM_WORLD);

    if (my_rank == 0) {
        int ok = 1;
        for (int i = 0; i < tam; i++) {
            if (vetor[i] != i + 1) {
                ok = 0;
                break;
            }
        }
        printf("%.6f %s delta=%d\n", fim - inicio, ok ? "ok" : "ERRO", delta);
        if (estatisticas) {
            for (int r = 0; r < num_procs; r++) {
                double *e = &todas[r * NUM_ESTAT];
                printf("# rank %d nivel %d papel %d tam %d ordena %.6f "
                       "espera %.6f intercala %.6f\n",
                       r, (int)e[E_NIVEL], (int)e[E_PAPEL], (int)e[E_TAM],
                       e[E_ORDENA], e[E_ESPERA], e[E_INTERCALA]);
            }
        }
        free(todas);
    }
    free(vetor);

    MPI_Finalize();
    return 0;
}
