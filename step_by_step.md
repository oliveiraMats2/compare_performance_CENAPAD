# Instalação passo a passo (MO652, nativo vs contêiner)

Arquivo de acompanhamento: cada imprevisto que muda a instalação é corrigido aqui e anotado em
**Imprevistos**, no fim.

- **Cluster:** `/home/lovelace/proj/proj1163/m203656/compare_performance_CENAPAD`
- **Mac:** `~/Documents/phd_documents/1_semester/High_perfomance_computer/compare_performance_CENAPAD`

Versões (iguais no host e no contêiner): MPICH **5.0.1** (ch4:ucx), UCX **1.20.1**,
OSU **7.5.2**, rdma-core **48.0**, GCC.

---

## A. Cluster: host com Spack

- [x] A1. Clonar o Spack
  ```bash
  git clone --depth=2 --branch v1.2.2 https://github.com/spack/spack.git ~/spack
  ```
- [x] A2. Atualizar o catálogo de pacotes
  ```bash
  . ~/spack/share/spack/setup-env.sh
  spack repo update
  spack compiler find
  ```
- [x] A3. Instalar MPICH, UCX e OSU
  ```bash
  cd ~/compare_performance_CENAPAD
  spack env activate ./spack
  spack external find --not-buildable rdma-core
  spack concretize -f && spack install -j 8
  ```
- [x] A4. Registrar versões para reproduzir
  ```bash
  spack spec -l > spack/spack_spec.txt
  spack find -lv >> spack/spack_spec.txt
  { mpichversion; ucx_info -v; rpm -q rdma-core; gcc --version | head -1; } > spack/versions.txt
  ```
  O `spack/spack.lock` é criado pelo `concretize` (A3).

## B. Mac: imagem do contêiner

- [x] B1. Corrigir a receita (MPICH 5.0.1 + `ca-certificates`)
- [x] B2. Gerar o `.def` e o `Dockerfile`
  ```bash
  .venv/bin/hpccm --recipe container/osu_mpich.py --format singularity > container/osu_mpich.def
  .venv/bin/hpccm --recipe container/osu_mpich.py --format docker      > container/Dockerfile
  ```
- [x] B3. Construir a imagem (demora no Mac M1/M2/M3, por causa da emulação x86)
  ```bash
  docker build --platform linux/amd64 -t osu -f container/Dockerfile container/ && docker save osu -o osu.tar
  ```
- [x] B4. Commitar e enviar
  ```bash
  git add container/ && git commit -m "MPICH 5.0.1 e ca-certificates na receita HPCCM" && git push origin main
  ```
- [x] B5. Mandar a imagem para o cluster
  ```bash
  rsync -avP osu.tar lovelace:/home/lovelace/proj/proj1163/m203656/compare_performance_CENAPAD/container/
  ```

## C. Cluster: converter e conferir a imagem

- [x] C1. Puxar a receita nova e converter para `.sif`
  ```bash
  cd ~/compare_performance_CENAPAD
  git pull
  singularity build container/osu.sif docker-archive://container/osu.tar
  ```
- [x] C2. Conferir as versões dentro do contêiner
  ```bash
  singularity exec container/osu.sif mpichversion    # 5.0.1
  singularity exec container/osu.sif ucx_info -v     # 1.20.1
  singularity exec container/osu.sif which osu_bw
  ```

## D. Cluster: rodar os benchmarks

- [x] D1. Nome da placa InfiniBand
  ```bash
  ls /sys/class/infiniband; cat /sys/class/infiniband/*/ports/1/{state,rate}
  ```
  Se não for `mlx5_0`, submeta com `qsub -v UCX_NET_DEVICES=<nome>:1 run/osu.pbs`.
- [x] D2. Submeter (fila `paralela`, 2 nós, 1 processo MPI por nó) e acompanhar
  ```bash
  qsub run/osu.pbs
  qstat -u $USER
  tail -1 logs/ib_check.log        # ib_lines > 0 e tcp_lines = 0
  ls logs/native logs/container    # resultados parciais
  ```
  Se o job cair, rode `qsub run/osu.pbs` de novo: ele pula os logs já completos.

## E. Mac: gráficos e relatório

- [ ] E1. Trazer os logs
  ```bash
  rsync -avz lovelace:/home/lovelace/proj/proj1163/m203656/compare_performance_CENAPAD/logs/ ./logs/
  ```
- [x] E2. Gerar `.npy`, gráficos e resumo
  ```bash
  .venv/bin/pip install numpy matplotlib
  .venv/bin/python analysis/plot.py
  cat results/summary.txt
  ```
- [ ] E3. Preencher os `[...]` do `report.md` com o `summary.txt`
- [ ] E4. Antes de entregar: tirar do `.gitignore` o que o enunciado pede commitado (`spack/`,
  `run/`, `analysis/`, `logs/`, `results/`, `figures/`, `report.md`) e commitar

---

## Imprevistos

| Data | Problema | Mudança |
|---|---|---|
| 2026-10-02 | `qsub -I -q testes -l select=1:ncpus=1` recusado ("violates queue limits") | A fila `testes` exige no mínimo 2 CPUs: usar `ncpus=2` |
| 2026-10-02 | Python 3.6 do cluster não instala o hpccm (erro no `pip`) | `.def` e `Dockerfile` gerados no Mac |
| 2026-10-02 | Os nós não têm MOFED, só o rdma-core 48.0 do AlmaLinux | Receita usa rdma-core 48.0 no lugar do MOFED |
| 2026-10-02 | Fila `testes` aceita só 1 nó; a única fila com 2+ nós é a `paralela` (mín. 256 CPUs) | `osu.pbs` usa `paralela`, `select=2:ncpus=128:mpiprocs=1` |
| 2026-10-02 | Sem Apptainer e sem `--fakeroot` no cluster | Imagem construída com Docker no Mac e convertida com `singularity build ... docker-archive://` |
| 2026-10-04 | `docker build` falhou no `wget` (código 5, certificado SSL) | `ca-certificates` adicionado à receita |
| 2026-10-04 | `spack concretize` não achou `mpich@5.0.2` (catálogo `builtin` antigo) | Passo A2 com `spack repo update`; mesmo assim só há até 5.0.1 (linha abaixo) |
| 2026-10-04 | Spack não tem MPICH 5.0.2, só até 5.0.1 | MPICH 5.0.1 no `spack.yaml` e na receita (citar no relatório) |
| 2026-10-04 | `git pull` no cluster recusado: `Dockerfile` e `.def` locais vazios (gerados com `hpccm >` no cluster, que falha) | `git checkout -- container/Dockerfile container/osu_mpich.def` e `git pull`; gerar esses arquivos só no Mac |
| 2026-10-04 | `ibv_devinfo` não existe no login (sem permissão para instalar `libibverbs-utils`) | Placa lida em `/sys/class/infiniband`: `mlx5_0`, ACTIVE, 100 Gb/s HDR; `UCX_NET_DEVICES=mlx5_0:1` (padrão do script) está certo |
| 2026-10-05 | Job 1026343 terminou em 30 s sem medir: `Host key verification failed` (chave SSH antiga de `adano08`/172.26.0.8 no `~/.ssh/known_hosts`; o `mpiexec` usa SSH para abrir o 2º nó) | Remover as chaves antigas com `ssh-keygen -R` e submeter de novo |
| 2026-10-05 | Job 1027070: contêiner OK (~12 300 MB/s), nativo falhou (`mlx5_0:1 is not available`, UCX só com tcp) | O host não tem headers do rdma-core (`verbs.h`), então o UCX do Spack foi compilado sem InfiniBand. `spack.yaml` passa a compilar rdma-core 49.0 (Spack não tem 48.0); criado `run/smoke.pbs` (fila `testes`, 5 min) para testar antes do job oficial |
