# Curso de MySQL da 4Linux

Este repositório é um *fork* do repositório oficial da 4Linux sobre o curso de MySQL (805).

Eu resolvi fazer modificações no repositório por questões didáticas e mudar algumas coisas que não achei boas do
repositório original.

## Diferenças do repositório da 4Linux

- Melhorias na virtualização com o Vagrant: melhor desempenho, configuração simplificada.
- Scripts: no diretório `scripts` você vai encontrar programas de CLI escritos em Python, que substituem os anteriores escritos em Perl ou ainda shell scripts usados na apostila.
- Mais bonito e mais cheiroso do que o original.

## Provisionamento

Este `Vagrantfile` provisiona 6 máquinas virtuais:
- 3 máquinas de banco de dados MySQL (Debian)
- 1 HAProxy (Debian)
- 1 servidor de monitoramento (Debian)
- 1 máquina AlmaLinux, usada para simular a instalação do MySQL em ambientes baseados no RHEL.

Para provisionar as máquinas, instale o [Vagrant](https://www.vagrantup.com/) em sua máquina, além de um *hypervisor*,
como o [VirtualBox](https://www.virtualbox.org/) ou o [Libvirt](https://libvirt.org/).

O Hyper-V não é compatível com a definição de endereços IP fixos, aliás ele é uma **bosta** para funcionar com o Vagrant.

Observe que o provisionamento das VMs depende de ter o Virtual Guest Additions funcional. Caso esteja com problemas,
verifique a seção [Resolvendo Problemas](#resolvendo-problemas) neste README.

## Obtendo os arquivos.

Clone este repositório. Se você não sabe fazer isso, não deveria estar aqui.

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

Para iniciar uma VM (se for a primeira vez, ela será criada), execute:

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

### Virtual Guest Additions desatualizado

Pode ser que a versão do Virtual Guest Additions instalada seja incompatível com a versão do Virtualbox que você tenha
instalado na máquina hospedeira.

Se isso ocorrer, você teria que resolver essa questão manualmente.

Para evitar isso, instale o plug-in do Vagrant chamado [vbguest](https://github.com/dotless-de/vagrant-vbguest):

```bash
vagrant plugin install vbguest
```

### Kernel do Linux desatualizado

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

### Travamento por falta de X.Org ou XFree86

Pode ser que o vbguest faça todo o trabalho corretamente, mas trave logo após as mensagens abaixo:

```
VirtualBox Guest Additions: Could not find the X.Org or XFree86 Window System,
skipping.
VirtualBox Guest Additions: Starting.
VirtualBox Guest Additions: reloading kernel modules and services
VirtualBox Guest Additions: kernel modules and services 7.1.18 r173720 reloaded
VirtualBox Guest Additions: NOTE: you may still consider to re-login if some
user session specific services (Shared Clipboard, Drag and Drop, Seamless or
Guest Screen Resize) were not restarted automatically
```

Use CRTL+C duas vezes para interromper e reinicie a VM (no exemplo abaixo, db2):

```bash
^C==> db2: Waiting for cleanup before exiting...
^C==> db2: Exiting immediately, without cleanup!
Unmounting Virtualbox Guest Additions ISO from: /mnt
Vagrant exited after cleanup due to external interrupt.
$ vagrant reload db2
```