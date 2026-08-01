#!/bin/bash

function set_root_keys() {
    local root_ssh=/root/.ssh
    local ssh_keys_path=/vagrant/files

    if [[ -d /vagrant ]]
    then
        mkdir -p "$root_ssh"

        for file in key key.pub key_teste
        do
            file_path="$ssh_keys_path/$file"

            if [[ -f $file_path ]]
            then
                cp -v $file_path $root_ssh
                chmod 400 "$root_ssh/$file"
            fi
        done
    fi
}

