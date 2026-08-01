# frozen_string_literal: true

# -*- mode: ruby -*-
# vi: set ft=ruby :

# Boxes: https://portal.cloud.hashicorp.com/vagrant/discover
boxes = {
  debian: 'debian/bookworm64',
  alma: 'almalinux/9'
}

vms = {
  db1: {ip: '10', box: :debian, script: 'debian.sh', port: 3306},
  db2: {ip: '20', box: :debian, script: 'debian.sh', port: 3307},
  db3: {ip: '30', box: :debian, script: 'debian.sh', port: 3308},
  haproxy: {cpus: 1, ip: '40', box: :debian, script: 'haproxy.sh'},
  monitor: {cpus: 2, memory: 2048, ip: '50', box: :debian, script: 'debian.sh'},
  rhel_demo: {ip: '60', box: :alma, script: 'rhel.sh', memory: 2048}
}

resources = {
  cpus: 2,
  memory: 1024
}

# IPs estáticos de cada VM, indexados pelo nome já convertido (com "-"), para o ip_resolver do hostmanager abaixo.
vm_ips = vms.each_with_object({}) { |(name, conf), h| h[name.to_s.sub('_', '-')] = "172.27.11.#{conf[:ip]}" }

Vagrant.configure('2') do |config|

  # Desativa verificação automatica de atualização do BOX a cada vagrant up.
  config.vm.box_check_update = false
  # Habilitar a linha abaixo somente no caso de problemas com o Guest Additions
  # config.vm.synced_folder '.', '/vagrant', disabled: true

  # Necessário instalar o plugin: vagrant plugin install vagrant-disksize
  # config.disksize.size = '10GB'

  config.hostmanager.enabled = true
  config.hostmanager.manage_host = false
  config.hostmanager.manage_guest = true
  config.hostmanager.include_offline = true
  config.hostmanager.ignore_private_ip = false

  # Os boxes Debian já vêm com uma linha "127.0.1.1 <hostname>" no /etc/hosts, criada antes da rede privada subir.
  # Sem isso, o resolver padrão do hostmanager entra em cada VM via SSH para descobrir o IP e acaba pegando essa
  # linha em vez do IP da rede privada, propagando "127.0.1.1 <hostname>" para o /etc/hosts de todas as VMs (e do
  # host) — o que quebra a resolução de nome usada pelo InnoDB Cluster/Galera entre os nós.
  config.hostmanager.ip_resolver = proc do |machine, _resolving_machine|
    vm_ips[machine.name.to_s]
  end

  vms.each do |name, conf|
    vm_name = name.to_s.sub('_', '-')  # symbols no Ruby não aceitam "-", já o Virtualbox não aceita nome de VMs com "_"
    config.vm.define vm_name do |my|
      args = [conf['fork'] || 'mysql', conf['sample'] || 0]
      my.vm.box = boxes[conf[:box]]
      my.vm.hostname = vm_name
      my.vm.network 'private_network', ip: "172.27.11.#{conf[:ip]}"

      if vms[name].has_key?(:port)  # executa um servidor MySQL
        my.vm.network "forwarded_port", guest: 3306, host: vms[name][:port]
      end

      my.vm.provision 'file', source: 'provision/debian-ntp.sh', destination: '/tmp/debian-ntp.sh'
      my.vm.provision 'file', source: 'provision/ssh-keys.sh', destination: '/tmp/ssh-keys.sh'
      my.vm.provision 'file', source: 'provision/ntp-br.conf', destination: '/tmp/ntp-br.conf'
      my.vm.provision 'shell', path: "provision/#{conf[:script]}", args: args

      my.vbguest.auto_update = false

      my.vm.provider 'virtualbox' do |vb|
        vb.name = vm_name
        vb.memory = conf[:memory] || resources[:memory]
        vb.cpus = conf[:cpus] || resources[:cpus]
        vb.customize ['modifyvm', :id, '--vram', '16']
        vb.customize ['modifyvm', :id, '--graphicscontroller', 'vmsvga']
        vb.customize ['storageattach', :id, '--storagectl', 'SATA Controller', '--port', '1', '--device', '0',
                      '--type', 'dvddrive', '--medium', 'emptydrive']
      end

      my.vm.provider 'libvirt' do |lv|
        lv.memory = conf[:memory] || resources[:memory]
        lv.cpus = conf[:cpus] || resources[:cpus]
        lv.cputopology :sockets => 1, :cores => conf[:cpus] || resources[:cpus], :threads => '1'
      end
    end
  end
end
