# MO652: nativo (Spack) vs contêiner (HPCCM + Apptainer) no CENAPAD

osu_bw e osu_latency entre 2 nós CPU (1 processo por nó), InfiniBand HDR100.
Versões iguais nos dois ambientes: MPICH 5.0.2 (ch4:ucx), UCX 1.20.1, OSU 7.5.2, rdma-core 48.0, GCC.

| Arquivo | O que é |
|---|---|
| `container/osu_mpich.py` | receita HPCCM |
| `container/osu_mpich.def` | definição Singularity/Apptainer gerada pela receita |
| `container/Dockerfile` | Dockerfile gerado pela receita (usado para construir a imagem) |
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
{ mpichversion; ucx_info -v; rpm -q rdma-core; gcc --version | head -1; } > spack/versions.txt
```

`spack.lock` fica em `spack/`. Para reproduzir: `spack env create x spack/spack.lock && spack -e x install`.

## 2. Imagem (rdma-core igual ao do cluster)

Os nós do CENAPAD não têm MOFED: a InfiniBand usa o rdma-core 48.0 do AlmaLinux
(`rpm -q rdma-core`). A receita compila esse mesmo rdma-core 48.0 no Ubuntu 24.04.

Gerar `.def` e `Dockerfile` (precisa só do hpccm):

```bash
python3 -m venv ~/hpccm-venv && ~/hpccm-venv/bin/pip install hpccm
~/hpccm-venv/bin/hpccm --recipe container/osu_mpich.py --format singularity > container/osu_mpich.def
~/hpccm-venv/bin/hpccm --recipe container/osu_mpich.py --format docker      > container/Dockerfile
```

O cluster tem Singularity 3.8.5 sem `--fakeroot` para o usuário, então a imagem é
construída com Docker numa máquina x86_64 (no Mac M1/M2/M3, `--platform linux/amd64`):

```bash
docker build --platform linux/amd64 -t osu -f container/Dockerfile container/
docker save osu -o osu.tar
scp osu.tar <usuario>@<login-cenapad>:~/compare_performance_CENAPAD/container/
```

No cluster:

```bash
singularity build container/osu.sif docker-archive://container/osu.tar
singularity exec container/osu.sif mpichversion     # 5.0.2
singularity exec container/osu.sif ucx_info -v      # 1.20.1
singularity exec container/osu.sif which osu_bw
```

## 3. Rodar (PBS, fila `paralela`)

`paralela` é a única fila com mais de um nó (mínimo 2 nós / 256 CPUs): o job reserva os
2 nós inteiros e lança 1 processo MPI por nó.

```bash
cd ~/compare_performance_CENAPAD
qsub run/osu.pbs                          # tudo
qsub -v SCENARIOS=container run/osu.pbs   # só um cenário
qstat -u $USER
tail -1 logs/ib_check.log     # ib_lines > 0 e tcp_lines = 0 -> passou pela InfiniBand
```

Logs: `logs/{native,container}/{osu_bw,osu_latency}_run{1,2,3}.log`.
Resubmeter retoma: logs completos são pulados, só roda o que falta.

## 4. Gráficos e números (pode rodar com resultados parciais)

```bash
uv venv && uv pip install numpy matplotlib
.venv/bin/python analysis/plot.py      # ou traga logs/ para o laptop e rode aqui
```

Saída: `results/<cenario>_<bench>.npy` (runs x tamanhos) + `_sizes.npy`,
`figures/bandwidth.png`, `figures/latency.png`, `results/summary.txt`.
Os números do `summary.txt` entram no `report.md`.
