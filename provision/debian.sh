#!/bin/bash

set -eo pipefail

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

apt-get update && apt-get install -y gnupg2 vim
