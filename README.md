# MO652: nativo (Spack) vs contêiner (HPCCM + Apptainer) no CENAPAD

osu_bw e osu_latency entre 2 nós CPU (1 processo por nó), InfiniBand HDR100.
Versões iguais nos dois ambientes: MPICH 5.0.2 (ch4:ucx), UCX 1.20.1, OSU 7.5.2, GCC.

| Arquivo | O que é |
|---|---|
| `container/osu_mpich.py` | receita HPCCM |
| `container/osu_mpich.def` | definição Apptainer gerada pela receita |
| `spack/spack.yaml` | ambiente Spack (o `spack.lock` sai do cluster) |
| `run/osu.pbs` | job PBS: checagem de IB + 3 repetições de cada teste, nos dois cenários |
| `analysis/plot.py` | logs -> `results/*.npy`, `figures/*.png`, `results/summary.txt` |
| `report.md` | relatório curto (preencher com o `summary.txt`) |

`spack/`, `run/`, `analysis/`, `report.md` e os resultados estão no `.gitignore`,
então vão para o cluster por `rsync`, não por `git clone`.

## 0. Copiar para o cluster (no laptop)

```bash
rsync -av --exclude .git ./ <usuario>@<login-cenapad>:~/compare_performance_CENAPAD/
```

## 1. Host com Spack (no login node)

```bash
git clone --depth=2 --branch v1.2.2 https://github.com/spack/spack.git ~/spack
. ~/spack/share/spack/setup-env.sh
spack repo update                      # traz mpich@5.0.2 se o builtin estiver velho
spack info mpich | grep 5.0.2          # confere
spack compiler find
cd ~/compare_performance_CENAPAD
spack env activate ./spack
spack external find --not-buildable rdma-core   # usa os verbs do MOFED do host
spack concretize -f && spack install -j 8
# registro para reproduzir
spack spec -l > spack/spack_spec.txt
spack find -lv >> spack/spack_spec.txt
{ mpichversion; ucx_info -v; ofed_info -s; gcc --version | head -1; } > spack/versions.txt
```

`spack.lock` fica em `spack/`. Para reproduzir: `spack env create x spack/spack.lock && spack -e x install`.

## 2. Imagem (MOFED igual ao do cluster)

```bash
ofed_info -s        # ex.: MLNX_OFED_LINUX-24.10-3.2.5.0 -> use 24.10-3.2.5.0
```

Gerar o `.def` (laptop ou cluster, precisa só do hpccm):

```bash
uvx --from hpccm hpccm --recipe container/osu_mpich.py --format singularity \
    --userarg mofed=<versao do ofed_info> > container/osu_mpich.def
```

Construir no cluster:

```bash
apptainer build --fakeroot container/osu.sif container/osu_mpich.def
apptainer exec container/osu.sif mpichversion      # tem que dar 5.0.2
apptainer exec container/osu.sif ucx_info -v       # 1.20.1
apptainer exec container/osu.sif which osu_bw
```

Sem `--fakeroot` no cluster: `--format docker` num x86_64 com Docker,
`docker build -t osu . && docker save osu -o osu.tar`, depois
`apptainer build container/osu.sif docker-archive://osu.tar` no cluster.

Atenção: MOFED só tem pacote para Ubuntu 24.04 a partir da 24.04-x. Se o cluster
estiver em 5.x/23.x, use a 24.x mais antiga (a userspace nova funciona com driver antigo).

## 3. Rodar (PBS)

```bash
cd ~/compare_performance_CENAPAD
qsub -q <fila> run/osu.pbs                          # tudo
qsub -q <fila> -v SCENARIOS=container run/osu.pbs   # só um cenário
qstat -u $USER
tail -1 logs/ib_check.log     # ib_lines > 0 e tcp_lines = 0 -> passou pela InfiniBand
```

Logs: `logs/{native,container}/{osu_bw,osu_latency}_run{1,2,3}.log`.
Resubmeter retoma: logs completos são pulados, só roda o que falta.
Descomente `# module load apptainer` no `run/osu.pbs` se o cluster exigir.

## 4. Gráficos e números (pode rodar com resultados parciais)

```bash
uv venv && uv pip install numpy matplotlib
.venv/bin/python analysis/plot.py      # ou traga logs/ para o laptop e rode aqui
```

Saída: `results/<cenario>_<bench>.npy` (runs x tamanhos) + `_sizes.npy`,
`figures/bandwidth.png`, `figures/latency.png`, `results/summary.txt`.
Os números do `summary.txt` entram no `report.md`.
