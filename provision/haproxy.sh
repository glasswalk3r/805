#!/bin/bash

set -eo pipefail

# O Vagrant monta o /vagrant duas vezes: uma via SSH logo que a VM sobe, e outra pela entrada persistente que ele
# mesmo escreve em /etc/fstab (com _netdev). Como essa segunda é montada pelo systemd, ela entra no remote-fs.target
# e atrasa o desligamento da VM esperando a rede cair. Mascarar a unit evita esse segundo mount sem afetar o
# primeiro, que não passa pelo systemd.
systemctl mask vagrant.mount
systemctl stop vagrant.mount 2>/dev/null || true

if [[ -d /vagrant ]]
then
    mkdir -p /root/.ssh
    cp /vagrant/files/key /root/.ssh/id_rsa
    cp /vagrant/files/key.pub /root/.ssh/id_rsa.pub
    cp /vagrant/files/key.pub /root/.ssh/authorized_keys
    chmod 400 /root/.ssh/*
fi

rm -rf /etc/apt/sources.list.d/mysql.list

export DEBIAN_FRONTEND=noninteractive

apt-get update && apt-get upgrade -y && \
    apt-get install -y haproxy vim mariadb-client && \
    apt-get autoremove -y && apt-get clean

cat > /etc/haproxy/haproxy.cfg <<EOF
# Load Balancing for Galera Cluster
defaults
    log         /dev/log local0
    option  tcplog
    option  log-health-checks
    timeout connect 5s
    timeout client 30s
    timeout server 30s

listen galera
     bind    *:3306
     balance source
     mode    tcp
     option  tcpka
     option  mysql-check user haproxy
     server  node1 172.27.11.10:3306 check weight 1
     server  node2 172.27.11.20:3306 check weight 1
     server  node3 172.27.11.30:3306 check weight 1
EOF

systemctl restart haproxy
systemctl enable haproxy

set_ntp
