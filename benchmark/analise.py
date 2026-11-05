# /// script
# requires-python = ">=3.10"
# dependencies = ["matplotlib>=3.8"]
# ///
"""
Analise dos resultados do T3: le ../resultados/brutos-*.csv e processos-*.csv
(gerados por benchmark.py no LAD) e produz

  ../relatorio/tabelas.tex       tabelas da pagina 2 do relatorio
  ../relatorio/fig_*.pdf         figuras vetoriais para o relatorio
  ../slides/fig_*.png            as mesmas figuras em PNG para a apresentacao
  ../resultados/resumo.md        todos os numeros, para conferencia

Dois speed-ups:
  S     = T_seq / T_p, com T_seq = bubble sort no vetor inteiro (o do enunciado).
          Como o bubble sort e O(n^2), dividir o vetor em L pedacos ja reduz o
          trabalho total por L, e S passa de p (superlinear).
  S_dc  = T_dcseq(L) / T_p, com T_dcseq(L) = a mesma divisao em L pedacos em 1
          core. Isola o ganho do paralelismo; E_dc = S_dc / p mostra quantos
          dos p processos estao de fato ordenando.

Uso: uv run analise.py
"""

import csv
import glob
import os
import statistics
from collections import defaultdict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(AQUI, "..", "resultados")
REL = os.path.join(AQUI, "..", "relatorio")
SLI = os.path.join(AQUI, "..", "slides")

# Paleta validada (scripts/validate_palette.js): a cor segue a entidade.
COR = {"sem_balanc": "#2a78d6", "artigo": "#eb6834", "artigo_bloq": "#1baf7a"}
COR_ATIV = {"ordena": "#008300", "espera": "#c9c8c3", "intercala": "#6250d6"}
ROTULO = {"sem_balanc": "sem balanceamento", "artigo": "artigo (MPI_Isend)",
          "artigo_bloq": "artigo, envio bloqueante"}
TEXTO, TEXTO_2, GRADE, IDEAL = "#0b0b0b", "#52514e", "#e4e3df", "#8a8984"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 8,
    "axes.edgecolor": TEXTO_2, "axes.labelcolor": TEXTO,
    "axes.linewidth": 0.6, "xtick.color": TEXTO_2, "ytick.color": TEXTO_2,
    "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "figure.dpi": 200,
})


def ler(padrao):
    linhas = []
    for caminho in sorted(glob.glob(os.path.join(RES, padrao))):
        with open(caminho) as f:
            linhas += list(csv.DictReader(f))
    return linhas


def br(x, casas=2):
    return "--" if x is None else f"{x:.{casas}f}".replace(".", ",")


brutos = ler("brutos-*.csv")
procs = ler("processos-*.csv")
assert all(r["ok"] == "ok" for r in brutos), "ha execucao com vetor mal ordenado"

tempos = defaultdict(list)
for r in brutos:
    tempos[(r["experimento"], r["versao"], int(r["processos"]),
            int(r["pedacos"]))].append(float(r["tempo_s"]))


def medida(exp, versao, p, pedacos):
    t = tempos.get((exp, versao, p, pedacos))
    if not t:
        return None
    return statistics.mean(t), (statistics.stdev(t) if len(t) > 1 else 0.0)


T_SEQ = medida("seq", "bs", 1, 1)
DCSEQ = {L: medida("dcseq", "dc_seq", 1, L) for L in (2, 4, 8, 16)}
P_SEM = [3, 7, 15, 31]
P_ART = [2, 3, 4, 7, 8, 15, 16, 31, 32]
P_MUITOS = [63, 127, 255, 511, 1023]


def folhas(versao, p):
    """Pedacos ordenados em paralelo (o maior pedaco define o tempo)."""
    if versao == "sem_balanc":
        return (p + 1) // 2
    # versao do artigo: com 2^k - 1 processos, o maior pedaco e o de 2^(k-1)
    L = 1
    while 2 * L <= p:
        L *= 2
    return L


def t_dcseq(L):
    """D&C sequencial com L pedacos: medido para 2, 4, 8 e 16; para os demais,
    T_seq / L, que as medicoes confirmam (diferenca <= 0,5%)."""
    if L == 1:
        return T_SEQ[0]
    m = DCSEQ.get(L)
    return m[0] if m else T_SEQ[0] / L


def linha(exp, versao, p):
    m = medida(exp, versao, p, (p + 1) // 2 if versao == "sem_balanc" else p)
    if m is None or T_SEQ is None:
        return None
    s = T_SEQ[0] / m[0]
    L = folhas(versao, p)
    s_dc = t_dcseq(L) / m[0]
    return dict(t=m[0], dp=m[1], s=s, e=100 * s / p, L=L, s_dc=s_dc,
                e_dc=100 * s_dc / p if s_dc else None)


forte = {(v, p): linha("forte", v, p) for v in COR for p in
         (P_SEM if v == "sem_balanc" else P_ART)}
muitos = {(v, p): linha("muitos", v, p) for v in COR for p in P_MUITOS}
ciclico = {(v, p): linha("ciclico", v, p) for v, ps in
           (("sem_balanc", (15, 31)), ("artigo_bloq", (16, 31, 32)))
           for p in ps}


def salvar(fig, nome):
    fig.savefig(os.path.join(REL, f"{nome}.pdf"), bbox_inches="tight")
    fig.savefig(os.path.join(SLI, f"{nome}.png"), bbox_inches="tight", dpi=220)
    plt.close(fig)


def fig_forte():
    """Speed-up (log) e eficiencia em relacao ao D&C sequencial."""
    ps = sorted(set(P_SEM) | set(P_ART))
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.4, 2.3))
    larg = 0.27
    for i, v in enumerate(COR):
        xs, ys, ys2, xs2 = [], [], [], []
        for g, p in enumerate(ps):
            d = forte.get((v, p))
            if d is None:
                continue
            x = g + (i - 1) * larg
            xs.append(x); ys.append(d["s"])
            if d["e_dc"] is not None:
                xs2.append(x); ys2.append(d["e_dc"])
        a1.bar(xs, ys, width=larg * 0.92, color=COR[v], label=ROTULO[v],
               zorder=3)
        a2.bar(xs2, ys2, width=larg * 0.92, color=COR[v], label=ROTULO[v],
               zorder=3)
    a1.plot(range(len(ps)), ps, color=IDEAL, ls="--", lw=1.2, marker="_",
            ms=9, label="ideal (S = p)", zorder=4)
    a1.set_yscale("log")
    a1.set_ylabel("Speed-up S = T_seq / T_p (log)")
    a2.axhline(100, color=IDEAL, ls="--", lw=1.2, zorder=4)
    a2.set_ylim(0, 115)
    a2.set_ylabel("Eficiência vs. D&C sequencial (%)")
    for ax in (a1, a2):
        ax.set_xticks(range(len(ps)), [str(p) for p in ps])
        ax.set_xlabel("Processos")
        ax.yaxis.grid(True, color=GRADE, lw=0.6, zorder=0)
        idx = ps.index(31)
        ax.axvspan(idx - 0.5, len(ps) - 0.5, color="#f3f2ef", zorder=0)
    a1.text(len(ps) - 0.55, a1.get_ylim()[1] * 0.8, "HT", ha="right",
            color=TEXTO_2, fontsize=7)
    a1.legend(loc="upper left", fontsize=6.5)
    fig.suptitle("Escalabilidade forte — 1.000.000 de elementos, 2 nós",
                 fontsize=9, color=TEXTO, x=0.01, ha="left")
    fig.tight_layout()
    salvar(fig, "fig_forte")


def fig_niveis():
    """Tempo de cada processo por atividade: sem balanceamento x artigo."""
    casos = [("sem_balanc", 15), ("artigo", 16), ("artigo_bloq", 16)]
    fig, eixos = plt.subplots(1, 3, figsize=(7.4, 2.2), sharey=True)
    for ax, (v, p) in zip(eixos, casos):
        ls = sorted((r for r in procs if r["experimento"] == "forte"
                     and r["versao"] == v and int(r["processos"]) == p),
                    key=lambda r: int(r["rank"]))
        if not ls:
            continue
        ranks = [int(r["rank"]) for r in ls]
        base = [0.0] * len(ls)
        for ativ in ("ordena", "espera", "intercala"):
            vals = [float(r[f"{ativ}_s"]) for r in ls]
            ax.bar(ranks, vals, bottom=base, color=COR_ATIV[ativ], width=0.75,
                   zorder=3)
            base = [b + x for b, x in zip(base, vals)]
        ax.set_title(f"{ROTULO[v]}, p = {p}", fontsize=8, loc="left",
                     color=TEXTO)
        ax.set_xlabel("Rank (nível na árvore)")
        ax.set_xticks([r for r in ranks if r % 3 == 0],
                      [f"{r}\n({ls[r]['nivel']})" for r in ranks if r % 3 == 0],
                      fontsize=6)
        ax.yaxis.grid(True, color=GRADE, lw=0.6, zorder=0)
    eixos[0].set_ylabel("Tempo (s)")
    fig.legend(handles=[Patch(color=COR_ATIV[a], label=l) for a, l in
                        (("ordena", "bubble sort"), ("espera", "espera os filhos"),
                         ("intercala", "intercalação"))],
               loc="upper right", ncol=3, fontsize=7, bbox_to_anchor=(1, 1.02))
    fig.suptitle("Tempo por processo", fontsize=9, color=TEXTO, x=0.01,
                 ha="left")
    fig.tight_layout()
    salvar(fig, "fig_niveis")


def fig_muitos():
    ps = [15, 31] + P_MUITOS
    fig, ax = plt.subplots(figsize=(7.4, 2.0))
    larg = 0.27
    for i, v in enumerate(COR):
        xs, ys = [], []
        for g, p in enumerate(ps):
            d = forte.get((v, p)) or muitos.get((v, p))
            if d:
                xs.append(g + (i - 1) * larg); ys.append(d["t"])
        ax.bar(xs, ys, width=larg * 0.92, color=COR[v], label=ROTULO[v],
               zorder=3)
    ax.set_yscale("log")
    ax.set_xticks(range(len(ps)), [str(p) for p in ps])
    ax.set_xlabel("Processos (acima de 32: overcommit em 32 CPUs lógicas)")
    ax.set_ylabel("Tempo (s, log)")
    ax.yaxis.grid(True, color=GRADE, lw=0.6, zorder=0)
    ax.legend(loc="upper right", fontsize=7)
    fig.suptitle("Mais processos que CPUs", fontsize=9, color=TEXTO, x=0.01,
                 ha="left")
    fig.tight_layout()
    salvar(fig, "fig_muitos")


os.makedirs(SLI, exist_ok=True)
fig_forte()
fig_niveis()
fig_muitos()


# ---------------------------------------------------------------- tabelas
def tab_forte(v, ps, dados):
    l = [r"\begin{tabular}{@{}cccccccc@{}}", r"\toprule",
         r"p & Pedaços & Tempo (s) & DP & S & E (\%) & S$_{dc}$ & E$_{dc}$ (\%) \\",
         r"\midrule"]
    for p in ps:
        d = dados.get((v, p))
        if d is None:
            continue
        l.append(f"{p} & {d['L']} & {br(d['t'], 2)} & {br(d['dp'], 2)} & "
                 f"{br(d['s'], 1)} & {br(d['e'], 0)} & {br(d['s_dc'], 1)} & "
                 f"{br(d['e_dc'], 0)} \\\\")
    l += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(l)


def tab_ref():
    l = [r"\begin{tabular}{@{}lcc@{}}", r"\toprule",
         r"Referência (1 core) & Tempo (s) & DP \\", r"\midrule"]
    if T_SEQ:
        l.append(f"Bubble sort, vetor inteiro & {br(T_SEQ[0], 1)} & "
                 f"{br(T_SEQ[1], 1)} \\\\")
    for L, m in DCSEQ.items():
        if m:
            l.append(f"D\\&C sequencial, {L} pedaços & {br(m[0], 1)} & "
                     f"{br(m[1], 1)} \\\\")
    l += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(l)


def tab_muitos():
    l = [r"\begin{tabular}{@{}c|cc|cc|cc@{}}", r"\toprule",
         r" & \multicolumn{2}{c|}{sem balanc.} & "
         r"\multicolumn{2}{c|}{artigo (Isend)} & "
         r"\multicolumn{2}{c}{artigo (bloq.)} \\",
         r"p & Tempo (s) & DP & Tempo (s) & DP & Tempo (s) & DP \\",
         r"\midrule"]
    for p in P_MUITOS:
        cel = [str(p)]
        for v in COR:
            d = muitos.get((v, p))
            cel += [br(d["t"], 3), br(d["dp"], 3)] if d else ["--", "--"]
        l.append(" & ".join(cel) + r" \\")
    l += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(l)


def tab_ciclico():
    """Mesmo programa com os ranks em bloco (padrao do srun) e alternados."""
    l = [r"\begin{tabular}{@{}lccc@{}}", r"\toprule",
         r"Versão & p & Em bloco (s) & Cíclica (s) \\", r"\midrule"]
    for (v, p), d in ciclico.items():
        b = forte.get((v, p))
        if d and b:
            l.append(f"{ROTULO[v]} & {p} & {br(b['t'], 2)} & {br(d['t'], 2)} \\\\")
    l += [r"\bottomrule", r"\end{tabular}"]
    return "\n".join(l)


with open(os.path.join(REL, "tabelas.tex"), "w") as f:
    f.write("% Gerado por benchmark/analise.py -- nao editar a mao.\n")
    if T_SEQ:
        f.write(f"\\newcommand{{\\Tseq}}{{{br(T_SEQ[0], 1)}}}\n")
    f.write("\\newcommand{\\TabRef}{%\n" + tab_ref() + "}\n")
    f.write("\\newcommand{\\TabSem}{%\n" + tab_forte("sem_balanc", P_SEM, forte)
            + "}\n")
    f.write("\\newcommand{\\TabArtigo}{%\n" + tab_forte("artigo", P_ART, forte)
            + "}\n")
    f.write("\\newcommand{\\TabBloq}{%\n" +
            tab_forte("artigo_bloq", P_ART, forte) + "}\n")
    f.write("\\newcommand{\\TabMuitos}{%\n" + tab_muitos() + "}\n")
    f.write("\\newcommand{\\TabCiclico}{%\n" + tab_ciclico() + "}\n")


# ----------------------------------------------------------------- resumo
with open(os.path.join(RES, "resumo.md"), "w") as f:
    f.write("# Resumo (gerado por analise.py)\n\n")
    f.write(f"T_seq = {T_SEQ}\n\nD&C sequencial: {DCSEQ}\n\n")
    for nome, dados in (("forte", forte), ("muitos", muitos),
                        ("ciclico", ciclico)):
        f.write(f"## {nome}\n\n| versao | p | pedacos | tempo | dp | S | E% | "
                "S_dc | E_dc% |\n|---|---|---|---|---|---|---|---|---|\n")
        for (v, p), d in sorted(dados.items()):
            if d:
                f.write(f"| {v} | {p} | {d['L']} | {d['t']:.3f} | {d['dp']:.3f}"
                        f" | {d['s']:.1f} | {d['e']:.0f} | "
                        f"{d['s_dc'] if d['s_dc'] is None else round(d['s_dc'], 1)}"
                        f" | {d['e_dc'] if d['e_dc'] is None else round(d['e_dc'])}"
                        " |\n")
        f.write("\n")
    f.write("## tempo por nivel (forte, rep 0)\n\n")
    for v in COR:
        for p in (P_SEM if v == "sem_balanc" else P_ART):
            ls = [r for r in procs if r["experimento"] == "forte"
                  and r["versao"] == v and int(r["processos"]) == p]
            por = defaultdict(list)
            for r in ls:
                por[int(r["nivel"])].append(r)
            partes = []
            for n in sorted(por):
                rs = por[n]
                partes.append(
                    f"nivel {n}: {len(rs)} proc, ordena max "
                    f"{max(float(r['ordena_s']) for r in rs):.2f}s, espera max "
                    f"{max(float(r['espera_s']) for r in rs):.2f}s, intercala "
                    f"max {max(float(r['intercala_s']) for r in rs):.3f}s")
            f.write(f"- {v} p={p}: " + "; ".join(partes) + "\n")

print(open(os.path.join(RES, "resumo.md")).read())
