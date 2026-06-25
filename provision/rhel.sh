#!/bin/bash

set -eo pipefail

mkdir -p /root/.ssh

if [[ -d /vagrant ]]
then
    for file in /vagrant/files/key /vagrant/files/key.pub /vagrant/files/key.pub
    do
        if [[ -f $file ]]
        then
            cp -v $file /root/.ssh/
        fi
    done
    chmod 400 /root/.ssh/*
fi

# O Alma Linux requer correções no instalador do Virtualbox Guest Additions para
# que este simplesmente funcione. Manter o kernel atual (que já vem com o Guest
# Additions instalado) vai evitar muita dor de cabeça
echo 'exclude=kernel*' >> /etc/dnf/dnf.conf

dnf makecache && dnf update -y && dnf install epel-release -y && dnf makecache && \
    dnf install -y wget && dnf clean packages
