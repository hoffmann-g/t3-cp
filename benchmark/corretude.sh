#!/bin/bash
# Confere que as duas versoes MPI devolvem o vetor ordenado (1, 2, ..., n) em
# casos de borda: tamanho par, impar e pequeno, numero de processos que forma
# ou nao uma arvore cheia, e overcommit. Rodar dentro de uma alocacao:
#   salloc -N 2 --exclusive bash corretude.sh
set -u
cd "$(dirname "$0")"

falhas=0
testar() {  # testar <binario> <processos> <tam>
    local bin=$1 np=$2 tam=$3 extra=""
    [ "$np" -gt 32 ] && extra="--overcommit"
    local saida
    saida=$(srun $extra -N 2 -n "$np" "./$bin" --tam "$tam" 2>&1 | head -1)
    if [[ "$saida" == *" ok"* ]]; then
        echo "OK    $bin np=$np tam=$tam ($saida)"
    else
        echo "FALHA $bin np=$np tam=$tam: $saida"
        falhas=$((falhas + 1))
    fi
}

for bin in dc_mpi dc_artigo_mpi; do
    for np in 2 3 4 5 7 8 15 16 31 32; do
        testar "$bin" "$np" 40
        testar "$bin" "$np" 1001
    done
    testar "$bin" 63 100000
    testar "$bin" 1023 100000
done

echo "sequencial 100000: $(srun -N 1 -n 1 ./bs_seq --tam 100000)"
echo "falhas: $falhas"
exit $falhas
