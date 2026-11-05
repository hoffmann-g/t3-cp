/*
 * Bubble sort por divisao e conquista com MPI -- versao COM balanceamento
 *
 * Adaptacao do mpi_mergesort.c de Radenski (PDPTA'11, codigo em
 * github.com/gary-funck/parallel-merge-sort). A unica mudanca de algoritmo e a
 * fase serial: o artigo usa merge sort, e aqui usamos o bubble sort do
 * enunciado, para que as duas versoes do trabalho ordenem da mesma forma.
 *
 * Diferenca em relacao a versao sem balanceamento: o processo NAO entrega as
 * duas metades e fica esperando. Ele envia so a segunda metade a um ajudante e
 * continua trabalhando na primeira, recursivamente. Assim todo processo,
 * inclusive a raiz, termina ordenando um pedaco do vetor.
 *
 * Mensagens e arvore de processos:
 *   - No nivel L, o processo r usa como ajudante o processo r + 2^L
 *     (raiz: ajudantes 1, 2, 4, 8...; processo 1: ajudantes 3, 5, 9...).
 *   - Envio da segunda metade com MPI_Isend; o processo ordena a primeira
 *     metade (descendo um nivel), recebe a segunda metade ordenada com MPI_Recv
 *     e intercala.
 *   - Cada ajudante calcula o nivel em que entra na arvore (o menor L com
 *     2^L > rank), recebe do pai com MPI_Probe/MPI_Get_count (o tamanho e o pai
 *     vem da propria mensagem), repete o procedimento e devolve o resultado.
 *
 * Condicao de parada: nao ha "delta". Quando o ajudante calculado nao existe
 * (r + 2^L > ultimo rank), o processo ordena sozinho o pedaco que tem. A
 * profundidade da arvore sai do numero de processos: com p = 2^k, todos os p
 * processos ordenam pedacos de n/p; com p = 2^k - 1, um processo fica com o
 * dobro dos demais.
 *
 * --bloqueante: troca o MPI_Isend por MPI_Send. Com MPI_Isend, uma mensagem
 * grande so e transferida quando o remetente volta a chamar o MPI; como ele
 * entra direto no bubble sort, o ajudante so recebe a sua metade depois que o
 * pai termina a propria parte, e os dois trabalhos acabam em sequencia. Com
 * MPI_Send, o pai so segue depois de entregar a metade, e o ajudante comeca
 * na hora (ele ja esta esperando em MPI_Probe).
 */

#include <mpi.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DEFAULT_TAM 1000000
#define TAG_VETOR 1

static int envio_bloqueante = 0; /* --bloqueante */

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

/* Nivel em que o processo entra na arvore: menor L com 2^L > rank. */
static int nivel_inicial(int rank) {
    int nivel = 0;
    while ((1 << nivel) <= rank) nivel++;
    return nivel;
}

/*
 * Ordena a[0..tam) a partir do nivel "nivel" da arvore. "estat" acumula o
 * tempo deste processo em cada atividade.
 */
static void ordenar_paralelo(int *a, int tam, int nivel, int my_rank,
                             int max_rank, double *estat) {
    int ajudante = my_rank + (1 << nivel);

    if (ajudante > max_rank) {
        /* condicao de parada: nao ha mais processos, ordeno sozinho */
        double t = MPI_Wtime();
        bs(tam, a);
        estat[E_ORDENA] += MPI_Wtime() - t;
        estat[E_TAM] = tam;
        return;
    }

    /* envio a segunda metade ao ajudante e continuo com a primeira */
    int metade = tam / 2;
    MPI_Request requisicao = MPI_REQUEST_NULL;
    if (envio_bloqueante) {
        MPI_Send(a + metade, tam - metade, MPI_INT, ajudante, TAG_VETOR,
                 MPI_COMM_WORLD);
    } else {
        MPI_Isend(a + metade, tam - metade, MPI_INT, ajudante, TAG_VETOR,
                  MPI_COMM_WORLD, &requisicao);
    }
    ordenar_paralelo(a, metade, nivel + 1, my_rank, max_rank, estat);
    MPI_Wait(&requisicao, MPI_STATUS_IGNORE);

    /* recebo a segunda metade ordenada */
    double t = MPI_Wtime();
    MPI_Recv(a + metade, tam - metade, MPI_INT, ajudante, TAG_VETOR,
             MPI_COMM_WORLD, MPI_STATUS_IGNORE);
    estat[E_ESPERA] += MPI_Wtime() - t;

    /* intercalo as duas metades */
    t = MPI_Wtime();
    int *intercalado = interleaving(a, tam);
    memcpy(a, intercalado, sizeof(int) * tam);
    free(intercalado);
    estat[E_INTERCALA] += MPI_Wtime() - t;
}

int main(int argc, char *argv[]) {
    int my_rank, num_procs;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &my_rank);
    MPI_Comm_size(MPI_COMM_WORLD, &num_procs);
    int max_rank = num_procs - 1;

    int tam = DEFAULT_TAM, estatisticas = 0;
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--tam") == 0 && i + 1 < argc) {
            tam = atoi(argv[++i]);
        } else if (strcmp(argv[i], "--estatisticas") == 0) {
            estatisticas = 1;
        } else if (strcmp(argv[i], "--bloqueante") == 0) {
            envio_bloqueante = 1;
        }
    }

    double estat[NUM_ESTAT] = {0};
    int nivel = (my_rank == 0) ? 0 : nivel_inicial(my_rank);
    estat[E_NIVEL] = nivel;
    estat[E_PAPEL] = 1; /* todo processo ordena um pedaco */

    int *vetor = NULL;
    if (my_rank == 0) {
        vetor = malloc(sizeof(int) * tam);
        for (int i = 0; i < tam; i++) vetor[i] = tam - i; /* pior caso */
    }

    MPI_Barrier(MPI_COMM_WORLD);
    double inicio = MPI_Wtime();

    if (my_rank == 0) {
        ordenar_paralelo(vetor, tam, 0, my_rank, max_rank, estat);
    } else {
        /* ajudante: o pai e o tamanho vem da propria mensagem */
        MPI_Status status;
        int tam_vetor;
        MPI_Probe(MPI_ANY_SOURCE, TAG_VETOR, MPI_COMM_WORLD, &status);
        MPI_Get_count(&status, MPI_INT, &tam_vetor);
        int pai = status.MPI_SOURCE;
        vetor = malloc(sizeof(int) * tam_vetor);
        MPI_Recv(vetor, tam_vetor, MPI_INT, pai, TAG_VETOR, MPI_COMM_WORLD,
                 MPI_STATUS_IGNORE);
        ordenar_paralelo(vetor, tam_vetor, nivel, my_rank, max_rank, estat);
        MPI_Send(vetor, tam_vetor, MPI_INT, pai, TAG_VETOR, MPI_COMM_WORLD);
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
        printf("%.6f %s\n", fim - inicio, ok ? "ok" : "ERRO");
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
