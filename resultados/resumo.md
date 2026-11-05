# Resumo (gerado por analise.py)

T_seq = (993.3547598, 0.3917192633847298)

D&C sequencial: {2: (499.3946528, 0.07045273678998269), 4: (250.4462964, 0.08957928265397791), 8: (125.4807296, 0.033511045273165105), 16: (62.3154958, 0.036209277681278296)}

## forte

| versao | p | pedacos | tempo | dp | S | E% | S_dc | E_dc% |
|---|---|---|---|---|---|---|---|---|
| artigo | 2 | 2 | 498.969 | 0.113 | 2.0 | 100 | 1.0 | 50 |
| artigo | 3 | 2 | 249.292 | 0.069 | 4.0 | 133 | 2.0 | 67 |
| artigo | 4 | 4 | 125.344 | 0.167 | 7.9 | 198 | 2.0 | 50 |
| artigo | 7 | 4 | 62.690 | 0.181 | 15.8 | 226 | 4.0 | 57 |
| artigo | 8 | 8 | 31.707 | 0.201 | 31.3 | 392 | 4.0 | 49 |
| artigo | 15 | 8 | 16.410 | 0.005 | 60.5 | 404 | 7.6 | 51 |
| artigo | 16 | 16 | 8.237 | 0.017 | 120.6 | 754 | 7.6 | 47 |
| artigo | 31 | 16 | 5.014 | 0.030 | 198.1 | 639 | 12.4 | 40 |
| artigo | 32 | 32 | 3.368 | 0.013 | 294.9 | 922 | 9.2 | 29 |
| artigo_bloq | 2 | 2 | 249.868 | 0.123 | 4.0 | 199 | 2.0 | 100 |
| artigo_bloq | 3 | 2 | 249.421 | 0.120 | 4.0 | 133 | 2.0 | 67 |
| artigo_bloq | 4 | 4 | 62.681 | 0.094 | 15.8 | 396 | 4.0 | 100 |
| artigo_bloq | 7 | 4 | 63.791 | 1.623 | 15.6 | 222 | 3.9 | 56 |
| artigo_bloq | 8 | 8 | 16.077 | 0.074 | 61.8 | 772 | 7.8 | 98 |
| artigo_bloq | 15 | 8 | 16.436 | 0.018 | 60.4 | 403 | 7.6 | 51 |
| artigo_bloq | 16 | 16 | 4.139 | 0.017 | 240.0 | 1500 | 15.1 | 94 |
| artigo_bloq | 31 | 16 | 4.774 | 0.003 | 208.1 | 671 | 13.1 | 42 |
| artigo_bloq | 32 | 32 | 1.690 | 0.004 | 587.8 | 1837 | 18.4 | 57 |
| sem_balanc | 3 | 2 | 249.492 | 0.062 | 4.0 | 133 | 2.0 | 67 |
| sem_balanc | 7 | 4 | 64.217 | 0.274 | 15.5 | 221 | 3.9 | 56 |
| sem_balanc | 15 | 8 | 16.581 | 0.058 | 59.9 | 399 | 7.6 | 50 |
| sem_balanc | 31 | 16 | 6.665 | 0.068 | 149.0 | 481 | 9.3 | 30 |

## muitos

| versao | p | pedacos | tempo | dp | S | E% | S_dc | E_dc% |
|---|---|---|---|---|---|---|---|---|
| artigo | 63 | 32 | 1.968 | 0.147 | 504.8 | 801 | 15.8 | 25 |
| artigo | 127 | 64 | 1.240 | 0.010 | 801.4 | 631 | 12.5 | 10 |
| artigo | 255 | 128 | 0.704 | 0.036 | 1411.2 | 553 | 11.0 | 4 |
| artigo | 511 | 256 | 1.503 | 0.507 | 661.1 | 129 | 2.6 | 1 |
| artigo | 1023 | 512 | 2.117 | 0.185 | 469.1 | 46 | 0.9 | 0 |
| artigo_bloq | 63 | 32 | 1.953 | 0.201 | 508.7 | 807 | 15.9 | 25 |
| artigo_bloq | 127 | 64 | 1.012 | 0.059 | 981.8 | 773 | 15.3 | 12 |
| artigo_bloq | 255 | 128 | 0.813 | 0.326 | 1222.5 | 479 | 9.6 | 4 |
| artigo_bloq | 511 | 256 | 1.351 | 0.265 | 735.5 | 144 | 2.9 | 1 |
| artigo_bloq | 1023 | 512 | 2.385 | 0.169 | 416.6 | 41 | 0.8 | 0 |
| sem_balanc | 63 | 32 | 3.553 | 0.110 | 279.6 | 444 | 8.7 | 14 |
| sem_balanc | 127 | 64 | 2.062 | 0.057 | 481.8 | 379 | 7.5 | 6 |
| sem_balanc | 255 | 128 | 1.296 | 0.042 | 766.7 | 301 | 6.0 | 2 |
| sem_balanc | 511 | 256 | 2.296 | 0.358 | 432.7 | 85 | 1.7 | 0 |
| sem_balanc | 1023 | 512 | 3.380 | 0.136 | 293.9 | 29 | 0.6 | 0 |

## ciclico

| versao | p | pedacos | tempo | dp | S | E% | S_dc | E_dc% |
|---|---|---|---|---|---|---|---|---|
| artigo_bloq | 16 | 16 | 4.134 | 0.009 | 240.3 | 1502 | 15.1 | 94 |
| artigo_bloq | 31 | 16 | 4.802 | 0.126 | 206.9 | 667 | 13.0 | 42 |
| artigo_bloq | 32 | 32 | 1.691 | 0.003 | 587.4 | 1836 | 18.4 | 57 |
| sem_balanc | 15 | 8 | 16.478 | 0.022 | 60.3 | 402 | 7.6 | 51 |
| sem_balanc | 31 | 16 | 6.617 | 0.004 | 150.1 | 484 | 9.4 | 30 |

## tempo por nivel (forte, rep 0)

- sem_balanc p=3: nivel 0: 1 proc, ordena max 0.00s, espera max 249.38s, intercala max 0.005s; nivel 1: 2 proc, ordena max 249.33s, espera max 0.00s, intercala max 0.000s
- sem_balanc p=7: nivel 0: 1 proc, ordena max 0.00s, espera max 63.87s, intercala max 0.004s; nivel 1: 2 proc, ordena max 0.00s, espera max 63.86s, intercala max 0.002s; nivel 2: 4 proc, ordena max 63.83s, espera max 0.00s, intercala max 0.000s
- sem_balanc p=15: nivel 0: 1 proc, ordena max 0.00s, espera max 16.50s, intercala max 0.008s; nivel 1: 2 proc, ordena max 0.00s, espera max 16.49s, intercala max 0.002s; nivel 2: 4 proc, ordena max 0.00s, espera max 16.48s, intercala max 0.001s; nivel 3: 8 proc, ordena max 16.43s, espera max 0.00s, intercala max 0.000s
- sem_balanc p=31: nivel 0: 1 proc, ordena max 0.00s, espera max 6.62s, intercala max 0.015s; nivel 1: 2 proc, ordena max 0.00s, espera max 6.61s, intercala max 0.003s; nivel 2: 4 proc, ordena max 0.00s, espera max 6.61s, intercala max 0.002s; nivel 3: 8 proc, ordena max 0.00s, espera max 6.59s, intercala max 0.001s; nivel 4: 16 proc, ordena max 6.54s, espera max 0.00s, intercala max 0.000s
- artigo p=2: nivel 0: 1 proc, ordena max 249.57s, espera max 249.53s, intercala max 0.005s; nivel 1: 1 proc, ordena max 249.55s, espera max 0.00s, intercala max 0.000s
- artigo p=3: nivel 0: 1 proc, ordena max 62.55s, espera max 186.72s, intercala max 0.008s; nivel 1: 1 proc, ordena max 249.28s, espera max 0.00s, intercala max 0.000s; nivel 2: 1 proc, ordena max 62.51s, espera max 0.00s, intercala max 0.000s
- artigo p=4: nivel 0: 1 proc, ordena max 62.71s, espera max 62.71s, intercala max 0.008s; nivel 1: 1 proc, ordena max 62.53s, espera max 62.59s, intercala max 0.003s; nivel 2: 2 proc, ordena max 62.69s, espera max 0.00s, intercala max 0.000s
- artigo p=7: nivel 0: 1 proc, ordena max 15.72s, espera max 47.26s, intercala max 0.012s; nivel 1: 1 proc, ordena max 15.70s, espera max 47.27s, intercala max 0.004s; nivel 2: 2 proc, ordena max 62.98s, espera max 15.65s, intercala max 0.001s; nivel 3: 3 proc, ordena max 15.74s, espera max 0.00s, intercala max 0.000s
- artigo p=8: nivel 0: 1 proc, ordena max 15.64s, espera max 16.10s, intercala max 0.008s; nivel 1: 1 proc, ordena max 15.64s, espera max 15.78s, intercala max 0.004s; nivel 2: 2 proc, ordena max 15.68s, espera max 15.80s, intercala max 0.001s; nivel 3: 4 proc, ordena max 16.09s, espera max 0.00s, intercala max 0.000s
- artigo p=15: nivel 0: 1 proc, ordena max 4.08s, espera max 12.31s, intercala max 0.015s; nivel 1: 1 proc, ordena max 4.08s, espera max 12.31s, intercala max 0.004s; nivel 2: 2 proc, ordena max 4.08s, espera max 12.30s, intercala max 0.002s; nivel 3: 4 proc, ordena max 16.38s, espera max 4.11s, intercala max 0.001s; nivel 4: 7 proc, ordena max 4.10s, espera max 0.00s, intercala max 0.000s
- artigo p=16: nivel 0: 1 proc, ordena max 4.09s, espera max 4.12s, intercala max 0.019s; nivel 1: 1 proc, ordena max 4.08s, espera max 4.12s, intercala max 0.004s; nivel 2: 2 proc, ordena max 4.08s, espera max 4.12s, intercala max 0.002s; nivel 3: 4 proc, ordena max 4.08s, espera max 4.12s, intercala max 0.001s; nivel 4: 8 proc, ordena max 4.10s, espera max 0.00s, intercala max 0.000s
- artigo p=31: nivel 0: 1 proc, ordena max 1.63s, espera max 3.39s, intercala max 0.026s; nivel 1: 1 proc, ordena max 1.63s, espera max 3.38s, intercala max 0.005s; nivel 2: 2 proc, ordena max 1.63s, espera max 3.38s, intercala max 0.003s; nivel 3: 4 proc, ordena max 1.63s, espera max 3.39s, intercala max 0.001s; nivel 4: 8 proc, ordena max 5.02s, espera max 1.67s, intercala max 0.001s; nivel 5: 15 proc, ordena max 1.70s, espera max 0.00s, intercala max 0.000s
- artigo p=32: nivel 0: 1 proc, ordena max 1.63s, espera max 1.69s, intercala max 0.024s; nivel 1: 1 proc, ordena max 1.63s, espera max 1.68s, intercala max 0.005s; nivel 2: 2 proc, ordena max 1.63s, espera max 1.68s, intercala max 0.003s; nivel 3: 4 proc, ordena max 1.63s, espera max 1.68s, intercala max 0.001s; nivel 4: 8 proc, ordena max 1.63s, espera max 1.68s, intercala max 0.000s; nivel 5: 16 proc, ordena max 1.64s, espera max 0.00s, intercala max 0.000s
- artigo_bloq p=2: nivel 0: 1 proc, ordena max 250.06s, espera max 0.01s, intercala max 0.005s; nivel 1: 1 proc, ordena max 249.43s, espera max 0.00s, intercala max 0.000s
- artigo_bloq p=3: nivel 0: 1 proc, ordena max 62.88s, espera max 186.60s, intercala max 0.008s; nivel 1: 1 proc, ordena max 249.48s, espera max 0.00s, intercala max 0.000s; nivel 2: 1 proc, ordena max 62.55s, espera max 0.00s, intercala max 0.000s
- artigo_bloq p=4: nivel 0: 1 proc, ordena max 62.66s, espera max 0.16s, intercala max 0.007s; nivel 1: 1 proc, ordena max 62.65s, espera max 0.00s, intercala max 0.002s; nivel 2: 2 proc, ordena max 62.81s, espera max 0.00s, intercala max 0.000s
- artigo_bloq p=7: nivel 0: 1 proc, ordena max 16.02s, espera max 46.91s, intercala max 0.009s; nivel 1: 1 proc, ordena max 15.99s, espera max 46.93s, intercala max 0.004s; nivel 2: 2 proc, ordena max 62.93s, espera max 0.00s, intercala max 0.001s; nivel 3: 3 proc, ordena max 15.87s, espera max 0.00s, intercala max 0.000s
- artigo_bloq p=8: nivel 0: 1 proc, ordena max 15.77s, espera max 0.32s, intercala max 0.008s; nivel 1: 1 proc, ordena max 15.94s, espera max 0.00s, intercala max 0.003s; nivel 2: 2 proc, ordena max 16.08s, espera max 0.00s, intercala max 0.001s; nivel 3: 4 proc, ordena max 15.82s, espera max 0.00s, intercala max 0.000s
- artigo_bloq p=15: nivel 0: 1 proc, ordena max 4.08s, espera max 12.32s, intercala max 0.016s; nivel 1: 1 proc, ordena max 4.08s, espera max 12.32s, intercala max 0.004s; nivel 2: 2 proc, ordena max 4.09s, espera max 12.33s, intercala max 0.002s; nivel 3: 4 proc, ordena max 16.40s, espera max 0.03s, intercala max 0.001s; nivel 4: 7 proc, ordena max 4.11s, espera max 0.00s, intercala max 0.000s
- artigo_bloq p=16: nivel 0: 1 proc, ordena max 4.09s, espera max 0.02s, intercala max 0.019s; nivel 1: 1 proc, ordena max 4.08s, espera max 0.01s, intercala max 0.004s; nivel 2: 2 proc, ordena max 4.08s, espera max 0.01s, intercala max 0.002s; nivel 3: 4 proc, ordena max 4.08s, espera max 0.01s, intercala max 0.001s; nivel 4: 8 proc, ordena max 4.09s, espera max 0.00s, intercala max 0.000s
- artigo_bloq p=31: nivel 0: 1 proc, ordena max 1.64s, espera max 3.11s, intercala max 0.028s; nivel 1: 1 proc, ordena max 1.63s, espera max 3.11s, intercala max 0.006s; nivel 2: 2 proc, ordena max 1.64s, espera max 3.10s, intercala max 0.003s; nivel 3: 4 proc, ordena max 1.64s, espera max 3.10s, intercala max 0.001s; nivel 4: 8 proc, ordena max 4.74s, espera max 0.01s, intercala max 0.001s; nivel 5: 15 proc, ordena max 1.63s, espera max 0.00s, intercala max 0.000s
- artigo_bloq p=32: nivel 0: 1 proc, ordena max 1.64s, espera max 0.01s, intercala max 0.031s; nivel 1: 1 proc, ordena max 1.64s, espera max 0.01s, intercala max 0.006s; nivel 2: 2 proc, ordena max 1.64s, espera max 0.01s, intercala max 0.003s; nivel 3: 4 proc, ordena max 1.64s, espera max 0.01s, intercala max 0.002s; nivel 4: 8 proc, ordena max 1.64s, espera max 0.04s, intercala max 0.001s; nivel 5: 16 proc, ordena max 1.63s, espera max 0.00s, intercala max 0.000s
