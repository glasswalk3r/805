# MySQL

Este `Vagrantfile` provisiona 6 máquinas virtuais: 3 máquinas de banco de dados MySQL, 1 HAProxy, 1 servidor de monitoramento (todos com Debian 12) e 1 máquina AlmaLinux, usada para simular a instalação do MySQL em ambientes baseados no RHEL.

## Provisionamento

Para provisionar as máquinas, instale o [Vagrant](https://www.vagrantup.com/) em sua máquina, além de um *hypervisor*, como o [VirtualBox](https://www.virtualbox.org/) ou o [Libvirt](https://libvirt.org/). O Hyper-V não é compatível com a definição de endereços IP fixos.

Observe que o provisionamento das VMs depende de ter o Virtual Guest Additions funcional. Caso esteja com problemas,
verifique a seção [Resolvendo Problemas](#resolvendo-problemas) neste README.

## Obtendo os arquivos.

Clone este repositório ou baixe o arquivo do Vagrant em [vagrant-mysql.zip](https://storage.googleapis.com/4805-repositorio/vagrant-mysql/vagrant-mysql.zip) e descompacte-o.

```bash
unzip vagrant-mysql.zip
cd vagrant-mysql/
```

Em seguida, inicie as máquinas com o Vagrant:

```bash
vagrant up
```

Verifique quais máquinas estão disponíveis:

```bash
vagrant status
Current machine states:

db1             not created (virtualbox)
db2             not created (virtualbox)
db3             not created (virtualbox)
haproxy         not created (virtualbox)
monitor         not created (virtualbox)
rhel-demo       not created (virtualbox)

This environment represents multiple VMs. The VMs are all listed
above with their current state. For more information about a specific
VM, run `vagrant status NAME`.
```

Para criar ou iniciar uma VM, execute:

```bash
vagrant up db1
```

Para acessá-la via SSH:

```bash
vagrant ssh db1
```

## Máquinas

| Nome      | Distro        | IP           |
| --------- | ------------- | ------------ |
| db1       | Debian 12     | 172.27.11.10 |
| db2       | Debian 12     | 172.27.11.20 |
| db3       | Debian 12     | 172.27.11.30 |
| haproxy   | Debian 12     | 172.27.11.40 |
| monitor   | Debian 12     | 172.27.11.50 |
| rhel-demo | AlmaLinux EL9 | 172.27.11.60 |

## Resolvendo problemas

Pode ser que a versão do Virtual Guest Additions instalada seja incompatível com a versão do Virtualbox que você tenha
instalado na máquina hospedeira.

Se isso ocorrer, você teria que resolver essa questão manualmente.

Para evitar isso, instale o plug-in do Vagrant chamado vbguest:

```bash
vagrant plugin install vbguest
```

Caso você já tenha o plug-in instalado, pode ser que vbguest falhe por não achar o pacote correto para instalar e criar
o módulo do Virtual Guest Additions junto ao kernel atualizado.

Para que isso funcione, ajuste a linha de configuração no `Vagrantfile` conforme mostrado abaixo:

```ruby
my.vbguest.auto_update = false
```

Repita o provisionamento com o Vagrant (o exemplo abaixo usa a VM "db1"):

```bash
vagrant reload db1 --provision
```

Isso vai reiniciar a VM e atualizar os pacotes, e aí com o kernel novo instalado, o vbguest conseguirá fazer o seu
trabalho. Então permita que ele faça seu trabalho alterando a mesma linha no `Vagrantfile` para que fique igual a
`true`, e então repita o mesmo comando de `reload` para isto aconteça.
