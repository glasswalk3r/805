#!/bin/bash

function set_ntp() {
    local chrony_conf_dir=/etc/chrony

    timedatectl set-timezone America/Sao_Paulo
    cp -v /vagrant/provision/ntp-br.conf "$chrony_conf_dir/conf.d"
    chmod 644 "$chrony_conf_dir/conf.d/ntp-br.conf"
    sed -i -e '/pool/d' "$chrony_conf_dir/chrony.conf"
    systemctl restart chrony
    timedatectl status
}
