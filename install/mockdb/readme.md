[The Link Contains the List of Oracle 12c R2 Database Releases.](https://www.oracle.com/database/technologies/oracle-database-software-downloads.html)

<code>
  
unzip -d /tmp linuxx64_122*.zip
sudo groupadd -g 505 asmadmin
sudo groupadd -g 503 dba
sudo groupadd -g 504 oper
sudo groupadd nobody
sudo groupadd -g 505 asmadmin
sudo useradd -u 502 -g oinstall -G dba,asmadmin,oper -s /bin/bash -m oracle

sudo mkdir -p /u01/app/oracle/product/12/dbhome_1
sudo chown -R oracle:oinstall /u01
sudo chmod -R 775 /u01
sudo chown -R oracle:oinstall /tmp/database

hostname
/sbin/ifconfig
sudo nano /etc/hosts

sudo apt install xorg
sudo apt install gksu
sudo xhost +[myIP]

sudo nano /etc/sysctl.conf


# Oracle 12c R2 Kernel Parameters 
fs.suid_dumpable = 1
fs.aio-max-nr = 1048576
fs.file-max = 6815744
kernel.shmall = 818227
kernel.shmmax = 4189323264
kernel.shmmni = 4096
kernel.panic_on_oops = 1
# semaphores: semmsl, semmns, semopm, semmni
kernel.sem = 250 32000 100 128
net.ipv4.ip_local_port_range = 9000 65500
net.core.rmem_default=262144
net.core.rmem_max=4194304
net.core.wmem_default=262144
net.core.wmem_max=1048576

<code>
