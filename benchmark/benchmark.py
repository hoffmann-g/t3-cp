#!/usr/bin/env python3
"""
Benchmark do T3: bubble sort por divisao e conquista com MPI.

Cada execucao vira uma linha em ../resultados/brutos-<job>.csv, gravada assim que
termina, para que um job interrompido nao perca o que ja mediu. As
estatisticas por processo (nivel, tamanho do pedaco, tempo ordenando,
esperando e intercalando) da primeira repeticao de cada configuracao vao para
../resultados/processos-<job>.csv. A analise e feita fora do cluster (analise.py).

Experimentos:
  seq      bubble sort sequencial no vetor inteiro (linha de base do enunciado)
  dcseq    divisao e conquista em 1 core, com 2, 4, 8 e 16 pedacos: separa o
           ganho algoritmico (dividir um problema O(n^2)) do ganho do paralelismo
  forte    as duas versoes MPI em 2 nos: sem balanceamento com 3, 7, 15 e 31
           processos; versao do artigo com 2, 3, 4, 7, 8, 15, 16, 31 e 32
  muitos   as duas versoes com 63, 127, 255, 511 e 1023 processos (overcommit)
  extra    versao do artigo com envio bloqueante (--bloqueante) e distribuicao
           ciclica dos ranks entre os nos (srun -m cyclic)
"""

import argparse
import csv
import os
import subprocess
import sys
import time

TAM = 1_000_000
TIMEOUT = 3 * 3600

AQUI = os.path.dirname(os.path.abspath(__file__))
RESULTADOS = os.path.join(AQUI, "..", "resultados")
# Um par de arquivos por job: os jobs de 1 e 2 nos rodam ao mesmo tempo e nao
# devem escrever no mesmo arquivo.
JOB = os.environ.get("SLURM_JOB_ID", "local")
BRUTOS = os.path.join(RESULTADOS, f"brutos-{JOB}.csv")
PROCESSOS = os.path.join(RESULTADOS, f"processos-{JOB}.csv")

CAMPOS_BRUTOS = ["experimento", "versao", "processos", "nos", "tam", "pedacos",
                 "repeticao", "tempo_s", "ok"]
CAMPOS_PROC = ["experimento", "versao", "processos", "rank", "nivel", "papel",
               "tam", "ordena_s", "espera_s", "intercala_s"]


def anexar(caminho, campos, linhas):
    novo = not os.path.exists(caminho)
    with open(caminho, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        if novo:
            w.writeheader()
        w.writerows(linhas)


def executar(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=TIMEOUT,
                       cwd=AQUI)
    linhas = [l for l in r.stdout.splitlines() if l.strip()]
    if r.returncode != 0 or not linhas:
        raise RuntimeError(f"{' '.join(cmd)}\n{r.stdout}\n{r.stderr}")
    tempo, ok = linhas[0].split()[:2]
    procs = []
    for l in linhas[1:]:
        # "# rank R nivel N papel P tam T ordena X espera Y intercala Z"
        p = l.split()
        if p[0] == "#" and p[1] == "rank":
            procs.append(dict(rank=p[2], nivel=p[4], papel=p[6], tam=p[8],
                              ordena_s=p[10], espera_s=p[12],
                              intercala_s=p[14]))
    return float(tempo), ok, procs


def medir(experimento, versao, cmd, processos, nos, pedacos, reps):
    tempos = []
    for rep in range(reps):
        tempo, ok, procs = executar(cmd)
        tempos.append(tempo)
        anexar(BRUTOS, CAMPOS_BRUTOS, [dict(
            experimento=experimento, versao=versao, processos=processos,
            nos=nos, tam=TAM, pedacos=pedacos, repeticao=rep,
            tempo_s=f"{tempo:.6f}", ok=ok)])
        if rep == 0 and procs:
            anexar(PROCESSOS, CAMPOS_PROC, [dict(
                experimento=experimento, versao=versao, processos=processos,
                **p) for p in procs])
        if ok != "ok":
            print(f"  ERRO de ordenacao: {versao} p={processos}", flush=True)
    print(f"  {experimento} {versao} p={processos} pedacos={pedacos}: "
          f"{sum(tempos) / len(tempos):.3f}s (n={len(tempos)}) "
          f"[{', '.join(f'{t:.2f}' for t in tempos)}]", flush=True)


def cmd_mpi(binario, processos, opcoes=(), ciclico=False):
    extra = ["--overcommit"] if processos > 32 else []
    if ciclico:
        extra += ["-m", "cyclic"]  # ranks alternados entre os nos
    return ["srun", *extra, "-N", "2", "-n", str(processos), f"./{binario}",
            "--tam", str(TAM), "--estatisticas", *opcoes]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("experimentos", nargs="+",
                    choices=["seq", "dcseq", "forte", "muitos", "extra"])
    ap.add_argument("--reps", type=int, default=5)
    a = ap.parse_args()
    os.makedirs(RESULTADOS, exist_ok=True)
    inicio = time.time()

    for exp in a.experimentos:
        print(f"== {exp}", flush=True)
        if exp == "seq":
            medir("seq", "bs", ["srun", "-N", "1", "-n", "1", "./bs_seq",
                                "--tam", str(TAM)], 1, 1, 1, a.reps)
        elif exp == "dcseq":
            for pedacos in [2, 4, 8, 16]:
                delta = (TAM + pedacos - 1) // pedacos
                medir("dcseq", "dc_seq",
                      ["srun", "-N", "1", "-n", "1", "./bs_seq", "--tam",
                       str(TAM), "--delta", str(delta)],
                      1, 1, pedacos, a.reps)
        elif exp == "forte":
            for p in [3, 7, 15, 31]:
                medir("forte", "sem_balanc", cmd_mpi("dc_mpi", p), p, 2,
                      (p + 1) // 2, a.reps)
            for p in [2, 3, 4, 7, 8, 15, 16, 31, 32]:
                medir("forte", "artigo", cmd_mpi("dc_artigo_mpi", p), p, 2, p,
                      a.reps)
        elif exp == "muitos":
            for p in [63, 127, 255, 511, 1023]:
                medir("muitos", "sem_balanc", cmd_mpi("dc_mpi", p), p, 2,
                      (p + 1) // 2, a.reps)
                medir("muitos", "artigo", cmd_mpi("dc_artigo_mpi", p), p, 2,
                      p, a.reps)

        elif exp == "extra":
            # artigo com envio bloqueante (corrige o atraso do MPI_Isend)
            for p in [2, 3, 4, 7, 8, 15, 16, 31, 32] + [63, 127, 255, 511, 1023]:
                medir("forte" if p <= 32 else "muitos", "artigo_bloq",
                      cmd_mpi("dc_artigo_mpi", p, ["--bloqueante"]), p, 2, p,
                      a.reps)
            # distribuicao ciclica dos ranks: espalha as folhas pelos 2 nos
            for p in [15, 31]:
                medir("ciclico", "sem_balanc", cmd_mpi("dc_mpi", p,
                      ciclico=True), p, 2, (p + 1) // 2, a.reps)
            for p in [16, 31, 32]:
                medir("ciclico", "artigo_bloq", cmd_mpi(
                      "dc_artigo_mpi", p, ["--bloqueante"], ciclico=True),
                      p, 2, p, a.reps)

    print(f"== fim em {(time.time() - inicio) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    sys.exit(main())
