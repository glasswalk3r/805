#!/bin/bash

set -eo pipefail

. /tmp/debian-ntp.sh

# Remove a linha "127.0.1.1 <hostname>" que o Debian adiciona por padrão: ela atrapalha a resolução de nomes entre
# os nós do cluster (InnoDB Cluster/Galera), já que outras VMs precisam resolver o hostname para o IP da rede
# privada, e não para loopback.
sed -i '/^127\.0\.1\.1/d' /etc/hosts

# O Vagrant monta o /vagrant duas vezes: uma via SSH logo que a VM sobe, e outra pela entrada persistente que ele
# mesmo escreve em /etc/fstab (com _netdev). Como essa segunda é montada pelo systemd, ela entra no remote-fs.target
# e atrasa o desligamento da VM esperando a rede cair. Mascarar a unit evita esse segundo mount sem afetar o
# primeiro, que não passa pelo systemd.
systemctl mask vagrant.mount
systemctl stop vagrant.mount 2>/dev/null || true

set_root_keys

# Cria swap se não existir
swap_check=$(swapon -v)

if [[ -z $swap_check ]]
then
    dd if=/dev/zero of=/swapfile bs=1M count=512
    chmod 0600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile       swap    swap    defaults        0       0' >> /etc/fstab
else
    echo 'Swap file already created'
fi

export DEBIAN_FRONTEND=noninteractive

apt-get update && apt-get upgrade -y
apt-get install -y gnupg2 vim linux-image-amd64 zstd build-essential dkms chrony
apt-get dist-upgrade # force kernel upgrade
apt-get autoremove -y
apt-get clean

set_ntp
