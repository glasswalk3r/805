#!/bin/bash

set -eo pipefail

. /tmp/ssh-keys.sh

# O Vagrant monta o /vagrant duas vezes: uma via SSH logo que a VM sobe, e outra pela entrada persistente que ele
# mesmo escreve em /etc/fstab (com _netdev). Como essa segunda é montada pelo systemd, ela entra no remote-fs.target
# e atrasa o desligamento da VM esperando a rede cair. Mascarar a unit evita esse segundo mount sem afetar o
# primeiro, que não passa pelo systemd.
systemctl mask vagrant.mount
systemctl stop vagrant.mount 2>/dev/null || true

set_root_keys

# O Alma Linux requer correções no instalador do Virtualbox Guest Additions para
# que este simplesmente funcione. Manter o kernel atual (que já vem com o Guest
# Additions instalado) vai evitar muita dor de cabeça
echo 'exclude=kernel*' >> /etc/dnf/dnf.conf

dnf makecache
dnf update -y
dnf install epel-release -y
dnf makecache
dnf install -y wget chrony
dnf clean packages

timedatectl set-timezone America/Sao_Paulo
sed -i -e '/pool/d' /etc/chrony.conf
cat /tmp/ntp-br.conf >> /etc/chrony.conf
systemctl restart chronyd
timedatectl status
