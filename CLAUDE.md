# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

This is a personal fork of 4Linux's course 805 (MySQL) repository. It is a Vagrant lab environment for
practicing MySQL/Galera cluster administration, plus a small set of Python CLI scripts (rewrites of the
original Perl/shell scripts used in the course workbook) for generating test load. It is not an application
with a build/test/lint pipeline in the traditional sense — most "verification" here means provisioning VMs
and checking the resulting cluster state by hand.

Content is primarily in Portuguese (comments, docs, provisioning messages) — match that language when
editing existing docs/scripts unless asked otherwise.

## Repository layout

- `Vagrantfile` — defines 6 VMs (`vms` hash): `db1`/`db2`/`db3` (Debian, MySQL/Galera nodes on
  172.27.11.10/20/30, each with a forwarded port to host 3306/3307/3308), `haproxy` (172.27.11.40, load
  balances the 3 db nodes), `monitor` (172.27.11.50), and `rhel-demo` (AlmaLinux, 172.27.11.60, used only to
  demo RHEL-family installs). All VMs are on the private network `172.27.11.0/24`.
- `Clusterfile` — a second, unrelated Vagrantfile-like file for a separate MySQL NDB Cluster lab
  (`data1`/`data2`/`mgm`/`sql`), provisioned by `provision/ndb.sh`. Despite the name it's Ruby, evaluated
  independently of `Vagrantfile`.
- `provision/` — shell provisioning scripts run by Vagrant:
  - `debian.sh` — base provisioning for Debian nodes (swap file, kernel/package upgrades, NTP via chrony).
  - `haproxy.sh` — installs and configures HAProxy in front of the 3 Galera nodes (`/etc/haproxy/haproxy.cfg`
    is generated inline from a heredoc — edit it there, not on a live VM, if the LB config needs to change).
  - `rhel.sh` — AlmaLinux/RHEL-family provisioning (uses `dnf`, `timedatectl`, `chronyd`).
  - `debian-ntp.sh` — shared `set_ntp()` function sourced by the other Debian-family scripts; configures
    Brazilian NTP pools (`ntp-br.conf`) and America/Sao_Paulo timezone.
  - All provisioning scripts copy `files/key`/`files/key.pub` into `/root/.ssh` for inter-node SSH.
- `scripts/` — Python 3.12 CLI tools (see `scripts/README.md`), dependency-managed via `uv` from the root
  `pyproject.toml`:
  - `gen-load.py` — connects to a local MySQL instance (credentials from `.env`, database `curso`) and
    inserts random rows into a `seed` table in a loop, to simulate write load; has a progress bar (`tqdm`)
    and is preferred over a shell loop because it authenticates once instead of per-insert.
  - `gen-users.py` — smaller ad-hoc MySQL connection example.
- `files/` — reference SQL/Perl/shell material used during the course (PITR practice scripts, Galera
  `wsrep_*` monitoring one-liners in Perl, an NDB `config.ini`, a `sales`/`chunks` sample dataset, and
  `4linux/` with the original unmodified course scripts for comparison). Treat this directory as reference
  material, not code to be refactored — it mirrors the original course content deliberately.
- `exercicios/` — per-lesson (`aula-NN`) exercise scripts/SQL matching the course workbook.
- `sakila.tar.xz` — the standard MySQL Sakila sample database archive, loaded onto lab VMs as needed.

## Working with the Vagrant environment

```bash
vagrant up            # create/start all VMs
vagrant up db1         # create/start a single VM
vagrant status         # list VM states
vagrant ssh db1         # SSH into a VM
vagrant reload db1 --provision   # re-run provisioning (e.g. after a kernel update via vbguest)
```

- `my.vbguest.auto_update` in `Vagrantfile` controls whether the VirtualBox Guest Additions plugin
  auto-updates; toggling it to `false` then `true` (per the README's troubleshooting section) is the known
  workaround when `vbguest` can't find a matching kernel package.
- Requires the Vagrant `vbguest` plugin (`vagrant plugin install vbguest`) and, for fixed private-network
  IPs, is not compatible with the Hyper-V provider — use VirtualBox or Libvirt.

## Working with the Python scripts

```bash
uv venv .venv
uv sync
. .venv/bin/activate
./scripts/gen-load.py --help
```

- All script dependencies are declared in the single root `pyproject.toml` (managed by `uv`, not per-script).
- `ruff` is the configured dev dependency for linting (`uv run ruff check .`); no custom ruff config is
  present beyond the dependency itself.
- `gen-load.py` reads `USERNAME`/`PASSWORD` from a root `.env` file (gitignored) and connects to
  `localhost`/database `curso` — run it from inside a VM (or with the relevant port forwarded) rather than
  expecting it to reach the cluster from the host.
